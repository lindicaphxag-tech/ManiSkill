import unittest
from research.benchmark_epoch_fenced_repair import benchmark

class FencedReplayBenchmarkCheck(unittest.TestCase):
    def test_locked_pair_512_cases_and_unconfirmed_probes(self):
        r=benchmark()
        self.assertEqual(r["constructed_stale_reads"],256)
        self.assertEqual(r["fenced_stale_halts"],256)
        self.assertEqual(r["legacy_stale_claimed_fresh_authorizations"],256)
        self.assertEqual(r["fenced_fresh_correct"],256)
        self.assertEqual(r["legacy_fresh_correct"],256)
        self.assertEqual(r["fenced_unknown_probe_delivery_halts"],256)
        self.assertEqual(r["actual_cpu_physx_trials"],0)
        self.assertFalse(r["externally_independently_run"])

    def test_reject_odd_denominator(self):
        with self.assertRaises(ValueError):
            benchmark(n=7)

if __name__=="__main__":
    unittest.main()
