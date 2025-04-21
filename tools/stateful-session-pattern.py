from mcp.server.fastmcp import FastMCP
import uuid
import time

mcp = FastMCP("stateful-session-server")

# Session storage
sessions = {}

@mcp.tool()
async def create_session(ttl_minutes: int = 30) -> str:
    """Create a new session for stateful operations.
    
    Args:
        ttl_minutes: Time-to-live in minutes for session
    """
    session_id = str(uuid.uuid4())
    
    sessions[session_id] = {
        "created_at": time.time(),
        "expires_at": time.time() + (ttl_minutes * 60),
        "data": {},
        "history": []
    }
    
    return f"Session created with ID: {session_id}. This session will expire in {ttl_minutes} minutes."

@mcp.tool()
async def store_value(session_id: str, key: str, value: str) -> str:
    """Store a value in a session.
    
    Args:
        session_id: Session identifier
        key: Key to store the value under
        value: Value to store
    """
    # Validate session
    if session_id not in sessions:
        return f"Error: Session {session_id} not found or expired."
    
    if time.time() > sessions[session_id]["expires_at"]:
        del sessions[session_id]
        return f"Error: Session {session_id} has expired."
    
    # Store value
    sessions[session_id]["data"][key] = value
    sessions[session_id]["history"].append(f"STORE: {key}={value}")
    
    return f"Value stored for key '{key}' in session {session_id}."

@mcp.tool()
async def retrieve_value(session_id: str, key: str) -> str:
    """Retrieve a value from a session.
    
    Args:
        session_id: Session identifier
        key: Key to retrieve
    """
    # Validate session
    if session_id not in sessions:
        return f"Error: Session {session_id} not found or expired."
    
    if time.time() > sessions[session_id]["expires_at"]:
        del sessions[session_id]
        return f"Error: Session {session_id} has expired."
    
    # Retrieve value
    if key not in sessions[session_id]["data"]:
        return f"Error: Key '{key}' not found in session {session_id}."
    
    value = sessions[session_id]["data"][key]
    sessions[session_id]["history"].append(f"RETRIEVE: {key}")
    
    return f"Value for key '{key}': {value}"

@mcp.tool()
async def get_session_history(session_id: str) -> str:
    """Get the history of operations for a session.
    
    Args:
        session_id: Session identifier
    """
    # Validate session
    if session_id not in sessions:
        return f"Error: Session {session_id} not found or expired."
    
    if time.time() > sessions[session_id]["expires_at"]:
        del sessions[session_id]
        return f"Error: Session {session_id} has expired."
    
    # Return history
    history = sessions[session_id]["history"]
    
    if not history:
        return f"No history for session {session_id}."
    
    return f"History for session {session_id}:\n" + "\n".join([f"- {entry}" for entry in history])
