"""
Database connection manager using SQLAlchemy.
Provides connection pooling, session management, and error handling.
"""
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import QueuePool
from contextlib import contextmanager
import logging
from config import DatabaseConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Base class for ORM models
Base = declarative_base()

class DatabaseManager:
    """Singleton database manager for connection pooling and session management"""
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize database engine and session factory"""
        try:
            database_uri = DatabaseConfig.get_database_uri()
            
            # Create engine with connection pooling
            if 'sqlite' in database_uri:
                # SQLite-specific configuration
                self._engine = create_engine(
                    database_uri,
                    connect_args={'check_same_thread': False},
                    echo=False
                )
            else:
                # MySQL/PostgreSQL configuration
                self._engine = create_engine(
                    database_uri,
                    poolclass=QueuePool,
                    pool_size=10,
                    max_overflow=20,
                    pool_pre_ping=True,  # Verify connections before using
                    echo=False
                )
            
            # Create session factory
            self._session_factory = scoped_session(
                sessionmaker(
                    bind=self._engine,
                    autocommit=False,
                    autoflush=False
                )
            )
            
            logger.info(f"Database connection established: {DatabaseConfig.DB_TYPE}")
            
        except Exception as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise
    
    def get_engine(self):
        """Get database engine"""
        return self._engine
    
    def get_session(self):
        """Get a new database session"""
        return self._session_factory()
    
    def remove_session(self):
        """Remove current session"""
        self._session_factory.remove()
    
    def create_all_tables(self):
        """Create all tables defined in models"""
        try:
            Base.metadata.create_all(self._engine)
            logger.info("All tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise
    
    def drop_all_tables(self):
        """Drop all tables (use with caution!)"""
        try:
            Base.metadata.drop_all(self._engine)
            logger.warning("All tables dropped")
        except Exception as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            raise

# Context manager for database sessions
@contextmanager
def get_db_session():
    """
    Context manager for database sessions.
    Automatically commits on success and rolls back on error.
    
    Usage:
        with get_db_session() as session:
            session.add(obj)
    """
    db_manager = DatabaseManager()
    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()

# Initialize database on module import
db_manager = DatabaseManager()

# Export commonly used objects
__all__ = ['DatabaseManager', 'get_db_session', 'Base', 'db_manager']
