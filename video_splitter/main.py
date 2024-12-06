import os

from video_splitter.ffmpeg import detect_black_scene, get_video_metadata, smart_cut_video


def process_video(video_path: str, black_min_duration: float = 1.0,
                                       pic_black_ratio_th: float = 0.98, pixel_black_th: float = 0.1) -> None:
    """
    Split a video into two parts at the black screen nearest to the middle using smart cutting.
    """
    # Detect black screens
    black_start_times = detect_black_scene(
        video_path,
        black_min_duration=black_min_duration,
        picture_black_ratio_th=pic_black_ratio_th,
        pixel_black_th=pixel_black_th
    )

    if not black_start_times:
        print("No black scenes detected in the video.")
        return

    # Get video duration
    _, duration, _ = get_video_metadata(video_path)
    middle_time = duration / 2

    # Find the black screen nearest to the middle
    nearest_black_time = min(black_start_times, key=lambda t: abs(t - middle_time))
    print(f"Nearest black screen found at: {nearest_black_time:.5f}s")

    # Define output file names
    base_name, ext = os.path.splitext(video_path)
    output_part1 = f"{base_name}.part1{ext}"
    output_part2 = f"{base_name}.part2{ext}"

    # Use smart cutting for both parts
    print(f"Smart cutting the video at {nearest_black_time:.5f}s...")

    # Part 1: From start to the nearest black time
    print(f"Creating {output_part1}...")
    smart_cut_video(video_path, 0, nearest_black_time, output_part1)

    # Part 2: From the nearest black time to the end
    print(f"Creating {output_part2}...")
    smart_cut_video(video_path, nearest_black_time, duration, output_part2)

    print(f"Video successfully split into:\n{output_part1}\n{output_part2}")

#
# def process_video(
#         video_path: str,
#         black_min_duration: float = 1.0,
#         picture_black_ratio_th: float = 0.98,
#         pixel_black_th: float = 0.1,
# ) -> None:
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(levelname)s - %(message)s",
#     )
#
#     base_name, ext = os.path.splitext(video_path)
#     output_part1 = f"{base_name}.part1{ext}"
#     output_part2 = f"{base_name}.part2{ext}"
#
#     # 检测黑屏
#     logging.info("检测黑屏中...")
#     split_frames = detect_black_frames(
#         video_path, black_min_duration, picture_black_ratio_th, pixel_black_th
#     )
#     if not split_frames:
#         logging.info("未检测到黑屏，尝试检测转场。")
#         split_frames = detect_scene_frames(video_path=video_path)
#         if not split_frames:
#             logging.info("未检测到可用时间点，无法切分视频。")
#             return
#
#     total_duration = get_video_duration(video_path)
#     closest_split = find_closest_to_middle(split_frames, total_duration)
#     logging.info(f"找到距离中间最近的时间点: {closest_split:.3f} 秒")
#
#     # 对齐关键帧
#     keyframe = find_key_frames(video_path, closest_split)
#
#     # 切分视频
#     logging.info("开始切分视频...")
#     split_video_fast(video_path, keyframe, output_part1, output_part2)
#     logging.info("视频切分完成。")


# def find_closest_to_middle(times: List[float], duration: float) -> float:
#     """在所有时间点中，找到距离视频中间最近的点"""
#     middle = duration / 2
#     closest_time = min(times, key=lambda t: abs(t - middle))
#     return closest_time
