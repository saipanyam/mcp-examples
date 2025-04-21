from mcp.server.fastmcp import FastMCP
import uuid
import json

mcp = FastMCP("chunked-processing-server")

# Storage for chunked uploads
chunked_data = {}

@mcp.tool()
async def start_chunked_upload(content_type: str) -> str:
    """Start a new chunked upload process.
    
    Args:
        content_type: Type of content being uploaded
    """
    upload_id = str(uuid.uuid4())
    
    chunked_data[upload_id] = {
        "content_type": content_type,
        "chunks": [],
        "complete": False
    }
    
    return f"Chunked upload started with ID: {upload_id}"

@mcp.tool()
async def upload_chunk(upload_id: str, chunk_index: int, chunk_data: str, is_last: bool) -> str:
    """Upload a chunk of data.
    
    Args:
        upload_id: Upload identifier
        chunk_index: Index of the chunk (0-based)
        chunk_data: Content of the chunk
        is_last: Whether this is the last chunk
    """
    # Validate upload
    if upload_id not in chunked_data:
        return f"Error: Upload ID {upload_id} not found."
    
    if chunked_data[upload_id]["complete"]:
        return f"Error: Upload {upload_id} is already complete."
    
    # Store chunk
    upload = chunked_data[upload_id]
    
    # Ensure chunks list is large enough
    while len(upload["chunks"]) <= chunk_index:
        upload["chunks"].append(None)
    
    # Store the chunk
    upload["chunks"][chunk_index] = chunk_data
    
    if is_last:
        upload["complete"] = True
        
        # Check if all chunks are uploaded
        if None in upload["chunks"]:
            return f"Error: Upload {upload_id} marked as complete but missing chunks. Expected {len(upload['chunks'])} chunks."
    
    return f"Chunk {chunk_index} uploaded successfully for upload {upload_id}."

@mcp.tool()
async def process_chunked_upload(upload_id: str) -> str:
    """Process a completed chunked upload.
    
    Args:
        upload_id: Upload identifier
    """
    # Validate upload
    if upload_id not in chunked_data:
        return f"Error: Upload ID {upload_id} not found."
    
    upload = chunked_data[upload_id]
    
    if not upload["complete"]:
        return f"Error: Upload {upload_id} is not complete."
    
    # Combine chunks
    combined_data = "".join(upload["chunks"])
    
    # Process based on content type
    if upload["content_type"] == "json":
        try:
            parsed_data = json.loads(combined_data)
            item_count = len(parsed_data) if isinstance(parsed_data, list) else 1
            return f"Successfully processed JSON with {item_count} items."
        except json.JSONDecodeError:
            return "Error: Invalid JSON data."
    
    elif upload["content_type"] == "csv":
        lines = combined_data.strip().split("\n")
        return f"Successfully processed CSV with {len(lines)} lines (including header)."
    
    else:
        return f"Successfully processed {len(combined_data)} bytes of {upload['content_type']} data."
