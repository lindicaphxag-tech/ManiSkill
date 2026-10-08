# Upstream submission packet — robomimic #270

Maintainer issue: https://github.com/ARISE-Initiative/robomimic/issues/270

**PR creation link** (the user must open it in an authenticated browser):
https://github.com/ARISE-Initiative/robomimic/compare/master...lindicaphxag-tech:robomimic:fix/add-delta-actions-converter-pr?expand=1

The connected GitHub integration attempted to create this upstream PR on
2026-10-09 and got `403 Resource not accessible by integration`.
**No upstream PR has been created through the integration**.
Use the browser's green **Create pull request** button to publish.

## PR title

`feat(robosuite): convert absolute OSC demonstrations to native delta actions`

## PR body (copy verbatim or edit)

Related to #270 — thanks for the maintainer invitation to contribute this
converter.

This adds a robosuite absolute-OSC-pose to delta-OSC-action conversion path
for robomimic datasets. It allows data generated using an absolute OSC
controller to be re-expressed for the matching achieved-relative delta
controller, with a clear accounting of commands that are not representable
under target input bounds.

### Design
- Inverts the actual native input limits and controller action scaling,
  rather than treating position/rotation values as interchangeable.
- Computes relative orientation in **SO(3)** through pose composition;
  does not subtract axis-angle vectors.
- Uses the controller's actual achieved EE pose and input reference frame.
- Handles both legacy robosuite and >=1.5 composite controller metadata.
- Preserves gripper actions, supports dataset-level processing, and
  integrates with existing robomimic conversion/action-extraction paths.
- **Refuses** controller modes relying on inaccessible previous
  desired-target memory, variable impedance or unsupported semantics;
  documents representability/saturation instead of promising lossless
  conversion.

### Validation
- Includes focused native scaling/SO(3) inverse unit tests and
  simulator-backed real Panda OSC inverse tests.
- The six files in this one-commit PR are **Git-blob identical** to the
  same files on the tested fork validation branch
  `validation/delta-actions-real-osc-20261008`.
- 20-test public robosuite CPU integration run:
  https://github.com/lindicaphxag-tech/robomimic/actions/runs/37715504522
- Separate cross-task Lift/Stack controller run:
  https://github.com/lindicaphxag-tech/robomimic/actions/runs/37713698317

The external validation suite contains additional research tests beyond
the six-file upstream patch; the test results must not be described as
a full upstream robomimic CI pass.

### Limitations
This patch does not claim perfect conversion of every demonstration or
physical task-success parity after source/target controller swaps. It
targets *known achieved-relative fixed-impedance OSC semantics*; controller
memory that is not present in the dataset cannot be fabricated.

**AI assistance disclosure:** AI tools assisted with code drafting, review
and test automation. All relevant source and CI artifacts are public for
maintainer review; I welcome changes to fit repository conventions.

## Submission readiness

- [x] Target base is official `master`
- [x] Head has **1 commit ahead, 0 behind** as verified Oct 9
- [x] No duplicate PR from this author found in an upstream query
- [x] Six code/test files match the publicly tested fork by Git blob
- [x] Maintainer comment #270 explicitly welcomes a PR
- [ ] User must open the link and click **Create pull request**
- [ ] Await real maintainer feedback/CI, make requested revisions and
      distinguish acceptance from mere publication
