from research.eprc.runtime import (
    ContractClass,
    Decision,
    Evidence,
    compile_contract,
    contract_agreement,
    verify_certificate,
)


PROVENANCE = (
    "policy=diffusion_pusht",
    "chunk=42",
    "anchor=state_t",
    "controller=pd_ee_delta_pose",
)


def base(**overrides):
    values = dict(
        semantics_known=True,
        provenance_valid=True,
        representability_margin=0.2,
        canonical_command_error=0.2,
        exact_transport_available=False,
        support_stability=0.99,
        held_out_residual=0.01,
        transverse_norm=0.02,
        certified_repair_radius=0.05,
        contract_class=ContractClass.RELATIONAL_INVARIANT,
        support_ids=("block",),
    )
    values.update(overrides)
    return Evidence(**values)


def test_pass_when_physical_command_is_already_valid():
    c = compile_contract(base(canonical_command_error=1e-8), provenance_parts=PROVENANCE)
    assert c.decision is Decision.PASS


def test_exact_transport_precedes_local_repair():
    c = compile_contract(base(exact_transport_available=True), provenance_parts=PROVENANCE)
    assert c.decision is Decision.TRANSPORT


def test_bounded_repair_requires_all_evidence_gates():
    c = compile_contract(base(), provenance_parts=PROVENANCE)
    assert c.decision is Decision.REPAIR
    assert verify_certificate(c, base(), provenance_parts=PROVENANCE)


def test_rejects_nonrepresentable_command():
    c = compile_contract(base(representability_margin=-1e-3), provenance_parts=PROVENANCE)
    assert c.decision is Decision.REJECT


def test_rejects_unstable_support_even_if_local_error_is_small():
    c = compile_contract(base(support_stability=0.4), provenance_parts=PROVENANCE)
    assert c.decision is Decision.REJECT


def test_rejects_failed_heldout_intervention_prediction():
    c = compile_contract(base(held_out_residual=0.2), provenance_parts=PROVENANCE)
    assert c.decision is Decision.REJECT


def test_rejects_outside_certified_repair_radius():
    c = compile_contract(
        base(transverse_norm=0.08, certified_repair_radius=0.05),
        provenance_parts=PROVENANCE,
    )
    assert c.decision is Decision.REJECT


def test_certificate_is_bound_to_provenance():
    c = compile_contract(base(), provenance_parts=PROVENANCE)
    changed = (*PROVENANCE[:-1], "controller=pd_joint_pos")
    assert not verify_certificate(c, base(), provenance_parts=changed)


def test_cross_policy_contract_class_agreement():
    assert contract_agreement(
        [ContractClass.RELATIONAL_INVARIANT, ContractClass.RELATIONAL_INVARIANT]
    )
    assert not contract_agreement(
        [ContractClass.RELATIONAL_INVARIANT, ContractClass.MIXED]
    )
