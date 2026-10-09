"""Real ManiSkill multi-history integration, WITHOUT pretending a synthetic VLA is pretrained.

Runs the actual source classes `TargetPose`, `UncertainDeliveryBelief`
and `common_multi_history_command`; tests physical action provenance,
idempotency, source-root transform and uncertain ACK failure/recovery.
"""
import unittest
import numpy as np
from scipy.spatial.transform import Rotation
from research.action_abi_history_observer import TargetPose
from research.action_abi_uncertain_delivery_belief import UncertainDeliveryBelief
from research.multi_ack_se3_bounded import common_multi_history_command
from research.vla_beliefbridge.vla_controller_bridge import (
    ActionProvenance,VisualObservation,RecedingHorizonVLAGateway,ContractViolation)

def contract(**changes):
    cfg=dict(model_id="lerobot/smolvla_base",
        checkpoint_sha="a"*40,dataset_id="operator-verified-task-specific-vla-dataset",
        normalization_sha="b"*40,
        action_representation="ee_delta_xyz_rotvec_gripper",
        action_frame="root",rotation_rule="root_left_multiply",
        linear_units="meter",angular_units="radian",
        pipeline="lerobot_postprocessed_physical",
        task_specific_action_mapping_verified=True)
    cfg.update(changes)
    return ActionProvenance(**cfg)

def obs(t,episode="real_controller_test"):
    return VisualObservation(episode,t,(0.,0.,0.),(0.,0.,0.,1.))

def actions(dx=.01):
    c=np.zeros((4,7),dtype=float)
    c[:,0]=dx
    c[:,6]=.4
    return c

def gateway(*,pos_budget=.05):
    belief=UncertainDeliveryBelief([-.1]*3,[.1]*3,[.2]*3,max_hypotheses=16)
    belief.reset(TargetPose.from_arrays([0]*3,[0,0,0,1]))
    return RecedingHorizonVLAGateway(
        contract(),belief,common_multi_history_command,TargetPose,
        max_pos_error_m=pos_budget)

def fresh(g,t,dx=.01):
    g.observe(obs(t),actions(dx),model_checkpoint_sha="a"*40,
              normalizer_sha="b"*40)

