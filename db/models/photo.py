import datetime

from sqlalchemy import Column, Integer, BigInteger, LargeBinary, DateTime

from db.base import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    chat_id = Column(BigInteger, nullable=False, index=True)
    message_id = Column(Integer, nullable=False)
    image_bytes = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
