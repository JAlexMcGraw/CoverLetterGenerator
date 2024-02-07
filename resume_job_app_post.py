import requests
import json

resume_url = "http://127.0.0.1:8000/generate_cover_letter"
header = {
    "accept": "application/json",
}

params = {
    "resume_path": "/Users/alexmcgraw/Documents/Resumes:Cover Letters:Case_stuff/Alex McGraw Resume, December '23, v2.pdf",
    "job_posting": "https://boards.greenhouse.io/snorkelai/jobs/4971098004"
}

response = requests.post(resume_url, headers=header, params=params)

print(response.json())