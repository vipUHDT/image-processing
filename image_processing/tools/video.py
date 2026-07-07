"""Frame extraction utilities for single videos and synchronized video pairs."""

import math
from pathlib import Path
from typing import Optional, Tuple

import cv2
from tqdm import tqdm


def extractFrames(
    video_path: Path | str,
    output_dir: Path | str = "frames",
    offset: int = 0
):
    """
    Extract every frame of a video to PNG files.

    Frames are written to ``output_dir`` as ``frame_<index>.png``, starting
    ``offset`` seconds into the video.

    Parameters
    ----------
    video_path : Path or str
        Path to the input video.
    output_dir : Path or str, optional
        Directory for the extracted frames; created if missing.
    offset : int, optional
        Number of seconds to skip at the start of the video.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError("Could not open video.")

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        raise RuntimeError("Could not determine video FPS.")

    print(f"Video FPS: {fps:.2f}")

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    start_frame = int(offset * fps)

    if start_frame >= total_frames:
        raise ValueError("Offset exceeds video duration.")

    frames_to_process = total_frames - start_frame

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    frame_idx = start_frame
    saved = 0

    with tqdm(
        total=frames_to_process,
        unit="frame",
        desc="Extracting frames"
    ) as pbar:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            filename = output_dir / f"frame_{frame_idx:06d}.png"
            cv2.imwrite(str(filename), frame)

            frame_idx += 1
            saved += 1
            pbar.update(1)

    cap.release()
    print(f"Saved {saved} frames to {output_dir}")

def extractSynchronizedFrames(
    video0: str | Path,
    video1: str | Path,
    out_dir0: str | Path,
    out_dir1: str | Path,
    offset0: float = 0.0,
    offset1: float = 0.0,
    target_fps: float | None = None,
    t_start: float | None = None,
    t_end: float | None = None,
    time_tolerance: float = 1 / 60.0,
) -> None:
    """
    Extract time-aligned frame pairs from two videos with different frame rates.

    A shared timeline is sampled at ``target_fps`` over the overlapping window
    of both videos; at each step, the closest frame from each video is saved
    (``cam0_<index>.png`` / ``cam1_<index>.png``) if both fall within
    ``time_tolerance`` of the target timestamp.

    Parameters
    ----------
    video0, video1 : str or Path
        Paths to the two input videos.
    out_dir0, out_dir1 : str or Path
        Output directories for the paired frames; created if missing.
    offset0, offset1 : float, optional
        Time in seconds at which each video's first frame occurs on the
        shared timeline (compensates for recording start offsets).
    target_fps : float, optional
        Sampling rate of the shared timeline. Defaults to the lower of the
        two videos' frame rates.
    t_start, t_end : float, optional
        Bounds of the extraction window on the shared timeline. Default to
        the overlapping portion of both videos.
    time_tolerance : float, optional
        Maximum frame-to-target time difference in seconds for a pair to be
        saved (default 1/60 s).
    """
    video0 = str(video0)
    video1 = str(video1)

    out_dir0 = Path(out_dir0)
    out_dir1 = Path(out_dir1)
    out_dir0.mkdir(parents=True, exist_ok=True)
    out_dir1.mkdir(parents=True, exist_ok=True)

    cap0 = cv2.VideoCapture(video0)
    cap1 = cv2.VideoCapture(video1)

    if not cap0.isOpened():
        raise RuntimeError(f"Could not open video0: {video0}")
    if not cap1.isOpened():
        raise RuntimeError(f"Could not open video1: {video1}")

    fps0 = cap0.get(cv2.CAP_PROP_FPS)
    fps1 = cap1.get(cv2.CAP_PROP_FPS)

    if fps0 <= 0 or fps1 <= 0:
        raise RuntimeError(f"Could not determine FPS values: fps0={fps0}, fps1={fps1}")

    dur0 = cap0.get(cv2.CAP_PROP_FRAME_COUNT) / max(fps0, 1e-6)
    dur1 = cap1.get(cv2.CAP_PROP_FRAME_COUNT) / max(fps1, 1e-6)

    if target_fps is None:
        target_fps = min(fps0, fps1)

    if target_fps <= 0:
        raise ValueError("target_fps must be > 0")

    if t_start is None:
        t_start = max(offset0, offset1)

    if t_end is None:
        t_end = min(offset0 + dur0, offset1 + dur1)

    if t_end <= t_start:
        raise ValueError("No overlapping time window between both videos.")

    print(f"video0 fps={fps0:.3f}, duration={dur0:.2f}s")
    print(f"video1 fps={fps1:.3f}, duration={dur1:.2f}s")
    print(f"Using target_fps={target_fps:.3f}")
    print(f"Global window: [{t_start:.3f}, {t_end:.3f}] seconds")

    total_steps = int((t_end - t_start) * target_fps)

    ret0, frame0, t0_local = _readNext(cap0)
    ret1, frame1, t1_local = _readNext(cap1)

    dt = 1.0 / target_fps
    saved_pairs = 0

    with tqdm(
        total=total_steps,
        unit="pair",
        desc="Synchronizing EO/IR",
        dynamic_ncols=True
    ) as pbar:
        for n in range(total_steps):
            t_global = t_start + n * dt

            t0_target = t_global - offset0
            t1_target = t_global - offset1

            while ret0 and t0_local < t0_target:
                ret0, frame0, t0_local = _readNext(cap0)

            while ret1 and t1_local < t1_target:
                ret1, frame1, t1_local = _readNext(cap1)

            if not ret0 or not ret1:
                break

            if (
                abs(t0_local - t0_target) <= time_tolerance
                and abs(t1_local - t1_target) <= time_tolerance
            ):
                idx_str = f"{saved_pairs:06d}"

                cv2.imwrite(
                    str(out_dir0 / f"cam0_{idx_str}.png"),
                    frame0,
                )
                cv2.imwrite(
                    str(out_dir1 / f"cam1_{idx_str}.png"),
                    frame1,
                )
                saved_pairs += 1

            pbar.update(1)

    cap0.release()
    cap1.release()

    print(f"\nSaved {saved_pairs} synchronized frame pairs:")
    print(f"  - {out_dir0}")
    print(f"  - {out_dir1}")

def _readNext(cap: cv2.VideoCapture) -> Tuple[bool, Optional[cv2.Mat], float]:
    """Read the next frame and its timestamp in seconds; ``(False, None, inf)`` at EOF."""
    ret, frame = cap.read()
    if not ret:
        return False, None, math.inf
    t_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
    return True, frame, t_ms / 1000.0
