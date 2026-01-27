import os
import uuid
import csv
from typing import List, Dict, Any
from fastapi import UploadFile
from backend.core.config import settings

os.makedirs(settings.upload_dir, exist_ok=True)

class ChartService:
    def upload_csv(self, file: UploadFile) -> str:
        csv_id = str(uuid.uuid4())
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        
        with open(file_path, "wb") as f:
            content = file.file.read()
            f.write(content)
            
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

    def get_csv_content(self, csv_id: str) -> List[Dict[str, Any]]:
        file_path = os.path.join(settings.upload_dir, f"{csv_id}.csv")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"CSV with ID {csv_id} not found")
        
        data = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Basic type conversion for the content to be useful
                converted_row = {}
                for k, v in row.items():
                    if v is None:
                        converted_row[k] = None
                        continue
                    
                    type_ = self._infer_type(v)
                    if type_ == "int":
                        converted_row[k] = int(v)
                    elif type_ == "float":
                        converted_row[k] = float(v)
                    elif type_ == "bool":
                        converted_row[k] = v.lower() in ("true", "yes")
                    else:
                        converted_row[k] = v
                data.append(converted_row)
        return data

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
