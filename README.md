# ARSYS #
## Auomated Reddit Stories for Youtube Shorts

This project uses packages such as asyncpraw, edge TTS, Faster Whisper, moviepy, cv2, and google API to find reddit posts from a chosen batch of subreddits, and make shortform tiktokesque videos with subtitles, tts, and background footage & music, and later post them to YouTube shorts.

<ins>How to use this program:</ins>

1. Setting up & Dependencies:
   1. Clone this [repository](https://github.com/vorkutavorkutlag/arsys.git)
   2. Import all the packages from `requirements.txt`
   3. Download **ImageMagick** and change the path to the .exe in `footage_handler.py` in `line 12` accordingly.
   4. Download **MySQL** and create a database called `arsys`. Run the following queries:
      ```
            CREATE TABLE `subreddits` (
        `name` varchar(255) DEFAULT NULL,
        `scary` tinyint(1) DEFAULT NULL,
        `check_comments` tinyint(1) DEFAULT NULL)
      ```
      ```
            CREATE TABLE `subreddits` (
        `name` varchar(255) DEFAULT NULL,
        `scary` tinyint(1) DEFAULT NULL,
        `check_comments` tinyint(1) DEFAULT NULL)
      ```
   5. Launch `reddit_handler.py` to add/remove subreddits.
   6. Created the following folders in the root directory of the clone: `footage`, `background_music`, `scary_bgm`, `output`. The first three must be filled with background footage, normal background music and scary background music respectively. The output folder is reserved for temporarily storing files while they are being uploaded - anything placed there will get deleted!
   7. Create a `.env` file in the root dir with the following keys and fill out the values:
      ```
        REDDIT_CLIENT_ID=
        REDDIT_SECRET=
        REDDIT_USER_AGENT=
        
        MYSQL_USER=
        MYSQL_PASS=
      ```
      Get the Reddit credentials by creating a [Reddit application](https://www.reddit.com/prefs/apps). You will have the MySQL credentails from setting up the database.
   8. Create a `youtube_creds.json` file in the root dir in the next, expandable format:
      ```
        {
          "youtube_api_1":
          {
            "YOUTUBE_ACCESS_TOKEN": "",
            "YOUTUBE_CLIENT_ID": "",
            "YOUTUBE_CLIENT_SECRET": "",
            "YOUTUBE_REFRESH_TOKEN": "",
            "YOUTUBE_TOKEN_URI": "https://oauth2.googleapis.com/token"
          },
          "youtube_api_2":
          {
            "YOUTUBE_ACCESS_TOKEN": "",
            "YOUTUBE_CLIENT_ID": "",
            "YOUTUBE_CLIENT_SECRET": "",
            "YOUTUBE_REFRESH_TOKEN": "",
            "YOUTUBE_TOKEN_URI": "https://oauth2.googleapis.com/token"
          },
          ...
      ```
      Extend for as many accounts as you are planning to run.

      <ins>To get the credentials:</ins>
        * Go to [Google Cloud Console](https://console.cloud.google.com/welcome)
        * Create a new project (recommended name is `arsys`)
        * Search for and add the `YouTube Data API v3`
        * Complete the `Navigation` -> `APIs and services` -> `OAuth Consent Screen` by choosing the applicaiton as a `Desktop App`, and (IMPORTANT) **add your current email as a testing member**. Publish the app thereafter.
        * Go to `Navigation` -> `APIs and services` -> `Credentials` -> `Create Credentials` -> `API Key`. That is the `YOUTUBE_ACCESS_TOKEN`.
        * Go to `Navigation` -> `APIs and services` -> `Credentials` -> `Create Credentials` -> `OAuth Client ID`. Those are `YOUTUBE_CLIENT_ID` and `YOUTUBE_CLIENT_SECRET` respectively.
        * Run `upload_handler.py` and input what the program asks you to. Note: `YOUTUBE_TOKEN_URI` is always the same. Once ran, it will open a prompt which will ask you to log in. LOG IN WITH THE ACCOUNT YOU CHOSE TO BE A TEST MEMBER! THAT SHOULD BE THE ACCOUNT YOU WANT TO UPLOAD VIDEOS ON! After logging in, the program will print an `Acess Token` and `Refresh Token`. You don't need the `Access Token`. Save the `Refresh Token` into `YOUTUBE_REFRESH_TOKEN`.
  
     
        * Repeat this process for as many accounts as you may need. **YOU DON'T NEED TO REPEAT THE REDDIT/DATABASE/FOOTAGE PARTS**.


2. Running:

    Upon running `main.py`, The app will go through each account listed on `youtube_creds.json` and post 3 shorts on that account. It does so by searching for reddit posts and making the videos, until it has made three videos. It posts those three and deletes it from your system. Sometimes this may result in posting only certain part(s) of the post and not the entirety, leaving viewers unsatisfied. Not much can be done about this. This is done because of the **Google API quota** which restricts its use to only 6 video uploads per day.

    I recommend running it two times per day at a designated time, one time between 12pm - 3pm and one time between 7pm - 10pm. If you're on Windows, you can use the `Task Scheduler` to run the program for you. Simply create a `.bat` file and designate it to be executed at that time.

    The result would be 6 videos per day on each of your accounts. 
