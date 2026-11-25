"""KP-019 identity, kept as a permanent check (A.8 of the design): every program that existed before the batch
(the 12 kernel programs and the strategies of 469c1cd) parses to the same canonical form, lookback, node count,
literals, param order and types, and gives the same interpreter output on the probe panels, bit for bit; the
engines' existing outputs are bit-identical. The expected values were captured from the untouched files of
469c1cd (a verified copy) by the builder's harness; a strategy whose source has changed since is skipped.
Synthetic data only."""
import hashlib
import json

import numpy as np
import pandas as pd
import pytest

from conftest import ROOT
from omr import constants as C
from omr import engine as E
from omr import interp as X
from omr import lang as L
from omr import probe

# name: (sha256 of the source [:24], hash of the parse record, hash of raw, hash of known)
EXPECTED = {
    'kernel/gen000_donchian_ls': ('0c3ee868dc894306fdef9404', '51770a620d8b948cda871a98', '9662959279f04e3f2303298b', '58599295c721756e0733c3d1'),
    'kernel/gen000_funding_carry': ('2f78f28416e423487c654c9c', '1f022aa7315dbc07f334abcc', 'e5024e92f10d1a15355771d0', '43f9fee5d6e53e21df322fa1'),
    'kernel/gen000_rsi_meanrev_ls': ('d49f9e50691dbe94e956730d', '8fc531a6b4ef296fca0ee480', '43848fc5f4fb6c07d1e148f9', 'c2ddbb34c797effc54ade1b5'),
    'kernel/gen000_sma_cross_ls': ('2bbb8e59175cc0232bd1d48b', 'b03b1c48d7702ad5de5ee0ee', '56d7354768ee9b9f462d44ef', 'c92aa8cb09e62f0c3a11cf1b'),
    'kernel/gen000_voltarget_trend_ls': ('903f8254d51b61a5e308fe5e', '62de6b374a53c19d55fc01e4', '14d1c8169d3d0d08961b99cf', 'de581c734c6381f706670867'),
    'kernel/kernel_kitchen_sink': ('3dec7c6933b29dd760d535d8', '798f8bf54a0fc257ec101b42', '7bbcc580dcb94ebe9ed669b1', '70e63e2a79f0840dfdef7dfa'),
    'kernel/kernel_noise_portfolio': ('fea6765564b6869a9c90933f', 'bc54bf148e4b24a5b18b586d', 'ec6338b644252a744e106062', 'ead9ccba5e018b108e85e918'),
    'kernel/kernel_noise_single': ('ccd048c8d73177c38ae966fc', 'c3351837c8d7a4640a93cf9e', '8a6b9e726fbf7a7a70a61391', '14fac32ee4f803fd76813f36'),
    'kernel/kernel_noise_top30': ('a8424e1c1f12119a16a10416', '345a01ccb080848038a5c91e', 'f790b05c1b430b3e0bce6f83', '6d8b81d99a457d43684b4905'),
    'kernel/ucal_xs_carry': ('7c719b4b19f02fbac884c2b8', 'ae2e1c227bc36b4801086277', '3d6479a15a13b7b43b4c2157', '52902b355df0c54ce7cefe5a'),
    'kernel/ucal_xs_momentum': ('d47db75420d1e80bcc93e46f', '6bfc2dc6aeb736fc1609b025', 'a4b8e47c6770964dafc77ef7', 'f96805c50e584056a5198710'),
    'kernel/ucal_xs_reversal': ('9d3619b70799a0476285b6ba', 'b98dbaefee799aceaeb552d9', '84a14c9dd83be8260aa88420', 'd18a34bd4a17af7387cd3f04'),
    'strategies/gen000_donchian_ls': ('0c3ee868dc894306fdef9404', '51770a620d8b948cda871a98', '9662959279f04e3f2303298b', '58599295c721756e0733c3d1'),
    'strategies/gen000_funding_carry': ('2f78f28416e423487c654c9c', '1f022aa7315dbc07f334abcc', 'e5024e92f10d1a15355771d0', '43f9fee5d6e53e21df322fa1'),
    'strategies/gen000_rsi_meanrev_ls': ('d49f9e50691dbe94e956730d', '8fc531a6b4ef296fca0ee480', '43848fc5f4fb6c07d1e148f9', 'c2ddbb34c797effc54ade1b5'),
    'strategies/gen000_sma_cross_ls': ('2bbb8e59175cc0232bd1d48b', 'b03b1c48d7702ad5de5ee0ee', '56d7354768ee9b9f462d44ef', 'c92aa8cb09e62f0c3a11cf1b'),
    'strategies/gen000_voltarget_trend_ls': ('903f8254d51b61a5e308fe5e', '62de6b374a53c19d55fc01e4', '14d1c8169d3d0d08961b99cf', 'de581c734c6381f706670867'),
    'strategies/gen001_calm_long': ('20a3044351b3938fb8f7cb86', '25e5535a201aa53a9af93b3c', '8ebb4ad3d98ad327e7ca2740', '43ab8e9862f6aed6055d281a'),
    'strategies/gen001_capitulation_long': ('c4c343fa88aa2354d92a411c', 'e7d5e1e71e96f47499eb8634', '540d4a32cc1440a99ed0ee27', '057934e352aa62cba52970ad'),
    'strategies/gen001_diag_volsized_long': ('1d1c9db65521c24c889580e9', '34bd450f15d7668bce712d85', '33e2139a0086d26d6d29cb03', '7f331e082b33a9c1258f9e84'),
    'strategies/gen001_relmom_pair': ('4c1914f2b95982d3dc14b8af', '7122e879724154cafe542287', '5622c3c63a908beeaffe9892', 'b01e66a62b96f9546789ebb7'),
    'strategies/gen001_taker_flow_long': ('1056b53f80c6fdf194aaf7aa', '1db228cdceb620d19d23b7d0', '5a2b7004723a90314c1c1403', 'a1d26661f1b5a0e3823483ef'),
    'strategies/gen001_tsmom_long_flat': ('72f1a0d871f9f2ebae45c0d6', '7be797e13efdcf39f8cf289f', 'f8d67adfa04cf214acd02328', '7f331e082b33a9c1258f9e84'),
    'strategies/gen002_absorbed_flow': ('94b013e0d614fb0d542a05cb', '23b8569fac2a644ef2305aba', 'dbc30d8a2b0275a73e125ab0', '114c1ab4eae5d98002e2a219'),
    'strategies/gen002_activity_fade': ('5e1fc508fad04f91c5ce96d0', 'dbec689edaf909dd895b1a19', 'c78932ac1d5dcb3f334ddf68', '114c1ab4eae5d98002e2a219'),
    'strategies/gen002_averaged_funding_shock': ('a9fa8d496b64f85000d9261a', '39bf8e4c2a74f6462d69ad42', 'cf6a2500dbed908795543b2e', '0b93f4dcff264578c54d10b4'),
    'strategies/gen002_averaged_unrewarded_shift': ('b7c58a74ff5a97c3d964f2d5', 'cc77009e22bafa487bd73d16', '0b4632626e8017b14fbbeefc', '9a9398473750fe25ad7886a6'),
    'strategies/gen002_diag_acf_absorbed_flow': ('0eb1c138370b691e27db0cf1', '067b1ed5ac79ddd91d5f64c1', '720957840f783c3a6e3246a0', 'df5d125e015a39b8201e837c'),
    'strategies/gen002_diag_acf_activity_fade': ('102814b7e1cd7eb75785b721', 'aa748000114e681eb511a0ea', '3538b37ccca8f89f149b21d0', 'df5d125e015a39b8201e837c'),
    'strategies/gen002_diag_acf_averaged_funding_shock': ('9ce365b407e1f772f9c24b71', '5cd49194ef9a99e0d29ab029', 'f0b8d394825068639ceff14b', '1a1ac053a9b807a61de6df95'),
    'strategies/gen002_diag_acf_averaged_unrewarded_shift': ('47b0476d320dbb0c08e2b072', '5668725eb6f13a44b2d2010e', 'a3469e709055c594eacbca60', '1a1ac053a9b807a61de6df95'),
    'strategies/gen002_diag_acf_funding_shock': ('a345074d9bb580935bba9254', 'eccb6b4fa4805f1d9b3fdcd6', '0d434cfbf73b5da766888a9b', 'c13ec36bb52339425d7adcf6'),
    'strategies/gen002_diag_acf_premium_shock': ('3c9f1ddcf723c02686fecfe5', '27dc12bb85c610a4e96ff55b', '58035d7331e509136703cdf2', '342ec0fca1b9d32f0a2ba3ab'),
    'strategies/gen002_diag_acf_resid_momentum': ('058b047457716037b8fdbe41', '8349d453a15b37dd0333754f', 'da72bd3d97c2861a98c66898', '957c2420ff1d482470ae48f0'),
    'strategies/gen002_diag_acf_resid_reversal': ('5d692daaac47996aa933f467', 'af9a1c82e1e47a73f14ca0e1', 'e87438967af9e4968b0bfa33', 'a09f7f20321b4f0a4bbcdc4e'),
    'strategies/gen002_diag_acf_resid_skew': ('191c9ba790ffb0579479762e', '67ff5b85dae5104a86d20120', '631b511153898aac0f01151d', '342ec0fca1b9d32f0a2ba3ab'),
    'strategies/gen002_diag_acf_small_tickets': ('7acb7cb2ceb336cec576c11b', 'a4f3423314dfe8fe70876ad7', '893e5647428288fb8b0ced3d', 'df5d125e015a39b8201e837c'),
    'strategies/gen002_diag_acf_unrewarded_premium': ('cf68da80aedd560eecfbfc73', 'd96839e120c7ee46c796f9ce', '9fbadbd9bcff4ae7dc3ee0b9', '8b00ab998181125dfad9a727'),
    'strategies/gen002_diag_plain_momentum': ('fde72df8c29967682cc1ce2e', 'fd818e481d81c9f1e064bde8', 'e1facd837d4595c3746df969', 'd18d3d836ff0f8b9ad0015e5'),
    'strategies/gen002_diag_plain_reversal': ('aff13fdf1678ab6c2e0ea676', '16d6a8089100bfb100c32a6a', 'e5a30f4ec525764108403a9b', 'e0b01efb33c0ff0dfc045a2b'),
    'strategies/gen002_diag_stale_averaged_funding_shock': ('9eea6566df49d43cc6758079', '86cd575fd3fd7d8fdfe7ed2a', '025f3d7017dbc865fec34ce0', '7102994d63441342a91ae3c1'),
    'strategies/gen002_diag_stale_averaged_unrewarded_shift': ('855f64db0e460d450c157232', '15b6e80f61fb3c592daa29f1', '219e119291dcc164c4166512', 'd1848fb4fe54db5aee2ac597'),
    'strategies/gen002_diag_stale_funding_shock': ('3147c0de7c47075f3f4e5337', 'ef97833f568660945f9f0b36', '06bbb4707200c6602d00cac2', 'cf7be1a69447cf2f4ae58aae'),
    'strategies/gen002_diag_stale_premium_shock': ('a4f0a27f3e17b9484089dabd', '1424cda35864ee7afbec4da5', 'd590397afd462ce8d57f835c', '3a2ed474a43f9c50c3deb2fd'),
    'strategies/gen002_diag_stale_unrewarded_premium': ('ad6212f0adad83cf4cd9ce11', '70e5909ad3c05d2e63771043', '31f14974590d829c1f543229', 'd609c541f97237f355afde85'),
    'strategies/gen002_diag_twin_averaged_funding_shock': ('297db3ab7bb9f4bc1cf2ec43', 'd4056dd04c705e302237af55', '1b0b2d96172f07753b992a62', '0b93f4dcff264578c54d10b4'),
    'strategies/gen002_diag_twin_averaged_unrewarded_shift': ('be280bac965493c68c746f21', '21f0f23ec1caa73ebddf5595', '30406f86de0bf82c3214c8bb', '9a9398473750fe25ad7886a6'),
    'strategies/gen002_diag_twin_funding_shock': ('34b89410b0818c18b555031e', '2e2a078798ca3e7c2623c011', 'ace793aef0226a72afcd96bc', '5240d41a47cdc03437093a33'),
    'strategies/gen002_diag_twin_premium_shock': ('74bf89a3d8b12ac7b326e21e', 'a11e6294848cc5373c0e0228', '3a63921fe2f354528a4cc913', '3709233ddc6145ab175e0c7c'),
    'strategies/gen002_funding_shock': ('5edff8855493f357c9ec67f4', '2d2c5706a73dc763cbaf2c26', '673c2e9516e4e49ae05a9318', '5240d41a47cdc03437093a33'),
    'strategies/gen002_premium_shock': ('6cc22514f04cc3bdf25ea641', '7657dc46dd39dc9994af11b9', 'a7120955b2b4c6912d01a482', '3709233ddc6145ab175e0c7c'),
    'strategies/gen002_prior_month_reversal': ('0449b770a3cb374e7eff4585', '43831f502eea0e6253d71cc7', 'eac57fc4c04749307bdceac6', '72704067dfac48092a449711'),
    'strategies/gen002_resid_momentum': ('9265fdadce0f3f517cf43e07', 'b901f34d3c2a738926aab523', '61188dd370fa41f0338c6d48', 'd18d3d836ff0f8b9ad0015e5'),
    'strategies/gen002_resid_reversal': ('782e81c56de232515da4040e', '2e035f9d971290cdfdde72b3', 'c92d642485013608faab53bb', '8b4bb8614e07910e27f065ea'),
    'strategies/gen002_resid_skew': ('18cc16c73f576ba95403cb21', '75389d4b6a53f9e2ca3bb62a', '962cd1f3af6c5828f1af6b46', '3709233ddc6145ab175e0c7c'),
    'strategies/gen002_small_tickets': ('1fb10b21eb1f26b75001ddf2', '89d991fdbd2de88bf8c45c65', '6d2a2baa775f4ff997daf3c3', '114c1ab4eae5d98002e2a219'),
    'strategies/gen002_unrewarded_premium': ('57694b11bb87ba6c6a5f29ac', 'ebf14f6b5e2fd57e61756a07', '4c8c9c347fc8e1662853e24b', 'f96805c50e584056a5198710'),
}
ENGINE = {'core_a': ['d3fd904346d86b1ec1ced93b',
            '3fbcd3f094e56366b4388d34',
            '67ccc6566de67a4dee393098',
            'a109bc10f5f76e1a60af8a4e',
            '8d65d8b5ef762a45e583479f',
            '6c3806cc7577555b4c0aea45',
            '-0.00019658339212095724',
            '-1',
            '626c3cc43832e9b73e292c8b'],
 'core_b': ['c019fb02bba189e66cece5bc',
            'd0ae2d8896e5a088d2ba47a1',
            'b4e8fcb977bbe1947b28ea98',
            '4b92b9ff3eec1f712e0ea605',
            'bb36bce8455af41379133bfe',
            'dc0b47394177c93802eabac3',
            '0.005281147710884695',
            '-1',
            '6acbaf20085f53c04426b770'],
 'core_liq': ['ed7937133eb13dd3b5f13051',
              'cf989f6c519bb83e600eee1a',
              'cf989f6c519bb83e600eee1a',
              '16a0d6e09e3da90bdedf6e1d',
              'b051d8c739095b43a2fd274d',
              'e03ce001abd85e2206e58287',
              '0.00010325876137136319',
              '-1',
              '112f0a1e3c5f6e4675d560e8'],
 'u_base': ['d018c1efd1236f4a2fa1b96a',
            '5a57d504f0999cc66bb9c118',
            '25a14007a568e851e7a90d85',
            'b91238b54f9fe3facf51376e',
            '29de12fe561587bf311adf52',
            '84f8501eb3c7e6fcb0ca65d4',
            '0.00016553354976574114',
            '-1',
            'c3818218b38eeb01c9744284',
            '39569b7ea8a574938c45ed01',
            '1.0471809933534852',
            'False'],
 'u_base_arrays_u': ['d018c1efd1236f4a2fa1b96a',
                     '5a57d504f0999cc66bb9c118',
                     '25a14007a568e851e7a90d85',
                     'b91238b54f9fe3facf51376e',
                     '29de12fe561587bf311adf52',
                     '84f8501eb3c7e6fcb0ca65d4',
                     '0.00016553354976574114',
                     '-1',
                     'c3818218b38eeb01c9744284'],
 'u_continuation': ['f9e569d63fa210455bff6965',
                    '94b3de43cffcab98156a2bdb',
                    'c9699305cb95352d4cd9f2cb',
                    'cff2a5e5f35d717b4d7085e1',
                    '0c49d147aceb357df6eb7f01',
                    '23ec89494a5570fee142a40c',
                    '0.00016553354976574114',
                    '-1',
                    'f9a62d1d6a36fb6c1429bb03',
                    '39569b7ea8a574938c45ed01',
                    '1.0471809933534852',
                    'False'],
 'u_cost2': ['3311171161ae629a65150e23',
             '331ebef1055028164a29d0f1',
             '0d63152c4f0eeb6610d35af7',
             'b91238b54f9fe3facf51376e',
             '5d6c885bfba577fff33fa2c2',
             'f7c23653a927055ce8ddb394',
             '0.00018337071862725598',
             '-1',
             '5c423382c6782f1e02328069',
             '01a81013114a0ac14bb466c9',
             '0.8855396359865475',
             'False'],
 'u_cost2_arrays_u': ['3311171161ae629a65150e23',
                      '331ebef1055028164a29d0f1',
                      '0d63152c4f0eeb6610d35af7',
                      'b91238b54f9fe3facf51376e',
                      '5d6c885bfba577fff33fa2c2',
                      'f7c23653a927055ce8ddb394',
                      '0.00018337071862725598',
                      '-1',
                      '5c423382c6782f1e02328069'],
 'u_run_daily': 'cb1e2bd8228a960c96dc2a05',
 'u_run_fields': ['d018c1efd1236f4a2fa1b96a',
                  '5a57d504f0999cc66bb9c118',
                  '25a14007a568e851e7a90d85',
                  'b91238b54f9fe3facf51376e',
                  '29de12fe561587bf311adf52',
                  '84f8501eb3c7e6fcb0ca65d4',
                  '0.00016553354976574114',
                  '-1',
                  'c3818218b38eeb01c9744284'],
 'u_stress': ['29e588d89e63c1c70e26cef6',
              'ef370ff1d897b3c6932bbb88',
              '8895caea44a89b4c9d5e4334',
              'b91238b54f9fe3facf51376e',
              '39bcf830fb9e8a63e0c30676',
              'f6c334716f65b5c708f3ddc7',
              '0.013608555811114273',
              '-1',
              '01b1f9433b0d09a35092d6ba',
              '134a35954e7729b4b9240974',
              '1.033248832669598',
              'False'],
 'u_stress_arrays_u': ['29e588d89e63c1c70e26cef6',
                       'ef370ff1d897b3c6932bbb88',
                       '8895caea44a89b4c9d5e4334',
                       'b91238b54f9fe3facf51376e',
                       '39bcf830fb9e8a63e0c30676',
                       'f6c334716f65b5c708f3ddc7',
                       '0.013608555811114273',
                       '-1',
                       '01b1f9433b0d09a35092d6ba']}


