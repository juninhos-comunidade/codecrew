from llm_tags import job_analysis
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()
# Configuração do banco de dados
engine = create_engine(os.getenv("DATABASE_URL"))

QUERY = text(
    """
    SELECT title, content_md
    FROM questions
    WHERE tags && CAST(:tags as varchar[])
    AND difficulty = :difficulty
    ORDER BY random()
    """
    )

def query_questions(tags: list, difficulty: str) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(QUERY, {
            "tags": tags,
            "difficulty": difficulty
        })
        return [dict(row._mapping) for row in result]
        
if __name__ == "__main__":
    url = input("Enter the Gupy job URL: ")
    tags, difficulty = job_analysis(url)
    result = query_questions(tags, difficulty)
    print(len(result))