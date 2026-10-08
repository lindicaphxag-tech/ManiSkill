"""Exact finite-sample paired uncertainty for the original NEW64 PhysX audit.

No iid or sampling claim is made by this module. The point estimates and
exact tests describe the given task-seed population; inferential coverage
requires exchangeable, prespecified sampling from a target population.

One source of truth is the eight original, SHA-256-pinned public JSONs.
No new simulator rollouts and no independent academic replication.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from math import comb, isfinite
from pathlib import Path

EVIDENCE = Path(__file__).resolve().parents[1] / (
    "evidence/robust_query_new64_142001_152032"
)
ARMS = (
    "fault_robust_then_single_privileged_query",
    "fault_always_single_privileged_query",
)
TASKS = ("pull_cube", "stack_cube")


def _binomial_cdf(k: int, n: int, p: float) -> float:
    """Exact finite binomial sum, stable enough for the fixed n<=64 assay."""
    if p == 0.0:
        return 1.0
    if p == 1.0:
        return float(k == n)
    return sum(comb(n, j) * p**j * (1-p)**(n-j)
               for j in range(k+1))


def _binomial_survival(k: int, n: int, p: float) -> float:
    """P[X >= k]; compute directly rather than 1-cdf for tiny tail."""
    if p == 0.0:
        return float(k == 0)
    if p == 1.0:
        return 1.0
    return sum(comb(n, j) * p**j * (1-p)**(n-j)
               for j in range(k,n+1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float,float]:
    """Invert binomial tails; exact conservative 1-alpha CI when iid applies."""
    if not (type(k) is int and type(n) is int and n >= 1 and 0 <= k <= n):
        raise ValueError("0 <= integer successes <= positive integer n required")
    if not (isfinite(alpha) and 0 < alpha < 1):
        raise ValueError("alpha must lie strictly between 0 and 1")
    low = 0.0
    high = 1.0
    if k > 0:
        left, right = 0.0, 1.0
        for _ in range(95):
            mid = (left+right)/2
            if _binomial_survival(k,n,mid) < alpha/2:
                left = mid
            else:
                right = mid
        low = (left+right)/2
    if k < n:
        left, right = 0.0, 1.0
        for _ in range(95):
            mid = (left+right)/2
            if _binomial_cdf(k,n,mid) > alpha/2:
                left = mid
            else:
                right = mid
        high = (left+right)/2
    return low, high


def exact_discordant_sign_test(win: int, loss: int) -> float:
    """Two-sided exact McNemar conditional-binomial p; no normal approx."""
    if (type(win) is not int or type(loss) is not int
            or win < 0 or loss < 0):
        raise ValueError("Discordant counts must be nonnegative integers")
    n = win+loss
    if n == 0:
        return 1.0
    tail = sum(comb(n,k) for k in range(min(win,loss)+1)) / 2**n
    return min(1.0,2*tail)


def paired_difference_interval_bonferroni(
    adaptive_only: int, mandatory_only: int, n: int, alpha: float = .05
) -> tuple[float,float]:
    """Conservative joint 1-alpha CI for p10-p01 under iid paired trials.

    Build (1-alpha/2) exact CP intervals for the two multinomial marginal
    cell probabilities, then subtract their endpoints. Bonferroni union
    bound gives >=1-alpha simultaneous coverage, without pretending that
    p10 and p01 are independent. This is deliberately conservative.
    """
    if not (0 <= adaptive_only and 0 <= mandatory_only
            and adaptive_only+mandatory_only <= n):
        raise ValueError("Impossible paired discordance")
    if not (isfinite(alpha) and 0 < alpha < 1):
        raise ValueError("Invalid alpha")
    pa = clopper_pearson(adaptive_only,n,alpha/2)
    pb = clopper_pearson(mandatory_only,n,alpha/2)
    return max(-1.,pa[0]-pb[1]),min(1.,pa[1]-pb[0])


def _load_original_rows(source_root: Path = EVIDENCE) -> list[dict]:
    manifest = source_root/"SHA256SUMS"
    if not manifest.is_file():
        raise ValueError("Missing pinned SHA-256 manifest")
    expected: dict[str,str] = {}
    for raw in manifest.read_text(encoding="utf-8").splitlines():
        sha, name = raw.split(maxsplit=1)
        if len(sha) != 64 or name in expected or "/" in name or not name.endswith(".json"):
            raise ValueError("Malformed SHA manifest")
        expected[name] = sha
    if len(expected) != 8 or {p.name for p in source_root.glob("*.json")} != set(expected):
        raise ValueError("Expected exactly eight original 8-trial JSON shards")
    rows = []
    for task,first in (("pull_cube",142001),("stack_cube",152001)):
        for chunk in range(4):
            name = f"bounded_query_holdout_{task}_chunk{chunk}_original8.json"
            data = (source_root/name).read_bytes()
            if hashlib.sha256(data).hexdigest()!=expected[name]:
                raise ValueError(f"Source file changed: {name}")
            q = json.loads(data)
            chunk_rows = q["episodes"]
            expected_seeds = list(range(first+8*chunk,first+8*chunk+8))
            if [r["seed"] for r in chunk_rows]!=expected_seeds:
                raise ValueError("Missing, duplicated or moved original seed")
            for row in chunk_rows:
                counts = row.get("privileged_target_readback_decision_count",{})
                success = row.get("success_once",{})
                if (any(type(success.get(a)) is not bool for a in ARMS)
                    or type(counts.get(ARMS[0])) is not int
                    or counts[ARMS[0]] not in (0,1)
                    or counts.get(ARMS[1])!=1):
                    raise ValueError("Invalid original source query/success provenance")
                rows.append({"task":task,"seed":row["seed"],
                             "selective_success":success[ARMS[0]],
                             "mandatory_success":success[ARMS[1]],
                             "selective_read":counts[ARMS[0]],
                             "mandatory_read":counts[ARMS[1]]})
    if len(rows)!=64 or len({(r["task"],r["seed"]) for r in rows})!=64:
        raise ValueError("Full independent held-out denominator missing")
    return rows


def analyze_originals(source_root: Path = EVIDENCE) -> dict:
    rows = _load_original_rows(source_root)
    a = sum(r["selective_success"] for r in rows)
    b = sum(r["mandatory_success"] for r in rows)
    wa = sum(r["selective_success"] and not r["mandatory_success"] for r in rows)
    wb = sum(r["mandatory_success"] and not r["selective_success"] for r in rows)
    selected = sum(r["selective_read"] for r in rows)
    mandatory = sum(r["mandatory_read"] for r in rows)
    if (a,b,wa,wb,selected,mandatory)!=(60,57,5,2,15,64):
        raise ValueError("Original preregistered outcomes changed")
    per_task = {
        name:{
            "n":sum(r["task"]==name for r in rows),
            "selective_success":sum(r["task"]==name and r["selective_success"] for r in rows),
            "mandatory_success":sum(r["task"]==name and r["mandatory_success"] for r in rows),
            "selective_reads":sum(r["selective_read"] for r in rows if r["task"]==name),
            "selective_only":sum(r["task"]==name and r["selective_success"]
                                 and not r["mandatory_success"] for r in rows),
            "mandatory_only":sum(r["task"]==name and r["mandatory_success"]
                                 and not r["selective_success"] for r in rows),
        }
        for name in TASKS
    }
    out = {
        "status":"FIRST_SOURCE_ORIGINALS_EXACT_PAIRED_INFERENCE_NOT_EXTERNAL_REPLICATION",
        "population":"64 PREDECLARED source seeds; 32 each on two task families, one simulator",
        "n":64,"n_trained_policies":2,
        "selective_success":a,"mandatory_success":b,
        "selective_privileged_decision_reads":selected,
        "mandatory_privileged_decision_reads":mandatory,
        "relative_read_reduction":1-selected/mandatory,
        "paired_adaptive_only_success":wa,"paired_mandatory_only_success":wb,
        "observed_paired_risk_difference":(wa-wb)/64,
        "exact_two_sided_discordant_sign_test_p":exact_discordant_sign_test(wa,wb),
        "paired_risk_difference_95pct_joint_exact_conservative_ci":
            paired_difference_interval_bonferroni(wa,wb,64),
        "selective_read_probability_95pct_exact_ci_if_iid":
            clopper_pearson(selected,64),
        "per_task_original_paired":per_task,
        "inference_veto":[
            "p-values/intervals require an independently justified exchangeable sampling population; selected simulator reset seeds alone do not establish it",
            "only TWO distinct task families and pretrained policies; 64 different states are not 64 independent policies or robot embodiments",
            "non-significant exact paired success contrast cannot be converted into a non-inferiority/equivalence conclusion",
            "no audit-only controller reads were counted as decision budget; this does not measure wall-clock/network cost",
            "simulation commanded-target bounds are not actuator tracking/contact/collision safety",
            "no independent external lab reproduction or source method novel-theorem acceptance"
        ]
    }
    return out


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    data=analyze_originals()
    content=json.dumps(data,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(content,encoding="utf-8")
    print(content)


if __name__=="__main__":
    main()
