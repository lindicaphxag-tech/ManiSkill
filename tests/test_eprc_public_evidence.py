from research.eprc.audit_public_evidence import audit


def test_public_diffusion_pusht_refusal_evidence():
    result = audit("research/eprc/evidence/diffusion_pusht_refusal.json")
    assert result == {
        "states": 4,
        "harmful_raw_repairs": 4,
        "accepted_repairs": 0,
        "exact_fallbacks": 4,
    }
