import os
import json
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("filesystem-resources")

# Define the root directory - adjust to your system
# Can also be implemented as Roots - Sent by the client
ROOT_DIR = "/safe/read/directory"

@mcp.resource(
    uri="file://read/{path}",import os
import json
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("filesystem-resources")

# Define the root directory - adjust to your system
# Can also be implemented as Roots - Sent by the client
ROOT_DIR = "/safe/read/directory"

@mcp.resource(
    uri="file://read/{path}",
    name="File Reader",
    description="Read files from the filesystem"
)
async def read_file(path):
    """Read a file from the filesystem."""
    # Validate path for security
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith(".."):
        return "Access denied: Cannot access parent directories"
    
    full_path = os.path.join(ROOT_DIR, normalized_path)
    
    # Check if the path exists
    if not os.path.exists(full_path):
        return f"File not found: {path}"
    
    # Check if it's a directory
    if os.path.isdir(full_path):
        # List directory contents
        files = os.listdir(full_path)
        return json.dumps({
            "type": "directory",
            "path": path,
            "contents": files
        }, indent=2)
    
    # Try to read the file
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.resource(
    uri="file://info/{path}",
    name="File Info",
    description="Get metadata about files and directories"
)
async def file_info(path):
    """Get metadata about a file or directory."""
    # Validate path for security
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith(".."):
        return "Access denied: Cannot access parent directories"
    
    full_path = os.path.join(ROOT_DIR, normalized_path)
    
    # Check if the path exists
    if not os.path.exists(full_path):
        return f"Path not found: {path}"
    
    # Get file/directory info
    stat_info = os.stat(full_path)
    
    # Basic info
    info = {
        "path": path,
        "full_path": full_path,
        "exists": True,
        "is_file": os.path.isfile(full_path),
        "is_dir": os.path.isdir(full_path),
        "size_bytes": stat_info.st_size,
        "last_modified": stat_info.st_mtime,
        "permissions": stat_info.st_mode
    }
    
    # Return formatted info
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')
    name="File Reader",
    description="Read files from the filesystem"
)
async def read_file(path):
    """Read a file from the filesystem."""
    # Validate path for security
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith(".."):
        return "Access denied: Cannot access parent directories"
    
    full_path = os.path.join(ROOT_DIR, normalized_path)
    
    # Check if the path exists
    if not os.path.exists(full_path):
        return f"File not found: {path}"
    
    # Check if it's a directory
    if os.path.isdir(full_path):
        # List directory contents
        files = os.listdir(full_path)
        return json.dumps({
            "type": "directory",
            "path": path,
            "contents": files
        }, indent=2)
    
    # Try to read the file
    try:
        with open(full_path, 'r') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.resource(
    uri="file://info/{path}",
    name="File Info",
    description="Get metadata about files and directories"
)
async def file_info(path):
    """Get metadata about a file or directory."""
    # Validate path for security
    normalized_path = os.path.normpath(path)
    if normalized_path.startswith(".."):
        return "Access denied: Cannot access parent directories"
    
    full_path = os.path.join(ROOT_DIR, normalized_path)
    
    # Check if the path exists
    if not os.path.exists(full_path):
        return f"Path not found: {path}"
    
    # Get file/directory info
    stat_info = os.stat(full_path)
    
    # Basic info
    info = {
        "path": path,
        "full_path": full_path,
        "exists": True,
        "is_file": os.path.isfile(full_path),
        "is_dir": os.path.isdir(full_path),
        "size_bytes": stat_info.st_size,
        "last_modified": stat_info.st_mtime,
        "permissions": stat_info.st_mode
    }
    
    # Return formatted info
    return json.dumps(info, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')
