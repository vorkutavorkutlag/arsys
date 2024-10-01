import os
import asyncpraw
import hashlib
from os import getenv
from dotenv import load_dotenv
from random import choice
from json import load, dump
from pprint import pprint
from requests import get
from bs4 import BeautifulSoup
from datetime import date


class RedditHandler:
    def __init__(self, rd: str):
        load_dotenv()
        self.reddit = asyncpraw.Reddit(
            client_id=getenv("REDDIT_CLIENT_ID"),
            client_secret=getenv("REDDIT_SECRET"),
            user_agent=getenv("REDDIT_USER_AGENT"),
            database="arsys"
        )
        self.subreddits: dict = {"nosleep": (1, 0),
                                 "scarystories": (1, 0),
                                 "tifu": (0, 0),
                                 "AmITheAsshole": (0, 0),
                                 "entitledparents": (0, 0),
                                 "confession": (1, 0),
                                 "confessions": (1, 0),
                                 }
        self.weights_dict = {}
        self.ROOT_DIR = rd

    def recalibrate_weights(self):
        with open('../config/subreddit-video-dict.json', 'r') as file:
            data_dict: dict = load(file)
        interaction_dict: dict = {}
        pprint(data_dict)
        for pair in data_dict:
            sub = pair[0]
            vid_list = pair[1]
            sum_interaction: int = 0

            for vid_id in vid_list:
                video_url = f"https://www.youtube.com/watch?v={vid_id}"
                response = get(video_url)

                soup = BeautifulSoup(response.content, 'html.parser')
                views: int = int(soup.find("div", class_="watch-view-count").text) + 1
                likes: int = int(soup.find("button", class_="like-button-renderer-like-button").text) + 1

                sum_interaction += views * likes
            interaction_dict[sub] = sum_interaction
        for sub, score in interaction_dict:
            # SOFTMAX ACTIVATION FUNCTION
            # Because all the values are positive, there is no need in exponentiation
            self.weights_dict[sub] = interaction_dict[sub] / sum(interaction_dict.values())

    async def get_random_post(self, forget: bool = False) -> tuple:
        subname = choice(list(self.subreddits.keys()))
        subreddit = await self.reddit.subreddit(subname)
        scary = self.subreddits[subname][0]
        today = date.today()

        found_post = False
        num_posts = 1
        while not found_post:
            posts = subreddit.hot(limit=num_posts)

            async for post in posts:
                if post.stickied or post.title == "[ Removed by Reddit ]":
                    continue

                post_hash = hashlib.sha1(post.selftext.encode()).hexdigest()
                with open(os.path.join(self.ROOT_DIR, "config", "posts_cache.json"), 'r+') as file:
                    post_cache = load(file)

                    try:                                   # CHECK IF POST WAS POSTED RECENTLY
                        if post_hash in post_cache[today]:
                            continue
                    except (KeyError, TypeError):
                        pass

                    for day in list(post_cache.keys()):   # ELIMINATE OLD POSTS
                        if (today - day).days >= 3:
                            del post_cache[day]

                    if not forget:
                        try:                               # APPEND POST TO MEMORY
                            post_cache[today].append(post_hash)
                        except TypeError:
                            post_cache[today] = [post_hash]

                        file.seek(0)
                        dump(post_cache, file, indent=6)

                    return subname, post.title, post.selftext, scary

            num_posts += 1


if __name__ == "__main__":
    pass
