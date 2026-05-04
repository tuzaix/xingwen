from typing import Generator, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.config import settings
from app.db.session import get_db
from app.models.admin import AdminUser
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(reusable_oauth2)
) -> AdminUser:
    return await get_user_from_token(db, token)

async def get_current_user_from_query(
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = None,
    auth_token: str = Depends(reusable_oauth2)
) -> AdminUser:
    # Use token from query if provided, otherwise from header
    actual_token = token or auth_token
    return await get_user_from_token(db, actual_token)

async def get_user_from_token(db: AsyncSession, token: str) -> AdminUser:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    
    result = await db.execute(select(AdminUser).filter(AdminUser.id == int(token_data.sub)))
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.status:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
