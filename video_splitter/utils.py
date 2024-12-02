import re
import subprocess
from typing import List, Optional

from moviepy.video.io.VideoFileClip import VideoFileClip


def get_video_duration(video_path: str) -> Optional[float]:
    """获取视频时长"""
    cmd = [
        "ffprobe",
        "-v",
        "error",
        "-show_entries",
        "format=duration",
        "-of",
        "default=noprint_wrappers=1:nokey=1",
        video_path,
    ]
    duration = float(subprocess.check_output(cmd, text=True).strip())
    return duration


def detect_black_frames(
    video_path: str,
    black_min_duration: float = 1.0,
    picture_black_ratio_th: float = 0.98,
    pixel_black_th: float = 0.1,
) -> List[float]:
    """检测指定时间范围内的黑屏时间点，并返回黑屏时间点列表"""
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"blackdetect=d={black_min_duration}:pic_th={picture_black_ratio_th}:pix_th={pixel_black_th}",
        "-an",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    output = result.stderr
    black_segments = re.findall(
        r"black_start:(\d+\.\d+)\s+black_end:(\d+\.\d+)\s+black_duration:(\d+\.\d+)",
        output,
    )
    # black_frames = re.findall(r"black_start:(\d+\.\d+)\s+", output, re.MULTILINE)
    # return [] if not black_frames else [float(time) for time in black_frames]
    return (
        []
        if not black_segments
        else [(float(start) + float(end)) / 2 for start, end, _ in black_segments]
    )


def detect_scene_frames(video_path: str) -> List[float]:
    """检测视频中的转场时间点"""
    cmd = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        "select='gt(scene,0.3)',showinfo",
        "-f",
        "null",
        "-",
    ]
    result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    output = result.stderr
    scene_times = re.findall(r"pts_time:(\d+\.\d+)", output)
    return [float(time) for time in scene_times]


def split_video_fast(
    video_path: str, split_time: float, output_path1: str, output_path2: str
) -> None:
    """快速切分视频，通过关键帧对齐避免重新编码"""
    # 分割前半部分
    cmd1 = [
        "ffmpeg",
        "-ss",
        "0",  # 从头开始
        "-i",
        video_path,
        "-to",
        f"{split_time:.2f}",
        "-c",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        output_path1,
    ]
    subprocess.run(cmd1, stderr=subprocess.DEVNULL, check=True)

    # 分割后半部分
    cmd2 = [
        "ffmpeg",
        "-ss",
        f"{split_time:.2f}",
        "-i",
        video_path,
        "-c",
        "copy",
        "-avoid_negative_ts",
        "make_zero",
        output_path2,
    ]
    subprocess.run(cmd2, stderr=subprocess.DEVNULL, check=True)
