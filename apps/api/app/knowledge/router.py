from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.knowledge import service
from app.knowledge.schemas import (
    DuplicateActionGroupRead,
    KnowledgeDecisionRead,
    KnowledgeSearchResultRead,
)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/search", response_model=list[KnowledgeSearchResultRead])
def search_workspace(
    workspace_id: str = Query(min_length=1),
    query: str = Query(min_length=1),
    session: Session = Depends(get_db_session),
) -> list[KnowledgeSearchResultRead]:
    return service.search_workspace(session, workspace_id=workspace_id, query=query)


@router.get("/decisions", response_model=list[KnowledgeDecisionRead])
def list_workspace_decisions(
    workspace_id: str = Query(min_length=1),
    session: Session = Depends(get_db_session),
) -> list[KnowledgeDecisionRead]:
    return service.list_workspace_decisions(session, workspace_id=workspace_id)


@router.get("/duplicate-actions", response_model=list[DuplicateActionGroupRead])
def list_duplicate_action_candidates(
    workspace_id: str = Query(min_length=1),
    session: Session = Depends(get_db_session),
) -> list[DuplicateActionGroupRead]:
    return service.list_duplicate_action_candidates(
        session,
        workspace_id=workspace_id,
    )
