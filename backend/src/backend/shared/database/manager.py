"""
Database connection manager using SQLAlchemy with session management.
"""
import threading
from typing import Optional
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import sessionmaker, Session, scoped_session
from sqlalchemy.pool import QueuePool
from backend.core.config import settings


class DatabaseManager:
    """
    Singleton class to manage SQLAlchemy database connections and sessions.
    
    Usage:
        # Method 1: Direct session management
        db = DatabaseManager.get_instance()
        session = db.get_session()
        try:
            result = session.execute(text("SELECT * FROM users"))
            rows = result.fetchall()
        finally:
            session.close()
        
        # Method 2: Using context manager (recommended)
        db = DatabaseManager.get_instance()
        with db as session:
            result = session.execute(text("SELECT * FROM users"))
            rows = result.fetchall()
    """
    
    _instance: Optional['DatabaseManager'] = None
    _lock: threading.Lock = threading.Lock()
    _engine: Optional[Engine] = None
    _session_factory: Optional[sessionmaker] = None
    _scoped_session: Optional[scoped_session] = None
    
    def __new__(cls):
        """
        Create singleton instance with thread-safe implementation.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialize_engine()
        return cls._instance
    
    def _initialize_engine(self) -> None:
        """
        Initialize the SQLAlchemy engine and session factory.
        """
        try:
            # Create engine with connection pooling
            self._engine = create_engine(
                settings.database_url,
                poolclass=QueuePool,
                pool_size=settings.mysql_pool_size,
                pool_pre_ping=True,  # Verify connections before using
                pool_recycle=3600,   # Recycle connections after 1 hour
                echo=False,          # Set to True for SQL debugging
            )
            
            # Create session factory
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
            )
            
            # Create scoped session for thread-local sessions
            self._scoped_session = scoped_session(self._session_factory)
            
            print(f"✓ SQLAlchemy engine initialized with pool size {settings.mysql_pool_size}")
            
        except Exception as e:
            print(f"✗ Error initializing SQLAlchemy engine: {e}")
            raise
    
    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        """
        Get the singleton instance of DatabaseManager.
        
        Returns:
            DatabaseManager: The singleton instance
        """
        return cls()
    
    @property
    def engine(self) -> Engine:
        """
        Get the SQLAlchemy engine.
        
        Returns:
            Engine: The SQLAlchemy engine
        """
        if self._engine is None:
            raise RuntimeError("Database engine not initialized")
        return self._engine
    
    def get_session(self) -> Session:
        """
        Get a new database session.
        
        Returns:
            Session: A new SQLAlchemy session
            
        Raises:
            RuntimeError: If session factory not initialized
        """
        if self._session_factory is None:
            raise RuntimeError("Session factory not initialized")
        
        return self._session_factory()
    
    def get_scoped_session(self) -> Session:
        """
        Get a thread-local scoped session.
        
        Returns:
            Session: A thread-local SQLAlchemy session
            
        Raises:
            RuntimeError: If scoped session not initialized
        """
        if self._scoped_session is None:
            raise RuntimeError("Scoped session not initialized")
        
        return self._scoped_session()
    
    def close_session(self, session: Session) -> None:
        """
        Close a database session.
        
        Args:
            session: The session to close
        """
        if session:
            session.close()
    
    def remove_scoped_session(self) -> None:
        """
        Remove the current thread's scoped session.
        """
        if self._scoped_session:
            self._scoped_session.remove()
    
    def close_all(self) -> None:
        """
        Dispose of the engine and all connections.
        Should be called during application shutdown.
        """
        if self._scoped_session:
            self._scoped_session.remove()
        
        if self._engine:
            self._engine.dispose()
            print(f"✓ SQLAlchemy engine disposed")
    
    def __enter__(self) -> Session:
        """
        Context manager entry - get a new session.
        
        Returns:
            Session: A new SQLAlchemy session
        """
        self._current_session = self.get_session()
        return self._current_session
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit - close the session.
        Rollback on exception, commit otherwise.
        """
        if hasattr(self, '_current_session'):
            try:
                if exc_type is not None:
                    # Exception occurred, rollback
                    self._current_session.rollback()
                else:
                    # No exception, commit
                    self._current_session.commit()
            finally:
                self._current_session.close()
                delattr(self, '_current_session')


# Convenience function to get database instance
def get_db() -> DatabaseManager:
    """
    Convenience function to get the DatabaseManager singleton instance.
    
    Returns:
        DatabaseManager: The singleton instance
    """
    return DatabaseManager.get_instance()
