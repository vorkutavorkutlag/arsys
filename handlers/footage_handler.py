import random
from librosa import get_duration
from os import listdir
from moviepy.editor import VideoFileClip, AudioFileClip
from faster_whisper import WhisperModel


class Footage_Handler:
    @staticmethod
    def select_rand_footage(title: str, tts_path: str):
        not_videos = ['__pycache__', 'desktop.ini']
        background_footage = f"footage\\" \
                             f"{random.choice([file for file in listdir('footage') if file not in not_videos])}"
        background_footage = VideoFileClip(background_footage)

        speech_duration = get_duration(filename=tts_path)
        audio_clip = AudioFileClip(filename=tts_path)

        new_start = random.randrange(0, round(background_footage.duration - speech_duration))
        video_clip = background_footage.subclip(new_start, new_start + speech_duration)
        video_clip.audio = audio_clip
        video_clip.write_videofile(f"output\\building_{title}.mp4")

    @staticmethod
    def generate_subtitles(tts_path: str, cuda=True):
        model_size = "large"
        model = WhisperModel("model_size", device="cuda") if cuda else WhisperModel("model_size")

        wordlevel_info = []
        segments, info = model.transcribe(tts_path, word_timestamps=True)
        segments = list(segments)  # The transcription will actually run here.
        for segment in segments:
            for word in segment.words:
                wordlevel_info.append({'word': word.word, 'start': word.start, 'end': word.end})