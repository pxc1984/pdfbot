from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from db.base import Base
from db.models.user import User
from settings import get_settings

settings = get_settings()
engine = create_engine(settings.resolved_database_url, echo=False)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def try_register_user(chat_id: int, username: str = "") -> bool:
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(chat_id=chat_id).first()
        if not user:
            session.add(User(chat_id=chat_id, username=username))
            session.commit()
            return True
    finally:
        session.close()
        return False


def init_db():
    Base.metadata.create_all(bind=engine)
