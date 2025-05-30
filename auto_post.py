import os
import base64
import csv
import time
import schedule
import requests
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# === Step A: Set up Google Drive Credentials ===
# If a Base64 encoded secret is provided, decode it and write credentials.json
credentials_base64 = os.environ.get("GOOGLE_DRIVE_CREDENTIALS_BASE64")
SERVICE_ACCOUNT_FILE = "credentials.json"
if credentials_base64:
    with open(SERVICE_ACCOUNT_FILE, "wb") as f:
        f.write(base64.b64decode(credentials_base64))

# === Step B: Read Configuration from Environment Variables ===
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")
CSV_FILE = "posts.csv"
DOWNLOAD_DIR = "downloads"  # Local directory to temporarily download videos

DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']

# === Step C: Set up Google Drive API Client ===
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=DRIVE_SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def list_files_in_folder(folder_id):
    """List video files in the specified Google Drive folder."""
    query = f"'{folder_id}' in parents and mimeType contains 'video/'"
    results = drive_service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def download_file(file_id, destination):
    """Download a file from Google Drive to a local destination."""
    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO(destination, 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}% complete.")
    fh.close()

def get_public_url(drive_file_id):
    """
    Generate a public download URL for a Google Drive file.
    Note: Your file must be shared publicly.
    """
    return f"https://drive.google.com/uc?export=download&id={drive_file_id}"

# === Step D: Instagram Graph API Function ===
def post_instagram_reel(video_url, caption):
    """Post a reel to Instagram using the Graph API, with polling until the media is ready."""
    create_url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media"
    params = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN,
        "share_to_feed": "true"
    }
    response = requests.post(create_url, params=params)
    data = response.json()
    print("Create media response:", data)
    if "id" not in data:
        print("Error creating media container:", data)
        return None
    creation_id = data["id"]
    time.sleep(2)
    
    publish_url = f"https://graph.facebook.com/v17.0/{INSTAGRAM_USER_ID}/media_publish"
    publish_params = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    max_retries = 10
    retry_delay = 10  # seconds
    for attempt in range(max_retries):
        publish_response = requests.post(publish_url, params=publish_params)
        publish_data = publish_response.json()
        print(f"Publish attempt {attempt + 1}: {publish_data}")
        if "id" in publish_data:
            return publish_data
        error = publish_data.get("error", {})
        if error.get("code") == 9007 and error.get("error_subcode") == 2207027:
            print("Media not ready, waiting before retrying...")
            time.sleep(retry_delay)
        else:
            print("Unexpected error during publish:", publish_data)
            break
    return publish_data

# === Step E: CSV Handling Functions ===
def load_posts(csv_file):
    """Load the CSV file containing posts (columns: filename, caption)."""
    posts = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
    return posts

def save_posts(csv_file, posts):
    """Save the updated list of posts back to the CSV."""
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        if posts:
            fieldnames = posts[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in posts:
                writer.writerow(row)

# === Step F: Main Posting Function ===
def process_next_post():
    posts = load_posts(CSV_FILE)
    if not posts:
        print("No posts left in the CSV.")
        return
    post = posts[0]
    filename = post['filename']
    caption = post['caption']
    drive_files = list_files_in_folder(DRIVE_FOLDER_ID)
    file_entry = next((f for f in drive_files if f['name'] == filename), None)
    if not file_entry:
        print(f"File {filename} not found in Drive.")
        return
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    local_path = os.path.join(DOWNLOAD_DIR, filename)
    print(f"Downloading {filename}...")
    download_file(file_entry['id'], local_path)
    public_url = get_public_url(file_entry['id'])
    print(f"Public URL for {filename}: {public_url}")
    result = post_instagram_reel(public_url, caption)
    if result and "id" in result:
        print("Reel posted successfully!")
        posts.pop(0)
        save_posts(CSV_FILE, posts)
    else:
        print("Failed to post reel.")

# === Step G: Scheduling the Script ===
# For local testing, we use schedule to run at a set time. (For example, every day at 06:00 UTC.)
#schedule.every().day.at("01:37").do(process_next_post)

print("Running process_next_post() now...")
process_next_post()
#print("Automation started. Waiting for scheduled time (06:00 daily)...")
#while True:
 #   schedule.run_pending()
  #  time.sleep(60)

   # print("Current time:", time.strftime("%H:%M"))

##UNDO THvfsfw
