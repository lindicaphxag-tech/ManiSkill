"""All tests in this module are CPU-only contract negative tests, not PhysX trials."""
import unittest
from research.external_cross_robot_ack_reproduction import (
    checked_inputs,actual_original_method_locked,
    git_object_blob
)


class SourceGateTests(unittest.TestCase):
    def test_original_source_blobs_unchanged(self):
        actual_original_method_locked()

    def test_allowed_new_seed_interval(self):
        self.assertEqual(checked_inputs('panda',.75,710001,4),
                         [710001,710002,710003,710004])

    def test_reject_previous_author_seeds(self):
        for seed in (420001,430001,480001,490008,610001,620004,700000):
            with self.subTest(seed=seed),self.assertRaises(ValueError):
                checked_inputs('panda',.75,seed,4)

    def test_reject_unregistered_robot(self):
        with self.assertRaises(ValueError):
            checked_inputs('fake_panda','0.75',710001,1)

    def test_reject_unregistered_scale(self):
        for value in (.6,1.35,0.,-1.,1.6):
            with self.subTest(scale=value),self.assertRaises(ValueError):
                checked_inputs('xarm6_robotiq',value,710001,1)

    def test_reject_incomplete_or_excessive_cohort(self):
        for n in (0,2,3,5,9,1.0):
            with self.subTest(count=n),self.assertRaises(ValueError):
                checked_inputs('panda',.75,710001,n)

    def test_reject_float_seed_and_overflow(self):
        for seed in (710001.0,2147483647):
            with self.subTest(seed=seed),self.assertRaises(ValueError):
                checked_inputs('panda',.75,seed,4)

    def test_git_blob_hash_changes_when_bytes_change(self):
        self.assertNotEqual(git_object_blob(b'original'),git_object_blob(b'original!'))


if __name__=='__main__':
    unittest.main()
