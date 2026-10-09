"""Dependency-free adversarial falsifiers for full-source cross-robot evidence."""
import unittest
from copy import deepcopy

from research.audit_cross_robot_ack_physx import audit


def valid(robot="panda",chunk=0):
    first=420001 if robot=="panda" else 430001
    rows=[]
    for seed in range(first+4*chunk,first+4*chunk+4):
        error={"linf_m":0.0,"l2_m":0.0,"so3_rad":0.0}
        rows.append(dict(
            robot_uid=robot,seed=seed,task="PickCube-v1",
            control_mode="pd_ee_target_delta_pose",
            real_physx_cpu=True,source_policy_trained=False,
            native_command_ack_visible="unknown",
            xarm6_is_not_a_Panda_relabel=robot=="xarm6_robotiq",
            pair_reset_l2_m=0.,
            both_private_target_reads_for_audit_only=True,
            native_requested_commands=[
                [0.15,-0.1,0.1,0.02,-0.02,0.01],
                [-0.1,0.16,0.05,0.02,0.015,-0.01],
                [0.45,-0.3,0.35,0.25,-0.12,0.1],
                [0.]*6,[0.]*6,[0.]*6],
            commanded_target_residual_by_step={
                "applied":[error.copy() for _ in range(6)],
                "held":[error.copy() for _ in range(6)]},
            commanded_target_residual_max_linf_m_applied=0.,
            commanded_target_residual_max_linf_m_held=0.,
            commanded_target_residual_max_so3_rad_applied=0.,
            commanded_target_residual_max_so3_rad_held=0.,
            fault_divergence={"linf_m":0.02,"l2_m":0.02,"so3_rad":0.},
            fault_target_distinct=True,
            probe={"achieved_ee_xyz_applied":[0.01,0,0],
                   "achieved_ee_xyz_held":[0,0,0],
                   "achieved_ee_branch_distance_m":0.01,
                   "probe_native_arm_command":[0.]*6,
                   "private_target_reads_used_in_inference":0},
            official_task_success_by_truth={"applied":False,"held":False}))
    return dict(schema="cross_embodiment_stateful_action_observability_physics_v1",
        protocol="research/CROSS_EMBODIMENT_ACK_PREOUTCOME_V1.json",
        robot=robot,task="PickCube-v1",control="pd_ee_target_delta_pose",
        real_physx_cpu=True,all_seeds=[r["seed"] for r in rows],done=True,
        author_executed_only=True,external_independent_replication=False,
        not_policy_transfer_or_task_success_claim=True,
        nonzero_target_divergence=4,
        probe_achieved_ee_separation_m=[0.01]*4,
        rows=rows)


class AuditContract(unittest.TestCase):
    def test_valid_two_distinct_robots(self):
        for robot in ("panda","xarm6_robotiq"):
            self.assertEqual(audit(valid(robot),robot,0)["target_history_divergence"],4)
    def test_mislabeled_panda_as_xarm_is_rejected(self):
        source=valid("xarm6_robotiq")
        source["rows"][0]["robot_uid"]="panda"
        with self.assertRaises(ValueError):audit(source,"xarm6_robotiq",0)
    def test_missing_negative_seeds_not_hidden(self):
        source=valid()
        source["rows"].pop()
        with self.assertRaises(ValueError):audit(source,"panda",0)
    def test_private_target_read_in_observer_is_rejected(self):
        source=valid()
        source["rows"][0]["probe"]["private_target_reads_used_in_inference"]=1
        with self.assertRaises(ValueError):audit(source,"panda",0)
    def test_false_nonzero_divergence_claim_refused(self):
        source=valid()
        source["rows"][0]["fault_divergence"]={"linf_m":0.,"l2_m":0.,"so3_rad":0.}
        with self.assertRaises(ValueError):audit(source,"panda",0)
    def test_reconstruction_error_cannot_be_hidden(self):
        source=valid()
        source["rows"][0]["commanded_target_residual_by_step"]["held"][2]["linf_m"]=.02
        with self.assertRaises(ValueError):audit(source,"panda",0)
    def test_physical_proprioceptive_separation_must_match_coordinates(self):
        source=valid()
        source["rows"][0]["probe"]["achieved_ee_branch_distance_m"]=0.
        with self.assertRaises(ValueError):audit(source,"panda",0)
    def test_negative_official_task_outcomes_are_permitted(self):
        z=valid()
        self.assertFalse(any(r["official_task_success_by_truth"]["applied"] for r in z["rows"]))
        self.assertEqual(audit(z,"panda",0)["n"],4)
    def test_ground_truth_exposure_not_a_policy_transfer(self):
        z=valid()
        z["not_policy_transfer_or_task_success_claim"]=False
        with self.assertRaises(ValueError):audit(z,"panda",0)

if __name__=="__main__":unittest.main()
