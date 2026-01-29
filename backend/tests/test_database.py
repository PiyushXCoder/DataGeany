"""
Unit tests for DatabaseManager singleton pattern.
These tests verify the singleton pattern works correctly without requiring actual MySQL connection.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
import threading
import time


class TestDatabaseManagerSingleton(unittest.TestCase):
    """Test cases for DatabaseManager singleton pattern"""
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_singleton_same_instance(self, mock_pool_class):
        """Test that multiple calls return the same instance"""
        from backend.shared.database import DatabaseManager
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        db1 = DatabaseManager.get_instance()
        db2 = DatabaseManager.get_instance()
        
        self.assertIs(db1, db2, "DatabaseManager should return the same instance")
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_singleton_thread_safety(self, mock_pool_class):
        """Test that singleton is thread-safe"""
        from backend.shared.database import DatabaseManager
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        instances = []
        
        def create_instance():
            instance = DatabaseManager.get_instance()
            instances.append(instance)
            time.sleep(0.01)  # Small delay to simulate concurrent access
        
        # Create 10 threads that try to get instance simultaneously
        threads = [threading.Thread(target=create_instance) for _ in range(10)]
        
        for thread in threads:
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # All instances should be the same object
        first_instance = instances[0]
        for instance in instances:
            self.assertIs(instance, first_instance, "All instances should be the same in thread-safe singleton")
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_pool_initialization(self, mock_pool_class):
        """Test that connection pool is initialized with correct parameters"""
        from backend.shared.database import DatabaseManager
        from backend.core.config import settings
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        db = DatabaseManager.get_instance()
        
        # Verify pool was created with correct parameters
        mock_pool_class.assert_called_once()
        call_kwargs = mock_pool_class.call_args[1]
        
        self.assertEqual(call_kwargs['pool_name'], settings.mysql_pool_name)
        self.assertEqual(call_kwargs['pool_size'], settings.mysql_pool_size)
        self.assertEqual(call_kwargs['host'], settings.mysql_host)
        self.assertEqual(call_kwargs['port'], settings.mysql_port)
        self.assertEqual(call_kwargs['user'], settings.mysql_user)
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_get_connection(self, mock_pool_class):
        """Test getting a connection from the pool"""
        from backend.shared.database import DatabaseManager
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        # Setup mock
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        db = DatabaseManager.get_instance()
        conn = db.get_connection()
        
        mock_pool.get_connection.assert_called_once()
        self.assertEqual(conn, mock_connection)
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_release_connection(self, mock_pool_class):
        """Test releasing a connection back to the pool"""
        from backend.shared.database import DatabaseManager
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        # Setup mock
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        db = DatabaseManager.get_instance()
        conn = db.get_connection()
        db.release_connection(conn)
        
        mock_connection.close.assert_called_once()
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_context_manager(self, mock_pool_class):
        """Test using DatabaseManager as context manager"""
        from backend.shared.database import DatabaseManager
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        # Setup mock
        mock_pool = MagicMock()
        mock_connection = MagicMock()
        mock_connection.is_connected.return_value = True
        mock_pool.get_connection.return_value = mock_connection
        mock_pool_class.return_value = mock_pool
        
        db = DatabaseManager.get_instance()
        
        with db as conn:
            self.assertEqual(conn, mock_connection)
            mock_pool.get_connection.assert_called_once()
        
        # Connection should be released after exiting context
        mock_connection.close.assert_called_once()
    
    @patch('backend.shared.database.pooling.MySQLConnectionPool')
    def test_get_db_convenience_function(self, mock_pool_class):
        """Test the get_db convenience function"""
        from backend.shared.database import get_db, DatabaseManager
        
        # Reset singleton for testing
        DatabaseManager._instance = None
        
        db = get_db()
        
        self.assertIsInstance(db, DatabaseManager)


if __name__ == '__main__':
    unittest.main()
