import os

import click

from video_splitter.ffmpeg import detect_black_scene, get_video_metadata, smart_cut_video


@click.command()
@click.option(
    "--video-path",
    "-v",
    required=True,
    type=click.Path(exists=True, dir_okay=False),
    help="视频文件路径",
)
@click.option(
    "--black-min-duration",
    "-d",
    default=1.0,
    type=float,
    help="黑屏最短持续时间(秒)",
)
@click.option(
    "--pic_black_ratio_th",
    "--pic-th",
    default=0.98,
    type=float,
    help="图像黑屏比例阈值",
)
@click.option(
    "--pixel-black-th",
    "--pix-th",
    default=0.1,
    type=float,
    help="像素黑屏阈值",
)
def main(video_path: str, black_min_duration: float = 1.0,
         pic_black_ratio_th: float = 0.98, pixel_black_th: float = 0.1) -> None:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"文件不存在：{video_path}")

    codec, duration, bitrate = get_video_metadata(video_path)
    click.echo(f"Video information: codec={codec}, duration={duration:.5f}s, bitrate={bitrate}kbps")

    # Detect black screens
    black_start_times = detect_black_scene(
        video_path,
        black_min_duration=black_min_duration,
        picture_black_ratio_th=pic_black_ratio_th,
        pixel_black_th=pixel_black_th
    )

    if not black_start_times:
        click.echo("No black scenes detected in the video.")
        return

    if len(black_start_times) == 1:
        # Only one black screen, use it as the middle time
        nearest_black_time = black_start_times[0]
        click.echo(f"Only one black screen detected, using it as the middle time: {nearest_black_time:.5f}s")
    else:
        # Multiple black screens, prompt the user to select one
        click.echo("Multiple black scenes detected, please select one:")
        for i, start_time in enumerate(black_start_times):
            click.echo(f"{i+1}. {start_time:.5f}s")
        choice = click.prompt("Enter the number of the black screen you want to use", type=int)
        nearest_black_time = black_start_times[choice - 1]

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


if __name__ == "__main__":
    main()
