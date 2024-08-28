import reddit_handler

if __name__ == '__main__':
    RH: reddit_handler.RedditHandler = reddit_handler.RedditHandler()
    RH.init_mem()
    title, text = RH.get_random_post()
    RH.wipe_mem()

    print(f"{title=}, {text=}")