# LeRobot DATA-04 maintainer decision packet

Target: Community Roadmap DATA-04 — converge on one reliable video frame-addressing convention.

This packet asks one design question before any upstream implementation.

## Source-level observation

LeRobot v3 already behaves as if **episode-local integer frame index** is the logical sample identity:

- writer sets `frame_index = n`;
- writer derives `timestamp = n / fps`;
- delta timestamps are required to lie on the `1/fps` grid and are converted back to integer delta indices;
- tabular neighbor selection is index-based.

The video decoder path can then re-derive a frame index from timestamp and decoder-reported average fps.

Therefore the chain is potentially:

`n -> n/dataset_fps -> round(ts * decoder_average_fps) -> m`.

This is not an identity for arbitrary rate representations.

## Lowest-migration design

No v3 schema change is required for a first index-first reader.

Existing per-episode metadata contains:

- episode `length`;
- video `chunk_index`;
- video `file_index`.

For episodes concatenated into one physical video file, the file-local logical offset is exactly derivable by cumulatively summing prior episode lengths that share the same `(chunk_index, file_index)`.

A compatibility gate can then require:

`decoded_frame_count == sum(episode lengths in that physical file)`.

If it passes, TorchCodec can use `get_frames_at(indices=...)` directly. If it fails or cannot be established, the reader keeps the legacy timestamp path and surfaces an integrity/compatibility status.

## Minimal maintainer question

Which semantic contract does LeRobot want DATA-04 to converge on?

**A — Integer logical frame identity.**
Timestamp remains synchronization/seek metadata; index is canonical when file integrity is provable.

**B — Timestamp/PTS identity.**
Frame index remains derived/non-normative, and the fix should instead tighten container timestamp guarantees.

**C — Explicit dual identity.**
Persist both logical frame offset and timestamp/PTS in a future format version.

A design-direction answer is enough. Implementation should follow that answer; the RFC should not force a schema migration if maintainers prefer A.

## Claim boundary

This is a design proposal built from current source semantics. It is not SemRepair adoption and does not claim discovery of the existing LeRobot relative-action bug or other community work.
