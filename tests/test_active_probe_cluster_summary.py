import unittest
from research.active_probe_cluster_summary import science,signflip

A='fault_public_t3_fourhistory_or_t4_query'
B='fault_same_public_posterior_or_query'
C='fault_always_single_privileged_query'

def full():
    rec=[]
    for task,start in (('pull_cube',4100001),('stack_cube',4200001)):
        for seed in range(start,start+16):
            for arm in (A,B,C):
                for truth in range(4):
                    ok=truth%2==0
                    rec.append(dict(task=task,seed=seed,arm=arm,truth=truth,
                        zero_success=ok,x_success=ok,
                        zero_wrong=False,x_wrong=False,
                        zero_privileged_reads=1,x_privileged_reads=1))
    return dict(status='REAL_COMPLETED_NEW_FREEZE_PPO_TASK_SOURCE_AUDITED',
        physically_executed_original_controller_worlds=2560,
        new_independent_reset_clusters=32,
        all_full_actual_PPO_task_outcomes=rec)

class ClusterScienceTests(unittest.TestCase):
    def test_exact_signflip_known_case(self):
        self.assertEqual(signflip([0,0]),1.)
        self.assertEqual(signflip([1]*5),.0625)

    def test_zero_effect_not_claimed_as_noninferiority(self):
        got=science(full(),n_boot=80)
        self.assertFalse(got['task_success_noninferiority_certified'])
        for task in got['by_task'].values():
            for arm in task.values():
                self.assertEqual(arm['task_success_rate_x_minus_zero'],0.)
                self.assertEqual(arm['descriptive_reset_cluster_bootstrap_95'],[0.,0.])
                self.assertEqual(arm['exploratory_two_sided_cluster_signflip_p'],1.)

    def test_one_bad_reset_keeps_original_denominator(self):
        d=full()
        for x in d['all_full_actual_PPO_task_outcomes']:
            if x['task']=='pull_cube' and x['seed']==4100001:x['x_success']=False
        arm=science(d,n_boot=80)['by_task']['pull_cube'][A]
        self.assertEqual(arm['task_success_rate_x_minus_zero'],-2/64)
        self.assertEqual(arm['zero_only_success'],2)
        self.assertEqual(arm['exploratory_two_sided_cluster_signflip_p'],1.)

    def test_missing_truth_rejected(self):
        d=full();d['all_full_actual_PPO_task_outcomes'].pop()
        with self.assertRaises(ValueError):science(d,n_boot=5)

    def test_duplicate_truth_rejected(self):
        d=full()
        d['all_full_actual_PPO_task_outcomes'][0]['truth']=1
        with self.assertRaises(ValueError):science(d,n_boot=5)

    def test_non_native_fake_rejected(self):
        d=full();d['physically_executed_original_controller_worlds']=2559
        with self.assertRaises(ValueError):science(d,n_boot=5)

    def test_int_masquerading_as_boolean_rejected(self):
        d=full();d['all_full_actual_PPO_task_outcomes'][0]['x_wrong']=0
        with self.assertRaises(ValueError):science(d,n_boot=5)

if __name__=='__main__':unittest.main()
