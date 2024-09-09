import asyncpraw
import mysql.connector
import hashlib
from os import getenv
from dotenv import load_dotenv
from random import choice

from pprint import pprint


class RedditHandler:
    def __init__(self):
        load_dotenv()
        self.reddit = asyncpraw.Reddit(
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
        self.arsys_cursor.execute("SELECT name FROM subreddits")
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

    def add_subreddit(self, sub: str, scary: bool = False, check_comments: bool = False):
        sql = "INSERT INTO subreddits (name, scary, check_comments) VALUES (%s, %s, %s)"
        self.arsys_cursor.execute(sql, (sub, scary, check_comments))
        self.arsys_db.commit()


    def remove_sub(self, sub: str):
        sql = f"DELETE FROM subreddits WHERE name = '{sub}'"
        self.arsys_cursor.execute(sql)
        self.arsys_db.commit()


    async def get_random_post(self, forget: bool = False) -> tuple:
        subname = choice(self.subreddits)
        subreddit = await self.reddit.subreddit(subname[0])
        self.arsys_cursor.execute(f"SELECT scary FROM subreddits WHERE name = '{subname[0]}'")
        scary = bool(list(self.arsys_cursor.fetchall())[0][0])   # FETCHALL RETURNS LIST OF TUPLES

        found_post = False
        num_posts = 1
        while not found_post:
            posts = subreddit.hot(limit=num_posts)

            async for post in posts:
                if post.stickied or post.title == "[ Removed by Reddit ]":
                    continue

                post_hash = hashlib.sha1(post.selftext.encode()).hexdigest()
                self.arsys_cursor.execute(f"SELECT hash FROM old_posts WHERE sub = '{subname[0]}'")
                used_hashes = self.arsys_cursor.fetchall()
                if (post_hash,) in used_hashes:
                    continue

                if not forget:
                    sql = "INSERT INTO old_posts (hash, sub) VALUES (%s, %s)"
                    var = (post_hash, subname[0])
                    self.arsys_cursor.execute(sql, var)
                    self.arsys_db.commit()

                return subname, post.title, post.selftext, scary


            num_posts += 1


if __name__ == "__main__":
    RH = RedditHandler()
    while True:
        answer = input("\n1: Add Subreddit\n"
                  "2: Remove Subreddit\n"
                  "3: Show Subreddits\n")
        match answer:
            case '1':
                name = input("\nSubreddit name (no 'r/'):\n")
                scary = bool(input("\nScary (1 or 0):\n"))
                check_comments = bool(input("\nCheck comments (1 or 0):\n"))
                RH.add_subreddit(sub=name, scary=scary, check_comments=check_comments)
                print("Successfully added.")
            case '2':
                name = input("\nSubreddit name (no 'r/'):\n")
                RH.remove_sub(sub=name)
                print(f"\n{RH.arsys_cursor.rowcount} row(s) deleted.")
            case '3':
                RH.show_subreddits()
            case _:
                break


