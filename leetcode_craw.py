import os, time, requests, json
from dotenv import load_dotenv
from markdownify import markdownify
from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData
from sqlalchemy.dialects.postgresql import ARRAY, insert

load_dotenv()
# Configuração do banco de dados
engine = create_engine(os.getenv("DATABASE_URL"))
metadata = MetaData()
questions = Table('questions', metadata,
    Column('id', String, primary_key=True),
    Column('slug', String, unique=True),
    Column('title', String),
    Column('difficulty', String),
    Column('tags', ARRAY(String)),
    Column('content_md', String)
)
metadata.create_all(engine)

LEETCODE = "https://leetcode.com"
HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/json',
        'Referer': LEETCODE,
    }

def fetch_leetcode(query: str, variables: dict) -> dict | None:
    HEADERS
    response = requests.post(
        f"{LEETCODE}/graphql",
        json={'query': query, 'variables': variables},
        headers=HEADERS
    )
    time.sleep(0.2)
    if response.status_code == 200:
        return response.json()
    print("HTTP", response.status_code, response.text[:500])
    return None

# Lista questoes por filtro
list_query="""
query problemList($filters: QuestionListFilterInput, $limit: Int, $skip: Int) {
    problemsetQuestionList: questionList(
        categorySlug: ""
        filters: $filters
        limit: $limit
        skip: $skip
    ) {
        total: totalNum
        questions: data {
            title
            titleSlug
            difficulty
            isPaidOnly
        }
    }
}
"""

# Busca questao por titleSlug
question_query = """
query getQuestion($titleSlug: String!) {
    question(titleSlug: $titleSlug) {
        questionId
        title
        difficulty
        content
        topicTags { slug }
    }
}
"""

todas = []
skip = 0
total = None

while total is None or skip < total:
    list_result = fetch_leetcode(list_query, {
        "filters": {},
        "limit": 100,
        "skip": skip,
    })

    if list_result is None:
        print("falha na pagina", skip)
        break

    bloc = list_result['data']['problemsetQuestionList']
    total = bloc['total']
    todas.extend(bloc['questions'])
    skip += 100

free = [q for q in todas if not q['isPaidOnly']]
slugs = [q['titleSlug'] for q in free]

for slug in slugs:
    q_result = fetch_leetcode(question_query, {"titleSlug": slug})
    
    if q_result is None:
        print("falha na questao", slug)
        continue

    question = q_result['data']['question']

    if question is None:
        print("pulando (sem question):", slug)
        continue
    
    if question['content'] is None:  
        print("pulando (sem content):", slug)
        continue
    
    question['content'] = markdownify(question['content'])
    
    registro = {
    "id": question['questionId'],
    "slug": slug,
    "title": question['title'],
    "difficulty": question['difficulty'],
    "tags": [t['slug'] for t in question['topicTags']],
    "content_md": question['content']
}
    stmt = insert(questions).values(**registro).on_conflict_do_nothing(index_elements=['id'])
    with engine.begin() as conn:
        conn.execute(stmt)
    print("inserido:", slug)