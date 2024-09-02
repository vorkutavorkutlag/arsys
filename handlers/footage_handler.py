import random
import os
import cv2
import numpy as np
from librosa import get_duration
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings
from faster_whisper import WhisperModel

from pprint import pprint

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


class Footage_Handler:
    @staticmethod
    def select_rand_footage(title: str, tts_path: str):
        not_videos = ['__pycache__', 'desktop.ini']
        background_footage = f"footage\\" \
                             f"{random.choice([file for file in os.listdir('footage') if file not in not_videos])}"
        background_footage = VideoFileClip(background_footage)

        speech_duration = get_duration(filename=tts_path)
        audio_clip = AudioFileClip(filename=tts_path)

        new_start = random.randrange(0, round(background_footage.duration - speech_duration))
        video_clip = background_footage.subclip(new_start, new_start + speech_duration)
        video_clip.audio = audio_clip
        video_clip.write_videofile(f"..\\output\\building_{title}.mp4")

    def generate_subtitles_video(self, tts_path: str, video_path: str, cuda=True):
        print(f"{tts_path=}")
        print(f"{video_path=}")
        model_size = "large"
        model = WhisperModel(model_size, device="cuda") if cuda else WhisperModel(model_size)

        wordlevel_info = []
        segments, info = model.transcribe(tts_path, word_timestamps=True)
        segments = list(segments)  # The transcription will actually run here.
        seg_gen = (seg for seg in segments)
        for segment in segments:
            for word in segment.words:
                wordlevel_info.append({'word': word.word, 'start': word.start, 'end': word.end})

        input_video = VideoFileClip(video_path)

        def pipeline(frame, t):
            try:
                frame = np.array(frame)
                # Print the current time
                pos_x = 10
                pos_y = 500
                # Find the current segment based on the time `t`
                current_segment = next((seg for seg in segments if seg.start <= t <= seg.end), None)

                if current_segment:
                    pprint(current_segment)
                    text = current_segment.text
                    cv2.putText(frame,
                                text,
                                (pos_x, pos_y),  # Position of the text
                                cv2.FONT_HERSHEY_SIMPLEX,
                                1,  # Font scale
                                (255, 255, 255),  # Text color (white)
                                3,  # Text thickness
                                cv2.LINE_AA)
            except (StopIteration, StopIteration):
                pass  # No subtitle for this time

            return frame

        out_video = input_video.fl(lambda gf, t: pipeline(gf(t), t))
        out_video.write_videofile("..\\output\\vid_with_subtitles.mp4", audio=True)



    @staticmethod
    def split_text_into_lines(data):

        MaxChars = 15
        MaxDuration = 2.5
        MaxGap = 1.5

        subtitles = []
        line = []
        line_duration = 0

        for idx, word_data in enumerate(data):
            start = word_data["start"]
            end = word_data["end"]

            line.append(word_data)
            line_duration += end - start

            temp = " ".join(item["word"] for item in line)

            # Check if adding a new word exceeds the maximum character count or duration
            new_line_chars = len(temp)

            duration_exceeded = line_duration > MaxDuration
            chars_exceeded = new_line_chars > MaxChars
            if idx > 0:
                gap = word_data['start'] - data[idx - 1]['end']
                # print (word,start,end,gap)
                maxgap_exceeded = gap > MaxGap
            else:
                maxgap_exceeded = False

            if duration_exceeded or chars_exceeded or maxgap_exceeded:
                if line:
                    subtitle_line = {
                        "word": " ".join(item["word"] for item in line),
                        "start": line[0]["start"],
                        "end": line[-1]["end"],
                        "textcontents": line
                    }
                    subtitles.append(subtitle_line)
                    line = []
                    line_duration = 0

        if line:
            subtitle_line = {
                "word": " ".join(item["word"] for item in line),
                "start": line[0]["start"],
                "end": line[-1]["end"],
                "textcontents": line
            }
            subtitles.append(subtitle_line)

        return subtitles


if __name__ == "__main__":
    FH = Footage_Handler()
    FH.generate_subtitles_video(r"C:\Users\mensc\PycharmProjects\arsys\audio.wav", r"C:\Users\mensc\PycharmProjects\arsys\output\video.mp4")
