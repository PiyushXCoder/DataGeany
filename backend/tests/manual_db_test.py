#!/usr/bin/env python3
"""
Manual test script for DatabaseManager.
This script requires a running MySQL instance with credentials configured in .env

Usage:
    1. Set up MySQL credentials in .env file
    2. Create a test database
    3. Run: poetry run python tests/manual_db_test.py
"""
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from backend.shared.database import DatabaseManager, get_db
from backend.core.config import settings


def test_connection():
    """Test basic database connection"""
    print("=" * 60)
    print("MySQL Connection Test")
    print("=" * 60)
    
    print(f"\nConnection Settings:")
    print(f"  Host: {settings.mysql_host}")
    print(f"  Port: {settings.mysql_port}")
    print(f"  User: {settings.mysql_user}")
    print(f"  Database: {settings.mysql_database}")
    print(f"  Pool Name: {settings.mysql_pool_name}")
    print(f"  Pool Size: {settings.mysql_pool_size}")
    
    try:
        # Test 1: Get singleton instance
        print(f"\n{'-' * 60}")
        print("Test 1: Getting DatabaseManager instance...")
        db = get_db()
        print("✓ DatabaseManager instance created successfully")
        
        # Test 2: Get connection from pool
        print(f"\n{'-' * 60}")
        print("Test 2: Getting connection from pool...")
        conn = db.get_connection()
        print(f"✓ Connection acquired: {conn}")
        
        # Test 3: Execute simple query
        print(f"\n{'-' * 60}")
        print("Test 3: Executing test query (SELECT 1)...")
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        print(f"✓ Query executed successfully. Result: {result}")
        
        # Test 4: Release connection
        print(f"\n{'-' * 60}")
        print("Test 4: Releasing connection back to pool...")
        db.release_connection(conn)
        print("✓ Connection released successfully")
        
        # Test 5: Context manager usage
        print(f"\n{'-' * 60}")
        print("Test 5: Testing context manager usage...")
        with db as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            print(f"✓ Context manager works. Result: {result}")
        print("✓ Connection automatically released")
        
        # Test 6: Multiple connections
        print(f"\n{'-' * 60}")
        print("Test 6: Testing multiple connections from pool...")
        connections = []
        for i in range(3):
            conn = db.get_connection()
            connections.append(conn)
            print(f"  Connection {i+1}: {conn}")
        
        for i, conn in enumerate(connections):
            db.release_connection(conn)
            print(f"  Released connection {i+1}")
        
        print("✓ Multiple connections handled successfully")
        
        # Test 7: Verify singleton
        print(f"\n{'-' * 60}")
        print("Test 7: Verifying singleton pattern...")
        db1 = DatabaseManager.get_instance()
        db2 = get_db()
        assert db1 is db2, "Instances should be the same"
        print(f"✓ Singleton verified: db1 is db2 = {db1 is db2}")
        
        print(f"\n{'=' * 60}")
        print("✅ All tests passed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("1. Ensure MySQL is running")
        print("2. Check credentials in .env file")
        print("3. Verify database exists")
        print("4. Check network connectivity")
        return False
    
    return True


def check_configuration():
    """Check if configuration is properly set"""
    print("\nChecking configuration...")
    
    issues = []
    
    if not settings.mysql_password:
        issues.append("MYSQL_PASSWORD is not set")
    
    if not settings.mysql_database:
        issues.append("MYSQL_DATABASE is not set")
    
    if issues:
        print(f"\n⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"  - {issue}")
        print("\nPlease set the following in your .env file:")
        print("  MYSQL_PASSWORD=your_password")
        print("  MYSQL_DATABASE=your_database")
        return False
    
    print("✓ Configuration looks good")
    return True


if __name__ == "__main__":
    if not check_configuration():
        sys.exit(1)
    
    success = test_connection()
    sys.exit(0 if success else 1)
