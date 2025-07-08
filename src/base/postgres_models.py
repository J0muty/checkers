from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import CITEXT

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(CITEXT, unique=True, nullable=False, index=True, comment="case-insensitive")
    email = Column(CITEXT, unique=True, nullable=False, index=True, comment="case-insensitive")
    password = Column(String(60), nullable=False, comment="bcrypt hash")
    stats = relationship("UserStats", back_populates="user", uselist=False)


class UserStats(Base):
    __tablename__ = "user_stats"

    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    total_games = Column(Integer, default=0)
    wins = Column(Integer, default=0)
    draws = Column(Integer, default=0)
    losses = Column(Integer, default=0)
    elo = Column(Integer, default=0)
    rank = Column("rang", String(50), default="Новичок")

    user = relationship("User", back_populates="stats")
