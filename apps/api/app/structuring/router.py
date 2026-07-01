from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.providers.llm.base import LLMExtractor
from app.providers.llm.dependencies import get_llm_extractor
from app.structuring import service
from app.structuring.schemas import StructuringRunRead

router = APIRouter(tags=["structuring"])


@router.post("/api/jobs/{job_id}/structure", response_model=StructuringRunRead)
def run_structuring_job(
    job_id: UUID,
    session: Session = Depends(get_db_session),
    extractor: LLMExtractor = Depends(get_llm_extractor),
    current_user: User = Depends(get_current_user),
) -> StructuringRunRead:
    return service.run_structuring_job(session, job_id, extractor=extractor)
