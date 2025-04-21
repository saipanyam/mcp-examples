from mcp.server.fastmcp import FastMCP
import asyncio
import uuid
import time
import threading

mcp = FastMCP("notification-server")

# Storage for tasks and notifications
tasks = {}
notifications = {}

def background_task(task_id, duration):
    """Simulates a long-running task with progress updates."""
    total_steps = 5
    
    for step in range(1, total_steps + 1):
        # Sleep for a portion of the total duration
        time.sleep(duration / total_steps)
        
        # Update progress
        progress = int((step / total_steps) * 100)
        notification_id = str(uuid.uuid4())
        
        notifications[notification_id] = {
            "task_id": task_id,
            "timestamp": time.time(),
            "message": f"Task {task_id} progress: {progress}%",
            "progress": progress,
            "read": False
        }
    
    # Final notification for completion
    notification_id = str(uuid.uuid4())
    notifications[notification_id] = {
        "task_id": task_id,
        "timestamp": time.time(),
        "message": f"Task {task_id} completed successfully.",
        "progress": 100,
        "read": False
    }
    
    # Mark task as complete
    tasks[task_id]["status"] = "completed"
    tasks[task_id]["completed_at"] = time.time()

@mcp.tool()
async def start_background_task(duration_seconds: int = 10) -> str:
    """Start a long-running background task that generates notifications.
    
    Args:
        duration_seconds: How long the task should run
    """
    task_id = str(uuid.uuid4())
    
    tasks[task_id] = {
        "created_at": time.time(),
        "status": "running",
        "duration": duration_seconds
    }
    
    # Start background thread for the task
    thread = threading.Thread(target=background_task, args=(task_id, duration_seconds))
    thread.daemon = True
    thread.start()
    
    return f"Background task started with ID: {task_id}. The task will run for approximately {duration_seconds} seconds."

@mcp.tool()
async def get_task_status(task_id: str) -> str:
    """Get the status of a background task.
    
    Args:
        task_id: Task identifier
    """
    if task_id not in tasks:
        return f"Error: Task {task_id} not found."
    
    task = tasks[task_id]
    
    status = f"Task {task_id} status: {task['status'].upper()}\n"
    status += f"Created at: {time.ctime(task['created_at'])}\n"
    
    if task["status"] == "completed":
        duration = task["completed_at"] - task["created_at"]
        status += f"Completed at: {time.ctime(task['completed_at'])}\n"
        status += f"Actual duration: {duration:.2f} seconds"
    
    return status

@mcp.tool()
async def get_notifications(task_id: str = None, unread_only: bool = True) -> str:
    """Get notifications, optionally filtered by task ID and read status.
    
    Args:
        task_id: Optional task identifier to filter notifications
        unread_only: Whether to only return unread notifications
    """
    filtered_notifications = []
    
    for notif_id, notif in notifications.items():
        if task_id and notif["task_id"] != task_id:
            continue
        
        if unread_only and notif["read"]:
            continue
        
        filtered_notifications.append({
            "id": notif_id,
            **notif
        })
    
    if not filtered_notifications:
        return "No matching notifications found."
    
    # Sort by timestamp
    filtered_notifications.sort(key=lambda n: n["timestamp"])
    
    # Format notifications
    formatted = []
    for notif in filtered_notifications:
        formatted.append(
            f"Notification ID: {notif['id']}\n"
            f"Task ID: {notif['task_id']}\n"
            f"Time: {time.ctime(notif['timestamp'])}\n"
            f"Message: {notif['message']}\n"
            f"Progress: {notif['progress']}%\n"
        )
        
        # Mark as read
        notifications[notif["id"]]["read"] = True
    
    return f"Found {len(formatted)} notifications:\n\n" + "\n".join(formatted)
