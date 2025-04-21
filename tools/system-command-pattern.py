import os
import subprocess
import pathlib
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("system-command-server")

# Define safe working directory
SAFE_DIR = pathlib.Path("/safe/working/directory")

@mcp.tool()
async def list_files(directory: str = ".") -> str:
    """List files in a directory relative to the safe working directory.
    
    Args:
        directory: Directory path (relative to safe working directory)
    """
    # Validate and sanitize directory path
    dir_path = pathlib.Path(directory)
    if dir_path.is_absolute():
        return "Error: Absolute paths are not allowed. Please use relative paths."
    
    # Resolve the full path within the safe directory
    full_path = (SAFE_DIR / dir_path).resolve()
    
    # Ensure the path is still within the safe directory
    if not str(full_path).startswith(str(SAFE_DIR)):
        return "Error: Path traversal outside of safe directory is not allowed."
    
    # Check if the directory exists
    if not full_path.exists():
        return f"Error: Directory '{directory}' does not exist."
    
    if not full_path.is_dir():
        return f"Error: '{directory}' is not a directory."
    
    # List files and directories
    files = []
    directories = []
    
    for item in full_path.iterdir():
        if item.is_file():
            files.append(item.name)
        elif item.is_dir():
            directories.append(item.name + "/")
    
    # Format output
    output = []
    if directories:
        output.append("Directories:")
        output.extend([f"  {d}" for d in sorted(directories)])
    
    if files:
        output.append("Files:")
        output.extend([f"  {f}" for f in sorted(files)])
    
    if not output:
        return "The directory is empty."
    
    return "\n".join(output)
