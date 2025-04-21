import pandas as pd
import io
import json
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("data-processing-server")

@mcp.tool()
async def analyze_csv(csv_data: str, operations: list) -> str:
    """Analyze CSV data with specified operations.
    
    Args:
        csv_data: CSV content as a string
        operations: List of analysis operations to perform
    """
    valid_operations = ["summary", "head", "filter", "sort", "groupby"]
    
    # Validate operations
    for op in operations:
        if op not in valid_operations:
            return f"Invalid operation: {op}. Valid operations are: {', '.join(valid_operations)}"
    
    try:
        # Parse CSV
        df = pd.read_csv(io.StringIO(csv_data))
        
        results = {}
        
        # Perform requested operations
        if "summary" in operations:
            results["summary"] = {
                "rows": len(df),
                "columns": len(df.columns),
                "column_types": {col: str(dtype) for col, dtype in df.dtypes.items()},
                "missing_values": df.isna().sum().to_dict()
            }
        
        if "head" in operations:
            results["head"] = df.head(5).to_dict(orient="records")
        
        # Add more operations as needed
        
        return json.dumps(results, indent=2)
    
    except Exception as e:
        return f"Error processing CSV data: {str(e)}"
