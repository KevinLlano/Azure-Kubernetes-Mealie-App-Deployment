from fastapi import APIRouter, Depends, HTTPException
from pydantic import UUID4
from sqlalchemy.orm.session import Session

from mealie.core.root_logger import get_logger
from mealie.db.db_setup import generate_session
from mealie.repos.all_repositories import get_repositories
from mealie.schema.recipe import Recipe
from mealie.schema.response import ErrorResponse

router = APIRouter()

logger = get_logger()


@router.get("/shared/{token_id}", response_model=Recipe)
def get_shared_recipe(token_id: UUID4, session: Session = Depends(generate_session)):
    db = get_repositories(session, group_id=None, household_id=None)

    token_summary = db.recipe_share_tokens.get_one(token_id)
    if token_summary and token_summary.is_expired:
        try:
            db.recipe_share_tokens.delete(token_id)
            session.commit()
        except Exception:
            logger.exception(f"Failed to delete expired token {token_id}")
            session.rollback()
        token_summary = None

    if token_summary is None:
        raise HTTPException(status_code=404, detail=ErrorResponse.respond("Token Not Found"))

    return token_summary.recipe
