import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import select
from base.models_postgres import Base, User

async_session: None | async_sessionmaker[AsyncSession] = None


# =============================================================================
# Инициализация и подключение к базе данных
# =============================================================================
async def async_main(url):
    global async_session
    engine = create_async_engine(url, future=True, echo=False, poolclass=NullPool)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в Base.metadata
        await conn.run_sync(Base.metadata.create_all)


# =============================================================================
# Декоратор для управления сессией базы данных
# =============================================================================
def connect(method):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            try:
                return await method(*args, session=session)
            except Exception as e:
                await session.rollback()
                raise Exception(
                    f'Ошибка при работе с базой данных: {repr(e)} args:\n{args} kwargs:\n{kwargs}'
                )

    return wrapper


# ============================================= Конекты ============================================= #

@connect
async def create_user(username: str, password: str, *, session):
    new_user = User(username=username, password=password)
    session.add(new_user)
    await session.commit()
    return new_user


@connect
async def get_user_by_username(username: str, *, session):
    result = await session.execute(select(User).filter(User.username == username))
    user = result.scalar_one_or_none()
    return user
