import os
import time
import json
from selenium import webdriver
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Path to your WebDriver (adjust this path)
webdriver_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"  # Replace with your chromedriver path
chrome_options = Options()
chrome_options.add_argument("--headless")

# Path to the cookie file (JSON format)


# Load cookies from a JSON file
def load_cookies(driver, cookies_file):
    # Load cookies from the file
    with open(cookies_file, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)


# Create a function to upload a video to YouTube
def upload_video(driver, video_path, title, tags):
    # Navigate to YouTube Upload page
    driver.get("https://www.youtube.com/upload")
    time.sleep(5)  # Wait for the upload page to load

    try:
        # Find the file input element to upload the video
        file_input = driver.find_element(By.XPATH, "//input[@type='file']")
        file_input.send_keys(video_path)  # Upload the video file
        print(f"Uploading {video_path}...")
    except NoSuchElementException:
        print("File input not found. Aborting upload.")
        return None

    # Wait for the video to be processed (adjust time as necessary)
    time.sleep(15)

    try:
        # Add the video title
        title_input = driver.find_element(By.XPATH, "//input[@id='textbox']")
        title_input.clear()
        title_input.send_keys(title)
        print(f"Setting title: {title}")
    except NoSuchElementException:
        print("Title input not found.")

    # Add tags
    try:
        # Navigate to the "More options" section where tags can be added
        more_options_button = driver.find_element(By.XPATH, "//ytcp-button[@id='more-options-button']")
        more_options_button.click()
        time.sleep(2)

        # Locate the tags input field
        tags_input = driver.find_element(By.XPATH, "//input[@aria-label='Tags']")
        tags_input.send_keys(", ".join(tags))
        print(f"Adding tags: {', '.join(tags)}")
    except NoSuchElementException:
        print("Tags input not found.")

    # Click on "Next" buttons multiple times (YouTube has multiple steps)
    try:
        next_buttons = driver.find_elements(By.XPATH, "//ytcp-button[@id='next-button']")
        for button in next_buttons:
            button.click()
            time.sleep(2)
        print("Clicked through 'Next' buttons.")
    except NoSuchElementException:
        print("Next button not found.")

    # Select "Public" for video visibility
    try:
        public_radio = driver.find_element(By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']")
        public_radio.click()
        print("Set video visibility to Public.")
    except NoSuchElementException:
        print("Public radio button not found.")

    # Click on "Publish" button
    try:
        publish_button = driver.find_element(By.XPATH, "//ytcp-button[@id='done-button']")
        publish_button.click()
        print("Clicked 'Publish' button.")
    except NoSuchElementException:
        print("Publish button not found.")

    # Wait for the upload to complete and for YouTube to redirect to the video page
    time.sleep(30)  # Adjust based on video size and upload speed

    # Retrieve the current URL, which should contain the video ID
    current_url = driver.current_url
    print(f"Current URL after upload: {current_url}")

    # Extract the video ID from the URL
    video_id = None
    if "watch?v=" in current_url:
        video_id = current_url.split("watch?v=")[1].split("&")[0]
    elif "/video/" in current_url:
        video_id = current_url.split("/video/")[1].split("/")[0]
    else:
        # Alternative method: Extract video ID from the page's meta tags or other elements
        try:
            video_id_element = driver.find_element(By.XPATH, "//meta[@itemprop='videoId']")
            video_id = video_id_element.get_attribute("content")
        except NoSuchElementException:
            print("Unable to locate video ID in the URL or page.")

    if video_id:
        print(f"Video uploaded successfully. Video ID: {video_id}")
    else:
        print("Video ID could not be retrieved.")

    return video_id


def upload_videos_to_channels(video_files, youtube_channels, tags, cookies_file_path):
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options,)

    # Load YouTube homepage and load cookies
    driver.get("https://www.youtube.com")
    time.sleep(5)  # Wait for the page to load

    # Load cookies into the browser session
    load_cookies(driver, cookies_file_path)

    # Refresh the page to apply the cookies
    driver.refresh()
    time.sleep(5)  # Wait for the refreshed page to load

    # Loop through the YouTube channels and upload the videos
    for channel_url in youtube_channels:
        driver.get(channel_url)  # Open YouTube Studio for each channel
        time.sleep(5)  # Wait for the channel page to load

        # Loop through all the videos in the folder
        for video_file in video_files:
            # Extract the video title from the file name
            video_title = os.path.basename(video_file).replace(".mp4", "")

            # Upload the video
            upload_video(driver, video_file, video_title, tags)
            print(f"Uploaded {video_file} to {channel_url}")

    # Close the driver after all uploads
    driver.quit()


def netscape_convertor(file_path: str):
    added_cookies: list[dict] = []
    cookie_cache_path: str = '..\\config\\cookies_cache.json'
    if not os.path.exists(cookie_cache_path):
        with open(cookie_cache_path, 'w') as file:
            json.dump([], file, indent=6)

    with open(file_path, 'r') as cookiestxt:
        for line in cookiestxt:
            if line.startswith('#') or line == "\n":
                continue

            line = line[1:]
            args: list[str] = line.split("	")
            args[1] = args[1].lower().capitalize(); args[3] = args[3].lower().capitalize()
            args[1] = eval(args[1]); args[3] = eval(args[3])

            cookie: dict = {"domain": args[0],
                      "httpOnly": args[1],
                      "path": args[2],
                      "secure": args[3],
                      "expiry": int(args[4]),
                      "name": args[5],
                      "value": args[6]}
            added_cookies.append(cookie)

    with open(cookie_cache_path, 'r+') as file:
        existing_cookies: list[dict] = json.load(file)
        existing_cookies.extend(added_cookies)
        file.seek(0)
        json.dump(existing_cookies, file, indent=6)


if __name__ == "__main__":
    netscape_convertor(r"C:\Users\mensc\Downloads\4cookies.txt")
