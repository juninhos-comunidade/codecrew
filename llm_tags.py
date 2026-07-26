import requests
import json
from craw_gupy import fetch_gupy_job, clean_job_data

OLLAMA = "http://localhost:11434/v1/chat/completions"
MODEL = "qwen2.5:3b"

TAGS = ["array", "string", "hash-table", "two-pointers", "sliding-window", "prefix-sum" ,
"sorting", "binary-search", "recursion", "math", "greedy", "counting",
"stack", "queue", "linked-list", "tree", "binary-tree", "graph", "heap-priority-queue", "matrix",
"dynamic-programming", "backtracking", "depth-first-search", "breadth-first-search",
"bit-manipulation", "design", "trie", "union-find",
"database", "concurrency", "simulation", "string-matching"]

SCHEMA = {
    "type": "object",
    "properties": {
        "tags": {
            "type": "array",
            "minItems": 2,
            "maxItems": 3,
            "items": {"type": "string", "enum": TAGS}
        },
        "difficulty": {"type": "string", "enum": ["Easy", "Medium", "Hard"]},
    },
    "required": ["tags", "difficulty"],
    "additionalProperties": False
}

PROMPT = """
Você analisa uma vaga de tecnologia e decide quais tópicos de algoritmos e
estruturas de dados provavelmente apareceriam na entrevista técnica dela.

Não procure as tecnologias citadas na vaga (frameworks, bancos, ferramentas) —
elas não estão na lista de tópicos. Pense no tipo de problema que a pessoa
resolve no dia a dia e traduza isso para os tópicos disponíveis.

Exemplo: backend com muita manipulação de dados e otimização de consultas
sugere hash-table, string e array. Não sugere "django" nem "postgresql".

Escolha de 3 a 5 tópicos, e a dificuldade adequada à senioridade da vaga.

VAGA
título: {titulo}
pré-requisitos: {pre_requisitos}
responsabilidades: {responsabilidades}
"""

url = input("Enter the Gupy job URL: ")


job = clean_job_data(fetch_gupy_job(url))

def set_difficulty(titulo: str, sugest: str) -> str:
    t = titulo.lower()
    if any (p in t for p in ("junior", "jr", "estagiario", "intern", "estagio")):
        return "Easy"
    if any (p in t for p in ("senior", "sr", "especialista", "specialist", "lead")):
        return "Hard"
    return sugest

def llm_question(prompt:str, schema: dict) -> dict:
    r = requests.post(OLLAMA, timeout=300, json={
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": "tags_vaga", "schema": schema, "strict": True},
        },
        "temperature": 0,
    })
    r.raise_for_status()
    return json.loads(r.json()["choices"][0]["message"]["content"])

response = llm_question(PROMPT.format(**job), SCHEMA)
response["tags"] = list(dict.fromkeys(response["tags"]))
difficulty = set_difficulty(job['titulo'], response["difficulty"])

print(response["tags"], difficulty)

