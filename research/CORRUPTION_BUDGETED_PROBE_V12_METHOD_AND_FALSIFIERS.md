# BeliefBridge v12 — Corruption-budgeted repair-aware minimax observation

Scientific status 2026-10-10: **MODEL-ONLY algorithm and independently verified code**, not a new robot task result. Public reference experiment has [6/6 GitHub Actions OS/Python matrix green](https://github.com/lindicaphxag-tech/ManiSkill/actions/runs/38001719893), including `python -O` no-assertions validation. All numbers below are deterministic finite-model arithmetic, not PhysX success rates.

## Problem / new repair-state decision contract

A frozen robot policy issues a desired move while a native target-relative controller may have silently held or applied a prior command. Let latent controller histories h belong to a finite set H with a map R(h) to an **authorized repair action** (not necessarily a unique physical history). A public, *repeatable and repair-preserving* probe has a deterministic correctly delivered symbolic response f(h) in a predeclared finite alphabet A. The entire episode admits at most K adversarially corrupted probe observations.

The new robust information state is B_t = {(h,c)}, where c is the number of already observed inconsistent public symbols under candidate history h. After observing y:

```
B_(t+1) = {(h,c+1[y != f(h)]): (h,c) in B_t and c+1[y != f(h)] <= K}
```

A decision may authorize R only if **all h represented in B agree on R(h)**; otherwise choose the next probe or a privileged controller target read. The finite-horizon Bellman value is

```
V(B,d) = 0                                   if repair-equivalent(B)
         min(C_read, C_probe+max_y V(post(B,y),d-1)) if d>0
         C_read                              if d=0
```

with max_y only over observation symbols compatible with at least one retained (history,corruption-count) state. The verifier independently replays the full tree, checks every declared branch and repair label, then recomputes the **globally cheapest minimax value**, rejecting a fully self-consistent but nonoptimal tree. Every unsupported observation forces a privileged read and invalidates any original cost certificate for that trace.

### Conditional finite guarantee (not new universal POMDP theory)

**Correct repair authorization** follows by induction: under (i) complete initial H, (ii) correct static f(h), (iii) at most K corrupted responses, (iv) repair-invariant probing, the real h with its accumulated c always belongs to B_t; authorization requires a common R. **Model-optimal abstract worst-case cost** follows by finite-horizon Bellman induction. These standard proof patterns do NOT guarantee actual dynamics, safety, collision clearance, latency, sensor calibration or correctness under K+1 corruptions.

### Actual code test results and quantified falsifiers

Public code `research/adversarial_probe_budget.py`, unit `tests/test_adversarial_probe_budget.py`, arithmetic `research/reliability_cost_tradeoff.py`.

- Two latent controller histories (APPLIED vs HELD), two distinct repairs, repeatable public probe cost 1, privileged read cost 5, at most 3 public probes.
- **K=0:** modeled optimal cost 1 (one separating response).
- **K=1:** modeled optimal worst cost 3 (may require three repeated corroborating responses); exact enumeration of all eight ground-truth response sequences containing at most one spoof found **zero incorrect model authorizations**.
- **K=1, probe depth=2:** modeled optimal cost 5 (direct privileged read).
- **K=1, privileged read cost=2:** modeled optimal cost 2 (read rather than probe).
- **K+1 corruption attack:** two systematic false 'held' replies can produce the wrong repair for the actually applied history. The code contains this deliberate counterexample.
- **Additional IID noise model** with independent per-probe error p: one-observation wrong repair p; robust protocol wrong repair `3p²−2p³`; mean number of public probes `2+2p(1−p)`. For hypothetical p=.10, 10.0% to 2.8% (**72% modeled relative reduction**), mean 2.18 public probes, worst 3.
- **CORRELATED counterexample:** mixture rho of episodes with fully correlated erroneous readings has failure `(1−rho)(3p²−2p³)+rho p`. At p=.10, rho=.5 -> 6.4%; rho=1 -> 10.0% (no reduction). This is particularly relevant for static camera occlusion or repeated environment mistakes.
- **Developer safety:** modeled input validation and proof field types are explicit ValueErrors, not `assert`, because Python -O suppresses assertions. `python -O -m unittest ...` passes on public OS/Python CI matrix. The finite model still assumes truly static h and a physically nondisruptive probe.

### Prior accepted work / main-track gap

Accepted RSS 2025 *Map Space Belief Prediction for Manipulation-Enhanced Mapping*: https://www.roboticsproceedings.org/rss21/p039.html physically grounds active belief updates. The current finite error-budget decision tree is *not* an unprecedented decision-tree invention or a physical result. The publishable robotic-science claim depends on **actual PhysX/real closed-loop probe action execution** on unseen initial states, with measured public-sensor error autocorrelation, complete response support, same-start comparator baselines and calibrated wrong-repair/mission-success outcomes. The historical distinct 32 reset states ×2 fault scenarios, zero-read midpoint 43/64 vs one-read 62/64, remains an unresolved negative task-control baseline. The model-only new 72% value is NOT a performance improvement on those 64 physical episodes.

### Release constraints

Sources and synthetic model artifacts are open in this ManiSkill research branch, but this does not mean merged external upstream, acceptance, independently lab-verified physical adaptation or a safety-certified clinical device. Review changes as Git commit and CI evidence, not a submission-ready publication.
