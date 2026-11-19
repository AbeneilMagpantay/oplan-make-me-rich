"""Core-unit bit-identity runner (KP-015 hard requirement). Not a test module: tests/test_core_identity.py
runs it as a separate process, once with the reference kernel (tests/ref_kernel_b12df97.zip, the omr/ of
commit b12df97, extracted to a temp folder) and once with the working kernel, and compares the outputs.

    python ref_core_runner.py <kernel_root> synthetic <data_dir> <programs_dir> <out_dir>
    python ref_core_runner.py <kernel_root> realdev <data_root> <programs_dir> <out_dir>

synthetic: every program through stage 1 and stage 2 (reduced options, fixed seeds) on the synthetic
world stored as parquet in data_dir; writes weights (npz) and metrics + gate values (json).
realdev: stage 1 (truncation and start cuts) on the REAL DEV frames (dev_end ceiling, no handle); writes
the weights. Nothing is written to the project's ledger (the VAL access log is redirected to out_dir).
"""
import json
import sys
from pathlib import Path


def main():
    root = Path(sys.argv[1]).resolve()
    sys.path.insert(0, str(root))
    import numpy as np
    import pandas as pd
    from omr import access
    from omr import constants as C
    from omr import datasets as D
    from omr import lang as L
    from omr import ledger
    from omr import paths as P
    from omr import pipeline

    mode = sys.argv[2]
    opts = pipeline.Opts(perm_n=25, jitter_n=3, truncation_cuts=4, start_cuts=2, start_cuts_val=1)
    if mode == "synthetic":
        data_dir, prog_dir, out = Path(sys.argv[3]), Path(sys.argv[4]), Path(sys.argv[5])
    else:
        from omr import data as DT
        droot = Path(sys.argv[3])                      # the project's data/ (both kernels read the same files)
        DT.DATA_DIR, DT.MANIFEST, DT.RAW_DIR = droot, droot / "manifest.json", droot / "raw"
        prog_dir, out = Path(sys.argv[4]), Path(sys.argv[5])
    out.mkdir(parents=True, exist_ok=True)
    P.VAL_ACCESS_LOG = out / "val_access_log.jsonl"
    P.REAL_TRIALS_JSONL = out / "trials.jsonl"
    progs = {f.stem: L.parse(f.read_text(encoding="ascii"), f.stem) for f in sorted(prog_dir.glob("*.omr"))}
    arrays, results = {}, {}
    if mode == "synthetic":
        raws = {}
        for f in sorted(data_dir.glob("*.parquet")):
            sym, ds = f.stem.split("__")
            raws.setdefault(sym, {})[ds] = pd.read_parquet(f)
        frames = {s: D.assemble_frame(r, D.PROGRAM_EXTRA) for s, r in raws.items()}
        liq = {s: D.liquidation_ratios(r["klines"], r["mark_klines"]) for s, r in raws.items()}
        core = {s: frames[s] for s in C.CORE}
        ext = {s: frames[s] for s in C.EXTENDED if s in frames}
        world = pipeline.World(core=core, extended=ext, btc=core[C.BTC], liq=liq, symbols=C.CORE)
        cap = pd.Timestamp(C.DEV_END, tz="UTC")
        dev = {s: f.loc[:cap] for s, f in core.items()}
        handle = access.for_calibration("core identity runner (tests)")
        grid = pipeline.core_grid(world.core, C.CORE)
        grid = grid[grid <= pd.Timestamp(C.VAL_END, tz="UTC")]
        for stem, prog in progs.items():
            q = L.default_params(prog)
            s1 = pipeline.stage1(prog, q, dev, dev[C.BTC], np.random.default_rng([11, 1]), opts)
            arrays[f"{stem}__s1W"] = s1["W"]
            W, raw = pipeline.unit_signals(prog, q, world.core, C.CORE, world.btc, grid)
            arrays[f"{stem}__W"] = W
            arrays[f"{stem}__raw"] = raw
            if not s1["ok"]:
                results[stem] = {"stage1": s1["code"]}
                continue
            res = pipeline.stage2(prog, q, world, s1, opts, handle, 12345, 0.1)
            r = {"status": res["status"], "canonical": prog.canonical}
            if res["status"] == "evaluated":
                r.update(metrics=res["metrics"], gates={k: v["pass"] for k, v in res["gates"].items()},
                         gate_values={k: v["value"] for k, v in res["gates"].items()}, info=res["info"],
                         daily=[float(x) for x in res["daily_returns"].to_numpy()])
            results[stem] = r
    else:
        frames = D.load_frames(C.CORE, D.PROGRAM_EXTRA, upto="dev_end")
        for stem, prog in progs.items():
            s1 = pipeline.stage1(prog, L.default_params(prog), frames, frames[C.BTC], np.random.default_rng([11, 1]),
                                 pipeline.Opts())
            arrays[f"{stem}__s1W"] = s1["W"]
            arrays[f"{stem}__raw"] = s1["raw"]
            results[stem] = {"ok": s1["ok"], "code": s1["code"], "fault": s1.get("fault"),
                             "direction_changes_dev": s1.get("direction_changes_dev"), "canonical": prog.canonical}
    np.savez(out / "arrays.npz", **arrays)
    (out / "results.json").write_text(json.dumps(ledger.clean(results), sort_keys=True), encoding="ascii")
    print("done", len(progs))


if __name__ == "__main__":
    main()