class RealNativeBeliefIntegration(unittest.TestCase):
    def test_true_multi_history_closed_loop_not_fake_singleton(self):
        g=gateway()
        fresh(g,0)
        decision=g.decide()
        self.assertEqual(decision.code,"SEND_CERTIFIED")
        self.assertEqual(decision.hypothesis_count,1)
        g.acknowledge(decision.ticket,applied=None)  # TWO physical target states.
        self.assertEqual(len(g.belief.hypotheses),2)
        with self.assertRaises(ContractViolation):
            g.decide()  # chunk cannot continue after unknown ACK.
        fresh(g,1)
        d2=g.decide()
        self.assertEqual(d2.code,"SEND_CERTIFIED")
        self.assertEqual(d2.hypothesis_count,2)
        self.assertLessEqual(d2.worst_position_m,.05)
        # A second unknown ACK keeps every candidate; no invented truth.
        g.acknowledge(d2.ticket,applied=None)
        self.assertGreaterEqual(len(g.belief.hypotheses),2)

    def test_no_query_unless_certified_bound_denied(self):
        g=gateway(pos_budget=.001)
        fresh(g,0,dx=.02); d=g.decide()
        self.assertEqual(d.code,"SEND_CERTIFIED")
        g.acknowledge(d.ticket,applied=None)
        fresh(g,1,dx=.02); second=g.decide()
        self.assertEqual(second.code,"QUERY_TARGET")
        self.assertIsNone(second.native_arm_command)
        with self.assertRaisesRegex(ContractViolation,"NOT private"):
            g.trusted_controller_resync(TargetPose.from_arrays([0]*3,[0,0,0,1]),
                evidence="achieved_ee_pose")
        g.trusted_controller_resync(TargetPose.from_arrays([0]*3,[0,0,0,1]),
            evidence="authoritative_controller_target_readback")
        self.assertEqual(len(g.belief.hypotheses),1)
        fresh(g,2,dx=.02)
        self.assertEqual(g.decide().code,"SEND_CERTIFIED")

    def test_policy_abi_mismatch_and_unnormalized_output_forbidden(self):
        with self.assertRaises(ContractViolation):
            RecedingHorizonVLAGateway(contract(task_specific_action_mapping_verified=False),
                gateway().belief,common_multi_history_command,TargetPose)
        with self.assertRaises(ContractViolation):
            RecedingHorizonVLAGateway(contract(action_representation="joint_position"),
                gateway().belief,common_multi_history_command,TargetPose)
        g=gateway()
        with self.assertRaises(ContractViolation):
            g.observe(obs(0),actions(),model_checkpoint_sha="mismatched",normalizer_sha="b"*40)
        wrong=actions();wrong[0,0]=float("nan")
        with self.assertRaises(ContractViolation):
            g.observe(obs(0),wrong,model_checkpoint_sha="a"*40,normalizer_sha="b"*40)

    def test_out_of_order_ack_and_duplicate_visual_state_forbidden(self):
        g=gateway()
        fresh(g,0)
        d=g.decide()
        with self.assertRaises(ContractViolation):
            g.acknowledge(("old",999),applied=True)
        with self.assertRaises(ContractViolation):
            g.trusted_controller_resync(TargetPose.from_arrays([0]*3,[0,0,0,1]),
                evidence="authoritative_controller_target_readback")
        g.acknowledge(d.ticket,applied=True)
        with self.assertRaises(ContractViolation):
            fresh(g,0)
        fresh(g,1)
        self.assertEqual(g.decide().code,"SEND_CERTIFIED")

    def test_live_smolvla_queue_is_dropped_after_dispatch_and_resync(self):
        class Policy:
            def __init__(self):self.queued=5;self.events=0
            def drop_queued_actions(self):self.queued=0;self.events+=1
            def count_queued_actions(self):return self.queued
        p=Policy();g=gateway()
        g.bind_live_policy(p)
        self.assertEqual(p.queued,0)
        p.queued=49  # A real SmolVLA select_action can cache a whole chunk.
        observed_generation=g.current_inference_generation
        g.observe(VisualObservation("real_controller_test",0,(0.,0.,0.),
            (0.,0.,0.,1.),inference_generation=observed_generation),
            actions(),model_checkpoint_sha="a"*40,normalizer_sha="b"*40)
        d=g.decide()
        self.assertEqual(d.code,"SEND_CERTIFIED")
        self.assertEqual(p.queued,0)
        self.assertGreater(g.current_inference_generation,observed_generation)
        p.queued=13
        g.acknowledge(d.ticket,applied=None)
        self.assertEqual(p.queued,0)
        p.queued=21
        g.trusted_controller_resync(
            TargetPose.from_arrays([0]*3,[0,0,0,1]),
            evidence="authoritative_controller_target_readback")
        self.assertEqual(p.queued,0)
        self.assertGreaterEqual(p.events,4)

    def test_delayed_async_vla_result_rejected_after_unknown_ack(self):
        class Policy:
            def __init__(self):self.queued=12
            def drop_queued_actions(self):self.queued=0
            def count_queued_actions(self):return self.queued
        g=gateway()
        g.bind_live_policy(Policy())
        old_generation=g.current_inference_generation
        g.observe(VisualObservation("real_controller_test",0,(0.,0.,0.),
            (0.,0.,0.,1.),inference_generation=old_generation),
            actions(),model_checkpoint_sha="a"*40,normalizer_sha="b"*40)
        d=g.decide()
        g.acknowledge(d.ticket,applied=None)
        # A model generation request launched before the command reached the
        # robot must not be replayed after the hidden target belief branches.
        with self.assertRaisesRegex(ContractViolation,"Stale asynchronous"):
            g.observe(VisualObservation("real_controller_test",1,(0.,0.,0.),
                (0.,0.,0.,1.),inference_generation=old_generation),
                actions(),model_checkpoint_sha="a"*40,normalizer_sha="b"*40)
        new_generation=g.current_inference_generation
        self.assertGreater(new_generation,old_generation)
        g.observe(VisualObservation("real_controller_test",1,(0.,0.,0.),
            (0.,0.,0.,1.),inference_generation=new_generation),
            actions(),model_checkpoint_sha="a"*40,normalizer_sha="b"*40)
        self.assertIn(g.decide().code,("SEND_CERTIFIED","QUERY_TARGET"))

    def test_live_policy_with_unverifiable_queue_rejected(self):
        class BrokenPolicy:
            def drop_queued_actions(self):pass
            def count_queued_actions(self):return 49
        g=gateway()
        with self.assertRaisesRegex(ContractViolation,"Stale"):
            g.bind_live_policy(BrokenPolicy())
        with self.assertRaises(ContractViolation):
            gateway().bind_live_policy(object())

    def test_episode_reset_cannot_launder_outstanding_physical_command(self):
        g=gateway()
        fresh(g,0)
        d=g.decide()
        self.assertEqual(d.code,"SEND_CERTIFIED")
        self.assertEqual(g.pending,d.ticket)
        before_hypotheses=tuple(g.belief.hypotheses)
        authoritative_zero=TargetPose.from_arrays([0]*3,[0,0,0,1])
        with self.assertRaisesRegex(ContractViolation,"pending native action"):
            g.reset_episode(authoritative_zero,evidence="authoritative_controller_reset")
        self.assertEqual(g.pending,d.ticket)
        self.assertEqual(tuple(g.belief.hypotheses),before_hypotheses)
        # A late, unknown ACK must remain valid and preserve its branching
        # until a genuine acknowledged episode transition occurs.
        g.acknowledge(d.ticket,applied=None)
        self.assertGreaterEqual(len(g.belief.hypotheses),2)
        g.reset_episode(authoritative_zero,evidence="authoritative_controller_reset")
        self.assertEqual(len(g.belief.hypotheses),1)
        self.assertIsNone(g.pending)

    def test_exact_root_left_compose_uses_achieved_pose_not_private_target(self):
        # A 90-degree rotation around X followed by a command around Z must
        # be pre-multiplied in the root frame, not right-multiplied.
        base=Rotation.from_euler("x",90,degrees=True)
        desired=Rotation.from_rotvec([0,0,.03])*base
        h=TargetPose.from_arrays([0]*3,base.as_quat())
        g=gateway()
        g.reset_episode(h,evidence="authoritative_controller_reset")
        o=VisualObservation("test",0,(0,0,0),tuple(base.as_quat()))
        a=actions(dx=0);a[0,3:6]=[0,0,.03]
        g.observe(o,a,model_checkpoint_sha="a"*40,normalizer_sha="b"*40)
        d=g.decide()
        self.assertEqual(d.code,"SEND_CERTIFIED")
        native=Rotation.from_euler("XYZ",np.asarray(d.native_arm_command)[3:]*.2)
        measured=native*base
        self.assertLess((measured.inv()*desired).magnitude(),.05)

if __name__=="__main__":
    unittest.main()
