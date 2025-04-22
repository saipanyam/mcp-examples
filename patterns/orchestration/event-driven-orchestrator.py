from mcp.server.fastmcp import FastMCP
import asyncio
import time
import uuid

mcp = FastMCP("event-orchestration-server")

# Event bus for inter-server communication
event_queue = asyncio.Queue()
active_workflows = {}

@mcp.tool()
async def start_event_driven_workflow(initial_data: dict, workflow_type: str) -> str:
    """Start an event-driven workflow that coordinates across servers."""
    # Generate workflow ID
    workflow_id = str(uuid.uuid4())
    
    # Initialize workflow state
    workflow_state = {
        "id": workflow_id,
        "type": workflow_type,
        "status": "initializing",
        "start_time": time.time(),
        "data": initial_data,
        "steps_completed": [],
        "current_step": None,
        "next_steps": [],
        "results": {}
    }
    
    # Determine initial steps based on workflow type
    if workflow_type == "data_processing":
        workflow_state["next_steps"] = [
            {"server": "data", "tool": "load_data", "parameters": {"source": initial_data["source"]}}
        ]
    elif workflow_type == "analysis":
        workflow_state["next_steps"] = [
            {"server": "data", "tool": "fetch_dataset", "parameters": {"dataset_id": initial_data["dataset_id"]}}
        ]
    elif workflow_type == "report_generation":
        workflow_state["next_steps"] = [
            {"server": "data", "tool": "get_report_data", "parameters": {"report_type": initial_data["report_type"]}}
        ]
    else:
        return f"Unknown workflow type: {workflow_type}"
    
    # Store workflow state
    active_workflows[workflow_id] = workflow_state
    
    # Start the workflow by posting initial event
    await event_queue.put({
        "type": "workflow_started",
        "workflow_id": workflow_id
    })
    
    # Start event processor if not already running
    asyncio.create_task(process_events())
    
    return f"Workflow started with ID: {workflow_id}. Use check_workflow_status tool to monitor progress."

@mcp.tool()
async def check_workflow_status(workflow_id: str) -> str:
    """Check the status of a running workflow."""
    if workflow_id not in active_workflows:
        return f"Workflow {workflow_id} not found."
    
    workflow = active_workflows[workflow_id]
    
    return f"""
    Workflow ID: {workflow_id}
    Type: {workflow["type"]}
    Status: {workflow["status"]}
    Steps completed: {len(workflow["steps_completed"])}
    Current step: {workflow["current_step"]}
    Pending steps: {len(workflow["next_steps"])}
    Run time: {time.time() - workflow["start_time"]:.2f} seconds
    """

async def process_events():
    """Process events from the event queue and orchestrate workflows."""
    while True:
        # Get next event
        event = await event_queue.get()
        
        # Process based on event type
        if event["type"] == "workflow_started":
            await handle_workflow_started(event["workflow_id"])
        elif event["type"] == "step_completed":
            await handle_step_completed(event["workflow_id"], event["result"])
        elif event["type"] == "error":
            await handle_error(event["workflow_id"], event["error"])
        elif event["type"] == "workflow_completed":
            await handle_workflow_completed(event["workflow_id"])
        
        # Mark event as processed
        event_queue.task_done()

async def handle_workflow_started(workflow_id):
    """Handle workflow started event by executing the first step."""
    workflow = active_workflows[workflow_id]
    
    if not workflow["next_steps"]:
        # No steps to execute
        workflow["status"] = "completed"
        await event_queue.put({
            "type": "workflow_completed",
            "workflow_id": workflow_id
        })
        return
    
    # Get the next step
    next_step = workflow["next_steps"].pop(0)
    workflow["current_step"] = f"{next_step['server']}.{next_step['tool']}"
    workflow["status"] = "running"
    
    # Execute the step
    try:
        server = await get_server_connection(next_step["server"])
        result = await server.call_tool(next_step["tool"], next_step["parameters"])
        
        # Post completion event
        await event_queue.put({
            "type": "step_completed",
            "workflow_id": workflow_id,
            "result": result
        })
    except Exception as e:
        # Post error event
        await event_queue.put({
            "type": "error",
            "workflow_id": workflow_id,
            "error": str(e)
        })

async def handle_step_completed(workflow_id, result):
    """Handle step completed event and determine next steps."""
    workflow = active_workflows[workflow_id]
    
    # Record completed step
    completed_step = workflow["current_step"]
    workflow["steps_completed"].append(completed_step)
    workflow["results"][completed_step] = result
    workflow["current_step"] = None
    
    # Determine next steps based on result and workflow type
    if workflow["type"] == "data_processing":
        if "data.load_data" in workflow["steps_completed"]:
            # After loading data, process it
            workflow["next_steps"].append({
                "server": "data", 
                "tool": "process_data", 
                "parameters": {
                    "data": result["data"],
                    "operations": workflow["data"].get("operations", ["clean", "transform"])
                }
            })
        elif "data.process_data" in workflow["steps_completed"]:
            # After processing, analyze
            workflow["next_steps"].append({
                "server": "analysis", 
                "tool": "analyze_processed_data", 
                "parameters": {
                    "data": result["processed_data"],
                    "metrics": workflow["data"].get("metrics", ["summary"])
                }
            })
    
    # Continue workflow execution
    if workflow["next_steps"]:
        # Continue with next step
        await handle_workflow_started(workflow_id)
    else:
        # No more steps, complete workflow
        workflow["status"] = "completed"
        await event_queue.put({
            "type": "workflow_completed",
            "workflow_id": workflow_id
        })

async def handle_error(workflow_id, error):
    """Handle error event in workflow."""
    workflow = active_workflows[workflow_id]
    workflow["status"] = "error"
    workflow["error"] = error
    
    # Perform error recovery if possible
    if workflow["type"] == "data_processing" and "retry_on_error" in workflow["data"]:
        if workflow["data"]["retry_on_error"]:
            # Reset to last successful state and retry
            workflow["status"] = "retrying"
            workflow["next_steps"].insert(0, {
                "server": workflow["current_step"].split(".")[0],
                "tool": workflow["current_step"].split(".")[1],
                "parameters": workflow["data"].get("retry_parameters", {})
            })
            
            # Continue workflow
            await handle_workflow_started(workflow_id)

async def handle_workflow_completed(workflow_id):
    """Handle workflow completed event."""
    workflow = active_workflows[workflow_id]
    workflow["end_time"] = time.time()
    workflow["duration"] = workflow["end_time"] - workflow["start_time"]
    
    # Perform any cleanup or notification
    # Could potentially start dependent workflows here
