import requests
import json
import re
from bs4 import BeautifulSoup

# Limpa os dados do job e ja retorna o que vamos alimentar a LLM
def clean_html(html):
    return BeautifulSoup(html, "html.parser").get_text("\n")

def clean_job_data(job: dict) -> dict:
    return {
        "titulo": job.get("name"),
        "pre_requisitos": clean_html(job.get("prerequisites")),
        "responsabilidades": clean_html(job.get("responsibilities")),
    }

# Coleta os dados de uma URL da Gupy e retorna um dict com os dados
def fetch_gupy_job(url: str) -> dict:
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text
    match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html_content, re.DOTALL)
    if match:
        json_data = json.loads(match.group(1))
        job = json_data['props']['pageProps']['job']
        return job
    else:
        raise ValueError("Data not found in the HTML content")

# Executa a pipe de coleta e limpeza
if __name__ == "__main__":
    url =  input("Enter the Gupy job URL: ")
    job_data = fetch_gupy_job(url)
    cleaned_data = clean_job_data(job_data)
    print(json.dumps(cleaned_data, indent=2, ensure_ascii=False))