import os

import click

from video_splitter.main import process_video


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
    "--picture-black-ratio-th",
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
def main(
    video_path: str,
    black_min_duration: float,
    picture_black_ratio_th: float,
    pixel_black_th: float,
) -> None:
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"文件不存在：{video_path}")

    process_video(
        video_path=video_path,
        black_min_duration=black_min_duration,
        pic_black_ratio_th=picture_black_ratio_th,
        pixel_black_th=pixel_black_th,
    )

if __name__ == "__main__":
    main()
