"""Position-independent window kernels for the interpreter. Kernel module.

Every output at row t is computed from its own trailing window only, in a fixed order (oldest value
first, plain sequential sums, two-pass variances), never with an online update carried from earlier
rows. So results are bit-identical when rows are removed from the END of a frame (truncation) and
when rows are removed from its START (start cuts): no output can depend on where the frame began.

Value rules (knownness is tracked separately by the interpreter): a window that contains a NaN value
gives NaN; rows before the first full window give NaN. Arrays are (T, K) float64, one column per
symbol. numba-compiled (no on-disk cache).
"""
from __future__ import annotations

import math

import numpy as np

try:
    import numba
    _jit = numba.njit(cache=False, nogil=True)
except Exception:  # pragma: no cover
    def _jit(f):
        return f

SUM, MEAN, STD, MIN, MAX, MEDIAN, RANK, ZSCORE = range(8)


@_jit
def known_run(known, n):
    """out[t, j] = known[t-n+1 .. t, j] all True (and t >= n-1). Integer counting: exact."""
    T, K = known.shape
    out = np.zeros((T, K), dtype=np.bool_)
    for j in range(K):
        bad = 0
        for t in range(T):
            if not known[t, j]:
                bad += 1
            if t >= n and not known[t - n, j]:
                bad -= 1
            if t >= n - 1 and bad == 0:
                out[t, j] = True
    return out


@_jit
def _window_has_nan(x, t, n, j):
    for i in range(n):
        v = x[t - n + 1 + i, j]
        if v != v:
            return True
    return False


