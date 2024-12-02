import os
from typing import List

from .utils import (
    detect_black_frames,
    detect_scene_frames,
    get_video_duration,
    split_video_fast,
)
import logging


def process_video(
    video_path: str,
    black_min_duration: float = 1.0,
    picture_black_ratio_th: float = 0.98,
    pixel_black_th: float = 0.1,
) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

    base_name, ext = os.path.splitext(video_path)
    # 输出文件名生成
    output_part1 = f"{base_name}.part1{ext}"
    output_part2 = f"{base_name}.part2{ext}"
    # 检测黑屏
    logging.info("检测黑屏中...")
    split_frames = detect_black_frames(
        video_path, black_min_duration, picture_black_ratio_th, pixel_black_th
    )
    if not split_frames:
        logging.info("未检测到黑屏，尝试检测转场。")
        split_frames = detect_scene_frames(video_path=video_path)
        if not split_frames:
            logging.info("未检测到黑屏，无法切分视频。")
            return
    total_duration = get_video_duration(video_path)
    closest_split = find_closest_to_middle(split_frames, total_duration)
    logging.info(f"找到距离中间最近的时间点: {closest_split:.2f} 秒")

    # 切分视频
    logging.info("开始切分视频...")
    split_video_fast(video_path, closest_split, output_part1, output_part2)
    logging.info("视频切分完成。")


def find_closest_to_middle(times: List[float], duration: float) -> float:
    """在所有时间点中，找到距离视频中间最近的点"""
    middle = duration / 2
    closest_time = min(times, key=lambda t: abs(t - middle))
    return closest_time
