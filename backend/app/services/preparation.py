import logging
import json
from pathlib import Path
from uuid import UUID

import requests
from sqlalchemy.exc import SQLAlchemyError

from backend.app.exceptions import (
    InvalidPreparationInputError,
    PreparationDependencyError,
)
from backend.app.integrations.gupy import GupyJobError
from backend.app.integrations.openrouter import LLMResponseError, request_json
from backend.app.repositories import SessionRepository
from backend.app.schemas import PreparationData, PreparationSession
from backend.app.services.pipeline import build_preparation


logger = logging.getLogger(__name__)

MENTOR_SCHEMA = {
    "type": "object",
    "properties": {"message": {"type": "string"}},
    "required": ["message"],
    "additionalProperties": False,
}

MENTOR_PROMPT = """
Você é o mentor técnico do CodeCrew. Ajude o candidato a se preparar para a
vaga usando o diagnóstico fornecido. Responda em português, de forma objetiva,
prática e encorajadora. Não invente experiências ou competências. Quando fizer
uma pergunta de entrevista, faça uma por vez. Quando sugerir estudo, priorize
as lacunas e os desafios disponíveis.

Formate a resposta com Markdown leve e legível:
- use parágrafos curtos;
- use listas quando houver passos ou opções;
- use negrito apenas para conceitos importantes;
- use código inline para tecnologias e comandos;
- evite tabelas e títulos de nível 1;
- não comece com saudações ou repita a pergunta do candidato.

CONTEXTO DA PREPARAÇÃO
{context}
"""


class PreparationApplicationService:
    def __init__(self, sessions: SessionRepository) -> None:
        self._sessions = sessions

    def create(
        self,
        job_url: str,
        cv_path: Path,
        question_limit: int,
    ) -> PreparationSession:
        try:
            result = build_preparation(
                job_url,
                cv_path=cv_path,
                question_limit=question_limit,
            )
            preparation = PreparationData.model_validate(result)
        except (FileNotFoundError, ValueError) as exc:
            raise InvalidPreparationInputError(str(exc)) from exc
        except (
            GupyJobError,
            LLMResponseError,
            requests.RequestException,
            SQLAlchemyError,
        ) as exc:
            logger.exception("Preparation dependency failed")
            raise PreparationDependencyError(
                "Não foi possível concluir a preparação."
            ) from exc

        session = PreparationSession(**preparation.model_dump())
        return self._sessions.save(session)

    def get(self, session_id: UUID) -> PreparationSession:
        return self._sessions.get(session_id)

    def reply(
        self,
        session_id: UUID,
        messages: list[dict[str, str]],
    ) -> str:
        session = self._sessions.get(session_id)
        context = {
            "vaga": session.job.model_dump(),
            "candidato": {
                "resumo": session.candidate.resumo,
                "habilidades": session.candidate.habilidades,
            },
            "diagnostico": session.match.model_dump(),
            "desafios": [
                {
                    "title": question.title,
                    "difficulty": question.difficulty,
                    "tags": question.tags,
                }
                for question in session.questions
            ],
        }
        conversation = [
            {
                "role": "system",
                "content": MENTOR_PROMPT.format(
                    context=json.dumps(context, ensure_ascii=False)
                ),
            },
            *messages[-12:],
        ]

        try:
            response = request_json(
                messages=conversation,
                schema=MENTOR_SCHEMA,
                schema_name="resposta_mentor_codecrew",
            )
        except (LLMResponseError, requests.RequestException, RuntimeError) as exc:
            logger.exception("Mentor dependency failed")
            raise PreparationDependencyError(
                "Não foi possível obter a resposta do mentor."
            ) from exc

        message = response.get("message")
        if not isinstance(message, str) or not message.strip():
            raise PreparationDependencyError(
                "O mentor retornou uma resposta vazia."
            )
        return message.strip()
