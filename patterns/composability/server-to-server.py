# Server-side code that connects to another server
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

mcp = FastMCP("workflow-server")

@mcp.tool()
async def integrated_analytics_workflow(dataset_name: str) -> str:
    """Run an integrated analytics workflow using multiple specialized servers."""
    
    # Connect to data processing server
    data_server_params = StdioServerParameters(
        command="python",
        args=["data_processing_server.py"],
        env=None
    )
    
    async with stdio_client(data_server_params) as (stdio, write):
        data_session = ClientSession(stdio, write)
        await data_session.initialize()
        
        # Fetch and preprocess data
        processed_data = await data_session.call_tool("preprocess_dataset", {
            "name": dataset_name,
            "operations": ["normalize", "remove_outliers", "fill_missing_values"]
        })
        
        # Connect to visualization server
        viz_server_params = StdioServerParameters(
            command="python",
            args=["visualization_server.py"],
            env=None
        )
        
        async with stdio_client(viz_server_params) as (stdio2, write2):
            viz_session = ClientSession(stdio2, write2)
            await viz_session.initialize()
            
            # Generate visualizations
            visualizations = await viz_session.call_tool("create_dashboard", {
                "data": processed_data,
                "chart_types": ["trend", "distribution", "correlation"]
            })
            
            # Combine results
            return f"Analysis complete for {dataset_name}.\n\nProcessed Data Summary:\n{processed_data['summary']}\n\nVisualizations:\n{visualizations}"
