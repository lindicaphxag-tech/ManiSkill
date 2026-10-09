"""Drop-in third-party JSON schema exercise; no ManiSkill/SAPIEN installed."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from research.effect_aware_authority_certificate import synthesize, verify_optimality
from research.repair_authority_cli import parse_contract

ROOT=Path("research/fixtures")

class ThirdPartyAuthorityCLI(unittest.TestCase):
    def load(self,which):
        return parse_contract(json.loads((ROOT/f"authority_{which}.json").read_text()))

    def test_aliased_getter_stops_instead_of_inventing_full_state(self):
        result=synthesize(self.load("aliased_getter"))
        self.assertEqual(result["root"]["kind"],"halt")
        self.assertEqual(result["minimax_cost"],10)

    def test_fresh_complete_getter_requires_read_before_repair(self):
        result=synthesize(self.load("fresh_complete_getter"))
        self.assertEqual(result["root"]["kind"],"read")
        self.assertEqual(result["minimax_cost"],2)

    def test_probe_outperforms_aliased_getter_in_known_synthetic_model(self):
        m=self.load("cheap_discriminating_probe")
        result=synthesize(m)
        self.assertEqual(result["root"]["kind"],"probe")
        self.assertEqual(result["root"]["probe"],"discriminating_probe")
        self.assertEqual(result["minimax_cost"],1)
        self.assertTrue(verify_optimality(m,result)["exact_independent_oracle_optimal"])

    def test_strict_json_rejects_missing_contract_fields(self):
        v=json.loads((ROOT/"authority_aliased_getter.json").read_text())
        del v["read_atomic_and_fresh"]
        with self.assertRaisesRegex(ValueError,"Unexpected"):
            parse_contract(v)

    def test_actual_no_dependencies_cli_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"cert.json"
            fixture=ROOT/"authority_cheap_discriminating_probe.json"
            command=[sys.executable,"-m","research.repair_authority_cli"]
            p=subprocess.run(command+["--mode","synthesize","--contract",
                                      str(fixture),"--output",str(out)],
                             text=True,capture_output=True,check=True)
            self.assertIn("FINITE_MODEL_ONLY",p.stdout)
            p=subprocess.run(command+["--mode","verify","--contract",
                                      str(fixture),"--certificate",str(out)],
                             text=True,capture_output=True,check=True)
            self.assertIn("PASS_CONDITIONAL",p.stdout)
            bad=json.loads(out.read_text())
            bad["root"]["branches"]["good_seen"]["repair"]="RESET"
            out.write_text(json.dumps(bad))
            fail=subprocess.run(command+["--mode","verify","--contract",
                                       str(fixture),"--certificate",str(out)],
                                text=True,capture_output=True)
            self.assertNotEqual(fail.returncode,0)
            self.assertIn("Unsafe repair effect",fail.stderr)


if __name__=="__main__":
    unittest.main()
