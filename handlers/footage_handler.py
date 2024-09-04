import random
import os
import cv2
import numpy as np
from librosa import get_duration
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeAudioClip, \
    concatenate_audioclips, concatenate_videoclips
from moviepy.config import change_settings
from faster_whisper import WhisperModel


os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
change_settings({"IMAGEMAGICK_BINARY": r"C:\\Program Files\\ImageMagick-7.1.1-Q16-HDRI\\magick.exe"})


class Footage_Handler:
    @staticmethod
    def select_rand_footage(tts_path: str):
        def loop_video_to_duration(clip: VideoFileClip, target_duration: int):
            clip_duration = clip.duration
            n_loops = int(target_duration // clip_duration) + 1

            looped_clip = concatenate_videoclips([clip] * n_loops)
            return looped_clip.subclip(0, target_duration)

        not_videos = ['__pycache__', 'desktop.ini']
        background_footage = f"footage\\" \
                             f"{random.choice([file for file in os.listdir('footage') if file not in not_videos])}"
        background_footage = VideoFileClip(background_footage)

        speech_duration = get_duration(filename=f"output\\{tts_path}")
        audio_clip = AudioFileClip(filename=f"output\\{tts_path}")

        if audio_clip.duration < background_footage.duration:
            new_start = random.randrange(0, round(background_footage.duration - speech_duration))
            video_clip = background_footage.subclip(new_start, new_start + speech_duration)
        else:
            video_clip = loop_video_to_duration(background_footage, audio_clip.duration)
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
        return out_video

    @staticmethod
    def split_footage(full_video: VideoFileClip, title):
        partDura = 59  # duration of a part in seconds
        fullDura = full_video.duration
        startPos = 0

        i = 1
        while True:
            endPos = startPos + partDura

            if endPos > fullDura:
                endPos = fullDura

            clip = full_video.subclip(startPos, endPos)
            part_name = f"output\\{title} Part {i}.mp4"
            clip.to_videofile(part_name, codec="libx264", temp_audiofile='temp-audio.m4a', remove_temp=True,
                              audio_codec='aac')
            print("part ", i, "done")
            i += 1

            startPos = endPos  # jump to next clip
            if startPos >= fullDura:
                break

    @staticmethod
    def select_rand_bgm(video: VideoFileClip, scary: bool):
        def loop_audio_clip(audio_clip, duration):
            loops = int(duration // audio_clip.duration) + 1
            audio_clips = [audio_clip] * loops
            return concatenate_audioclips(audio_clips).subclip(0, duration)

        not_bgms = ['__pycache__', 'desktop.ini']
        if scary:
            background_music = f"scary_bgm\\" \
                        f"{random.choice([file for file in os.listdir('scary_bgm') if file not in not_bgms])}"
        else:
            background_music = f"background_music\\" \
                        f"{random.choice([file for file in os.listdir('background_music') if file not in not_bgms])}"
        background_music = AudioFileClip(background_music)
        background_music = loop_audio_clip(background_music, duration=video.duration)
        background_music = background_music.set_duration(video.duration)
        background_music = background_music.volumex(0.4)
        combined_audio = CompositeAudioClip([video.audio, background_music])
        final_video = video.set_audio(combined_audio)
        background_music.close()
        return final_video
