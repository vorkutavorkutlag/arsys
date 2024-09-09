import asyncio
import os
import re
from json import load, dump
from handlers import footage_handler, reddit_handler, text_to_speech, upload_handler

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


async def main():
    with open(os.path.join(ROOT_DIR, "youtube_creds.json"), 'r') as file:
        creds = load(file)
    account_num: int = 1

    while True:
        num_uploaded: int = 0

        try:
            creds_values = list(creds[f'youtube_api_{account_num}'].values())
        except KeyError:    # == No more accounts
            return

        # region INITIALIZE HANDLERS
        RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
        TTSH: text_to_speech.TextSpeech = text_to_speech.TextSpeech()
        FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler(ROOT_DIR)
        UPLOADER: upload_handler.Uploader = upload_handler.Uploader(creds=creds_values, ROOT_DIR=ROOT_DIR)
        RH.init_mem()
        # endregion

        while num_uploaded < 3:
            print("ACCOUNT NUMBER: ", account_num)

            sub, title, body, scary = await RH.get_random_post()
            print("Got post")

            title = title.upper()
            text = ". ".join((title, body))
            stripped_title = re.sub('[!@#$,."?/]', '', title)

            await TTSH.tts(text, os.path.join(ROOT_DIR, "output", f"temp_{stripped_title}"))
            print("Got tts")

            tts_footage, tts_audio = FH.select_rand_footage(f"temp_{stripped_title}.wav")
            print("Got tts video")

            bgm_footage = FH.select_rand_bgm(tts_footage, scary)
            print("Got bgm")

            subtitle_footage = FH.generate_subtitles_video(f"temp_{stripped_title}.wav", bgm_footage)
            print("Got subtitles")

            FH.split_footage(subtitle_footage, stripped_title)
            print("Split footage")

            tts_audio.close()

            tags = ["shorts", "fyp", "funny", "reddit", "stories", "entertaining", "interesting"]
            num_uploaded, vid_ids = await UPLOADER.upload_videos_from_folder("output", tags, num_uploaded)
            print("Uploaded")


            if not os.path.exists("subreddit-video-dict.json"):
                with open('subreddit-video-dict.json', 'w+') as file:
                    empty_data = {}
                    dump(empty_data, file, indent=4)

            with open("subreddit-video-dict.json", 'r+') as file:
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

        account_num += 1

if __name__ == '__main__':
    asyncio.run(main())
