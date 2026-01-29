"""
Database connection manager using singleton pattern with connection pooling.
"""
import threading
from typing import Optional, Union
import mysql.connector
from mysql.connector import pooling, Error
from mysql.connector.pooling import MySQLConnectionPool, PooledMySQLConnection
from mysql.connector.connection import MySQLConnection
from backend.core.config import settings


# Type alias for connections (can be either pooled or direct)
ConnectionType = Union[PooledMySQLConnection, MySQLConnection]


class DatabaseManager:
    """
    Singleton class to manage MySQL database connections using connection pooling.
    
    Usage:
        # Method 1: Direct connection management
        db = DatabaseManager.get_instance()
        conn = db.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
        finally:
            db.release_connection(conn)
        
        # Method 2: Using context manager (recommended)
        db = DatabaseManager.get_instance()
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
            results = cursor.fetchall()
    """
    
    _instance: Optional['DatabaseManager'] = None
    _lock: threading.Lock = threading.Lock()
    _pool: Optional[MySQLConnectionPool] = None
    
    def __new__(cls):
        """
        Create singleton instance with thread-safe implementation.
        """
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = super(DatabaseManager, cls).__new__(cls)
                    cls._instance._initialize_pool()
        return cls._instance
    
    def _initialize_pool(self) -> None:
        """
        Initialize the MySQL connection pool with settings from config.
        """
        try:
            self._pool = pooling.MySQLConnectionPool(
                pool_name=settings.mysql_pool_name,
                pool_size=settings.mysql_pool_size,
                host=settings.mysql_host,
                port=settings.mysql_port,
                user=settings.mysql_user,
                password=settings.mysql_password,
                database=settings.mysql_database,
                autocommit=False,
                pool_reset_session=True
            )
            print(f"✓ MySQL connection pool '{settings.mysql_pool_name}' initialized with {settings.mysql_pool_size} connections")
        except Error as e:
            print(f"✗ Error initializing MySQL connection pool: {e}")
            raise
    
    @classmethod
    def get_instance(cls) -> 'DatabaseManager':
        """
        Get the singleton instance of DatabaseManager.
        
        Returns:
            DatabaseManager: The singleton instance
        """
        return cls()
    
    def get_connection(self) -> PooledMySQLConnection:
        """
        Get a connection from the pool.
        
        Returns:
            PooledMySQLConnection: A pooled connection from the pool
            
        Raises:
            Error: If unable to get connection from pool
        """
        if self._pool is None:
            raise RuntimeError("Connection pool not initialized")
        
        try:
            connection = self._pool.get_connection()
            return connection
        except Error as e:
            print(f"✗ Error getting connection from pool: {e}")
            raise
    
    def release_connection(self, connection: ConnectionType) -> None:
        """
        Release a connection back to the pool.
        
        Args:
            connection: The connection to release
        """
        if connection and connection.is_connected():
            connection.close()  # This returns it to the pool
    
    def close_all(self) -> None:
        """
        Close all connections in the pool.
        Should be called during application shutdown.
        """
        if self._pool:
            # Connection pools don't have a direct close_all method
            # Connections are closed when they're no longer referenced
            print(f"✓ Closing all connections in pool '{settings.mysql_pool_name}'")
            self._pool = None
    
    def __enter__(self) -> PooledMySQLConnection:
        """
        Context manager entry - get a connection from the pool.
        
        Returns:
            PooledMySQLConnection: A pooled connection from the pool
        """
        self._current_connection = self.get_connection()
        return self._current_connection
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """
        Context manager exit - release the connection back to the pool.
        """
        if hasattr(self, '_current_connection'):
            self.release_connection(self._current_connection)
            delattr(self, '_current_connection')


# Convenience function to get database instance
def get_db() -> DatabaseManager:
    """
    Convenience function to get the DatabaseManager singleton instance.
    
    Returns:
        DatabaseManager: The singleton instance
    """
    return DatabaseManager.get_instance()
