from setuptools import setup, find_packages

setup(
    name="video_splitter",
    version="1.0.0",
    description="视频黑屏检测和切分工具",
    author="a1oyss",
    packages=find_packages(),
    install_requires=[
        "opencv-python-headless",
        "numpy",
    ],
    entry_points={"console_scripts": ["video_splitter=video_splitter.cli:main"]},
)