@_jit
def roll(x, n, op):
    T, K = x.shape
    out = np.full((T, K), np.nan)
    buf = np.empty(n)
    for j in range(K):
        for t in range(n - 1, T):
            if _window_has_nan(x, t, n, j):
                continue
            s0 = t - n + 1
            if op == SUM or op == MEAN or op == STD or op == ZSCORE:
                s = 0.0
                for i in range(n):
                    s += x[s0 + i, j]
                if op == SUM:
                    out[t, j] = s
                    continue
                m = s / n
                if op == MEAN:
                    out[t, j] = m
                    continue
                if n < 2:
                    continue
                ss = 0.0
                for i in range(n):
                    d = x[s0 + i, j] - m
                    ss += d * d
                sd = math.sqrt(ss / (n - 1))
                if op == STD:
                    out[t, j] = sd
                elif sd > 0.0:
                    out[t, j] = (x[t, j] - m) / sd
            elif op == MIN or op == MAX:
                v = x[s0, j]
                for i in range(1, n):
                    w = x[s0 + i, j]
                    if (op == MIN and w < v) or (op == MAX and w > v):
                        v = w
                out[t, j] = v
            elif op == MEDIAN:
                for i in range(n):
                    buf[i] = x[s0 + i, j]
                b = np.sort(buf)
                if n % 2 == 1:
                    out[t, j] = b[n // 2]
                else:
                    out[t, j] = (b[n // 2 - 1] + b[n // 2]) / 2.0
            else:  # RANK: share of the window (current included) <= the current value, in (0, 1]
                c = 0
                cur = x[t, j]
                for i in range(n):
                    if x[s0 + i, j] <= cur:
                        c += 1
                out[t, j] = c / n
    return out


@_jit
def wmean(x, w):
    """Weighted mean over the last m = len(w) rows; w[0] weights the OLDEST row, w[m-1] the newest."""
    T, K = x.shape
    m = len(w)
    W = 0.0
    for i in range(m):
        W += w[i]
    out = np.full((T, K), np.nan)
    for j in range(K):
        for t in range(m - 1, T):
            if _window_has_nan(x, t, m, j):
                continue
            s = 0.0
            for i in range(m):
                s += w[i] * x[t - m + 1 + i, j]
            out[t, j] = s / W
    return out


@_jit
def rsi_finite(x, w):
    """Centred RSI over the last m = len(w) changes: (G - L) / (G + L), G and L the w-weighted sums of
    gains and losses (w[0] oldest). Uses rows t-m .. t. NaN when G + L == 0."""
    T, K = x.shape
    m = len(w)
    out = np.full((T, K), np.nan)
    for j in range(K):
        for t in range(m, T):
            if _window_has_nan(x, t, m + 1, j):
                continue
            G = 0.0
            Ls = 0.0
            for i in range(m):
                k = t - m + 1 + i
                d = x[k, j] - x[k - 1, j]
                if d > 0.0:
                    G += w[i] * d
                elif d < 0.0:
                    Ls += w[i] * (-d)
            if G + Ls > 0.0:
                out[t, j] = (G - Ls) / (G + Ls)
    return out


@_jit
def atr_finite(h, l, c, w):
    """w-weighted mean (w[0] oldest, normalised) of the last m = len(w) true ranges
    max(h - l, |h - prev c|, |l - prev c|). Uses rows t-m .. t."""
    T, K = h.shape
    m = len(w)
    W = 0.0
    for i in range(m):
        W += w[i]
    out = np.full((T, K), np.nan)
    for j in range(K):
        for t in range(m, T):
            if _window_has_nan(h, t, m, j) or _window_has_nan(l, t, m, j) or _window_has_nan(c, t, m + 1, j):
                continue
            s = 0.0
            for i in range(m):
                k = t - m + 1 + i
                pc = c[k - 1, j]
                tr = h[k, j] - l[k, j]
                a = abs(h[k, j] - pc)
                b = abs(l[k, j] - pc)
                if a > tr:
                    tr = a
                if b > tr:
                    tr = b
                s += w[i] * tr
            out[t, j] = s / W
    return out


@_jit
def corr(x, y, n):
    """Rolling covariance / (std x * std y), each ddof 1, two-pass within the window."""
    T, K = x.shape
    out = np.full((T, K), np.nan)
    if n < 2:
        return out
    for j in range(K):
        for t in range(n - 1, T):
            if _window_has_nan(x, t, n, j) or _window_has_nan(y, t, n, j):
                continue
            s0 = t - n + 1
            sx = 0.0
            sy = 0.0
            for i in range(n):
                sx += x[s0 + i, j]
                sy += y[s0 + i, j]
            mx = sx / n
            my = sy / n
            cxy = 0.0
            vx = 0.0
            vy = 0.0
            for i in range(n):
                dx = x[s0 + i, j] - mx
                dy = y[s0 + i, j] - my
                cxy += dx * dy
                vx += dx * dx
                vy += dy * dy
            den = math.sqrt(vx / (n - 1)) * math.sqrt(vy / (n - 1))
            if den > 0.0:
                out[t, j] = (cxy / (n - 1)) / den
    return out


@_jit
def log_ratio_std(x, n):
    """std (ddof 1, two-pass) of the last n log ratios log(x_k / x_k-1); uses rows t-n .. t."""
    T, K = x.shape
    out = np.full((T, K), np.nan)
    if n < 2:
        return out
    lr = np.empty(n)
    for j in range(K):
        for t in range(n, T):
            if _window_has_nan(x, t, n + 1, j):
                continue
            ok = True
            for i in range(n):
                k = t - n + 1 + i
                q = x[k, j] / x[k - 1, j]
                if not (q > 0.0) or q == np.inf:
                    ok = False
                    break
                lr[i] = math.log(q)
            if not ok:
                continue
            s = 0.0
            for i in range(n):
                s += lr[i]
            m = s / n
            ss = 0.0
            for i in range(n):
                d = lr[i] - m
                ss += d * d
            out[t, j] = math.sqrt(ss / (n - 1))
    return out


@_jit
def hold_window(el, xl, es, xs, h):
    """State in {-1, 0, +1} at t = the transition machine run FROM FLAT over rows t-h+1 .. t.
    Flat: enter_long and not enter_short -> +1; enter_short and not enter_long -> -1.
    Long: enter_short -> -1, else exit_long -> 0. Short: enter_long -> +1, else exit_short -> 0."""
    T, K = el.shape
    out = np.zeros((T, K))
    for j in range(K):
        for t in range(h - 1, T):
            st = 0.0
            for k in range(t - h + 1, t + 1):
                a = el[k, j]
                b = xl[k, j]
                c = es[k, j]
                d = xs[k, j]
                if st == 0.0:
                    if a and not c:
                        st = 1.0
                    elif c and not a:
                        st = -1.0
                elif st == 1.0:
                    if c:
                        st = -1.0
                    elif b:
                        st = 0.0
                else:
                    if a:
                        st = 1.0
                    elif d:
                        st = 0.0
            out[t, j] = st
    return out


@_jit
def event_mean(vals, new, n):
    """Mean of the last n EVENT values (rows where new is True), held until the next event.
    Returns (values, known): known once n events exist in the frame."""
    T, K = vals.shape
    out = np.full((T, K), np.nan)
    kn = np.zeros((T, K), dtype=np.bool_)
    ev = np.empty(T)
    for j in range(K):
        cnt = 0
        cur = np.nan
        for t in range(T):
            if new[t, j]:
                ev[cnt] = vals[t, j]
                cnt += 1
                if cnt >= n:
                    s = 0.0
                    for i in range(cnt - n, cnt):
                        s += ev[i]
                    cur = s / n
            if cnt >= n:
                out[t, j] = cur
                kn[t, j] = True
    return out, kn


def decay_weights(n: int, m: int, r: float) -> np.ndarray:
    """w[i] = r ** (m - 1 - i), i = 0 (oldest) .. m - 1 (newest = weight 1)."""
    k = np.arange(m - 1, -1, -1, dtype=np.float64)
    return np.power(float(r), k)
