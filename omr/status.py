"""python -m omr.status - kernel and seal, data, counted trials (M, N, rho), pool, last census."""
from __future__ import annotations

from omr import constants as C
from omr import data
from omr import kernel_lock
from omr import ledger
from omr import paths as P
from omr import pool
from omr import stats as S


def main(argv=None):
    pr = kernel_lock.verify()
    lock = kernel_lock.read_lock()
    seal = (lock or {}).get("seal")
    print(f"kernel: {'OK' if not pr else 'MISMATCH'}  {lock['combined'][:16] if lock else '-'}  "
          f"SEMANTICS_VERSION {C.SEMANTICS_VERSION}  "
          + (f"sealed: G6 threshold {seal['g6_threshold']}" if seal else "NOT SEALED (evaluate refuses)"))
    for p in pr[:10]:
        print("  " + p)
    try:
        m = data.load_manifest()
        print(f"data: snapshot_end {m['snapshot_end']}  vault_end {m['vault_end']}  research_hash {m['research_hash'][:16]}  "
              f"validated {'yes' if data.validation_ok() else 'NO'}")
    except FileNotFoundError:
        print("data: no manifest")
    st = ledger.trial_states()
    counted = [t for t in st.values() if t["counted"]]
    by = {}
    for t in st.values():
        by[t["status"]] = by.get(t["status"], 0) + 1
    print(f"ledger: {len(st)} trials {by}; counted M = {len(counted)} "
          f"(tier1 {sum(1 for t in counted if (t['final'] or {}).get('tier') == 'tier1')}); "
          f"stage-1 rejections logged {len(ledger.read_rows(P.STAGE1_LOG))}")
    hi = ledger.highest_generation()
    if hi is not None:
        print(f"generation {hi}: {ledger.counted_in_generation(hi)} / {C.MAX_COUNTED_PER_GENERATION} counted")
    if counted:
        mat = ledger.counted_val_matrix()
        rho = S.mean_pairwise_corr(mat)
        M = len(counted)
        print(f"counted trials: M {M} (with stored returns {mat.shape[1]})  rho {rho:.3f}  N {S.effective_n(M, rho):.2f}")
    ch = ledger.verify_chain(P.TRIALS_JSONL) if P.TRIALS_JSONL.exists() else []
    print(f"trial chain: {'OK' if not ch else 'BROKEN'}")
    pool.show()
    cen = ledger.read_rows(P.CENSUS_LOG)
    if cen:
        last = cen[-1]
        print(f"last census: {last['at']}  data end {last['snapshot_end']}")
        for r in last["members"]:
            print(f"  {r['trial_id']}  {r['program']}  days {r['days_forward']}  raw {r['forward_return_raw']:+.4f}  "
                  f"scaled {r['forward_return_scaled']:+.4f}")
    else:
        print("last census: none")


if __name__ == "__main__":
    main()
