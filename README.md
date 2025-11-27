# 🎬 Instagram Reel Automation

An automated Instagram Reel posting system that schedules and publishes video content from Google Drive to Instagram using GitHub Actions. Perfect for content creators, marketers, and social media managers who want to maintain a consistent posting schedule without manual intervention.

## ✨ Features

- 🤖 **Automated Posting**: Schedule Instagram Reels to post automatically at specific times
- ☁️ **Google Drive Integration**: Store and manage your video content in Google Drive
- 📅 **GitHub Actions Workflow**: Runs on GitHub's infrastructure - no server needed
- 📝 **CSV-Based Management**: Easy-to-manage posting queue with captions
- 🔄 **Auto-Update**: Automatically updates the CSV file after each post
- 🎯 **Retry Logic**: Built-in retry mechanism for handling Instagram API delays
- 🔐 **Secure**: Uses environment variables and GitHub Secrets for sensitive data

## 📋 Prerequisites

Before you begin, ensure you have:

1. **Instagram Business/Creator Account** connected to a Facebook Page
2. **Facebook Developer Account** with an app created
3. **Google Cloud Project** with Drive API enabled
4. **Google Service Account** with access to your Drive folder
5. **GitHub Account** for hosting and running the automation

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/krish070904/ig-reel-automation.git
cd ig-reel-automation
```

### 2. Set Up Google Drive

1. Create a folder in Google Drive for your video content
2. Create a Google Cloud Project and enable the Google Drive API
3. Create a Service Account and download the credentials JSON file
4. Share your Google Drive folder with the service account email
5. Note your Drive folder ID (from the folder URL)

### 3. Set Up Instagram API Access

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app or use an existing one
3. Add Instagram Graph API to your app
4. Get your Instagram Business Account ID
5. Generate a long-lived access token

### 4. Configure GitHub Secrets

Go to your repository's Settings → Secrets and variables → Actions, and add:

| Secret Name | Description |
|------------|-------------|
| `GOOGLE_DRIVE_CREDENTIALS_BASE64` | Base64-encoded Google Service Account JSON |
| `INSTAGRAM_USER_ID` | Your Instagram Business Account ID |
| `ACCESS_TOKEN` | Instagram Graph API Access Token |
| `DRIVE_FOLDER_ID` | Google Drive folder ID containing videos |

**To encode your credentials:**
```bash
# On Linux/Mac
base64 -i credentials.json

# On Windows (PowerShell)
[Convert]::ToBase64String([IO.File]::ReadAllBytes("credentials.json"))
```

### 5. Prepare Your Content

1. Upload your video files to the Google Drive folder
2. Update `posts.csv` with your posting schedule:

```csv
filename,caption
video1.mp4,Check out this amazing content! #instagram #reels
video2.mp4,Another great video coming your way! #viral
```

### 6. Configure Posting Schedule

Edit `.github/workflows/automation.yml` to set your desired posting time:

```yaml
on:
  schedule:
    # Cron format: minute hour day month weekday (UTC time)
    - cron: '30 23 * * *'  # Posts at 11:30 PM UTC daily
```

**Common Schedules:**
- Daily at 9 AM UTC: `'0 9 * * *'`
- Every 6 hours: `'0 */6 * * *'`
- Weekdays at noon UTC: `'0 12 * * 1-5'`

## 📁 Project Structure

```
ig-reel-automation/
├── .github/
│   └── workflows/
│       └── automation.yml      # GitHub Actions workflow
├── auto_post.py               # Main automation script
├── posts.csv                  # Posting queue with captions
├── metadata.json              # Sample metadata file
└── README.md                  # This file
```

## 🔧 How It Works

1. **Scheduled Trigger**: GitHub Actions runs at the specified cron schedule
2. **Fetch Video**: Script downloads the next video from Google Drive
3. **Create Media Container**: Uploads video to Instagram via Graph API
4. **Publish Reel**: Publishes the reel with the specified caption
5. **Update Queue**: Removes the posted entry from `posts.csv`
6. **Commit Changes**: Pushes updated CSV back to the repository

## 📊 CSV Format

The `posts.csv` file should follow this format:

```csv
filename,caption
video_name.mp4,Your caption here with #hashtags
another_video.mp4,Another amazing post! #content #creator
```

- **filename**: Must match the exact filename in Google Drive
- **caption**: Your post caption (supports emojis and hashtags)

## 🛠️ Manual Testing

You can manually trigger the workflow:

1. Go to the **Actions** tab in your GitHub repository
2. Select **Instagram Reel Automation**
3. Click **Run workflow**
4. Choose the branch and click **Run workflow**

## 🐛 Troubleshooting

### Common Issues

**1. "File not found in Drive"**
- Ensure the filename in CSV matches exactly (case-sensitive)
- Verify the service account has access to the folder

**2. "Error creating media container"**
- Check your access token is valid and not expired
- Ensure your Instagram account is a Business/Creator account
- Verify the video meets Instagram's requirements (aspect ratio, duration, size)

**3. "Media not ready" errors**
- The script includes retry logic for this
- Large videos may take longer to process
- If it persists, check video format and size

**4. Workflow not running**
- Verify GitHub Actions is enabled in repository settings
- Check the cron schedule syntax
- Ensure secrets are properly configured

### Instagram Video Requirements

- **Format**: MP4 or MOV
- **Duration**: 3-90 seconds for Reels
- **Aspect Ratio**: 9:16 (vertical) recommended
- **Resolution**: Minimum 540x960 pixels
- **File Size**: Maximum 1GB

## 🔐 Security Best Practices

- ✅ Never commit credentials directly to the repository
- ✅ Use GitHub Secrets for all sensitive information
- ✅ Regularly rotate your access tokens
- ✅ Use service accounts with minimal required permissions
- ✅ Enable 2FA on your GitHub account

## 📝 Local Development

To run the script locally:

```bash
# Install dependencies
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib schedule requests

# Set environment variables
export INSTAGRAM_USER_ID="your_instagram_id"
export ACCESS_TOKEN="your_access_token"
export DRIVE_FOLDER_ID="your_drive_folder_id"
export GOOGLE_DRIVE_CREDENTIALS_BASE64="your_base64_credentials"

# Run the script
python auto_post.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Acknowledgments

- Instagram Graph API Documentation
- Google Drive API Documentation
- GitHub Actions Documentation

## 📧 Contact

For questions or support, please open an issue in the GitHub repository.

---

**⭐ If you find this project helpful, please consider giving it a star!**
