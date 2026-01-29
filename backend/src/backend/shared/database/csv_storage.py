"""
CSV to MySQL table storage functionality.
Handles creation of MySQL tables from CSV schemas and data insertion.
"""
import csv
import re
from typing import Dict, List, Any
from mysql.connector import Error
from .manager import get_db


class CSVStorage:
    """Handles CSV to MySQL table conversion and storage."""
    
    @staticmethod
    def _sanitize_table_name(csv_id: str) -> str:
        """
        Generate a safe MySQL table name from CSV ID.
        
        Args:
            csv_id: UUID string of the CSV file
            
        Returns:
            Sanitized table name (csv_{uuid with underscores})
        """
        # Replace hyphens with underscores for MySQL compatibility
        sanitized = csv_id.replace('-', '_')
        return f"csv_{sanitized}"
    
    @staticmethod
    def _sanitize_column_name(column_name: str) -> str:
        """
        Sanitize column name for MySQL compatibility.
        
        Args:
            column_name: Original column name from CSV
            
        Returns:
            Sanitized column name
        """
        # Replace spaces and special characters with underscores
        sanitized = re.sub(r'[^\w]', '_', column_name)
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"col_{sanitized}"
        # MySQL reserved words - prefix with underscore
        reserved = {'select', 'from', 'where', 'order', 'group', 'by', 'limit'}
        if sanitized.lower() in reserved:
            sanitized = f"_{sanitized}"
        return sanitized.lower()
    
    @staticmethod
    def _map_csv_type_to_mysql(csv_type: str) -> str:
        """
        Map CSV schema type to MySQL column type.
        
        Args:
            csv_type: Type from CSV schema (int, float, bool, string)
            
        Returns:
            MySQL column type
        """
        type_mapping = {
            'int': 'INT',
            'float': 'DOUBLE',
            'bool': 'BOOLEAN',
            'string': 'TEXT'
        }
        return type_mapping.get(csv_type, 'TEXT')
    
    @staticmethod
    def create_table(csv_id: str, schema: Dict[str, str]) -> str:
        """
        Create a MySQL table from CSV schema.
        
        Args:
            csv_id: UUID of the CSV file
            schema: Dictionary mapping column names to types
            
        Returns:
            Table name created
            
        Raises:
            Error: If table creation fails
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        
        db = get_db()
        with db as conn:
            cursor = conn.cursor()
            
            try:
                # Drop table if it exists
                cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")
                
                # Build CREATE TABLE statement
                columns = ["id INT AUTO_INCREMENT PRIMARY KEY"]
                
                for col_name, col_type in schema.items():
                    safe_col_name = CSVStorage._sanitize_column_name(col_name)
                    mysql_type = CSVStorage._map_csv_type_to_mysql(col_type)
                    columns.append(f"`{safe_col_name}` {mysql_type}")
                
                create_statement = f"CREATE TABLE `{table_name}` ({', '.join(columns)})"
                
                cursor.execute(create_statement)
                conn.commit()
                
                print(f"✓ Created table `{table_name}` with {len(schema)} columns")
                return table_name
                
            except Error as e:
                conn.rollback()
                print(f"✗ Error creating table `{table_name}`: {e}")
                raise
            finally:
                cursor.close()
    
    @staticmethod
    def insert_csv_data(csv_id: str, file_path: str, schema: Dict[str, str]) -> int:
        """
        Insert CSV data into MySQL table.
        
        Args:
            csv_id: UUID of the CSV file
            file_path: Path to the CSV file
            schema: Dictionary mapping column names to types
            
        Returns:
            Number of rows inserted
            
        Raises:
            Error: If data insertion fails
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        
        db = get_db()
        with db as conn:
            cursor = conn.cursor()
            
            try:
                # Read CSV file
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    # Get sanitized column names
                    original_columns = list(schema.keys())
                    sanitized_columns = [CSVStorage._sanitize_column_name(col) for col in original_columns]
                    
                    # Prepare INSERT statement
                    placeholders = ', '.join(['%s'] * (len(sanitized_columns)))  
                    columns_str = ', '.join([f"`{col}`" for col in sanitized_columns])
                    insert_statement = f"INSERT INTO `{table_name}` ({columns_str}) VALUES ({placeholders})"
                    
                    # Batch insert
                    rows_inserted = 0
                    batch = []
                    batch_size = 1000
                    
                    for row in reader:
                        # Convert row values based on schema types
                        values = []  # Add csv_id as first value
                        for col in original_columns:
                            value = row.get(col, None)
                            
                            # Convert based on type
                            if value is None or value == '':
                                values.append(None)
                            elif schema[col] == 'int':
                                try:
                                    values.append(int(value))
                                except (ValueError, TypeError):
                                    values.append(None)
                            elif schema[col] == 'float':
                                try:
                                    values.append(float(value))
                                except (ValueError, TypeError):
                                    values.append(None)
                            elif schema[col] == 'bool':
                                values.append(value.lower() in ('true', 'yes', '1'))
                            else:
                                values.append(str(value))
                        
                        batch.append(tuple(values))
                        
                        # Execute batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            cursor.executemany(insert_statement, batch)
                            rows_inserted += len(batch)
                            batch = []
                    
                    # Insert remaining rows
                    if batch:
                        cursor.executemany(insert_statement, batch)
                        rows_inserted += len(batch)
                    
                    conn.commit()
                    print(f"✓ Inserted {rows_inserted} rows into `{table_name}`")
                    
                    return rows_inserted
                    
            except Error as e:
                conn.rollback()
                print(f"✗ Error inserting data into `{table_name}`: {e}")
                raise
            finally:
                cursor.close()
    
    @staticmethod
    def get_table_data(csv_id: str, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Retrieve data from MySQL table.
        
        Args:
            csv_id: UUID of the CSV file
            limit: Maximum number of rows to return
            offset: Number of rows to skip
            
        Returns:
            List of dictionaries representing rows
            
        Raises:
            Error: If query fails
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        
        db = get_db()
        with db as conn:
            cursor = conn.cursor(dictionary=True)
            
            try:
                query = f"SELECT * FROM `{table_name}` LIMIT %s OFFSET %s"
                cursor.execute(query, (limit, offset))
                rows = cursor.fetchall()
                
                return rows
                
            except Error as e:
                print(f"✗ Error retrieving data from `{table_name}`: {e}")
                raise
            finally:
                cursor.close()
