import unittest
from research.paired_action_portfolio_ceiling import audit_ceiling,TASKS,ARMS
def fake():
    rows=[]
    for task,start in TASKS.items():
        for arm in ARMS:
            for seed in range(start,start+16):
                for truth in range(4):
                    rows.append(dict(task=task,arm=arm,seed=seed,truth=truth,
                        zero_success=truth<3,x_success=truth in (1,2),
                        zero_wrong=False,x_wrong=False,zero_privileged_reads=0,
                        x_privileged_reads=0))
    return dict(status="REAL_COMPLETED_NEW_FREEZE_PPO_TASK_SOURCE_AUDITED",
        physically_executed_original_controller_worlds=2560,
        new_independent_reset_clusters=32,matched_original_PPO_task_cells=256,
        original_shard_file_sha256={str(i):"x"*64 for i in range(72)},
        all_full_actual_PPO_task_outcomes=rows)
class PortfolioCeiling(unittest.TestCase):
    def test_constructed_not_actual_physics(self):
        d=audit_ceiling(fake())["by_task"]["stack_cube:"+ARMS[0]]
        self.assertEqual((d["zero_success"],d["x_success"],d["both_fail"]),(48,32,16))
        self.assertEqual(d["hindsight_oracle_extra_success"],0)
    def test_x_only_does_not_mean_clean(self):
        a=fake();r=a["all_full_actual_PPO_task_outcomes"][0]
        r["zero_success"]=False;r["x_success"]=True;r["x_wrong"]=True
        d=audit_ceiling(a)["pooled"][ARMS[0]]
        self.assertEqual(d["hindsight_oracle_extra_success"],1)
        self.assertEqual(d["clean_hindsight_oracle_extra_success"],0)
    def test_reject_missing_cell(self):
        a=fake();a["all_full_actual_PPO_task_outcomes"].pop()
        with self.assertRaises(ValueError):audit_ceiling(a)
    def test_reject_duplicate_cell(self):
        a=fake();a["all_full_actual_PPO_task_outcomes"][1]=a["all_full_actual_PPO_task_outcomes"][0]
        with self.assertRaises(ValueError):audit_ceiling(a)
    def test_reject_false_sample_number(self):
        a=fake();a["new_independent_reset_clusters"]=256
        with self.assertRaises(ValueError):audit_ceiling(a)
    def test_reject_broken_truth(self):
        a=fake();a["all_full_actual_PPO_task_outcomes"][0]["x_wrong"]=1
        with self.assertRaises(ValueError):audit_ceiling(a)
if __name__=="__main__":unittest.main()
