import os
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Phạm vi quyền truy cập cần thiết cho API
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

def upload_video(video_path, title):
    # Đọc các token đã lưu nếu có
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Nếu chưa có hoặc hết hạn, yêu cầu người dùng đăng nhập
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Lưu token cho các lần truy cập sau
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    # Khởi tạo YouTube API client
    youtube = build('youtube', 'v3', credentials=creds)

    # Tạo dữ liệu cho video
    request_body = {
        'snippet': {
            'title': title + ' | #Shorts',  # Thêm từ khóa "Shorts"
            'description': (
                'A quick compilation of the funniest and most intriguing AskReddit questions and answers. '
                'Enjoy these Reddit Shorts! #Shorts'
            ),  # Mô tả ngắn gọn với từ khóa #Shorts
            'tags': ['AskReddit', 'Reddit Stories', 'Shorts', 'Reddit Shorts', 'Best of Reddit', 'Funny'],
            'categoryId': '24'  # Entertainment
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    }


    # Tải video lên
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part='snippet,status',
        body=request_body,
        media_body=media
    )

    response = request.execute()
    print(f'Video đã được tải lên với ID: {response["id"]}')

if __name__ == '__main__':
    upload_video()
