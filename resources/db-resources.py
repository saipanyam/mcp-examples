import sqlite3
import json
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("database-resources")

# Initialize database - In real applications, use connection pooling
DB_PATH = "example.db"

# Initialize example database with sample data
def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        signup_date TEXT
    )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        description TEXT,
        price REAL
    )
    ''')
    
    # Insert sample data
    cursor.execute('INSERT OR IGNORE INTO customers VALUES (1, "John Doe", "john@example.com", "2023-01-15")')
    cursor.execute('INSERT OR IGNORE INTO customers VALUES (2, "Jane Smith", "jane@example.com", "2023-03-20")')
    cursor.execute('INSERT OR IGNORE INTO products VALUES (1, "Basic Widget", "Standard widget model", 19.99)')
    cursor.execute('INSERT OR IGNORE INTO products VALUES (2, "Premium Widget", "Upgraded widget with features", 39.99)')
    
    conn.commit()
    conn.close()

# Initialize database
init_database()

@mcp.resource(
    uri="db://table/{table}",
    name="Database Table",
    description="Get all records from a database table"
)
async def get_table(table):
    """Get all records from a database table."""
    # Validate table name for security (prevent SQL injection)
    allowed_tables = ["customers", "products"]
    if table not in allowed_tables:
        return f"Access denied: Table '{table}' is not accessible"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get all records
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        result = []
        for row in rows:
            row_dict = {columns[i]: row[i] for i in range(len(columns))}
            result.append(row_dict)
        
        conn.close()
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Database error: {str(e)}"

@mcp.resource(
    uri="db://record/{table}/{id}",
    name="Database Record",
    description="Get a specific record from a database table"
)
async def get_record(table, id):
    """Get a specific record from a database table."""
    # Validate table name for security
    allowed_tables = ["customers", "products"]
    if table not in allowed_tables:
        return f"Access denied: Table '{table}' is not accessible"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [col[1] for col in cursor.fetchall()]
        
        # Get specific record
        cursor.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
        row = cursor.fetchone()
        
        if not row:
            return f"Record not found: {table}/{id}"
        
        # Convert to dictionary
        result = {columns[i]: row[i] for i in range(len(columns))}
        
        conn.close()
        return json.dumps(result, indent=2)
    
    except Exception as e:
        return f"Database error: {str(e)}"

@mcp.resource(
    uri="db://schema/{table}",
    name="Database Schema",
    description="Get schema information for a database table"
)
async def get_schema(table):
    """Get schema information for a database table."""
    # Validate table name for security
    allowed_tables = ["customers", "products"]
    if table not in allowed_tables:
        return f"Access denied: Table '{table}' is not accessible"
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Get table schema
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        
        # Format schema information
        schema = []
        for col in columns:
            schema.append({
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": col[3],
                "default_value": col[4],
                "pk": col[5]
            })
        
        conn.close()
        return json.dumps(schema, indent=2)
    
    except Exception as e:
        return f"Database error: {str(e)}"

if __name__ == "__main__":
    mcp.run(transport='stdio')
