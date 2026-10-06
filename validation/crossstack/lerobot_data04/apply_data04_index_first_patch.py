#!/usr/bin/env python3
"""Apply the minimal LeRobot DATA-04 index-first TorchCodec prototype.

Pinned source: huggingface/lerobot@d40e8709cffb93644db66e30604ef50fdec003cb

The script is deliberately anchor-checked and fails closed if upstream source
has drifted. It modifies only:

- src/lerobot/datasets/video_utils.py
- src/lerobot/datasets/dataset_reader.py

It does not change dataset v3 schema or writer output.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


PINNED = "d40e8709cffb93644db66e30604ef50fdec003cb"


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    if text.count(old) != 1:
        raise RuntimeError(
            f"{label}: expected exactly one source anchor, found {text.count(old)}"
        )
    return text.replace(old, new, 1)


def git_head(root: Path) -> str:
    return subprocess.check_output(
        ["git", "-C", str(root), "rev-parse", "HEAD"],
        text=True,
    ).strip()


def patch_video_utils(root: Path) -> None:
    path = root / "src/lerobot/datasets/video_utils.py"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """def decode_video_frames(
    video_path: Path | str,
    timestamps: list[float],
    tolerance_s: float,
    backend: str | None = None,
    return_uint8: bool = False,
    is_depth: bool = False,
) -> torch.Tensor:""",
        """def decode_video_frames(
    video_path: Path | str,
    timestamps: list[float],
    tolerance_s: float,
    backend: str | None = None,
    return_uint8: bool = False,
    is_depth: bool = False,
    *,
    frame_indices: list[int] | None = None,
) -> torch.Tensor:""",
        label="decode_video_frames signature",
    )

    text = replace_once(
        text,
        """        is_depth (bool): Set to True if the video is a depth map (1 channel, uint12).
""",
        """        is_depth (bool): Set to True if the video is a depth map (1 channel, uint12).
        frame_indices: Optional canonical logical frame indices for an index-capable
            backend. Timestamps remain the synchronization/PTS validation target.
            The PyAV path currently ignores this hint and keeps timestamp addressing.
""",
        label="decode_video_frames docs",
    )

    text = replace_once(
        text,
        """    if backend == "torchcodec":
        return decode_video_frames_torchcodec(video_path, timestamps, tolerance_s, return_uint8=return_uint8)
""",
        """    if backend == "torchcodec":
        return decode_video_frames_torchcodec(
            video_path,
            timestamps,
            tolerance_s,
            return_uint8=return_uint8,
            frame_indices=frame_indices,
        )
""",
        label="torchcodec dispatch",
    )

    text = replace_once(
        text,
        """def decode_video_frames_torchcodec(
    video_path: Path | str,
    timestamps: list[float],
    tolerance_s: float,
    log_loaded_timestamps: bool = False,
    decoder_cache: VideoDecoderCache | None = None,
    return_uint8: bool = False,
) -> torch.Tensor:""",
        """def decode_video_frames_torchcodec(
    video_path: Path | str,
    timestamps: list[float],
    tolerance_s: float,
    log_loaded_timestamps: bool = False,
    decoder_cache: VideoDecoderCache | None = None,
    return_uint8: bool = False,
    *,
    frame_indices: list[int] | None = None,
) -> torch.Tensor:""",
        label="torchcodec signature",
    )

    text = replace_once(
        text,
        """    # get metadata for frame information
    metadata = decoder.metadata
    average_fps = metadata.average_fps
    # convert timestamps to frame indices
    frame_indices = [round(ts * average_fps) for ts in timestamps]
    # retrieve frames based on indices
    frames_batch = decoder.get_frames_at(indices=frame_indices)
""",
        """    # The dataset may already know the logical frame identity. In that
    # case do not re-quantize it through timestamp * decoder.average_fps.
    if frame_indices is None:
        metadata = decoder.metadata
        average_fps = metadata.average_fps
        requested_indices = [round(ts * average_fps) for ts in timestamps]
        index_addressed = False
    else:
        if len(frame_indices) != len(timestamps):
            raise ValueError(
                "frame_indices and timestamps must have the same length"
            )
        if any(
            isinstance(index, bool) or not isinstance(index, int) or index < 0
            for index in frame_indices
        ):
            raise ValueError("frame_indices must contain non-negative integers")
        requested_indices = frame_indices
        index_addressed = True

    frames_batch = decoder.get_frames_at(indices=requested_indices)
