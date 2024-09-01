import random
import os
from librosa import get_duration
from moviepy.editor import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip
from moviepy.config import change_settings
from faster_whisper import WhisperModel


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
        for segment in segments:
            for word in segment.words:
                wordlevel_info.append({'word': word.word, 'start': word.start, 'end': word.end})
        linelevel_subtitles = self.split_text_into_lines(wordlevel_info)


        input_video = VideoFileClip(video_path)
        frame_size = input_video.size
        all_linelevel_splits = []

        for line in linelevel_subtitles:
            out_clips, positions = self.create_caption(line, frame_size, x_pos=0, y_pos=input_video.h)

            max_width = 0
            max_height = 0

            for position in positions:
                x_pos, y_pos = position['x_pos'], position['y_pos']
                width, height = position['width'], position['height']
                max_width = max(max_width, x_pos + width)
                max_height = max(max_height, y_pos + height)

            color_clip = ColorClip(size=(int(max_width * 1.1), int(max_height * 1.1)),
                                   color=(64, 64, 64))
            color_clip = color_clip.set_opacity(0)
            color_clip = color_clip.set_start(line['start']).set_duration(line['end'] - line['start'])

            # centered_clips = [each.set_position('center') for each in out_clips]

            clip_to_overlay = CompositeVideoClip([color_clip] + out_clips)
            clip_to_overlay = clip_to_overlay.set_position("bottom")

            all_linelevel_splits.append(clip_to_overlay)

        input_video_duration = input_video.duration

        final_video = CompositeVideoClip([input_video] + all_linelevel_splits)

        # Set the audio of the final video to be the same as the input video
        final_video = final_video.set_audio(input_video.audio)

        # Save the final clip as a video file with the audio included
        final_video.write_videofile("..\\output\\output.mp4", fps=35, codec="libx264", audio_codec="aac")


    @staticmethod
    def create_caption(textJSON, framesize,  x_pos, y_pos, font="Calibri-Bold", color='white',
                       highlight_color='red', stroke_color='black', stroke_width=1.5, ):

        wordcount = len(textJSON['textcontents'])
        full_duration = textJSON['end'] - textJSON['start']

        word_clips = []
        xy_textclips_positions = []

        line_width = 0  # Total width of words in the current line
        frame_width = framesize[0]
        frame_height = framesize[1]

        x_buffer = frame_width * 1 / 10

        max_line_width = frame_width - 2 * x_buffer

        fontsize = int(frame_height * 0.075)

        space_width = ""
        space_height = ""

        for index, wordJSON in enumerate(textJSON['textcontents']):
            duration = wordJSON['end'] - wordJSON['start']
            word_clip = TextClip(wordJSON['word'],
                                 font=font,
                                 fontsize=fontsize,
                                 color=color,
                                 stroke_color=stroke_color,
                                 stroke_width=stroke_width,
                                 bg_color='transparent',
                                 transparent=True).set_start(textJSON['start']).set_duration(full_duration)

            word_clip_space = TextClip(" ",
                                       font=font,
                                       fontsize=fontsize,
                                       color=color,
                                       bg_color='transparent',
                                       transparent=True).set_start(textJSON['start']).set_duration(full_duration)

            word_width, word_height = word_clip.size
            space_width, space_height = word_clip_space.size
            if line_width + word_width + space_width <= max_line_width:
                # Store info of each word_clip created
                xy_textclips_positions.append({
                    "x_pos": x_pos,
                    "y_pos": y_pos,
                    "width": word_width,
                    "height": word_height,
                    "word": wordJSON['word'],
                    "start": wordJSON['start'],
                    "end": wordJSON['end'],
                    "duration": duration
                })

                word_clip = word_clip.set_position((x_pos, y_pos))
                word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))

                x_pos = x_pos + word_width + space_width
                line_width = line_width + word_width + space_width
            else:
                # Move to the next line
                x_pos = 0
                y_pos = y_pos + word_height + 10
                line_width = word_width + space_width

                # Store info of each word_clip created
                xy_textclips_positions.append({
                    "x_pos": x_pos,
                    "y_pos": y_pos,
                    "width": word_width,
                    "height": word_height,
                    "word": wordJSON['word'],
                    "start": wordJSON['start'],
                    "end": wordJSON['end'],
                    "duration": duration
                })

                word_clip = word_clip.set_position((x_pos, y_pos))
                word_clip_space = word_clip_space.set_position((x_pos + word_width, y_pos))
                x_pos = word_width + space_width

            word_clips.append(word_clip)
            word_clips.append(word_clip_space)

        for highlight_word in xy_textclips_positions:
            word_clip_highlight = TextClip(highlight_word['word'],
                                           font=font,
                                           fontsize=fontsize,
                                           color=highlight_color,
                                           stroke_color=stroke_color,
                                           stroke_width=stroke_width).set_start(highlight_word['start']).\
                                           set_duration(highlight_word['duration'])

            word_clip_highlight = word_clip_highlight.set_position((highlight_word['x_pos'], highlight_word['y_pos']))
            word_clips.append(word_clip_highlight)

        return word_clips, xy_textclips_positions


    @staticmethod
    def split_text_into_lines(data):

        MaxChars = 20
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
