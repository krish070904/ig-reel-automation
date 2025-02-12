import csv
import os
import time
import schedule
import requests
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# ===== CONFIGURATION =====
# Instagram API details (obtain these from your Facebook Developer App)
INSTAGRAM_USER_ID = os.environ.get("INSTAGRAM_USER_ID")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# Google Drive settings
SERVICE_ACCOUNT_FILE = 'credentials.json'
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
DRIVE_FOLDER_ID = os.environ.get("DRIVE_FOLDER_ID")

  # from your Google Drive folder URL

# CSV file mapping filenames to captions
CSV_FILE = "posts.csv"
DOWNLOAD_DIR = "downloads"  # Local directory to download videos temporarily

# ===== SET UP GOOGLE DRIVE API CLIENT =====
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=DRIVE_SCOPES)
drive_service = build('drive', 'v3', credentials=credentials)

def list_files_in_folder(folder_id):
    """List files (videos) in the specified Google Drive folder."""
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
    Convert a Google Drive share link to a direct public URL.
    This function is highly dependent on your Drive settings.
    For example, if your file is shared publicly, you can use:
    https://drive.google.com/uc?export=download&id={drive_file_id}
    """
    return f"https://drive.google.com/uc?export=download&id={drive_file_id}"

# ===== INSTAGRAM GRAPH API FUNCTION =====
def post_instagram_reel(video_url, caption):
    """Post a reel to Instagram using the Graph API with polling until media is ready."""
    # Step 1: Create a media container
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
    
    # Step 2: Polling loop to publish once the media is ready
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
        # If the publish response returns an "id", then it is successful.
        if "id" in publish_data:
            return publish_data
        # Check if the error indicates the media is not yet ready.
        error = publish_data.get("error", {})
        if (error.get("code") == 9007 and
            error.get("error_subcode") == 2207027):
            print("Media not ready, waiting before retrying...")
            time.sleep(retry_delay)
        else:
            # If it's another error, break out of the loop.
            print("Unexpected error during publish:", publish_data)
            break
    return publish_data

# ===== PROCESS THE CSV FILE =====
def load_posts(csv_file):
    """Load the CSV file containing posts to be made."""
    posts = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            posts.append(row)
    return posts

def save_posts(csv_file, posts):
    """Save the updated posts list back to CSV."""
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        fieldnames = posts[0].keys() if posts else []
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in posts:
            writer.writerow(row)

# ===== MAIN POSTING FUNCTION =====
def process_next_post():
    posts = load_posts(CSV_FILE)
    if not posts:
        print("No posts left in the CSV.")
        return
    # Assume the CSV is in order; pick the first post
    post = posts[0]
    filename = post['filename']
    caption = post['caption']
    # Find the file in Drive (you may match by filename)
    drive_files = list_files_in_folder(DRIVE_FOLDER_ID)
    file_entry = next((f for f in drive_files if f['name'] == filename), None)
    if not file_entry:
        print(f"File {filename} not found in Drive.")
        return
    # Download the file locally
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    local_path = os.path.join(DOWNLOAD_DIR, filename)
    print(f"Downloading {filename}...")
    download_file(file_entry['id'], local_path)
    # Get a public URL for the video (this may require your file to be publicly shared)
    public_url = get_public_url(file_entry['id'])
    print(f"Public URL for {filename}: {public_url}")
    # Post the reel to Instagram
    result = post_instagram_reel(public_url, caption)
    if result:
        print("Reel posted successfully!")
        # Remove the post from the CSV so it isn’t posted again
        posts.pop(0)
        save_posts(CSV_FILE, posts)
    else:
        print("Failed to post reel.")

# ===== SCHEDULING =====
# Using the schedule library to run the process every day at 6:00 AM
schedule.every().day.at("23:10").do(process_next_post)

print("Automation started. Waiting for scheduled time (17:57 AM daily)...")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