""",
        label="index selection",
    )

    text = replace_once(
        text,
        """    # compute distances between each query timestamp and loaded timestamps
    dist = torch.cdist(query_ts[:, None], loaded_ts[:, None], p=1)
    min_, argmin_ = dist.min(1)

    is_within_tol = min_ <= tolerance_s
    if not is_within_tol.all():
        raise FrameTimestampError(
            f"One or several query timestamps unexpectedly violate the tolerance ({min_[~is_within_tol]} >= {tolerance_s=})."
            " It means that the closest frame that can be loaded from the video is too far away in time."
            " This might be due to synchronization issues with timestamps during data collection."
            " To be safe, we advise to ignore this item during training."
            f"\nqueried timestamps: {query_ts}"
            f"\nloaded timestamps: {loaded_ts}"
            f"\nvideo: {video_path}"
        )

    # get closest frames to the query timestamps
    closest_frames = torch.stack([loaded_frames[idx] for idx in argmin_])
    closest_ts = loaded_ts[argmin_]
""",
        """    if index_addressed:
        # get_frames_at preserves requested index order. Timestamp is now a
        # validation signal rather than the source of frame identity.
        if len(query_ts) != len(loaded_ts):
            raise FrameTimestampError(
                "Index-addressed decode returned a different number of frames "
                f"({len(loaded_ts)}) than requested ({len(query_ts)})."
            )
        error = torch.abs(query_ts - loaded_ts)
        is_within_tol = error <= tolerance_s
        if not is_within_tol.all():
            raise FrameTimestampError(
                "Index-addressed frame identity disagrees with the dataset "
                f"timestamp beyond tolerance ({error[~is_within_tol]} >= {tolerance_s=})."
                f"\nqueried timestamps: {query_ts}"
                f"\nloaded timestamps: {loaded_ts}"
                f"\nvideo: {video_path}"
                f"\nframe_indices: {requested_indices}"
            )
        closest_frames = torch.stack(loaded_frames)
        closest_ts = loaded_ts
    else:
        # Legacy timestamp-addressed path.
        dist = torch.cdist(query_ts[:, None], loaded_ts[:, None], p=1)
        min_, argmin_ = dist.min(1)

        is_within_tol = min_ <= tolerance_s
        if not is_within_tol.all():
            raise FrameTimestampError(
                f"One or several query timestamps unexpectedly violate the tolerance ({min_[~is_within_tol]} >= {tolerance_s=})."
                " It means that the closest frame that can be loaded from the video is too far away in time."
                " This might be due to synchronization issues with timestamps during data collection."
                " To be safe, we advise to ignore this item during training."
                f"\nqueried timestamps: {query_ts}"
                f"\nloaded timestamps: {loaded_ts}"
                f"\nvideo: {video_path}"
            )

        closest_frames = torch.stack([loaded_frames[idx] for idx in argmin_])
        closest_ts = loaded_ts[argmin_]
