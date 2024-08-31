import random
import subprocess
from librosa import get_duration
from random import choice
from os import listdir, remove
from moviepy.editor import VideoFileClip, AudioFileClip


class Footage_Handler:
    @staticmethod
    def download_video_part(start_time, video_url, duration, output_title):  # RESULTS IN ERROR BUT IM NOT DELETING THIS
        # IN THE ERROR MESSAGE YOU CAN FIND A LINK TO A WAY FASTER UPLOADING SERVER (google?)
        command_ytdl = ['yt-dlp', '-g', video_url]
        video_direct_link = subprocess.check_output(command_ytdl).decode('utf-8').strip()

        command = [
            'ffmpeg',
            '-ss', str(start_time),
            '-i', video_direct_link,
            '-t', str(duration),
            '-c:v', 'copy',
            '-c:a', 'copy',
            output_title
        ]

        # Run the command
        subprocess.run(command)

    @staticmethod
    def select_rand_footage(title: str, tts_path: str):
        not_videos = ['__pycache__', 'desktop.ini']
        background_footage = f"footage\\{choice([file for file in listdir('footage') if file not in not_videos])}"
        background_footage = VideoFileClip(background_footage)

        speech_duration = get_duration(filename=tts_path)
        audio_clip = AudioFileClip(filename=tts_path)

        new_start = random.randrange(0, round(background_footage.duration - speech_duration))
        video_clip = background_footage.subclip(new_start, new_start + speech_duration)
        video_clip.audio = audio_clip
        video_clip.write_videofile(f"output\\building_{title}.mp4")

        remove(tts_path)
