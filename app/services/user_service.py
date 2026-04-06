from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from app.core.security import hash_password, verify_password
from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(user: UserCreate, db: AsyncSession):
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password),
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


async def get_user(username: str, db: AsyncSession):
    find_user = await db.execute(
        select(User).where(User.username == username)
    )
    fetched_user = find_user.scalars().first()
    return fetched_user


async def update_user(username: str, user: UserUpdate, db: AsyncSession):
    find_user = await db.execute(
        select(User).where(User.username == username)
    )
    user_to_update = find_user.scalars().first()

    if user_to_update:
        user_to_update.hashed_password = hash_password(user.password)

        await db.commit()
        await db.refresh(user_to_update)
        return user_to_update
    return None


async def authenticate_user(username: str, password: str, db: AsyncSession):
    """Authenticate user by username and password. Returns user if valid, None otherwise."""
    find_user = await db.execute(
        select(User).where(User.username == username)
    )
    user = find_user.scalars().first()
    if user is None:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
