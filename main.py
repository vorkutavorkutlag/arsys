import asyncio
import os
import re
from gc import collect
from json import load, dump
from handlers import footage_handler, reddit_handler, text_to_speech, upload_handler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


async def main():
    if not os.path.exists(os.path.join(ROOT_DIR, "config", "subreddit-video-dict.json")):
        with open(os.path.join(ROOT_DIR, "config", 'subreddit-video-dict.json'), 'w+') as file:
            empty_data = {}
            dump(empty_data, file, indent=4)

    if not os.path.exists(os.path.join(ROOT_DIR, "config", "posts_cache.json")):
        with open(os.path.join(ROOT_DIR, "config", 'posts_cache.json'), 'w+') as file:
            empty_data = {}
            dump(empty_data, file, indent=4)

    # region INITIALIZE HANDLERS
    RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler(ROOT_DIR)
    TTSH: text_to_speech.TextSpeech = text_to_speech.TextSpeech()
    FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler(ROOT_DIR)
    # endregion

    num_uploaded = 0
    tags = ["shorts", "fyp", "funny", "reddit", "stories", "entertaining", "interesting"]

    video_folder = os.path.join(ROOT_DIR, "output")

    cookies_path = os.path.join(ROOT_DIR, "config", "cookies_cache.json")

    with open(os.path.join(ROOT_DIR, "config", "youtube_channels.json"), 'r') as file:
        youtube_channels = load(file)

    # for _ in range(3):
    #     sub, title, body, scary = await RH.get_random_post(ROOT_DIR)
    #     print("Got post")
    #
    #     title = title.upper()
    #     text = ". ".join((title, body))
    #     stripped_title = re.sub('[!@#$,."?/]', '', title)
    #
    #     await TTSH.tts(text, os.path.join(ROOT_DIR, "output", f"temp_{stripped_title}"))
    #     print("Got tts")
    #
    #     tts_footage, tts_audio = FH.select_rand_footage(f"temp_{stripped_title}.wav")
    #     print("Got tts video")
    #
    #     bgm_footage = FH.select_rand_bgm(tts_footage, scary)
    #     print("Got bgm")
    #
    #     subtitle_footage = FH.generate_subtitles_video(f"temp_{stripped_title}.wav", bgm_footage)
    #     print("Got subtitles")
    #
    #     FH.split_footage(subtitle_footage, stripped_title)
    #     print("Split footage")
    #
    #     tts_audio.close()

    video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]
    vid_ids = await upload_handler.upload_videos_to_channels(video_files,
                                                               youtube_channels,
                                                               tags,
                                                               cookies_path)
    print("Uploaded")

    with open(os.path.join(ROOT_DIR, "config", "subreddit-video-dict.json"), 'r+') as file:
        data_dict = load(file)
        try:
            data_dict[sub].extend(vid_ids)
        except KeyError:
            data_dict[sub] = vid_ids

        file.seek(0)
        dump(data_dict, file, indent=4)
        file.truncate()

    print("Added to archive")

    for file in os.listdir(os.path.join(ROOT_DIR, 'output')):
        if file.endswith((".mp4", ".mp3", ".wav")):
            os.remove(os.path.join(ROOT_DIR, 'output', file))
    print("Cleaned trash")



if __name__ == '__main__':
    asyncio.run(main())
    collect()      # GARBAGE COLLECTIONS