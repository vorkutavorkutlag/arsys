from handlers import footage_handler, reddit_handler, text_to_speech


def main():
    RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
    RH.init_mem()
    sub, title, body = RH.get_random_post()
    RH.wipe_mem()
    text = " ".join((title, body))
    TTSH: text_to_speech.TTS = text_to_speech.TTS()
    TTSH.tts(text, title)

    FH: footage_handler.Footage_Handler = footage_handler.Footage_Handler()
    # FH.download_video_part(start_time="2:03:47",
    #                        video_url="https://www.youtube.com/watch?v=u7kdVe8q5zs&t=879s",
    #                        duration="1:00:00",
    #                        output_title="skyrim_gameplay.mp4")
    print(FH.select_rand_footage(title, f"tts\\{title}.wav"))




if __name__ == '__main__':
    main()
