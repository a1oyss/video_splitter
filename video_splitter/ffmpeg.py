import json
import os
import re
import subprocess
import tempfile
from time import sleep
from typing import List


def run_ffmpeg_commands(commands: List[str]) -> str:
    try:
        output = subprocess.check_output(commands, stderr=subprocess.STDOUT, encoding="utf8")
        return output
    except subprocess.CalledProcessError as e:
        # 捕获异常并记录错误输出
        error_output = e.output
        print(f"FFmpeg command failed with error: {error_output}")
        raise e


def get_video_metadata(file_path):
    """Get video metadata including codec, duration, and size."""
    codec = run_ffmpeg_commands([
        "ffprobe",
        "-hide_banner",
        "-loglevel",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "stream=codec_name",
        "-of",
        "default=nk=1:nw=1",
        file_path
    ]).strip()
    duration = float(run_ffmpeg_commands([
        "ffprobe",
        "-hide_banner",
        "-loglevel",
        "error",
        "-select_streams",
        "v:0",
        "-show_entries",
        "format=duration",
        "-of",
        "default=nk=1:nw=1",
        file_path
    ]))
    output = run_ffmpeg_commands([
        "ffmpeg",
        "-hide_banner",
        "-i",
        file_path,
        "-f",
        "null",
        "-c",
        "copy",
        "-map",
        "0:v:0",
        "-"
    ])
    size = re.findall(r"video:(\d+)KiB", output)[0]
    bitrate = (float(size) / duration) * 8.192  # Calculate bitrate in kbps
    return codec, duration, bitrate


def get_interval_around_time(time: float, window: float) -> tuple[float, float]:
    return max(time - window / 2, 0), time + window / 2


def find_key_frames(video_path: str, black_point: float, window: float = 10.0) -> List[float]:
    """ find key frames in the video """
    start_interval, end_interval = get_interval_around_time(black_point, window)
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-read_intervals",
        f"{start_interval:.3f}%{end_interval:.3f}",
        "-show_packets",
        "-select_streams",
        "v:0",
        "-show_entries",
        "packet=pts_time,flags",
        "-of",
        "csv",
        video_path,
    ]
    output = subprocess.check_output(
        cmd, text=True, stderr=subprocess.STDOUT, encoding="utf8"
    )

    # 解析 ffprobe 输出
    keyframes = [
        float(line.split(",")[1]) for line in output.splitlines() if "K" in line
    ]

    if not keyframes:
        raise ValueError("No keyframes found in the video.")

    # 返回与目标黑屏点最近的关键帧时间点
    return keyframes


def detect_black_scene(video_path: str, black_min_duration: float = 1.0, picture_black_ratio_th: float = 0.98,
                       pixel_black_th: float = 0.1) -> List[float]:
    """ detect black scene in the video """
    cmd = [
        "ffmpeg",
        '-hide_banner',
        "-i",
        video_path,
        "-vf",
        f"blackdetect=d={black_min_duration}:pic_th={picture_black_ratio_th}:pix_th={pixel_black_th}",
        "-an",
        "-f",
        "null",
        "-",
    ]
    output = run_ffmpeg_commands(cmd)
    black_segments = re.findall(r"black_start:(\d+\.\d+)\s+black_end:(\d+\.\d+)\s+black_duration:(\d+\.\d+)",
                                output)
    return (
        [] if not black_segments else [(float(start) + float(end)) / 2 for start, end, _ in black_segments]
    )


def detect_scene_change(video_path: str, min_change: float = 0.3) -> List[float]:
    """ detect scene change in the video """
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"select='gt(scene,{min_change})',showinfo",
        "-f",
        "null",
        "-",
    ]
    output = subprocess.check_output(
        cmd, text=True, stderr=subprocess.STDOUT, encoding="utf8"
    )
    scene_times = re.findall(r"pts_time:(\d+\.\d+)", output)
    return [] if not scene_times else [float(time) for time in scene_times]


def smart_cut_video(video_path: str, start: float, end: float, output_path: str) -> None:
    """ Smart cut video based on the start and end time. """
    codec, _, bitrate = get_video_metadata(video_path)
    keyframes = find_key_frames(video_path, start)

    if start in keyframes:
        print(f"{start} is a keyframe, performing a keyframe cut.")
        commands = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-ss",
            str(start),
            "-i",
            video_path,
            "-ss",
            "0",
            "-t",
            str(end - start),
            "-c:v",
            "copy",
            "-map",
            "0:0",
            "-map",
            "0:1",
            "-map_metadata",
            "0",
            "-movflags",
            "use_metadata_tags",
            "-ignore_unknown",
            "-f",
            "mp4",
            "-y",
            output_path,
        ]
        run_ffmpeg_commands(commands)
        return

    print(f"{start} is not a keyframe, re-encoding video.")
    temp_dir = tempfile.TemporaryDirectory()
    print(f"temp dir: {temp_dir.name}")

    # Find the previous keyframe before the start
    keyframes.append(end)

    # Find the next keyframe after the start
    next_keyframe = min(kf for kf in keyframes if kf > start)
    end_pos = next_keyframe - 0.000001

    # Re-encode from start to the frame before the next keyframe
    print(f"Re-encoding from {start} to {end_pos}.")
    output0_path = os.path.join(temp_dir.name, "output0.mp4")
    run_ffmpeg_commands([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        video_path,
        "-ss",
        str(start),
        "-to",
        str(end_pos),
        "-c:a",
        "copy",
        "-map",
        "0:0",
        "-map",
        "0:1",
        "-map_metadata",
        "0",
        "-movflags",
        "use_metadata_tags",
        "-ignore_unknown",
        "-c:v",
        codec,
        "-b:v",
        str(bitrate) + "k",
        "-f",
        "mp4",
        "-y",
        output0_path
    ])

    # Copy from the next keyframe to the end
    print(f"Extracting video from {next_keyframe} to {end}.")
    output1_path = os.path.join(temp_dir.name, "output1.mp4")
    run_ffmpeg_commands([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        str(next_keyframe),
        "-i",
        video_path,
        "-to",
        str(end),
        "-c:v",
        "copy",
        "-map",
        "0:0",
        "-map",
        "0:1",
        "-map_metadata",
        "0",
        "-movflags",
        "use_metadata_tags",
        "-ignore_unknown",
        "-f",
        "mp4",
        "-y",
        output1_path
    ])

    # Concatenate the two parts
    print("Merging files...")
    filelist_path = os.path.join(temp_dir.name, "filelist.txt")
    with open(filelist_path, "w") as f:
        f.write(f"file '{output0_path}'\nfile '{output1_path}'\n")
    run_ffmpeg_commands([
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        filelist_path,
        "-c",
        "copy",
        output_path,
    ])
    temp_dir.cleanup()
    print("Done.")
