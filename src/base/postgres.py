from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import select
from src.base.postgres_models import Base, User, UserStats
from src.app.utils.security import hash_password, verify_password
from src.settings.config import MOSCOW_TZ, db_user, db_password, db_host, db_port, db_name

async_session: None | async_sessionmaker[AsyncSession] = None

async def init_db():
    print("Инициализация базы данных...")
    global async_session
    DATABASE_URL = URL.create(
        drivername="postgresql+asyncpg",
        username=db_user,
        password=db_password,
        host=db_host,
        port=db_port,
        database=db_name
    )
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={
            "server_settings": {
                "timezone": "Europe/Moscow"
            }
        },
        future=True,
        echo=False,
        poolclass=NullPool,
    )
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS citext;"))
        await conn.run_sync(Base.metadata.create_all)
    print("✅ База данных инициализирована")


def connect(method):
    async def wrapper(*args, **kwargs):
        async with async_session() as session:
            try:
                result = await method(*args, **kwargs, session=session)
                return result
            except Exception as e:
                await session.rollback()
                print(f"❌ Ошибка в методе {method.__name__}: {repr(e)}")
                raise Exception(
                    f'Ошибка при работе с базой данных: {repr(e)} \nargs:\n{args}'
                )
    return wrapper



@connect
async def create_user(
    login: str,
    email: str,
    password: str,
    session: AsyncSession
) -> User:
    login_norm = login.strip().lower()
    email_norm = email.strip().lower()

    exists = await session.execute(
        select(User).where(
            (User.login == login_norm) | (User.email == email_norm)
        )
    )
    if exists.scalar_one_or_none():
        raise ValueError("Пользователь с таким логином или почтой уже существует")

    pwd_hash = hash_password(password)
    user = User(login=login_norm, email=email_norm, password=pwd_hash)
    session.add(user)
    await session.commit()
    session.add(UserStats(user_id=user.id))
    await session.commit()
    return user

@connect
async def record_game_result(user_id: int, result: str, session: AsyncSession) -> None:
    stats = await session.get(UserStats, user_id)
    if not stats:
        stats = UserStats(
            user_id=user_id,
            total_games=0,
            wins=0,
            draws=0,
            losses=0,
        )
        session.add(stats)

    stats.total_games = (stats.total_games or 0) + 1

    if result == "win":
        stats.wins = (stats.wins or 0) + 1
    elif result == "loss":
        stats.losses = (stats.losses or 0) + 1
    elif result == "draw":
        stats.draws = (stats.draws or 0) + 1
    else:
        raise ValueError(f"Unknown result type: {result}")

    await session.commit()

@connect
async def authenticate_user(
    login_or_email: str,
    password: str,
    session: AsyncSession
) -> User | None:
    identifier = login_or_email.strip().lower()
    stmt = select(User).where(
        (User.login == identifier) | (User.email == identifier)
    )
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password):
        return user
    return None

@connect
async def get_user_stats(user_id: int, session: AsyncSession) -> dict:
    stats = await session.get(UserStats, user_id)
    if not stats:
        return {
            "total_games": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
        }
    return {
        "total_games": stats.total_games or 0,
        "wins": stats.wins or 0,
        "draws": stats.draws or 0,
        "losses": stats.losses or 0,
    }