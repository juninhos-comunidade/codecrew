import logging
from pathlib import Path
from uuid import UUID

import requests
from sqlalchemy.exc import SQLAlchemyError

from backend.app.exceptions import (
    InvalidPreparationInputError,
    PreparationDependencyError,
)
from backend.app.repositories import SessionRepository
from backend.app.schemas import PreparationData, PreparationSession
from craw_gupy import GupyJobError
from llm_client import LLMResponseError
from preparation_service import build_preparation


logger = logging.getLogger(__name__)


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
