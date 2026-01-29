import os
import uuid
import csv
from typing import List, Dict, Any
from fastapi import UploadFile
from backend.core.config import settings
from backend.shared.database import CSVStorage

os.makedirs(settings.upload_dir, exist_ok=True)

class ChartService:
    def upload_csv(self, file: UploadFile) -> str:
        csv_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        
        # Save CSV file
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
        
        # Get CSV schema
        schema = self.get_csv_schema(csv_id)
        
        # Create MySQL table and insert data
        try:
            # Register CSV in the csv table
            CSVStorage.register_csv(csv_id)
            
            # Create table and insert data
            table_name = CSVStorage.create_table(csv_id, schema)
            rows_inserted = CSVStorage.insert_csv_data(csv_id, file_path, schema)
            print(f"✓ CSV {csv_id}: Table '{table_name}' created with {rows_inserted} rows")  
        except Exception as e:
            print(f"✗ Error storing CSV {csv_id} in MySQL: {e}")
            raise  # Re-raise exception to fail the upload
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
            file.file.close()
            
        return csv_id

    def get_csv_path(self, csv_id: str) -> str:
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV with ID {csv_id} not found")
        return file_path

    def _infer_type(self, value: str) -> str:
        if not value:
            return "string"
        
        # Check for int
        try:
            int(value)
            return "int"
        except ValueError:
            pass

        # Check for float
        try:
            float(value)
            return "float"
        except ValueError:
            pass
            
        # Check for bool
        if value.lower() in ("true", "false", "yes", "no"):
            return "bool"
            
        return "string"

    def get_csv_schema(self, csv_id: str) -> Dict[str, str]:
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV with ID {csv_id} not found")
            
        schema = {}
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Read a sample of rows to infer types
            sample_rows = []
            try:
                for _ in range(100):
                    sample_rows.append(next(reader))
            except StopIteration:
                pass
            
            if not reader.fieldnames:
                return {}

            for col in reader.fieldnames:
                # Infer type based on sample values
                # If ANY value is string, it's string.
                # If ALL are int/float available and consistent, use that.
                
                col_type = None 
                
                for row in sample_rows:
                    val = row.get(col)
                    val_type = self._infer_type(val)
                    
                    if col_type is None:
                        col_type = val_type
                        continue
                    
                    if val_type == "string":
                        col_type = "string"
                        break
                    
                    if col_type == "string":
                         pass # stay string
                         
                    elif col_type == "int":
                        if val_type == "float":
                            col_type = "float"
                        elif val_type == "bool":
                            col_type = "string"
                            break
                            
                    elif col_type == "float":
                        if val_type == "bool":
                            col_type = "string"
                            break
                            
                    elif col_type == "bool":
                        if val_type != "bool":
                            col_type = "string"
                            break
                
                schema[col] = col_type if col_type else "string"
                
        return schema
