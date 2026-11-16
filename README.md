# Canvas Drive Sync

A command-line tool that syncs assignment submissions from Canvas LMS to Google Drive, automatically collecting and organizing files for a class.

Built so instructors can automatically collect, rename, and organize every student submission into Google Drive instead of downloading them by hand.

## How it works
- **Canvas REST API** (token auth): lists courses, assignments, and submissions
- **Regex naming rules**: rename files; files that don't match get flagged for review
- **Google Drive API** (OAuth 2.0): uploads into per-assignment folders
- **SQLite**: tracks what's already synced so each run only uploads new files

## Features
- Syncs Canvas assignments and student submissions to Google Drive
- Custom naming rules for assignment files (regex)
- CLI wizard for assignment setup and management
- View flagged files and active sync rules
- Run sync worker in a loop

---

## Quick Start

### 1. Clone the Repository
```
git clone https://github.com/pdumpa08/canvas-drive-sync.git
cd canvas-drive-sync
```

### 2. Install Dependencies
```
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root with the following:
```
CANVAS_BASE_URL=<your_canvas_url>
CANVAS_ACCESS_TOKEN=<your_canvas_access_token>
GOOGLE_CLIENT_ID=<your_google_client_id>
GOOGLE_CLIENT_SECRET=<your_google_client_secret>
GOOGLE_REDIRECT_URI=<your_google_redirect_uri>
SYNC_INTERVAL_SECONDS=60
DB_PATH=sync.db
```
- Get your Canvas API token from your Canvas account settings.
- Set up a Google Cloud project for Drive API and OAuth credentials.

### 4. Initialize the Database
The database is auto-initialized on first run.

### 5. Run the CLI Tool
```
python main.py
```

### 6. CLI Menu Options
- Configure new assignment to sync
- View active assignments
- View flagged files (bad names)
- Start sync loop (runs continuously)

---

## Troubleshooting
- Ensure your Canvas and Google credentials are correct.
- Check flagged files for naming issues.
- For Google Drive API issues, verify OAuth setup and token refresh.

---

## For Your Own Class
- Update `.env` with your Canvas and Google credentials.
- Configure assignments using the CLI wizard.
- Set naming rules as needed.
- Run the sync worker to collect and organize student submissions in Google Drive.

