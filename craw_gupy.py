import requests
import json
import re

def fetch_gupy_job(url: str) -> dict:
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html_content, re.DOTALL)
    if match:
        json_data = json.loads(match.group(1))
        job = json_data['props']['pageProps']['job']
        return job
    else:
        raise ValueError("Data not found in the HTML content")

if __name__ == "__main__":
    url =  input("Enter the Gupy job URL: ")
    job_data = fetch_gupy_job(url)
    print(json.dumps(job_data, indent=2, ensure_ascii=False))