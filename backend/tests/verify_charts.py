import sys
import os
import shutil
from typing import BinaryIO
from io import BytesIO
from fastapi import UploadFile
from backend.domains.charts.service import ChartService
from backend.core.config import settings

def test_csv_logic():
    print("Testing CSV implementation...")
    
    # Setup
    os.makedirs(settings.upload_dir, exist_ok=True)
    service = ChartService()
    
    # Create dummy CSV content
    csv_content = b"name,age,score,active\nAlice,30,85.5,true\nBob,25,90.0,false\nCharlie,35,88.2,yes"
    
    # Mock UploadFile
    file_obj = BytesIO(csv_content)
    upload_file = UploadFile(file=file_obj, filename="test.csv")
    
    # Test Upload
    try:
        csv_id = service.upload_csv(upload_file)
        print(f"Upload successful. ID: {csv_id}")
    except Exception as e:
        print(f"Upload failed: {e}")
        return

    # Test Schema
    try:
        schema = service.get_csv_schema(csv_id)
        print(f"Schema detected: {schema}")
        
        # assertions
        assert schema.get("name") == "string"
        assert schema.get("age") == "int"
        assert schema.get("score") == "float"
        assert schema.get("active") == "bool"
        print("Schema verification passed!")
    except Exception as e:
        print(f"Schema verification failed: {e}")

    # Test Content (via Path)
    try:
        path = service.get_csv_path(csv_id)
        print(f"Path retrieved: {path}")
        assert os.path.exists(path)
        
        # Verify it's readable
        with open(path, "r") as f:
            lines = f.readlines()
            # print(f"Raw lines: {lines}")
            assert len(lines) == 4 # Header + 3 rows
        print("File path verification passed!")
        
        # We can still test get_csv_content if intended for internal use, 
        # but let's confirm the file itself is correct.
    except Exception as e:
        print(f"File path verification failed: {e}")
        
    # Cleanup
    try:
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

if __name__ == "__main__":
    test_csv_logic()
