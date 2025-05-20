from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from sqlalchemy.dialects.postgresql import CITEXT

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(CITEXT, unique=True, nullable=False, index=True, comment="case-insensitive")
    email = Column(CITEXT, unique=True, nullable=False, index=True, comment="case-insensitive")
    password = Column(String(60), nullable=False, comment="bcrypt hash")