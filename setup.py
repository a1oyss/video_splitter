from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as f:
    required_packages = f.read().splitlines()

setup(
    name="video_splitter",
    version="1.0.0",
    description="视频黑屏检测和切分工具",
    author="a1oyss",
    packages=find_packages(),
    install_requires=required_packages,
)
