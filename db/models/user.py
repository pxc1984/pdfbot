from sqlalchemy import Column, Integer, BigInteger, Boolean, String
from db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String, unique=True)
