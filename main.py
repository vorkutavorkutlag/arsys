import asyncio
import os
import re
from dotenv import load_dotenv
from handlers import footage_handler, reddit_handler, text_to_speech, upload_handler

load_dotenv()
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


async def main():
    while True:
        num_uploaded: int = 0
        account_num: int = 1

        creds = [
            os.getenv(f'YOUTUBE_ACCESS_TOKEN_{account_num}'),
            os.getenv(f'YOUTUBE_REFRESH_TOKEN_{account_num}'),
            os.getenv(f'YOUTUBE_CLIENT_ID_{account_num}'),  # Will be None if not found
            os.getenv(f'YOUTUBE_CLIENT_SECRET_{account_num}'),
            os.getenv(f'YOUTUBE_TOKEN_URI_{account_num}')]

        if None in creds:
            return

        while num_uploaded < 3:
            RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
            TTSH: text_to_speech.TextSpeech = text_to_speech.TextSpeech()
            FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler(ROOT_DIR)
            UPLOADER: upload_handler.Uploader = upload_handler.Uploader(creds=creds, ROOT_DIR=ROOT_DIR)
            RH.init_mem()

            sub, title, body, scary = await RH.get_random_post()

            title = title.upper()
            text = ". ".join((title, body))
            stripped_title = re.sub('[!@#$,."?/]', '', title)

            await TTSH.tts(text, os.path.join(ROOT_DIR, "output", f"temp_{stripped_title}"))

            tts_footage, tts_audio = FH.select_rand_footage(f"temp_{stripped_title}.wav")

            bgm_footage = FH.select_rand_bgm(tts_footage, scary)

            subtitle_footage = FH.generate_subtitles_video(f"temp_{stripped_title}.wav", bgm_footage)

            FH.split_footage(subtitle_footage, stripped_title)

            tts_audio.close()

            tags = ["shorts", "fyp", "funny", "reddit", "stories", "entertaining", "interesting"]
            num_uploaded += await UPLOADER.upload_videos_from_folder("output", tags)

            account_num += 1

            for file in os.listdir(os.path.join(ROOT_DIR, 'output')):
                if file.endswith((".mp4", ".mp3", ".wav")):
                    os.remove(os.path.join(ROOT_DIR, 'output', file))


if __name__ == '__main__':
    asyncio.run(main())
