from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from app.config.config import Settings

settings = Settings()


database = settings.DATABASE_URL
engine = create_engine(database, echo=True)
SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=engine)

def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()