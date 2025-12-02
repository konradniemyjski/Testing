"""Router stub for auth endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..auth import login_for_access_token
from ..db import get_db
from ..schemas import Token
from ..auth import oauth2_scheme

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def token(
    form_data: Annotated[dict, Depends(login_for_access_token)],
) -> Token:
    """
    OAuth2 compatible token endpoint.

    Use this endpoint to authenticate users and get JWT tokens.
    """
    return form_data
