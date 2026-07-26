# CodeCrew

Preparação personalizada para entrevistas técnicas, guiada por IA e gamificada.

## Descrição

Se preparar para uma entrevista hoje é um processo genérico: o candidato estuda listas de
perguntas prontas e resolve exercícios aleatórios, sem saber se aquilo tem relação com a vaga
que ele realmente quer.

O CodeCrew parte de dois insumos concretos, o **currículo do candidato** e a **vaga desejada**, 
e usa inteligência artificial para gerar um roteiro de preparação sob medida:

- **Perguntas técnicas e comportamentais personalizadas**, derivadas dos pré-requisitos e das
  responsabilidades reais da vaga, cruzadas com a experiência descrita no currículo.
- **Desafios de código gamificados**, com pontuação e progressão, para que o treino técnico
  deixe de ser uma lista de tarefas e vire uma experiência com senso de avanço.

A ideia é simples: em vez de estudar "o que costuma cair", o candidato treina exatamente o que
aquela vaga exige.

### Como funciona

1. **Coleta da vaga** — a partir da URL de uma vaga, extraímos título, pré-requisitos e
   responsabilidades.
2. **Análise com IA** — esses dados são cruzados com o currículo do candidato para gerar as
   perguntas da entrevista.
3. **Trilha de desafios** — um acervo de questões de lógica alimenta o modo gamificado, filtrado
   por tema e dificuldade conforme o perfil da vaga.

Este repositório contém a **camada de coleta de dados** que alimenta as etapas 1 e 3.

## Requisitos

- Python 3.12+
- PostgreSQL

## Instalação

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Crie um arquivo `.env` na raiz do projeto:

```env
DATABASE_URL=postgresql+psycopg2://usuario:senha@localhost:5432/codecrew
```

## Uso

### Coletar uma vaga

```bash
python craw_gupy.py
```

O script pede a URL da vaga e devolve os campos usados como contexto para a IA:

```json
{
  "titulo": "Desenvolvedor(a) Python Pleno",
  "pre_requisitos": "Experiência com Python, SQL e APIs REST...",
  "responsabilidades": "Desenvolver e manter serviços backend..."
}
```

### Popular o acervo de desafios

```bash
python leetcode_craw.py
```

Busca as questões, converte os enunciados para Markdown e grava na tabela `questions`.
A inserção é idempotente, então rodar de novo não duplica registros.

Os filtros de coleta (tema, dificuldade e quantidade) ficam no próprio script:

```python
list_result = fetch_leetcode(list_query, {
    "filters": {"tags": ["array"], "difficulty": "EASY"},
    "limit": 50,
    "skip": 0
})
```

## Roadmap

- [ ] Upload e parsing do currículo
- [ ] Geração das perguntas de entrevista com IA
- [ ] Motor de pontuação e progressão dos desafios
- [ ] Interface web

## Status do projeto

Em desenvolvimento. A camada de coleta de dados já está funcional; as etapas de análise por IA
e a interface ainda estão sendo construídas.

## Autores

Rodrigo Rodrigues,
Joao Schramm e
Augusto Krause.
