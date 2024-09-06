import os

import aiohttp
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


load_dotenv()


class Uploader:

    def __init__(self, creds: list, ROOT_DIR):
        self.ROOT_DIR = ROOT_DIR
        self.token,\
        self.refresh_token,\
        self.client_id,\
        self.client_secret,\
        self.token_uri = creds

    @staticmethod
    def upload_video(youtube, file_path, title, tags, category="24", privacy_status="public"):
        try:
            body = {
                "snippet": {
                    "title": title,
                    "description": "",
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


    def authenticate_youtube(self):
        creds = Credentials(
            token=self.token,
            refresh_token=self.refresh_token,
            client_id=self.client_id,
            client_secret=self.client_secret,
            token_uri=self.token_uri
        )

        # Refresh the token if it's expired
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build('youtube', 'v3', credentials=creds)


    async def upload_videos_from_folder(self, folder_path, tags):
        upload_url = 'https://www.googleapis.com/upload/youtube/v3/videos?uploadType=resumable'
        async with aiohttp.ClientSession() as session:
            youtube = self.authenticate_youtube()
            num_uploaded = 0
            for file_name in os.listdir(os.path.join(self.ROOT_DIR, folder_path)):
                if file_name.endswith('.mp4'):
                    file_path = os.path.join(self.ROOT_DIR, folder_path, file_name)
                    title = file_name.replace("_", " ").strip(".mp4")
                    self.upload_video(youtube, file_path, title, tags)
                    num_uploaded += 1
            await session.post(upload_url, data={})
        return num_uploaded



def get_tokens(client_id, client_secret, token_uri):          # WILL PROMPT YOU TO LOG INTO YOUR ACCOUNT TO GET TOKENS. SHOULD BE USED ONLY ONCE
    SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

    flow = InstalledAppFlow.from_client_config({
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": token_uri,
            "redirect_uris": ["urn:ietf:wg:oauth:2.0:oob", "http://localhost"]
        }
    }, SCOPES)

    # Launch the OAuth flow and get credentials
    creds = flow.run_local_server(port=0)

    print(f"Access Token: {creds.token}")
    print(f"Refresh Token: {creds.refresh_token}")


if __name__ == "__main__":
    clientid = input("client id\n")
    clientsecret = input("client secret\n")
    tokenuri = input("token uri\n")

    get_tokens(clientid, clientsecret, tokenuri)
