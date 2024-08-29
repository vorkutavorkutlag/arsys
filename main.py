from handlers import reddit_handler, text_to_speech


def main():
    RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
    RH.init_mem()
    sub, title, body = RH.get_random_post()
    RH.wipe_mem()
    print(sub)
    print(title)
    text = " ".join((title, body))
    text_to_speech.TTS(text, "title")




if __name__ == '__main__':
    main()
