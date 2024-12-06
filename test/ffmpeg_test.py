import unittest

from video_splitter.ffmpeg import run_ffmpeg_commands, detect_black_scene, get_video_metadata


class FFmpegTest(unittest.TestCase):
    def test_run_command(self):
        video_path = "D:\\Downloads\\2023年6月\\6月1日 6月1本目の動画です🍰💕.mp4"
        cmd = [
            "ffprobe", "-of", "json", "-show_chapters", "-show_format", "-show_entries", "stream", "-i", video_path,
            '-hide_banner'
        ]
        output = run_ffmpeg_commands(cmd)
        print(output)

    def test_detect_black_scene(self):
        video_path = "D:\\Downloads\\2023年6月\\6月1日 6月1本目の動画です🍰💕.mp4"
        black_frames = detect_black_scene(video_path, 0.1, 0.98, 0.1)
        print(black_frames)

    def test_get_video_metadata(self):
        video_path = "D:\\Downloads\\2023年6月\\6月1日 6月1本目の動画です🍰💕.mp4"
        print(get_video_metadata(video_path))


if __name__ == "__main__":
    unittest.main()
