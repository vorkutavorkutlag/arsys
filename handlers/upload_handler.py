import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


load_dotenv()


class Uploader:

    @staticmethod
    def upload_video(youtube, file_path, title, description, tags, category="22", privacy_status="private"):
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": description,
                    "tags": tags,
                    "categoryId": category
                },
                "status": {
                    "privacyStatus": privacy_status  # "private", "public" or "unlisted"
                }
            }
            media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%")

            print(f"Upload complete: {response['id']}")

        except HttpError as e:
            print(f"An error occurred: {e}")
            return None


    @staticmethod
    def authenticate_youtube():
        creds = Credentials(
            token=os.getenv('YOUTUBE_ACCESS_TOKEN'),
            refresh_token=os.getenv('YOUTUBE_REFRESH_TOKEN'),
            client_id=os.getenv('YOUTUBE_CLIENT_ID'),
            client_secret=os.getenv('YOUTUBE_CLIENT_SECRET'),
            token_uri=os.getenv('YOUTUBE_TOKEN_URI')
        )

        # Refresh the token if it's expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build('youtube', 'v3', credentials=creds)

    @staticmethod             # WILL PROMPT YOU TO LOG INTO YOUR ACCOUNT TO GET TOKENS. SHOULD BE USED ONLY ONCE
    def get_tokens():
        SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

        flow = InstalledAppFlow.from_client_config({
            "installed": {
                "client_id": os.getenv('YOUTUBE_CLIENT_ID'),
                "client_secret": os.getenv('YOUTUBE_CLIENT_SECRET'),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": os.getenv('YOUTUBE_TOKEN_URI'),
                "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
            }
        }, SCOPES)

        # Launch the OAuth flow and get credentials
        creds = flow.run_local_server(port=0)

        print(f"Access Token: {creds.token}")
        print(f"Refresh Token: {creds.refresh_token}")

    def upload_videos_from_folder(self, folder_path, title, description, tags):
        youtube = self.authenticate_youtube()
        num_uploaded = 0
        for file_name in os.listdir(folder_path):
            if file_name.endswith(('.mp4', '.avi', '.mov', '.mkv')):
                file_path = os.path.join(folder_path, file_name)
                self.upload_video(youtube, file_path, title, description, tags)
                num_uploaded += 1
        return num_uploaded


if __name__ == "__main__":
    uploader = Uploader()
    uploader.get_tokens()
