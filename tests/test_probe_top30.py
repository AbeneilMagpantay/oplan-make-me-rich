"""U6: unit top30 programs are probed on a deterministic panel of 12 in-play symbols through the in-play
cross-section code; the core probe is unchanged."""
import pytest

from conftest import prog_text
from omr import lang as L
from omr import probe

TOP = 'unit = "top30"\n'
X = "n = param(24, 19, 30)\nx = ret(close, n)\n"


def _top30(body):
    return L.parse(prog_text(TOP + X + body, kind="portfolio"), "x_test")


def _core(body):
    return L.parse(prog_text(X + body, kind="portfolio"), "x_test")


@pytest.mark.parametrize("body", ["signal = abs(cs_rank(x))\n", "signal = cs_rank(x) * cs_rank(x)\n"])
def test_u6_top30_cross_section_programs_parse(body):
    prog = _top30(body)
    assert prog.unit == "top30"
    with pytest.raises(L.LangError) as e:                     # the two-symbol core probe would reject them
        _core(body)
    assert e.value.rule == "constant_subexpression"


@pytest.mark.parametrize("body", ["signal = cs_rank(x) / cs_rank(x)\n", "signal = cs_demean(x) + hour / hour\n"])
def test_u6_a_real_constant_is_still_rejected_in_top30(body):
    with pytest.raises(L.LangError) as e:
        _top30(body)
    assert e.value.rule == "constant_subexpression"


def test_u6_the_probe_panel_is_twelve_in_play_symbols_and_the_core_panel_is_unchanged():
    p, btc = probe.universe_panel()
    assert len(p.symbols) == probe.UNIVERSE_PROBE_SYMBOLS >= 12 and p.inplay.all() and p.unit_known.all()
    a, b, _ = probe.panel()
    assert (p.col("close")[:, 0] == a["close"].to_numpy()).all() and (p.col("close")[:, 1] == b["close"].to_numpy()).all()
    frames, _ = probe._probe_frames(_core("signal = cs_demean(x)\n"))
    assert len(frames) == 2
