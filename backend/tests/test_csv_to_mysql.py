#!/usr/bin/env python3
"""
Test CSV to MySQL integration.
Creates a test CSV, uploads it, and verifies table creation and data insertion.
"""
import sys
import os
from io import BytesIO

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from fastapi import UploadFile
from backend.domains.charts.service import ChartService
from backend.shared.database import get_db, CSVStorage
from backend.core.config import settings


def test_csv_to_mysql():
    """Test CSV upload with MySQL table creation"""
    print("=" * 60)
    print("CSV to MySQL Integration Test")
    print("=" * 60)
    
    # Setup
    os.makedirs(settings.upload_dir, exist_ok=True)
    service = ChartService()
    
    # Create test CSV content
    csv_content = b"""name,age,score,active
Alice,30,85.5,true
Bob,25,90.0,false
Charlie,35,88.2,yes
David,28,92.5,true"""
    
    print("\nTest CSV Content:")
    print(csv_content.decode('utf-8'))
    print()
    
    # Mock UploadFile
    file_obj = BytesIO(csv_content)
    upload_file = UploadFile(file=file_obj, filename="test.csv")
    
    try:
        # Test 1: Upload CSV
        print("-" * 60)
        print("Test 1: Uploading CSV...")
        csv_id = service.upload_csv(upload_file)
        print(f"✓ CSV uploaded with ID: {csv_id}")
        
        # Test 2: Verify table was created
        print("\n" + "-" * 60)
        print("Test 2: Verifying table creation...")
        table_name = CSVStorage._sanitize_table_name(csv_id)
        
        db = get_db()
        with db as conn:
            cursor = conn.cursor()
            cursor.execute(f"SHOW TABLES LIKE '{table_name}'")
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                print(f"✓ Table '{table_name}' exists")
            else:
                print(f"✗ Table '{table_name}' not found")
                return False
        
        # Test 3: Verify table structure
        print("\n" + "-" * 60)
        print("Test 3: Checking table structure...")
        with db as conn:
            cursor = conn.cursor()
            cursor.execute(f"DESCRIBE `{table_name}`")
            columns = cursor.fetchall()
            cursor.close()
            
            print(f"✓ Table has {len(columns)} columns:")
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
        
        # Test 4: Verify data was inserted
        print("\n" + "-" * 60)
        print("Test 4: Verifying data insertion...")
        data = CSVStorage.get_table_data(csv_id, limit=10)
        
        print(f"✓ Retrieved {len(data)} rows")
        print("\nSample data:")
        for i, row in enumerate(data[:3], 1):
            print(f"  Row {i}: {row}")
        
        # Test 5: Verify row count
        print("\n" + "-" * 60)
        print("Test 5: Counting rows...")
        with db as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM `{table_name}`")
            count = cursor.fetchone()[0]
            cursor.close()
            
            expected = 4  # 4 data rows in test CSV
            if count == expected:
                print(f"✓ Row count matches: {count}")
            else:
                print(f"✗ Row count mismatch: expected {expected}, got {count}")
                return False
        
        # Cleanup
        print("\n" + "-" * 60)
        print("Cleanup: Dropping test table...")
        with db as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
            conn.commit()
            cursor.close()
        print(f"✓ Table '{table_name}' dropped")
        
        # Remove test file
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ Test file removed")
        
        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"\n{'=' * 60}")
        print(f"❌ Test failed with error:")
        print(f"   {type(e).__name__}: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_csv_to_mysql()
    sys.exit(0 if success else 1)