def harr(a) -> str:
    a = np.asarray(a)
    if a.dtype.kind == "f":
        a = np.where(np.isnan(a), np.nan, a)
    return hashlib.sha256(f"{a.dtype.str}|{a.shape}|".encode() + np.ascontiguousarray(a).tobytes()).hexdigest()[:24]


def h(o) -> str:
    return hashlib.sha256(json.dumps(o, sort_keys=True).encode()).hexdigest()[:24]


def record(p) -> dict:
    return json.loads(json.dumps({
        "canonical": p.canonical, "lookback_hours": p.lookback_hours, "node_count": p.node_count,
        "n_literals": p.n_literals, "literals": [[list(k), v] for k, v in p.literals],
        "param_order": list(p.param_order), "unit": p.unit, "kind": p.kind,
        "types": {k: [t.kind, [list(u) for u in t.unit], t.tf] for k, t in p.types.items()}}))


@pytest.mark.parametrize("name", sorted(EXPECTED))
def test_every_earlier_program_parses_and_evaluates_bit_for_bit(name):
    kind, stem = name.split("/")
    f = ROOT / ("omr/programs" if kind == "kernel" else "strategies") / f"{stem}.omr"
    src, rec, raw_h, kn_h = EXPECTED[name]
    if hashlib.sha256(f.read_bytes()).hexdigest()[:24] != src:
        assert kind != "kernel", f"kernel program {stem} changed"
        pytest.skip("the strategy's source changed after 469c1cd")
    p = L.parse_file(f)
    assert h(record(p)) == rec, p.canonical
    frames, btc = probe._probe_frames(p)
    raw, kn = X.evaluate_full(p, L.default_params(p), frames, btc)
    assert (harr(raw), harr(kn)) == (raw_h, kn_h)


