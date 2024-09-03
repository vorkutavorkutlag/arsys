import asyncio
import os
import re
from time import sleep
from handlers import footage_handler, reddit_handler, text_to_speech


async def main():
    RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
    RH.init_mem()
    sub, title, body = RH.get_random_post()
    RH.wipe_mem()
    text = ". ".join((title, body))
    stripped_title = re.sub('[!@#$,."?/]', '', title)
    TTSH: text_to_speech.TextSpeech = text_to_speech.TextSpeech()
    await TTSH.tts(text, f"output\\temp_{stripped_title}")

    FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler()
    tts_footage, tts_audio = FH.select_rand_footage(stripped_title, f"temp_{stripped_title}.wav")
    subtitle_footage = FH.generate_subtitles_video(f"temp_{stripped_title}.wav", tts_footage)
    FH.split_footage(subtitle_footage, stripped_title)
    tts_audio.close()
    os.remove(f"output\\temp_{stripped_title}.wav")





if __name__ == '__main__':
    asyncio.run(main())
