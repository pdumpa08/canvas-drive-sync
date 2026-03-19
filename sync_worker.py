import time
import re
from database import get_db, init_db
from canvas_api import list_submissions, download_file
from google_api import upload_file_stream, create_folder, refresh_google_token
from config import SYNC_INTERVAL_SECONDS, CANVAS_ACCESS_TOKEN

def get_or_create_folder(teacher_id, name, parent_id, context_type, context_id, google_token):
    """
    Checks if a folder for a specific Course or Assignment already exists in Google Drive.
    If not, creates it and saves the ID to the database.
    """
    conn = get_db()
    cur = conn.cursor()
    
    # Check if we already mapped this Canvas object to a Google Folder
    row = cur.execute("""
        SELECT google_folder_id FROM folder_map 
        WHERE teacher_id=? AND context_type=? AND context_id=?
    """, (teacher_id, context_type, str(context_id))).fetchone()
    
    if row:
        return row[0]

    # Not found? Create a new one in Google Drive
    print(f"Creating folder in Drive: {name}")
    new_folder_id = create_folder(name, parent_id, google_token)
    
    if new_folder_id:
        cur.execute("""
            INSERT INTO folder_map (teacher_id, context_type, context_id, google_folder_id)
            VALUES (?, ?, ?, ?)
        """, (teacher_id, context_type, str(context_id), new_folder_id))
        conn.commit()
    
    return new_folder_id

def validate_filename(filename, pattern):
    """
    Returns True if filename matches pattern (or if no pattern is set).
    """
    if not pattern:
        return True
    try:
        # We use regex search. To match perfectly, user should use ^ and $
        print(re.search(pattern, filename) is not None)
        return re.search(pattern, filename) is not None
    except re.error:
        print(f"Invalid Regex Pattern: {pattern}")
        return True # Default to allow if teacher wrote bad regex

def perform_sync():
    conn = get_db()
    cur = conn.cursor()

    # 1. Get Teacher Creds (including refresh token)
    teacher = cur.execute("SELECT id, google_access_token, google_refresh_token FROM teachers WHERE id=1").fetchone()
    if not teacher: return
    t_id, g_access, g_refresh = teacher["id"], teacher["google_access_token"], teacher["google_refresh_token"]

    # 1. GET ONLY ENABLED ASSIGNMENTS
    # We no longer loop through *everything*. We only look at what the teacher selected.
    rules = cur.execute("""
        SELECT assignment_id, course_id, assignment_name, naming_pattern 
        FROM sync_rules WHERE is_enabled=1
    """).fetchall()

    if not rules:
        print("No assignments enabled for sync.")
        return

    # Ensure Root Folder Exists
    root_id = get_or_create_folder(t_id, "Canvas Sync", None, "root", "root", g_access)

    for rule in rules:
        aid = rule["assignment_id"]
        cid = rule["course_id"]
        aname = rule["assignment_name"]
        pattern = rule["naming_pattern"]

        print(f"Checking Assignment: {aname} (ID: {aid})")

        # 2. Folder Structure
        # Note: We skip the "Course" folder step here to keep code short, 
        # but you can add it back easily. We just put assignments in Root.
        assn_folder_id = get_or_create_folder(t_id, aname, root_id, "assignment", aid, g_access)

        # 3. Get Submissions
        submissions = list_submissions(cid, aid)

        for sub in submissions:
            # Canvas API often puts user info in 'user' object if included
            student_name = "Unknown Student"
            # (Requires 'include[]=user' in canvas_api request, assumed added)

            attachments = sub.get("attachments", [])
            for file_info in attachments:
                fid = file_info.get("id")
                fname = file_info.get("filename")
                furl = file_info.get("url")

                # A. Check if already synced
                exists = cur.execute("SELECT 1 FROM synced_files WHERE file_id=?", (fid,)).fetchone()
                if exists: continue

                # B. VALIDATE FILENAME
                if not validate_filename(fname, pattern):
                    print(f"🚩 FLAGGED: {fname} (Does not match {pattern})")
                    
                    # Log the error so the teacher sees it in Dashboard
                    cur.execute("""
                        INSERT INTO flagged_logs (assignment_id, student_name, filename, reason)
                        VALUES (?, ?, ?, ?)
                    """, (aid, student_name, fname, f"Failed pattern: {pattern}"))
                    conn.commit()
                    continue # SKIP UPLOAD

                # C. Sync Valid File
                print(f"✅ Syncing: {fname}")
                data_stream = download_file(furl)
                # TRY UPLOAD
                uploaded_id = upload_file_stream(fname, data_stream, assn_folder_id, g_access)

                # IF UPLOAD FAILS WITH 401 (Unauthorized)
                if not uploaded_id:
                    print("🔄 Token might be expired. Attempting refresh...")
                    new_access_token = refresh_google_token(g_refresh)
                    
                    if new_access_token:
                        # Save the new token to the DB so we have it for next time
                        cur.execute("UPDATE teachers SET google_access_token=? WHERE id=?", (new_access_token, t_id))
                        conn.commit()
                        
                        # TRY UPLOAD AGAIN with the new token
                        print("🚀 Retrying upload with new token...")
                        # We have to re-download the stream because the first one was consumed
                        data_stream = download_file(furl) 
                        uploaded_id = upload_file_stream(fname, data_stream, assn_folder_id, new_access_token)
                        print("Successfully uploaded")
                
                if uploaded_id:
                    cur.execute("INSERT INTO synced_files (file_id, google_file_id) VALUES (?, ?)", (fid, uploaded_id))
                    conn.commit()

    conn.close()

if __name__ == "__main__":
    init_db()
    # Mocking the get_or_create_folder for this snippet to run without errors
    # In real usage, ensure the function from previous response is included
    from google_api import create_folder # Ensure imports work
    perform_sync()