import random
import os
import cv2
import numpy as np
from librosa import get_duration
from moviepy.editor import VideoFileClip, AudioFileClip
from moviepy.config import change_settings
from faster_whisper import WhisperModel
from math import ceil

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


class Footage_Handler:
    @staticmethod
    def select_rand_footage(title: str, tts_path: str):
        not_videos = ['__pycache__', 'desktop.ini']
        background_footage = f"footage\\" \
                             f"{random.choice([file for file in os.listdir('footage') if file not in not_videos])}"
        background_footage = VideoFileClip(background_footage)

        speech_duration = get_duration(filename=f"output\\{tts_path}")
        audio_clip = AudioFileClip(filename=f"output\\{tts_path}")

        new_start = random.randrange(0, round(background_footage.duration - speech_duration))
        video_clip = background_footage.subclip(new_start, new_start + speech_duration)
        video_clip.audio = audio_clip
        return video_clip, audio_clip

    @staticmethod
    def generate_subtitles_video(tts_path: str, input_video: VideoFileClip, cuda=True):

        def split_text_into_lines(data):

            MaxChars = 8
            MaxDuration = 0.2
            MaxGap = 0.2

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

        def pipeline(frame, t):
            try:
                frame = np.array(frame)
                textcontnet = next((textcontnet for textcontnet in all_texccontents
                                        if textcontnet['start'] <= t <= textcontnet['end']), None)

                if textcontnet:
                    font_scale = 2.4 * (1.5*t + 0.9 - 1.5*textcontnet['end'])
                    pos_x = int(input_video.w/2 - (9.375*font_scale*(len(textcontnet['word']))))
                    pos_y = 400
                    cv2.putText(frame,
                                textcontnet['word'],
                                (pos_x, pos_y),  # Position of the text
                                cv2.CALIB_CB_PLAIN,
                                font_scale,  # Font scale
                                (150, 0, 0),  # Text color (white)
                                18,  # Text thickness
                                cv2.LINE_AA)
                    cv2.putText(frame,
                                textcontnet['word'],
                                (pos_x, pos_y),  # Position of the text
                                cv2.CALIB_CB_PLAIN,
                                font_scale,  # Font scale
                                (255, 255, 255),  # Text color (white)
                                6,  # Text thickness
                                cv2.LINE_AA)
            except (StopIteration, StopIteration):
                pass  # No subtitle for this time

            return frame

        model_size = "large"
        model = WhisperModel(model_size, device="cuda") if cuda else WhisperModel(model_size)

        wordlevel_info = []
        segments, info = model.transcribe(f"output\\{tts_path}", word_timestamps=True)
        segments = list(segments)  # The transcription will actually run here.
        for segment in segments:
            for word in segment.words:
                wordlevel_info.append({'word': word.word, 'start': word.start, 'end': word.end})

        linelevel_info = split_text_into_lines(wordlevel_info)
        all_texccontents = []
        for segment in linelevel_info:
            all_texccontents.extend(segment['textcontents'])

        out_video = input_video.fl(lambda gf, t: pipeline(gf(t), t))
        out_video.write_videofile("PLEASEWORK.mp4")
        return out_video

    @staticmethod
    def split_footage(full_video: VideoFileClip, title):
        current_duration = full_video.duration
        divide_into_count = ceil(current_duration / 60)
        single_duration = current_duration / divide_into_count

        if single_duration > current_duration:
            full_video.write_videofile(f"output\\{title}.mp4")
            return

        i = 0
        while current_duration > single_duration:
            i += 1
            print(f"writing part {i}")
            clip = full_video.subclip(current_duration - single_duration, current_duration)
            current_duration -= single_duration
            print(f"output\\{title} Part {i}")
            clip.to_videofile(f"output\\{title} Part {divide_into_count - i}.mp4",
                              codec="libx264",
                              remove_temp=True,
                              audio_codec='aac')
