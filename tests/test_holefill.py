"""U4: holes inside a universe symbol's life are filled from the daily files of the same archive
(checksum required), an hour already held must equal the daily row (else stop: revision), hours no
daily file has stay holes, nothing outside the life is added. Synthetic zips in a temp folder; the
network is replaced by a fake."""
import hashlib
import io
import json
import zipfile

import numpy as np
import pandas as pd
import pytest

from omr import data

HOUR_MS = 3_600_000
T0 = int(pd.Timestamp("2022-02-20 00:00", tz="UTC").value // 10 ** 6)


def _rows(first_ms, n, seed, kind="klines"):
    rng = np.random.default_rng(seed)
    out = []
    px = 100.0
    for i in range(n):
        t = first_ms + i * HOUR_MS
        o = px
        c = px * float(np.exp(rng.normal(0, 0.01)))
        h, l_ = max(o, c) * 1.001, min(o, c) * 0.999
        px = c
        if kind == "klines":
            out.append([t, o, h, l_, c, 10.0 + i, t + HOUR_MS - 1, 1000.0 + i, 5 + i % 7, 4.0, 400.0, 0])
        else:
            out.append([t, o, h, l_, c, 0, t + HOUR_MS - 1, 0, 3600, 0, 0, 0])
    return out


def _csv(rows):
    return ("\n".join(",".join(repr(v) if isinstance(v, float) else str(v) for v in r) for r in rows) + "\n").encode()


def _zip(path, rows, checksum=True, bad_checksum=False):
    path.parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr(path.stem + ".csv", _csv(rows))
    body = buf.getvalue()
    path.write_bytes(body)
    if checksum:
        sha = hashlib.sha256(body).hexdigest() if not bad_checksum else "0" * 64
        data._checksum_path(path).write_bytes(f"{sha}  {path.name}\n".encode())
    return body


@pytest.fixture
def raw_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(data, "RAW_DIR", tmp_path / "raw")
    return tmp_path / "raw"


def _daily(symbol, ds, day):
    return data._daily_items(symbol, day, (ds,))[0]


def _base(rows, drop):
    df, _ = data.parse_kline_bytes(_csv([r for r in rows if r[0] not in drop]))
    return df


def test_u4_a_hole_is_filled_from_the_daily_file_and_the_held_hours_are_compared(raw_dir):
    rows = _rows(T0, 24 * 10, 1)                                 # 2022-02-20 .. 2022-03-01
    day = "2022-02-26"
    lo = int(pd.Timestamp(day, tz="UTC").value // 10 ** 6)
    hole = {lo + k * HOUR_MS for k in range(24)} | {lo + 24 * HOUR_MS + k * HOUR_MS for k in range(5)}
    base = _base(rows, hole)
    it = _daily("AAAUSDT", "klines", day)
    _zip(it[3], [r for r in rows if lo <= r[0] < lo + 24 * HOUR_MS])
    life = (rows[0][0], rows[-1][0])
    merged, info = data.fill_from_daily("klines", base, [it], *life)
    assert info["filled"] == 24 and info["compared"] == 0 and list(info["daily_files"]) == [day]
    kl, _ = data._grid_klines(merged, pd.Timestamp(life[1], unit="ms", tz="UTC"))
    assert int(kl["is_gap"].sum()) == 5                          # the next day had no daily file: stays a hole
    full, _ = data._grid_klines(_base(rows, set()), pd.Timestamp(life[1], unit="ms", tz="UTC"))
    filled = kl.index[~kl["is_gap"].to_numpy()]
    assert np.array_equal(kl.loc[filled].to_numpy(dtype=float), full.loc[filled].to_numpy(dtype=float))
    # a daily file for a day the base holds in full: every hour compared, nothing added
    it2 = _daily("AAAUSDT", "klines", "2022-02-21")
    lo2 = int(pd.Timestamp("2022-02-21", tz="UTC").value // 10 ** 6)
    _zip(it2[3], [r for r in rows if lo2 <= r[0] < lo2 + 24 * HOUR_MS])
    _, info2 = data.fill_from_daily("klines", base, [it2], *life)
    assert info2["filled"] == 0 and info2["compared"] == 24


def test_u4_a_held_hour_that_differs_from_the_daily_row_stops_the_fill(raw_dir):
    rows = _rows(T0, 24 * 4, 2)
    day = "2022-02-21"
    lo = int(pd.Timestamp(day, tz="UTC").value // 10 ** 6)
    base = _base(rows, {lo + 3 * HOUR_MS})                       # one hole on that day
    drows = [list(r) for r in rows if lo <= r[0] < lo + 24 * HOUR_MS]
    drows[10][4] = drows[10][4] * (1 + 1e-12)                    # a held hour revised in the daily file
    it = _daily("AAAUSDT", "klines", day)
    _zip(it[3], drows)
    with pytest.raises(data.DailyRevision, match="close"):
        data.fill_from_daily("klines", base, [it], rows[0][0], rows[-1][0])


def test_u4_only_checksum_verified_files_are_used_and_nothing_outside_the_life_is_added(raw_dir):
    rows = _rows(T0, 24 * 6, 3, kind="mark")
    life = (rows[24][0], rows[24 * 5 - 1][0])                    # life: 2022-02-21 .. 2022-02-24
    df, _ = data.parse_mark_bytes(_csv([r for r in rows if life[0] <= r[0] <= life[1] and
                                        not (rows[48][0] <= r[0] < rows[72][0])]))
    no_chk = _daily("AAAUSDT", "mark_klines", "2022-02-22")
    _zip(no_chk[3], rows[48:72], checksum=False)
    merged, info = data.fill_from_daily("mark_klines", df, [no_chk], *life)
    assert info["filled"] == 0 and len(merged) == len(df)        # no CHECKSUM beside it: not read
    bad = _daily("AAAUSDT", "mark_klines", "2022-02-22")
    _zip(bad[3], rows[48:72], bad_checksum=True)
    with pytest.raises(data.DataIntegrityError):
        data.fill_from_daily("mark_klines", df, [bad], *life)
    good = [_daily("AAAUSDT", "mark_klines", d) for d in ("2022-02-20", "2022-02-22", "2022-02-25")]
    _zip(good[0][3], rows[0:24])
    _zip(good[1][3], rows[48:72])
    _zip(good[2][3], rows[120:144])
    merged, info = data.fill_from_daily("mark_klines", df, good, *life)
    assert info["filled"] == 24                                  # only the day inside the life
    t = merged.open_time_ms.to_numpy()
    assert t.min() == life[0] and t.max() == life[1] and len(t) == 24 * 4


def test_u4_fetch_daily_requires_the_checksum_and_remembers_a_404(raw_dir, monkeypatch):
    calls = []
    store = {}

    def fake_get(url, params=None, retries=5, timeout=60):
        calls.append(url)
        return store.get(url)

    monkeypatch.setattr(data, "http_get", fake_get)
    monkeypatch.setattr(data.C, "DOWNLOAD_PAUSE_S", 0.0)
    it = _daily("AAAUSDT", "klines", "2022-02-26")
    assert data._fetch_daily_polite(it) == "missing" and len(calls) == 1
    assert data._fetch_daily_polite(it) == "cached-missing" and len(calls) == 1      # no second request
    it2 = _daily("BBBUSDT", "klines", "2022-02-26")
    body = b"PK-not-really-a-zip"
    store[it2[2]] = body
    assert data._fetch_daily_polite(it2) == "nochecksum" and not it2[3].exists()
    store[it2[2] + ".CHECKSUM"] = ("0" * 64 + "  x\n").encode()
    assert data._fetch_daily_polite(it2).startswith("failed") and not it2[3].exists()
    store[it2[2] + ".CHECKSUM"] = (hashlib.sha256(body).hexdigest() + "  x\n").encode()
    assert data._fetch_daily_polite(it2) == "ok" and it2[3].read_bytes() == body
    n = len(calls)
    assert data._fetch_daily_polite(it2) == "cached" and len(calls) == n


def test_u4_universe_symbol_holes_before_and_after(raw_dir):
    """The per-symbol path of `data universe` (build only, files cached): monthly files with a 3-day hole
    in klines, mark and index; daily files exist for two of the three days."""
    first = int(pd.Timestamp("2022-02-01", tz="UTC").value // 10 ** 6)
    n = 24 * 28
    kr, mr = _rows(first, n, 4), _rows(first, n, 5, kind="mark")
    hole_days = ("2022-02-10", "2022-02-11", "2022-02-12")
    lo = int(pd.Timestamp(hole_days[0], tz="UTC").value // 10 ** 6)
    hole = {lo + k * HOUR_MS for k in range(72)}
    items = []
    for ds, rows in (("klines", kr), ("mark_klines", mr), ("index_klines", mr)):
        it = data._monthly_item(ds, "AAAUSDT", "2022-02")
        _zip(it[3], [r for r in rows if r[0] not in hole], checksum=False)
        items.append(it)
        for d in hole_days[:2]:
            dl = int(pd.Timestamp(d, tz="UTC").value // 10 ** 6)
            _zip(_daily("AAAUSDT", ds, d)[3], [r for r in rows if dl <= r[0] < dl + 24 * HOUR_MS])
    fz =data._monthly_item("funding", "AAAUSDT", "2022-02")
    fz[3].parent.mkdir(parents=True, exist_ok=True)
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        z.writestr("f.csv", "".join(f"{first + 8 * k * HOUR_MS},8,0.0001\n" for k in range(84)))
    fz[3].write_bytes(buf.getvalue())
    items.append(fz)
    fill = data._HoleFill(build_only=True, workers=1)
    res = data._universe_filled("AAAUSDT", items, None, fill)
    rep = fill.report()
    assert {ds: sum(v.values()) for ds, v in rep["missing_hours_before"].items()} == \
        {"klines": 72, "mark_klines": 72, "index_klines": 72}
    assert {ds: sum(v.values()) for ds, v in rep["missing_hours_after"].items()} == \
        {"klines": 24, "mark_klines": 24, "index_klines": 24}
    assert rep["rows_filled"] == {"klines": 48, "mark_klines": 48, "index_klines": 48}
    assert rep["unfilled"]["klines"] == [("AAAUSDT", "2022-02-12")]
    kl = res["tables"]["klines"]
    assert int(kl["is_gap"].sum()) == 24 and res["meta"]["klines"]["daily_rows_filled"] == 48
    assert sorted(res["meta"]["klines"]["daily_files"]) == list(hole_days[:2])
    # every hour the monthly files hold is unchanged by the fill (the revision check of `data universe`)
    plain = data.build_universe_symbol("AAAUSDT", items, None)["tables"]["klines"]
    keep = ~plain["is_gap"].to_numpy()
    assert np.array_equal(plain[keep].to_numpy(dtype=float), kl[keep].to_numpy(dtype=float))
    assert not data._revised("klines", plain, kl)


def test_r_a_core_tables_are_filled_by_the_same_rule_and_nothing_else_changes(raw_dir):
    """R-A: one of the ten (stored klines grid with a 2-day hole, mark and index bars missing there): the hole is
    filled from the daily files, every other row is bit-identical, the grid (same snapshot end) is unchanged,
    the meta keeps its keys; a held hour that differs from the daily row stops the fill."""
    first = int(pd.Timestamp("2022-02-20", tz="UTC").value // 10 ** 6)
    kr, mr = _rows(first, 24 * 12, 6), _rows(first, 24 * 12, 7, kind="mark")
    days = ("2022-02-26", "2022-02-27")
    lo = int(pd.Timestamp(days[0], tz="UTC").value // 10 ** 6)
    hole = {lo + k * HOUR_MS for k in range(48)}
    last = pd.Timestamp(kr[-1][0], unit="ms", tz="UTC")
    kl, info = data._grid_klines(_base(kr, hole), last)
    mk = data._bars_table(data.parse_mark_bytes(_csv([r for r in mr if r[0] not in hole]))[0], data.MARK_COLS)
    for ds, rows in (("klines", kr), ("mark_klines", mr), ("index_klines", mr)):
        for d in days:
            dl = int(pd.Timestamp(d, tz="UTC").value // 10 ** 6)
            _zip(_daily("BTCUSDT", ds, d)[3], [r for r in rows if dl <= r[0] < dl + 24 * HOUR_MS])
    metas = {"klines": {"rows": len(kl), "unit_check": {"x": 1}, "sha256": "s", **info},
             "mark_klines": {"rows": len(mk), "source": "bulk"}, "index_klines": {"rows": len(mk)}}
    fill = data._HoleFill(build_only=True, workers=1)
    t, m = data.fill_core_tables("BTCUSDT", {"klines": kl, "mark_klines": mk, "index_klines": mk}, metas, fill)
    assert t["klines"].index.equals(kl.index) and int(t["klines"]["is_gap"].sum()) == 0
    keep = ~kl["is_gap"].to_numpy()
    assert np.array_equal(t["klines"][keep].to_numpy(dtype=float), kl[keep].to_numpy(dtype=float))
    assert not data._revised("klines", kl, t["klines"])
    for ds in ("mark_klines", "index_klines"):
        assert len(t[ds]) == len(mk) + 48 and t[ds].loc[mk.index].equals(mk)
    assert m["klines"]["unit_check"] == {"x": 1} and "sha256" not in m["klines"] and m["klines"]["gap_count"] == 0
    assert m["klines"]["daily_rows_filled"] == 48 and sorted(m["mark_klines"]["daily_files"]) == list(days)
    assert m["mark_klines"]["source"] == "bulk" and m["mark_klines"]["rows"] == len(mk) + 48
    rec = fill.report()["core_symbols"]["BTCUSDT"]
    assert rec["klines"] == {"filled_hours": {"dev": 48}, "left_hours": {}}
    bad = kl.copy()                                                  # a stored real bar that the archive disagrees with
    r = int(np.nonzero(keep)[0][100])
    bad.iloc[r, bad.columns.get_loc("volume")] += 1.0
    ri = bad.index[r]
    dl = pd.Timestamp(ri.normalize())
    _zip(_daily("BTCUSDT", "klines", str(dl.date()))[3],
         [x for x in kr if dl.value // 10 ** 6 <= x[0] < dl.value // 10 ** 6 + 24 * HOUR_MS])
    j = r + 1 if bad.index[r + 1].normalize() == dl else r - 1
    bad.iloc[j, bad.columns.get_loc("is_gap")] = True                 # a hole on that day: its file is read
    with pytest.raises(data.DailyRevision):
        data.fill_core_tables("BTCUSDT", {"klines": bad, "mark_klines": mk, "index_klines": mk}, metas,
                              data._HoleFill(build_only=True, workers=1))


# ---------------------------------------------------------------- R-G: hardening of the hole fill (fix pass 5)

def test_r_g1_a_missing_marker_only_for_a_day_a_week_old(raw_dir, monkeypatch):
    calls = []
    monkeypatch.setattr(data, "http_get", lambda url, **k: calls.append(url))
    monkeypatch.setattr(data.C, "DOWNLOAD_PAUSE_S", 0.0)
    monkeypatch.setattr(data, "_utcnow", lambda: pd.Timestamp("2026-11-20 05:00", tz="UTC"))
    young = _daily("AAAUSDT", "klines", "2026-11-15")                   # 5 days old: not in the archive yet
    assert data._fetch_daily_polite(young) == "missing" and not data._missing_marker(young[3]).exists()
    assert data._fetch_daily_polite(young) == "missing" and len(calls) == 2           # asked again
    old = _daily("AAAUSDT", "klines", "2026-11-13")                     # 7 days old: remembered
    assert data._fetch_daily_polite(old) == "missing" and data._missing_marker(old[3]).exists()
    assert data._fetch_daily_polite(old) == "cached-missing" and len(calls) == 3


def test_r_g2_a_daily_file_must_equal_its_manifest_pin(raw_dir):
    rows = _rows(T0, 24 * 4, 8)
    day = "2022-02-21"
    lo = int(pd.Timestamp(day, tz="UTC").value // 10 ** 6)
    base = _base(rows, {lo + 5 * HOUR_MS})
    it = _daily("AAAUSDT", "klines", day)
    body = _zip(it[3], [r for r in rows if lo <= r[0] < lo + 24 * HOUR_MS])
    good = {day: hashlib.sha256(body).hexdigest()}
    merged, info = data.fill_from_daily("klines", base, [it], rows[0][0], rows[-1][0], pins=good)
    assert info["filled"] == 1 and info["daily_files"] == good
    with pytest.raises(data.DailyPinMismatch):
        data.fill_from_daily("klines", base, [it], rows[0][0], rows[-1][0], pins={day: "0" * 64})
    assert issubclass(data.DailyPinMismatch, data.DailyRevision)          # stops `data universe` like a revision
    kl, _ = data._grid_klines(base, pd.Timestamp(rows[-1][0], unit="ms", tz="UTC"))
    with pytest.raises(data.DailyPinMismatch):
        data.fill_core_tables("AAAUSDT", {"klines": kl},
                              {"klines": {"daily_files": {day: "f" * 64}}}, data._HoleFill(True, 1))


STEPS = ["manifest_new", "journal", ("kept_old", 0), ("moved_new", 0), ("kept_old", 1), ("moved_new", 1),
         "manifest", "cleanup"]


@pytest.fixture
def commit_dir(tmp_path, monkeypatch):
    """A scratch data folder: two stored tables and a manifest; staged: one replacement and one new table."""
    monkeypatch.setattr(data, "DATA_DIR", tmp_path)
    monkeypatch.setattr(data, "MANIFEST", tmp_path / "manifest.json")
    data._CACHE.clear()
    raw = {s: data._grid_klines(_base(_rows(T0, 48, i), set()), pd.Timestamp(T0 + 47 * HOUR_MS, unit="ms", tz="UTC"))[0]
           for i, s in enumerate(("AAAUSDT", "BBBUSDT", "CCCUSDT"))}
    man = {"datasets": {"klines": {}}, "research_hash": "old"}
    for s in ("AAAUSDT", "BBBUSDT"):
        p = data.stored_path("klines", s)
        p.parent.mkdir(parents=True, exist_ok=True)
        raw[s].to_parquet(p)
        man["datasets"]["klines"][s] = {"sha256": data.sha256_file(p)}
    (tmp_path / "manifest.json").write_text(json.dumps(man), encoding="ascii")
    new_man = json.loads(json.dumps(man))
    new_man["research_hash"] = "new"
    pairs = []
    for s, df in (("AAAUSDT", raw["AAAUSDT"].iloc[:40]), ("CCCUSDT", raw["CCCUSDT"])):
        fp = data.stored_path("klines", s)
        new = fp.with_suffix(".parquet.new")
        df.to_parquet(new)
        new_man["datasets"]["klines"][s] = {"sha256": data.sha256_file(new)}
        pairs.append((new, fp))
    yield tmp_path, man, new_man, pairs
    data._CACHE.clear()


def _consistent(root, want):
    """Every manifest entry's file matches its pin, no journal or kept / staged file is left, and the state is
    the wanted one."""
    m = data.load_manifest()
    assert m["research_hash"] == want
    for s in m["datasets"]["klines"]:
        data._read_stored("klines", s, m, cache=False)                    # raises on a hash mismatch
    left = [p.name for p in root.rglob("*") if p.suffix in (".old", ".new") or p.name.endswith(".journal.json")
            or p.name == ".commit_journal.json"]
    assert left == []
    assert data.stored_path("klines", "CCCUSDT").exists() == (want == "new")



@pytest.mark.parametrize("step", range(len(STEPS)))
def test_r_g3_a_crash_at_any_commit_step_recovers_to_one_state(commit_dir, step):
    root, man, new_man, pairs = commit_dir

    class Crash(Exception):
        pass

    def hook(s):
        if s == STEPS[step]:
            raise Crash(str(s))
    with pytest.raises(Crash):
        data.commit_tables(pairs, new_man, log=lambda s: None, hook=hook)
    logs = []
    state = data.recover_commit(log=logs.append)
    want = "new" if STEPS[step] in ("manifest", "cleanup") else "old"
    assert state == want and len(logs) == 1 and ("ALL NEW" if want == "new" else "ALL OLD") in logs[0]
    _consistent(root, want)
    assert data.recover_commit(log=logs.append) is None                   # nothing left to do


def test_r_g3_an_uninterrupted_commit_and_the_command_entry(commit_dir, monkeypatch):
    root, man, new_man, pairs = commit_dir
    data.commit_tables(pairs, new_man, log=lambda s: None)
    _consistent(root, "new")
    seen = []
    monkeypatch.setattr(data, "recover_commit", lambda log=print: seen.append("checked"))
    monkeypatch.setattr(data, "summary", lambda log=print: None)
    data.main(["summary"])
    assert seen == ["checked"]                                            # every command checks first
