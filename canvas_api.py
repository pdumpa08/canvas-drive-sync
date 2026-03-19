# canvas_api.py
import requests
from config import CANVAS_BASE_URL, CANVAS_ACCESS_TOKEN

def canvas_api_get_paginated(path):
    """
    Loops through all pages of results using the hardcoded ACCESS_TOKEN
    """
    url = f"{CANVAS_BASE_URL}{path}"
    results = []
    
    while url:
        resp = requests.get(url, headers={"Authorization": f"Bearer {CANVAS_ACCESS_TOKEN}"})
        if resp.status_code != 200:
            print(f"Canvas API Error ({url}):", resp.text)
            break
            
        data = resp.json()
        if isinstance(data, list):
            results.extend(data)
        else:
            return data 
            
        links = resp.links
        if 'next' in links:
            url = links['next']['url']
        else:
            url = None
            
    return results

def list_courses():
    return canvas_api_get_paginated("/api/v1/courses?enrollment_type=teacher&state[]=available")

def list_assignments(course_id):
    return canvas_api_get_paginated(f"/api/v1/courses/{course_id}/assignments")

def list_submissions(course_id, assignment_id):
    return canvas_api_get_paginated(
        f"/api/v1/courses/{course_id}/assignments/{assignment_id}/submissions?include[]=submission_history"
    )

def download_file(file_url):
    return requests.get(file_url, stream=True)