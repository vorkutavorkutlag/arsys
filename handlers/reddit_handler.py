import praw
import mysql.connector
import hashlib
from os import getenv
from dotenv import load_dotenv
from random import choice

from pprint import pprint


class RedditHandler:
    def __init__(self):
        load_dotenv()
        self.reddit = praw.Reddit(
            client_id=getenv("REDDIT_CLIENT_ID"),
            client_secret=getenv("REDDIT_SECRET"),
            user_agent=getenv("REDDIT_USER_AGENT"),
            database="arsys"
        )
        self.arsys_db = mysql.connector.connect(
            host="localhost",
            user=getenv("MYSQL_USER"),
            password=getenv("MYSQL_PASS"),
            database="arsys"
        )

        self.arsys_cursor = self.arsys_db.cursor()
        self.arsys_cursor.execute("SELECT * FROM subreddits")
        self.subreddits: list = self.arsys_cursor.fetchall()

    def init_mem(self):
        self.arsys_cursor.execute("CREATE TABLE IF NOT EXISTS old_posts (hash CHAR(255), sub VARCHAR(255))")
        self.arsys_db.commit()

    def wipe_mem(self):
        self.arsys_cursor.execute("DROP TABLE IF EXISTS old_posts")
        self.arsys_cursor.execute("CREATE TABLE old_posts (hash CHAR(255), sub VARCHAR(255))")
        self.arsys_db.commit()


    def show_mem(self):
        self.arsys_cursor.execute(f"SELECT * FROM old_posts")
        for pair in self.arsys_cursor.fetchall():
            pprint(pair)

    def show_subreddits(self):
        self.arsys_cursor.execute(f"SELECT * FROM subreddits")
        for pair in self.arsys_cursor.fetchall():
            pprint(pair)

    def add_subreddit(self, sub: str):
        sql = "INSERT INTO subreddits (name) VALUES (%s)"
        self.arsys_cursor.execute(sql, (sub,))
        self.arsys_db.commit()


    def remove_sub(self, sub: str):
        sql = f"DELETE FROM subreddits WHERE name = '{sub}'"
        self.arsys_cursor.execute(sql)
        self.arsys_db.commit()


    def get_random_post(self) -> tuple:
        subname = choice(self.subreddits)
        subreddit = self.reddit.subreddit(subname[0])

        found_post = False
        num_posts = 1
        while not found_post:
            posts = subreddit.hot(limit=num_posts)

            for post in posts:
                if post.stickied or post.title == "[ Removed by Reddit ]":
                    continue

                post_hash = hashlib.sha1(post.selftext.encode()).hexdigest()

                self.arsys_cursor.execute(f"SELECT hash FROM old_posts WHERE sub = '{subname[0]}'")
                used_hashes = self.arsys_cursor.fetchall()
                if (post_hash,) in used_hashes:
                    continue

                sql = "INSERT INTO old_posts (hash, sub) VALUES (%s, %s)"
                var = (post_hash, subname[0])
                self.arsys_cursor.execute(sql, var)
                self.arsys_db.commit()
                return subname, post.title, post.selftext


            num_posts += 1
