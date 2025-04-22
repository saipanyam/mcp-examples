from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

mcp = FastMCP("orchestration-server")

# Server registry
SERVER_REGISTRY = {
    "data": {"command": "python", "args": ["data_server.py"]},
    "analysis": {"command": "python", "args": ["analysis_server.py"]},
    "visualization": {"command": "python", "args": ["visualization_server.py"]},
    "reporting": {"command": "python", "args": ["reporting_server.py"]}
}

# Server connection cache
active_connections = {}

async def get_server_connection(server_name):
    """Get or create a connection to a specified server."""
    if server_name in active_connections:
        return active_connections[server_name]
    
    if server_name not in SERVER_REGISTRY:
        raise ValueError(f"Unknown server: {server_name}")
    
    server_config = SERVER_REGISTRY[server_name]
    server_params = StdioServerParameters(
        command=server_config["command"],
        args=server_config["args"],
        env=None
    )
    
    stdio_transport = await stdio_client(server_params)
    session = ClientSession(stdio_transport[0], stdio_transport[1])
    await session.initialize()
    
    active_connections[server_name] = session
    return session

@mcp.tool()
async def execute_data_analysis_workflow(data_source: str, analysis_params: dict, output_format: str = "pdf") -> str:
    """Execute a complete data analysis workflow across multiple specialized servers."""
    
    # Step 1: Data retrieval and preparation
    data_session = await get_server_connection("data")
    data_result = await data_session.call_tool("fetch_and_prepare_data", {
        "source": data_source,
        "preprocessing": analysis_params.get("preprocessing", ["clean", "normalize"])
    })
    
    # Check for errors and adjust workflow if needed
    if data_result.get("warnings"):
        # Handle warnings and potentially modify subsequent steps
        analysis_params["handle_missing"] = True
    
    # Step 2: Run appropriate analyses
    analysis_session = await get_server_connection("analysis")
    analysis_result = await analysis_session.call_tool("analyze_data", {
        "data": data_result["prepared_data"],
        "metrics": analysis_params.get("metrics", ["summary", "trends"]),
        "models": analysis_params.get("models", ["regression"])
    })
    
    # Step 3: Create visualizations
    viz_session = await get_server_connection("visualization")
    viz_result = await viz_session.call_tool("create_visualizations", {
        "data": data_result["prepared_data"],
        "analysis": analysis_result,
        "types": analysis_params.get("visualizations", ["bar", "line", "scatter"])
    })
    
    # Step 4: Generate final report
    report_session = await get_server_connection("reporting")
    report_result = await report_session.call_tool("generate_report", {
        "title": f"Analysis Report: {data_source}",
        "data_summary": data_result["summary"],
        "analysis_results": analysis_result,
        "visualizations": viz_result,
        "format": output_format
    })
    
    return f"Analysis workflow completed. Report available at: {report_result['report_url']}"
