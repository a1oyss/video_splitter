import unittest

from video_splitter.main import process_video


class MainTest(unittest.TestCase):
    def test_main(self):
        process_video(r"D:\Downloads\2023年6月\6月1日 6月1本目の動画です🍰💕.mp4", black_min_duration=0.1,
                      pic_black_ratio_th=0.98, pixel_black_th=0.1)
