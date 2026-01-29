"""
CSV to MySQL table storage functionality using SQLAlchemy.
Handles creation of MySQL tables from CSV schemas and data insertion.
"""
import csv
import re
from typing import Dict, List, Any
from sqlalchemy import text, MetaData, Table, Column, Integer, Float, Boolean, Text, String, inspect
from sqlalchemy.exc import SQLAlchemyError
from .manager import get_db


class CSVStorage:
    """Handles CSV to MySQL table conversion and storage using SQLAlchemy."""
    
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
    def _map_csv_type_to_sqlalchemy(csv_type: str):
        """
        Map CSV schema type to SQLAlchemy column type.
        
        Args:
            csv_type: Type from CSV schema (int, float, bool, string)
            
        Returns:
            SQLAlchemy type class
        """
        type_mapping = {
            'int': Integer,
            'float': Float,
            'bool': Boolean,
            'string': Text
        }
        return type_mapping.get(csv_type, Text)
    
    @staticmethod
    def register_csv(csv_id: str) -> None:
        """
        Register a CSV upload by inserting its ID into the csv table.
        
        Args:
            csv_id: UUID of the CSV file
            
        Raises:
            SQLAlchemyError: If insertion fails
        """
        db = get_db()
        with db as session:
            try:
                # Insert CSV ID into csv table
                # We use text() here assuming the 'csv' table already exists
                # from initial migrations/setup
                session.execute(
                    text("INSERT INTO csv (id) VALUES (:id)"),
                    {"id": csv_id}
                )
                # Session commits automatically on successful exit of context manager
                print(f"✓ Registered CSV with ID: {csv_id}")
                
            except SQLAlchemyError as e:
                # DatabaseManager context manager handles rollback on exception
                print(f"✗ Error registering CSV {csv_id}: {e}")
                raise
    
    @staticmethod
    def create_table(csv_id: str, schema: Dict[str, str]) -> str:
        """
        Create a MySQL table from CSV schema using SQLAlchemy.
        
        Args:
            csv_id: UUID of the CSV file
            schema: Dictionary mapping column names to types
            
        Returns:
            Table name created
            
        Raises:
            SQLAlchemyError: If table creation fails
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        db = get_db()
        
        try:
            metadata = MetaData()
            
            # Define columns
            columns = [
                Column('id', Integer, primary_key=True, autoincrement=True),
                Column('csv_id', String(36))
            ]
            
            for col_name, col_type in schema.items():
                safe_col_name = CSVStorage._sanitize_column_name(col_name)
                sa_type = CSVStorage._map_csv_type_to_sqlalchemy(col_type)
                columns.append(Column(safe_col_name, sa_type))
            
            # Define table object
            table = Table(table_name, metadata, *columns)
            
            # Drop table if exists and create new one
            # We use the engine directly for DDL operations
            table.drop(db.engine, checkfirst=True)
            table.create(db.engine)
            
            print(f"✓ Created table `{table_name}` with {len(schema)} columns")
            return table_name
            
        except SQLAlchemyError as e:
            print(f"✗ Error creating table `{table_name}`: {e}")
            raise
    
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
            SQLAlchemyError: If data insertion fails
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        db = get_db()
        
        # Reflect the table to get the Table object
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.engine)
        
        rows_inserted = 0
        
        with db as session:
            try:
                # Read CSV file
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    
                    original_columns = list(schema.keys())
                    batch = []
                    batch_size = 1000
                    
                    for row in reader:
                        # Prepare row dictionary with sanitized column names
                        row_data = {'csv_id': csv_id}
                        
                        for col in original_columns:
                            safe_col = CSVStorage._sanitize_column_name(col)
                            value = row.get(col, None)
                            
                            # Convert based on type
                            if value is None or value == '':
                                row_data[safe_col] = None
                            elif schema[col] == 'int':
                                try:
                                    row_data[safe_col] = int(value)
                                except (ValueError, TypeError):
                                    row_data[safe_col] = None
                            elif schema[col] == 'float':
                                try:
                                    row_data[safe_col] = float(value)
                                except (ValueError, TypeError):
                                    row_data[safe_col] = None
                            elif schema[col] == 'bool':
                                row_data[safe_col] = value.lower() in ('true', 'yes', '1')
                            else:
                                row_data[safe_col] = str(value)
                        
                        batch.append(row_data)
                        
                        # Execute batch when it reaches batch_size
                        if len(batch) >= batch_size:
                            session.execute(table.insert(), batch)
                            rows_inserted += len(batch)
                            batch = []
                    
                    # Insert remaining rows
                    if batch:
                        session.execute(table.insert(), batch)
                        rows_inserted += len(batch)
                    
                    # Commit happens on exit
                    print(f"✓ Inserted {rows_inserted} rows into `{table_name}`")
                    return rows_inserted
                    
            except SQLAlchemyError as e:
                # Automatic rollback on exception
                print(f"✗ Error inserting data into `{table_name}`: {e}")
                raise
    
    @staticmethod
    def get_table_schema(csv_id: str) -> Dict[str, str]:
        """
        Retrieve schema from MySQL table by inspecting column types.
        
        Args:
            csv_id: UUID of the CSV file
            
        Returns:
            Dictionary mapping column names to types (int, float, bool, string)
            
        Raises:
            SQLAlchemyError: If query fails or table doesn't exist
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        db = get_db()
        
        try:
            inspector = inspect(db.engine)
            if not inspector.has_table(table_name):
                raise ValueError(f"Table `{table_name}` not found")
            
            columns = inspector.get_columns(table_name)
            
            # Map SQLAlchemy types back to our schema types
            schema = {}
            
            for col in columns:
                col_name = col['name']
                if col_name in ('id', 'csv_id'):
                    continue
                
                type_name = str(col['type']).lower()
                
                if 'int' in type_name or 'integer' in type_name:
                    schema_type = 'int'
                elif 'bool' in type_name or 'tinyint' in type_name:
                    # MySQL often treats boolean as tinyint(1)
                    schema_type = 'bool'
                elif 'float' in type_name or 'double' in type_name or 'numeric' in type_name:
                    schema_type = 'float'
                else:
                    schema_type = 'string'
                    
                schema[col_name] = schema_type
            
            if not schema:
                # This could happen if only id and csv_id exist
                 pass 
                 
            return schema
            
        except SQLAlchemyError as e:
            print(f"✗ Error retrieving schema from `{table_name}`: {e}")
            raise
    
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
            SQLAlchemyError: If query fails
        """
        table_name = CSVStorage._sanitize_table_name(csv_id)
        db = get_db()
        
        with db as session:
            try:
                # Use quoted table name to prevent SQL injection (though we sanitize it)
                # In SQLAlchemy Core, we should usually use a Table object
                # But for simple SELECT * with limit/offset, text is efficient
                query = text(f"SELECT * FROM `{table_name}` LIMIT :limit OFFSET :offset")
                result = session.execute(query, {"limit": limit, "offset": offset})
                
                # Convert to list of dicts
                rows = [dict(row._mapping) for row in result]
                return rows
                
            except SQLAlchemyError as e:
                print(f"✗ Error retrieving data from `{table_name}`: {e}")
                raise