def test_the_kernel_programs_of_469c1cd_are_all_checked():
    stems = {n.split("/")[1] for n in EXPECTED if n.startswith("kernel/")}
    assert stems == {f.stem for f in (ROOT / "omr" / "programs").glob("*.omr")} - {"kernel_kitchen_sink_tf"}


def _engine_outputs():
    """The engine part of the builder's harness (golden.py g3), unchanged."""
    rng = np.random.default_rng(20261125)
    res = {}
    T, K = 3000, 3
    op = 100 * np.exp(np.cumsum(0.01 * rng.standard_normal((T, K)), axis=0))
    op[2000:, 2] *= 0.3
    dn = np.exp(-np.abs(0.01 * rng.standard_normal((T, K))))
    up = np.exp(np.abs(0.01 * rng.standard_normal((T, K))))
    fr = np.where((np.arange(T) % 8 == 0)[:, None], 1e-4 * rng.standard_normal((T, K)), 0.0)
    for nm, tgt, kw in (("core_a", np.repeat(rng.uniform(-0.3, 0.3, (T // 24 + 1, K)), 24, axis=0)[:T], {}),
                        ("core_b", np.repeat(rng.uniform(-0.33, 0.33, (T // 6 + 1, K)), 6, axis=0)[:T],
                         {"cost_rate": 0.002, "pay_mult": 1.5, "recv_mult": 0.5}),
                        ("core_liq", np.tile([0.0, 0.0, 1.0], (T, 1)), {})):
        out = E.run_arrays(op, dn, up, fr, tgt, **kw)
        res[nm] = [harr(x) if isinstance(x, np.ndarray) else repr(x) for x in out]
    K = 6
    op = 50 * np.exp(np.cumsum(0.012 * rng.standard_normal((T, K)), axis=0))
    cl = op * np.exp(0.003 * rng.standard_normal((T, K)))
    av = rng.uniform(size=(T, K)) > 0.02
    av[1500:1530, 4] = False
    dn = np.exp(-np.abs(0.01 * rng.standard_normal((T, K))))
    up = np.exp(np.abs(0.01 * rng.standard_normal((T, K))))
    fr = np.where((np.arange(T) % 8 == 0)[:, None], 2e-4 * rng.standard_normal((T, K)), 0.0)
    tgt = np.repeat(rng.uniform(-0.16, 0.16, (T // 24 + 1, K)), 24, axis=0)[:T]
    for nm, kw in (("u_base", {}), ("u_stress", {"pay_mult": 1.5, "recv_mult": 0.5}),
                   ("u_cost2", {"cost_rate": 2 * C.UNIVERSE_COST_RATE})):
        out = E.run_block_u(op, cl, av, dn, up, fr, tgt, **kw)
        res[nm] = [harr(x) if isinstance(x, np.ndarray) else repr(x) for x in out[:12]]
        o9 = E.run_arrays_u(op, cl, av, dn, up, fr, tgt, **kw)
        res[nm + "_arrays_u"] = [harr(x) if isinstance(x, np.ndarray) else repr(x) for x in o9]
    a = E.run_block_u(op[:1201], cl[:1201], av[:1201], dn[:1201], up[:1201], fr[:1201], tgt[:1201])
    b = E.run_block_u(op[1200:], cl[1200:], av[1200:], dn[1200:], up[1200:], fr[1200:], tgt[1200:], h0=a[9],
                      eq0=a[10], dead0=a[11], t0=1, fp0=a[6])
    res["u_continuation"] = [harr(x) if isinstance(x, np.ndarray) else repr(x) for x in b[:12]]
    run = E.run_u(pd.date_range("2021-01-01", periods=T, freq="h", tz="UTC"), op, cl, av, dn, up, fr, tgt)
    res["u_run_daily"] = harr(run.daily_returns().to_numpy())
    res["u_run_fields"] = [harr(getattr(run, k)) if isinstance(getattr(run, k), np.ndarray) else repr(getattr(run, k))
                           for k in ("equity", "gross", "net", "ev_idx", "ev_turn", "ev_cost", "funding_paid", "liq_idx",
                                     "pre")]
    return res


def test_the_engines_existing_outputs_are_bit_identical():
    assert _engine_outputs() == ENGINE
