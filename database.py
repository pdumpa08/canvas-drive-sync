import sqlite3
from config import DB_PATH

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # --- Existing Tables ---
    cur.execute("""
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            google_access_token TEXT,
            google_refresh_token TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS folder_map (
            teacher_id INTEGER,
            context_type TEXT, 
            context_id TEXT,   
            google_folder_id TEXT,
            PRIMARY KEY (teacher_id, context_type, context_id)
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS synced_files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER UNIQUE,
            google_file_id TEXT
        )
    """)

    # --- NEW TABLES ---

    # Stores which assignments to sync and their naming rules
    cur.execute("""
        CREATE TABLE IF NOT EXISTS sync_rules (
            assignment_id INTEGER PRIMARY KEY,
            course_id INTEGER,
            assignment_name TEXT,
            is_enabled BOOLEAN DEFAULT 0,
            naming_pattern TEXT -- e.g., '^[A-Za-z]+_[0-9]+$' (Regex)
        )
    """)

    # Stores files that failed the naming check
    cur.execute("""
        CREATE TABLE IF NOT EXISTS flagged_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assignment_id INTEGER,
            student_name TEXT,
            filename TEXT,
            reason TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()