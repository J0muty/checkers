from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from sqlalchemy.engine import URL
from sqlalchemy import select
from src.base.postgres_models import Base, User, UserStats, Friend, FriendRequest
from src.app.game.count_and_rang import update_elo, calculate_rank
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
        connect_args={"server_settings": {"timezone": "Europe/Moscow"}},
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
                raise Exception(f'Ошибка при работе с базой данных: {repr(e)} \nargs:\n{args}')
    return wrapper

@connect
async def create_user(login: str, email: str, password: str, session: AsyncSession) -> User:
    login_norm = login.strip().lower()
    email_norm = email.strip().lower()
    exists = await session.execute(select(User).where((User.login == login_norm) | (User.email == email_norm)))
    if exists.scalar_one_or_none():
        raise ValueError("Пользователь с таким логином или почтой уже существует")
    pwd_hash = hash_password(password)
    user = User(login=login_norm, email=email_norm, password=pwd_hash)
    session.add(user)
    await session.commit()
    session.add(UserStats(user_id=user.id, elo=0, rank="Новичок"))
    await session.commit()
    return user

@connect
async def record_game_result(
    user_id: int, result: str, opponent_elo: int, session: AsyncSession
) -> int:
    stats = await session.get(UserStats, user_id)
    if not stats:
        stats = UserStats(user_id=user_id, total_games=0, wins=0, draws=0, losses=0, elo=0, rank="Новичок")
        session.add(stats)
    old_elo = stats.elo or 0
    stats.total_games = (stats.total_games or 0) + 1
    if result == "win":
        stats.wins = (stats.wins or 0) + 1
    elif result == "loss":
        stats.losses = (stats.losses or 0) + 1
    elif result == "draw":
        stats.draws = (stats.draws or 0) + 1
    else:
        raise ValueError(f"Unknown result type: {result}")
    stats.elo = update_elo(old_elo, opponent_elo, result)
    stats.rank = calculate_rank(stats.elo)
    await session.commit()
    return stats.elo - old_elo

@connect
async def authenticate_user(login_or_email: str, password: str, session: AsyncSession) -> User | None:
    identifier = login_or_email.strip().lower()
    stmt = select(User).where((User.login == identifier) | (User.email == identifier))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password):
        return user
    return None

@connect
async def get_user_login(user_id: int, session: AsyncSession) -> str | None:
    user = await session.get(User, user_id)
    return user.login if user else None

@connect
async def get_user_stats(user_id: int, session: AsyncSession) -> dict:
    stats = await session.get(UserStats, user_id)
    if not stats:
        return {"total_games": 0, "wins": 0, "draws": 0, "losses": 0, "elo": 0, "rank": calculate_rank(0)}
    return {
        "total_games": stats.total_games or 0,
        "wins": stats.wins or 0,
        "draws": stats.draws or 0,
        "losses": stats.losses or 0,
        "elo": stats.elo or 0,
        "rank": stats.rank,
    }

@connect
async def get_friends(user_id: int, session: AsyncSession) -> list[dict]:
    result = await session.execute(select(User).join(Friend, Friend.friend_id == User.id).where(Friend.user_id == user_id))
    users = result.scalars().all()
    return [{"id": u.id, "login": u.login} for u in users]

@connect
async def get_friend_requests(user_id: int, session: AsyncSession) -> dict:
    out_res = await session.execute(select(User).join(FriendRequest, FriendRequest.to_user_id == User.id).where(FriendRequest.from_user_id == user_id))
    inc_res = await session.execute(select(User).join(FriendRequest, FriendRequest.from_user_id == User.id).where(FriendRequest.to_user_id == user_id))
    outgoing = out_res.scalars().all()
    incoming = inc_res.scalars().all()
    return {
        "outgoing": [{"id": u.id, "login": u.login} for u in outgoing],
        "incoming": [{"id": u.id, "login": u.login} for u in incoming],
    }

@connect
async def search_users(query: str, user_id: int, session: AsyncSession) -> list[dict]:
    stmt = select(User).where(User.login.ilike(f"%{query.lower()}%"), User.id != user_id)
    result = await session.execute(stmt)
    users = result.scalars().all()
    friends = await get_friends(user_id)
    requests = await get_friend_requests(user_id)
    exclude_ids = {u["id"] for u in friends}
    outgoing_ids = {u["id"] for u in requests["outgoing"]}
    filtered = [u for u in users if u.id not in exclude_ids]
    return [{"id": u.id, "login": u.login, "requested": u.id in outgoing_ids} for u in filtered]

@connect
async def send_friend_request(from_id: int, to_id: int, session: AsyncSession) -> None:
    exists = await session.execute(select(FriendRequest).where(FriendRequest.from_user_id == from_id, FriendRequest.to_user_id == to_id))
    if exists.scalar_one_or_none():
        return
    opposite = await session.execute(select(FriendRequest).where(FriendRequest.from_user_id == to_id, FriendRequest.to_user_id == from_id))
    opp = opposite.scalar_one_or_none()
    if opp:
        await session.delete(opp)
        session.add(Friend(user_id=from_id, friend_id=to_id))
        session.add(Friend(user_id=to_id, friend_id=from_id))
        await session.commit()
        return
    fr = FriendRequest(from_user_id=from_id, to_user_id=to_id)
    session.add(fr)
    await session.commit()

@connect
async def cancel_friend_request(from_id: int, to_id: int, session: AsyncSession) -> None:
    req = await session.execute(select(FriendRequest).where(FriendRequest.from_user_id == from_id, FriendRequest.to_user_id == to_id))
    obj = req.scalar_one_or_none()
    if obj:
        await session.delete(obj)
        await session.commit()

@connect
async def remove_friend(user_id: int, friend_id: int, session: AsyncSession) -> None:
    await session.execute(
        text(
            """
            DELETE FROM friends
            WHERE (user_id = :u AND friend_id = :f) OR (user_id = :f AND friend_id = :u)
            """
        ),
        {"u": user_id, "f": friend_id},
    )
    await session.commit()
