from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.db.session import get_db_session
from app.knowledge import service
from app.knowledge.schemas import (
    DuplicateActionGroupRead,
    KnowledgeDecisionRead,
    KnowledgeSearchResultRead,
)
from app.pagination import PaginatedResponse
from app.providers.embedding.base import Embedder
from app.providers.embedding.dependencies import get_embedder

router = APIRouter(prefix="/api/knowledge", tags=["knowledge"])


@router.get("/search", response_model=list[KnowledgeSearchResultRead])
def search_workspace(
    workspace_id: str = Query(min_length=1),
    query: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
    session: Session = Depends(get_db_session),
    embedder: Embedder = Depends(get_embedder),
    current_user: User = Depends(get_current_user),
) -> list[KnowledgeSearchResultRead]:
    return service.search_workspace(
        session,
        workspace_id=workspace_id,
        query=query,
        embedder=embedder,
        limit=limit,
    )


@router.get("/decisions", response_model=PaginatedResponse[KnowledgeDecisionRead])
def list_workspace_decisions(
    workspace_id: str = Query(min_length=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[KnowledgeDecisionRead]:
    items = service.list_workspace_decisions(
        session, workspace_id=workspace_id, offset=offset, limit=limit
    )
    total = service.count_workspace_decisions(session, workspace_id=workspace_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)


@router.get(
    "/duplicate-actions", response_model=PaginatedResponse[DuplicateActionGroupRead]
)
def list_duplicate_action_candidates(
    workspace_id: str = Query(min_length=1),
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    session: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
) -> PaginatedResponse[DuplicateActionGroupRead]:
    items = service.list_duplicate_action_candidates(
        session, workspace_id=workspace_id, offset=offset, limit=limit
    )
    total = service.count_duplicate_action_groups(session, workspace_id=workspace_id)
    return PaginatedResponse(items=items, total=total, offset=offset, limit=limit)