""",
        label="timestamp validation",
    )

    path.write_text(text, encoding="utf-8")


def patch_dataset_reader(root: Path) -> None:
    path = root / "src/lerobot/datasets/dataset_reader.py"
    text = path.read_text(encoding="utf-8")

    text = replace_once(
        text,
        """        self._column_views_transform: Callable | None = None

        # Setup delta_indices""",
        """        self._column_views_transform: Callable | None = None
        self._video_file_frame_offsets: dict[tuple[int, str], int] | None = None

        # Setup delta_indices""",
        label="reader cache init",
    )

    insert_before = """    def _query_videos(self, query_timestamps: dict[str, list[float]], ep_idx: int) -> dict[str, torch.Tensor]:
"""
    helper = """    def _build_video_file_frame_offsets(self) -> dict[tuple[int, str], int]:
        \"\"\"Derive file-local logical frame offsets from existing v3 metadata.

        No new persisted metadata is required: episodes already store length and
        the physical video (chunk_index, file_index) for every camera key.
        \"\"\"
        if self._meta.episodes is None:
            self._meta.ensure_readable()
        cursors: dict[tuple[str, int, int], int] = {}
        offsets: dict[tuple[int, str], int] = {}
        for episode_index in range(self._meta.total_episodes):
            ep = self._meta.episodes[episode_index]
            length = int(ep["length"])
            for vid_key in self._meta.video_keys:
                file_key = (
                    vid_key,
                    int(ep[f"videos/{vid_key}/chunk_index"]),
                    int(ep[f"videos/{vid_key}/file_index"]),
                )
                offsets[(episode_index, vid_key)] = cursors.get(file_key, 0)
                cursors[file_key] = offsets[(episode_index, vid_key)] + length
        return offsets

    def _get_query_video_frame_indices(
        self,
        *,
        abs_idx: int,
        ep_idx: int,
        query_indices: dict[str, list[int]] | None,
    ) -> dict[str, list[int]]:
        if self._video_file_frame_offsets is None:
            self._video_file_frame_offsets = self._build_video_file_frame_offsets()

        ep = self._meta.episodes[ep_idx]
        ep_start = int(ep["dataset_from_index"])
        result: dict[str, list[int]] = {}
        for vid_key in self._meta.video_keys:
            absolute = (
                query_indices[vid_key]
                if query_indices is not None and vid_key in query_indices
                else [abs_idx]
            )
            file_start = self._video_file_frame_offsets[(ep_idx, vid_key)]
            result[vid_key] = [
                file_start + int(index) - ep_start for index in absolute
            ]
        return result

"""
    if helper.strip() not in text:
        text = replace_once(
            text,
            insert_before,
            helper + insert_before,
            label="video frame-index helper insertion",
        )

    text = replace_once(
        text,
        """    def _query_videos(self, query_timestamps: dict[str, list[float]], ep_idx: int) -> dict[str, torch.Tensor]:
""",
        """    def _query_videos(
        self,
        query_timestamps: dict[str, list[float]],
        ep_idx: int,
        query_frame_indices: dict[str, list[int]] | None = None,
    ) -> dict[str, torch.Tensor]:
""",
        label="query videos signature",
    )

    text = replace_once(
        text,
        """            frames = decode_video_frames(
                video_path,
                shifted_query_ts,
                self._tolerance_s,
                self._video_backend,
                return_uint8=self._return_uint8,
                is_depth=vid_key in self._meta.depth_keys,
            )
""",
        """            frames = decode_video_frames(
                video_path,
                shifted_query_ts,
                self._tolerance_s,
                self._video_backend,
                return_uint8=self._return_uint8,
                is_depth=vid_key in self._meta.depth_keys,
                frame_indices=(
                    None
                    if query_frame_indices is None
                    else query_frame_indices[vid_key]
                ),
            )
""",
        label="decoder call",
    )

    text = replace_once(
        text,
        """            query_timestamps = self._get_query_timestamps(current_ts, query_indices)
            video_frames = self._query_videos(query_timestamps, ep_idx)
""",
        """            query_timestamps = self._get_query_timestamps(current_ts, query_indices)
            query_frame_indices = self._get_query_video_frame_indices(
                abs_idx=abs_idx,
                ep_idx=ep_idx,
                query_indices=query_indices,
            )
            video_frames = self._query_videos(
                query_timestamps,
                ep_idx,
                query_frame_indices,
            )
""",
        label="get_item frame indices",
    )

    path.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("lerobot_root", type=Path)
    parser.add_argument("--allow-source-drift", action="store_true")
    args = parser.parse_args()

    root = args.lerobot_root.resolve()
    head = git_head(root)
    if not args.allow_source_drift and head != PINNED:
        raise SystemExit(
            f"LeRobot source drifted: HEAD={head}, expected {PINNED}. "
            "Re-audit anchors before applying."
        )

    patch_video_utils(root)
    patch_dataset_reader(root)
    print("Applied DATA-04 minimal index-first TorchCodec prototype")
    print("Base:", head)


if __name__ == "__main__":
    main()
