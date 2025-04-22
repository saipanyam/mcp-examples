# Client code orchestrating multiple servers
async def client_orchestrated_workflow():
    # Connect to specialized servers
    database_client = await connect_to_server("database_server.py")
    analysis_client = await connect_to_server("analysis_server.py") 
    report_client = await connect_to_server("report_server.py")
    
    # Fetch data from database server
    raw_data = await database_client.call_tool("query_database", {
        "query": "SELECT * FROM sales WHERE region = 'Northeast' AND date > '2024-01-01'"
    })
    
    # Process data with analysis server
    analysis_results = await analysis_client.call_tool("analyze_trends", {
        "data": raw_data,
        "metrics": ["growth_rate", "seasonality", "regional_comparison"]
    })
    
    # Generate report with report server
    final_report = await report_client.call_tool("generate_sales_report", {
        "analysis": analysis_results,
        "template": "executive_summary",
        "include_visualizations": True
    })
    
    return final_report
