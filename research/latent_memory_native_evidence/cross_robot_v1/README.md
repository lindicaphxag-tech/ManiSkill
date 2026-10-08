# Actual native two-robot conditional joint-memory certificate witnesses
Original successful source: 37822030370, head abdaa361c3244d524c2c5b19214900058057f20d.
Frozen protocol before new runner: b08754959722f1639510b9cc7537aea4e479b1cf.
Byte-identical original JSON/log, exactly SHA-256 matched by this workflow before committing.
Four source robot/seed cases: Fetch 1271,1282 (7 arm joints; native 13D action) and XArm6 Robotiq 2373,2384 (6 arm joints; 7D native action).
Unmodified official ManiSkill PickCube PhysX target joint-position controller; minmax memory interval radius .001 radians, source-target prediction discrepancy <= 5.15e-8 rad and 2.10e-8 rad respectively.
This validates target-controller command semantics on two different simulated embodiments; it does NOT establish frozen-policy robot task transfer, physical robot actuation/safety, independently attested hidden memory, or external third-party adoption.
