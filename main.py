import asyncio
import os
import re
from handlers import footage_handler, reddit_handler, text_to_speech


async def main():
    while True:
        RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
        RH.init_mem()
        sub, title, body, scary = RH.get_random_post()
        RH.wipe_mem()
        text = ". ".join((title, body))
        stripped_title = re.sub('[!@#$,."?/]', '', title)
        TTSH: text_to_speech.TextSpeech = text_to_speech.TextSpeech()
        await TTSH.tts(text, f"output\\temp_{stripped_title}")

        FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler()
        tts_footage, tts_audio = FH.select_rand_footage(f"temp_{stripped_title}.wav")
        bgm_footage = FH.select_rand_bgm(tts_footage, scary)
        subtitle_footage = FH.generate_subtitles_video(f"temp_{stripped_title}.wav", bgm_footage)
        FH.split_footage(subtitle_footage, stripped_title)
        tts_audio.close()
        os.remove(f"output\\temp_{stripped_title}.wav")
        print(sub)
        return






if __name__ == '__main__':
    asyncio.run(main())
