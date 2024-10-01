import os
import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# Define the folder where the videos are stored
video_folder = "/path/to/your/videos"  # Replace with your actual folder path
video_files = [os.path.join(video_folder, f) for f in os.listdir(video_folder) if f.endswith(".mp4")]

# Define a list of YouTube channel URLs where you want to upload videos
youtube_channels = ["https://studio.youtube.com/channel/CHANNEL_ID1",
                    "https://studio.youtube.com/channel/CHANNEL_ID2"]

# Set up Chrome WebDriver options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")

# Path to your WebDriver (adjust this path)
webdriver_path = "/path/to/chromedriver"  # Replace with your chromedriver path

# Path to the cookie file (JSON format)
cookies_file_path = "/path/to/your/cookies.json"  # Replace with your actual cookie file path


# Load cookies from a JSON file
def load_cookies(driver, cookies_file):
    # Load cookies from the file
    with open(cookies_file, "r") as file:
        cookies = json.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)


# Create a function to upload a video to YouTube
def upload_video(driver, video_path, title):
    # Navigate to YouTube Upload page
    driver.get("https://www.youtube.com/upload")
    time.sleep(5)  # Wait for page to load

    # Find the file input element to upload the video
    file_input = driver.find_element(By.XPATH, "//input[@type='file']")
    file_input.send_keys(video_path)  # Upload the video file

    time.sleep(10)  # Wait for the upload to complete (adjust as necessary)

    # Add the video title
    title_input = driver.find_element(By.XPATH, "//input[@id='textbox']")
    title_input.clear()
    title_input.send_keys(title)

    time.sleep(2)  # Short pause for title input

    # Click on "Next" buttons multiple times (YouTube has multiple steps)
    next_button = driver.find_element(By.XPATH, "//ytcp-button[@id='next-button']")
    for _ in range(3):  # Click Next 3 times
        next_button.click()
        time.sleep(2)

    # Click on "Public" to make the video public
    public_button = driver.find_element(By.XPATH, "//tp-yt-paper-radio-button[@name='PUBLIC']")
    public_button.click()

    # Finally, click on "Publish"
    publish_button = driver.find_element(By.XPATH, "//ytcp-button[@id='done-button']")
    publish_button.click()

    # Wait for the video to be processed and uploaded
    time.sleep(20)  # Adjust as necessary based on the video size


# Create a function to log in using cookies and upload videos to multiple channels
def upload_videos_to_channels(video_files, youtube_channels):
    # Initialize WebDriver
    driver = webdriver.Chrome(service=Service(webdriver_path), options=chrome_options)

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
            upload_video(driver, video_file, video_title)
            print(f"Uploaded {video_file} to {channel_url}")

    # Close the driver after all uploads
    driver.quit()


# Call the function to start uploading
upload_videos_to_channels(video_files, youtube_channels)
