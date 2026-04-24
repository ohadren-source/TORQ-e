from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config import settings
from models import Base

# Create database engine
# Use postgresql+psycopg:// dialect to use psycopg[binary] instead of psycopg2
db_url = settings.database_url.replace("postgresql://", "postgresql+psycopg://")
engine = create_engine(db_url, echo=True)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database (create all tables)"""
    Base.metadata.create_all(bind=engine)

def drop_all_tables():
    """WARNING: Drops all tables. Use only for testing."""
    Base.metadata.drop_all(bind=engine)
