import time
import sys
from database import get_db, init_db
from canvas_api import list_courses, list_assignments
from sync_worker import perform_sync
from config import SYNC_INTERVAL_SECONDS

def print_header():
    print("\n" + "="*40)
    print("      CANVAS <-> DRIVE SYNC MANAGER      ")
    print("="*40)

def configure_new_assignment():
    """Interactive wizard to add an assignment to the sync list."""
    print("\nConnecting to Canvas...")
    try:
        courses = list_courses()
    except Exception as e:
        print(f"Error: {e}")
        return

    # --- Step 1: Pick a Course ---
    print("\n[ SELECT A COURSE ]")
    for i, c in enumerate(courses):
        print(f"{i+1}. {c.get('name', 'Unnamed')} (ID: {c['id']})")
    print("0. Back to Main Menu")

    try:
        choice = int(input("\nEnter number: "))
        if choice == 0: return
        selected_course = courses[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # --- Step 2: Pick an Assignment ---
    print(f"\nFetching assignments for '{selected_course['name']}'...")
    assignments = list_assignments(selected_course['id'])
    
    if not assignments:
        print("No assignments found in this course.")
        return

    print("\n[ SELECT AN ASSIGNMENT ]")
    for i, a in enumerate(assignments):
        print(f"{i+1}. {a.get('name', 'Unnamed')} (ID: {a['id']})")
    
    try:
        choice = int(input("\nEnter number: "))
        selected_assn = assignments[choice - 1]
    except (ValueError, IndexError):
        print("Invalid selection.")
        return

    # --- Step 3: Set Naming Rule (Regex) ---
    print("\n[ NAMING FORMAT ]")
    print("Enter a Regex pattern to enforce naming (or press Enter to skip).")
    print("Examples:")
    print("  ^Lab1_.* (Must start with 'Lab1_')")
    print("  .*\\.pdf$     (Must be a PDF)")
    print("  ^...._....$   (Two 4-letter words separated by underscore)")
    
    pattern = input("Pattern > ").strip()
    if not pattern:
        pattern = None
        print("No pattern set. All files will be synced.")

    # --- Step 4: Save to Database ---
    conn = get_db()
    conn.execute("""
        INSERT OR REPLACE INTO sync_rules 
        (assignment_id, course_id, assignment_name, is_enabled, naming_pattern)
        VALUES (?, ?, ?, 1, ?)
    """, (selected_assn['id'], selected_course['id'], selected_assn['name'], pattern))
    conn.commit()
    conn.close()
    
    print(f"\nSUCCESS: '{selected_assn['name']}' is now enabled!")

def view_active_rules():
    conn = get_db()
    rules = conn.execute("SELECT * FROM sync_rules WHERE is_enabled=1").fetchall()
    conn.close()

    print("\n[ ACTIVE SYNC RULES ]")
    if not rules:
        print("Checking... No assignments are currently configured.")
    else:
        for r in rules:
            pat = r['naming_pattern'] if r['naming_pattern'] else "(No Filter)"
            print(f"• {r['assignment_name']} [Rule: {pat}]")

def view_flagged_files():
    conn = get_db()
    # Assuming flagged_logs table exists from previous steps
    flags = conn.execute("SELECT * FROM flagged_logs ORDER BY timestamp DESC LIMIT 10").fetchall()
    conn.close()

    print("\n[ RECENT FLAGGED FILES (won't sync) ]")
    if not flags:
        print("No files flagged recently.")
    else:
        for f in flags:
            print(f"🚩 {f['filename']} (Student: {f['student_name']}) -> {f['reason']}")

def start_background_loop():
    print("\n🚀 Starting Sync Worker (Press Ctrl+C to stop)")
    print(f"   Updating every {SYNC_INTERVAL_SECONDS} seconds...")
    try:
        while True:
            perform_sync() # This imports from your sync_worker.py
            time.sleep(SYNC_INTERVAL_SECONDS)
    except KeyboardInterrupt:
        print("\nSync stopped.")

def main_menu():
    init_db()
    while True:
        print_header()
        print("1. Configure new assignment to sync")
        print("2. View active assignments")
        print("3. 🚩 View flagged files (Bad names)")
        print("4. START SYNC LOOP")
        print("q. Quit")
        
        choice = input("\nSelect option: ").lower()
        
        if choice == '1':
            configure_new_assignment()
        elif choice == '2':
            view_active_rules()
            input("\nPress Enter to continue...")
        elif choice == '3':
            view_flagged_files()
            input("\nPress Enter to continue...")
        elif choice == '4':
            start_background_loop()
        elif choice == 'q':
            sys.exit()
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main_menu()