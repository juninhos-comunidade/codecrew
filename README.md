# CodeCrew

Preparação personalizada para entrevistas a partir do currículo do candidato e
de uma vaga real.

## Fluxo da V1

1. Coleta e normaliza uma vaga publicada na Gupy.
2. Extrai o texto de um currículo em PDF e o estrutura com IA.
3. Compara currículo e vaga para encontrar pontos fortes e lacunas.
4. Usa o diagnóstico para definir tópicos e dificuldade de programação.
5. Seleciona desafios compatíveis no PostgreSQL.

As interações de IA usam o OpenRouter com o modelo
`deepseek/deepseek-v4-flash` por padrão.

## Requisitos

- Python 3.12+
- PostgreSQL com a tabela `questions` carregada
- Chave de API do OpenRouter

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Preencha o `.env`:

```env
OPENROUTER_API_KEY=coloque_sua_chave_aqui
OPENROUTER_MODEL=deepseek/deepseek-v4-flash
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/codecrew
```

## Carregar o banco de desafios

O coletor do LeetCode é um utilitário independente, usado somente para criar e
popular a tabela `questions`:

```bash
python leetcode_craw.py
```

Ele não faz parte do fluxo executado para cada candidato.

## Executar o fluxo completo

```bash
python preparation_service.py \
  "https://empresa.gupy.io/jobs/123456" \
  --cv "./curriculo.pdf" \
  --limit 10
```

O resultado é um JSON com este formato:

```json
{
  "job": {},
  "candidate": {},
  "match": {
    "aderencia": 75,
    "resumo": "...",
    "pontos_fortes": [],
    "lacunas": [],
    "focos_de_preparacao": []
  },
  "algorithm_profile": {
    "tags": ["array", "hash-table", "string"],
    "difficulty": "Medium"
  },
  "questions": []
}
```

## Módulos

- `craw_gupy.py`: coleta e normalização da vaga.
- `cv_parser.py`: extração e estruturação do currículo.
- `profile_matcher.py`: diagnóstico entre candidato e vaga.
- `llm_tags.py`: perfil de desafios orientado pelas lacunas do match.
- `preparation_service.py`: orquestração do fluxo completo.
- `llm_client.py`: comunicação estruturada com o OpenRouter.
- `leetcode_craw.py`: carga independente do acervo de desafios.

## Limites atuais

- A coleta automática aceita vagas da Gupy.
- O currículo precisa ser um PDF com texto selecionável; não há OCR.
- O banco de desafios deve ser carregado antes da execução.
- Interface e gamificação ficam para a próxima fase do MVP.

## Autores

Rodrigo Rodrigues, Joao Schramm e Augusto Krause.
