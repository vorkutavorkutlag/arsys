import asyncio
import os
import re
from handlers import footage_handler, reddit_handler, text_to_speech


async def main():
    RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
    RH.init_mem()
    sub, title, body = RH.get_random_post()
    RH.wipe_mem()
    text = ". ".join((title, body))
    stripped_title = re.sub('[!@#$,."?/]', '', title)
    TTSH: text_to_speech.TextSpeech = text_to_speech.TextSpeech()
    await TTSH.tts(text, stripped_title)

    FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler()
    FH.select_rand_footage(stripped_title, f"{stripped_title}.wav")

    FH.generate_subtitles_video(f"{stripped_title}.wav", f"output\\building_{stripped_title}.mp4")

    os.remove(f"{stripped_title}.wav")





if __name__ == '__main__':
    asyncio.run(main())
