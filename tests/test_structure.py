"""Structural tests over the kernel source (E3 and the removal of every code-execution path)."""
import ast
from pathlib import Path

from omr import data

ROOT = Path(__file__).resolve().parent.parent
OMR = ROOT / "omr"
LATEST_ALLOWED = {"data.py", "census.py"}
LOADERS = {"load_raw", "load_frame", "load_frames", "load_liq", "load_liqs"}
# E3: calls that execute or import code from text. The allowlist is explicit and EMPTY.
BANNED_CALLS = {"exec", "eval", "compile", "__import__"}
EXEC_ALLOWLIST: set = set()


def py_files():
    return sorted(list(OMR.rglob("*.py")) + list((ROOT / "tests").rglob("*.py")))


def test_no_exec_eval_compile_import_or_importlib_anywhere():
    """Any call named exec/eval/compile/__import__ (plain or attribute, e.g. re.compile, pd.eval,
    df.eval) and any use of importlib fails, outside an explicit empty allowlist."""
    offenders = []
    for f in py_files():
        tree = ast.parse(f.read_text(encoding="ascii"))
        rel = f.relative_to(ROOT).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
                if name in BANNED_CALLS and f"{rel}:{node.lineno}" not in EXEC_ALLOWLIST:
                    offenders.append(f"{rel}:{node.lineno} call {name}")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                if any(m and m.split(".")[0] == "importlib" for m in mods):
                    offenders.append(f"{rel}:{node.lineno} imports importlib")
            if isinstance(node, ast.Name) and node.id in ("importlib", "__import__", "exec", "eval", "compile"):
                if f"{rel}:{node.lineno}" not in EXEC_ALLOWLIST:
                    offenders.append(f"{rel}:{node.lineno} name {node.id}")
            if isinstance(node, ast.Attribute) and node.attr in ("importlib",):
                offenders.append(f"{rel}:{node.lineno} attribute {node.attr}")
    assert EXEC_ALLOWLIST == set()
    assert offenders == [], offenders


def test_the_scanner_can_fail():
    """The E3 scan flags each banned form (an assertion that cannot fail certifies nothing)."""
    samples = ["exec('x')", "eval('1')", "compile('1', 'f', 'eval')", "__import__('os')", "import importlib",
               "from importlib import import_module", "re.compile('x')", "pd.eval('1')", "x = importlib"]
    for s in samples:
        tree = ast.parse(s)
        hit = False
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
                hit |= name in BANNED_CALLS
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                hit |= any(m and m.split(".")[0] == "importlib" for m in mods)
            if isinstance(node, ast.Name) and node.id == "importlib":
                hit = True
        assert hit, s


def test_no_strategy_code_path_remains():
    """The Python sandbox is gone: no runner, allowlist, strategy API, or Python strategy file."""
    for gone in ("runner.py", "runner_child.py", "strategy_api.py", "integrity.py"):
        assert not (OMR / gone).exists(), gone
    assert list((ROOT / "strategies").glob("*.py")) == []
    for f in py_files():
        tree = ast.parse(f.read_text(encoding="ascii"))
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] + ([node.module] if isinstance(node, ast.ImportFrom) and node.module else [])
                assert not any(m and m.split(".")[-1] in ("runner", "runner_child", "strategy_api", "integrity")
                               for m in mods), f"{f.name}:{node.lineno}"


def test_latest_ceiling_only_in_data_and_census():
    offenders = []
    for f in sorted(OMR.glob("*.py")):
        tree = ast.parse(f.read_text(encoding="ascii"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and node.value == "latest" and f.name not in LATEST_ALLOWED:
                offenders.append(f"{f.name}:{node.lineno}")
    assert offenders == [], offenders


def test_every_loader_call_passes_a_literal_ceiling():
    bad, seen = [], 0
    for f in sorted(OMR.glob("*.py")):
        tree = ast.parse(f.read_text(encoding="ascii"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                fn = node.func
                name = fn.attr if isinstance(fn, ast.Attribute) else getattr(fn, "id", None)
                if name in LOADERS:
                    seen += 1
                    kw = {k.arg: k.value for k in node.keywords}
                    v = kw.get("upto")
                    if f.name == "datasets.py" and isinstance(v, ast.Name) and v.id == "upto":
                        continue        # the registry passes its own argument through
                    if not (isinstance(v, ast.Constant) and v.value in data.CEILINGS):
                        bad.append(f"{f.name}:{node.lineno}")
                    elif v.value == "latest" and f.name not in LATEST_ALLOWED:
                        bad.append(f"{f.name}:{node.lineno} uses latest")
    assert seen >= 4
    assert bad == [], bad


def test_private_readers_are_called_only_inside_the_data_layer():
    """B10: _read_stored / _tables_from_disk are called only by omr/data.py and omr/datasets.py."""
    bad = []
    for f in sorted(OMR.glob("*.py")):
        tree = ast.parse(f.read_text(encoding="ascii"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute) and node.attr in ("_read_stored", "_tables_from_disk", "read_stored",
                                                                 "tables_from_disk"):
                if f.name not in ("data.py", "datasets.py"):
                    bad.append(f"{f.name}:{node.lineno}")
    assert bad == [], bad


def test_ceilings_cap_at_region_ends():
    assert str(data.ceiling_ts("dev_end")) == "2022-06-30 23:00:00+00:00"
    assert str(data.ceiling_ts("val_end")) == "2025-06-30 23:00:00+00:00"
    assert data.ceiling_ts("latest") is None


def test_kernel_sources_and_programs_are_ascii():
    files = py_files() + sorted((OMR / "programs").glob("*.omr")) + sorted((ROOT / "strategies").glob("*.omr"))
    files += [ROOT / n for n in ("CONSTITUTION.md", "LANGUAGE.md", "README.md", "RESEARCH_PLAYBOOK.md", "STATE.md",
                                 "KERNEL_PROPOSALS.md", "requirements.txt") if (ROOT / n).exists()]
    for f in files:
        f.read_bytes().decode("ascii")


def test_generation0_strategies_are_the_kernel_baselines():
    for stem in ("gen000_sma_cross_ls", "gen000_donchian_ls", "gen000_rsi_meanrev_ls", "gen000_voltarget_trend_ls",
                 "gen000_funding_carry"):
        assert (ROOT / "strategies" / f"{stem}.omr").read_bytes() == (OMR / "programs" / f"{stem}.omr").read_bytes()
