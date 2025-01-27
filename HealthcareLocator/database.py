import os
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError
from models import Base
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database URL configuration
DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://")

def get_engine(max_retries=3, initial_delay=1):
    """Create database engine with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            engine = create_engine(
                DATABASE_URL,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                connect_args={
                    "sslmode": "prefer",  # Changed from require to prefer
                    "connect_timeout": 10
                }
            )

            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                conn.commit()
                logger.info("Database connection successful")
                return engine

        except Exception as e:
            delay = initial_delay * (2 ** attempt)  # Exponential backoff
            logger.error(f"Database connection attempt {attempt + 1} failed: {str(e)}")
            logger.info(f"Retrying in {delay} seconds...")

            if attempt == max_retries - 1:
                logger.error("Maximum retry attempts reached")
                raise
            time.sleep(delay)

# Create engine
try:
    engine = get_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise

@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record):
    connection_record.info['pid'] = os.getpid()

def init_db():
    """Initialize database schema"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        raise

def get_db():
    """Database session generator with error handling"""
    db = SessionLocal()
    try:
        yield db
    except OperationalError as e:
        logger.error(f"Database operation failed: {str(e)}")
        db.rollback()  # Rollback any failed transaction
        raise
    finally:
        db.close()