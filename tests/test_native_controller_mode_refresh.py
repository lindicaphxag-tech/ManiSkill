import unittest
from types import SimpleNamespace
from research.native_controller_mode_refresh import with_native_public_mode_refresh

class FakeVec:
    def __init__(self,n):self.shape=(1,n)
class PublicPose:
    p=FakeVec(3)
    q=FakeVec(4)
class PDEEPoseController:
    def __init__(self):
        self.config=SimpleNamespace(
            frame='root_translation:root_aligned_body_rotation',
            use_delta=True,use_target=True,normalize_action=True)
        self.ee_pose_at_base=PublicPose()
        self.hidden_target=2.0
        self.achieved=0.1
        self.dispatches=0
    def set_action_zero(self):
        self.dispatches+=1
        self.hidden_target=self.hidden_target if self.config.use_target else self.achieved
        return {'official_task_success':False}
    def set_state(self,*args):raise AssertionError('Forbidden hidden setter')
    def get_state(self,*args):raise AssertionError('Forbidden hidden getter')

class ModeRefreshReferenceTests(unittest.TestCase):
    def kwargs(self,arm):
        return dict(arm=arm,dispatch_actual_world_step=arm.set_action_zero,
          expected_controller_type='PDEEPoseController',
          current_cpu_simulator=True,mode_mutation_authorized=True,
          dispatch_is_known_delivered=True)
    def test_one_actual_step_reanchors_not_a_success_claim(self):
        a=PDEEPoseController()
        r,t=with_native_public_mode_refresh(**self.kwargs(a))
        self.assertEqual(r['official_task_success'],False)
        self.assertEqual((a.hidden_target,a.dispatches),(a.achieved,1))
        self.assertTrue(a.config.use_target)
        self.assertEqual((t.mode_writes,t.hidden_target_reads,t.hidden_target_writes),(2,0,0))
        self.assertFalse(t.success_claimed)
    def test_no_mode_write_permission(self):
        a=PDEEPoseController();k=self.kwargs(a);k['mode_mutation_authorized']=False
        with self.assertRaises(PermissionError):with_native_public_mode_refresh(**k)
        self.assertEqual(a.dispatches,0)
    def test_untrusted_ack_fails_closed(self):
        a=PDEEPoseController();k=self.kwargs(a);k['dispatch_is_known_delivered']=False
        with self.assertRaises(PermissionError):with_native_public_mode_refresh(**k)
    def test_wrong_chart_refuses(self):
        a=PDEEPoseController();a.config.frame='body_translation:body_aligned_body_rotation'
        with self.assertRaises(ValueError):with_native_public_mode_refresh(**self.kwargs(a))
    def test_no_accumulated_target_refuses(self):
        a=PDEEPoseController();a.config.use_target=False
        with self.assertRaises(ValueError):with_native_public_mode_refresh(**self.kwargs(a))
    def test_unsupported_runtime_controller_refuses(self):
        class Other(PDEEPoseController): pass
        a=Other()
        with self.assertRaises(ValueError):with_native_public_mode_refresh(**self.kwargs(a))
    def test_exception_restores_original_mode(self):
        a=PDEEPoseController();k=self.kwargs(a)
        def fail():
            self.assertFalse(a.config.use_target)
            raise RuntimeError('simulator failure')
        k['dispatch_actual_world_step']=fail
        with self.assertRaises(RuntimeError):with_native_public_mode_refresh(**k)
        self.assertTrue(a.config.use_target)
    def test_config_mode_mutated_only_during_one_step(self):
        a=PDEEPoseController()
        with_native_public_mode_refresh(**self.kwargs(a))
        self.assertEqual((a.dispatches,a.hidden_target),(1,.1))

if __name__=='__main__':unittest.main()
