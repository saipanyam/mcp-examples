# Proxy server that unifies access to multiple specialized servers
from mcp.server.fastmcp import FastMCP
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

mcp = FastMCP("ai-research-proxy")

# Server connections cache
server_connections = {}

async def get_server_connection(server_name):
    """Get or create a connection to a specific server."""
    if server_name in server_connections:
        return server_connections[server_name]
    
    # Server configurations
    server_configs = {
        "papers": ["python", "research_papers_server.py"],
        "data": ["python", "research_data_server.py"],
        "citations": ["python", "citation_generator_server.py"]
    }
    
    if server_name not in server_configs:
        raise ValueError(f"Unknown server: {server_name}")
    
    command, script = server_configs[server_name]
    
    # Create connection
    server_params = StdioServerParameters(
        command=command,
        args=[script],
        env=None
    )
    
    streams = await stdio_client(server_params)
    session = ClientSession(streams[0], streams[1])
    await session.initialize()
    
    # Cache connection
    server_connections[server_name] = session
    return session

@mcp.tool()
async def search_research_papers(query: str, filters: dict = None) -> list:
    """Search academic papers based on query and filters."""
    papers_client = await get_server_connection("papers")
    return await papers_client.call_tool("search_papers", {
        "query": query,
        "filters": filters or {}
    })

@mcp.tool()
async def analyze_research_data(dataset_id: str, analysis_type: str) -> dict:
    """Analyze research datasets."""
    data_client = await get_server_connection("data")
    return await data_client.call_tool("analyze_dataset", {
        "dataset_id": dataset_id,
        "analysis_type": analysis_type
    })

@mcp.tool()
async def generate_citation(paper_id: str, style: str = "APA") -> str:
    """Generate properly formatted citation for a paper."""
    citations_client = await get_server_connection("citations")
    return await citations_client.call_tool("format_citation", {
        "paper_id": paper_id,
        "style": style
    })

@mcp.tool()
async def comprehensive_research(topic: str, max_papers: int = 5) -> str:
    """Run a comprehensive research workflow combining multiple servers."""
    # Step 1: Find relevant papers
    papers_client = await get_server_connection("papers")
    papers = await papers_client.call_tool("search_papers", {
        "query": topic,
        "filters": {"max_results": max_papers, "sort_by": "relevance"}
    })
    
    # Step 2: Extract key datasets from papers
    datasets = []
    for paper in papers:
        if "datasets" in paper:
            datasets.extend(paper["datasets"])
    
    # Step 3: Analyze datasets if available
    analysis_results = []
    if datasets:
        data_client = await get_server_connection("data")
        for dataset_id in datasets[:3]:  # Limit to 3 datasets
            analysis = await data_client.call_tool("analyze_dataset", {
                "dataset_id": dataset_id,
                "analysis_type": "summary"
            })
            analysis_results.append(analysis)
    
    # Step 4: Generate citations
    citations = []
    citations_client = await get_server_connection("citations")
    for paper in papers:
        citation = await citations_client.call_tool("format_citation", {
            "paper_id": paper["id"],
            "style": "APA"
        })
        citations.append(citation)
    
    # Compile results
    report = f"# Research Report: {topic}\n\n"
    report += "## Key Papers\n"
    for i, paper in enumerate(papers):
        report += f"{i+1}. {paper['title']} ({paper['year']})\n"
        report += f"   Authors: {paper['authors']}\n"
        report += f"   Summary: {paper['abstract'][:150]}...\n\n"
    
    if analysis_results:
        report += "## Dataset Analysis\n"
        for analysis in analysis_results:
            report += f"- {analysis['name']}: {analysis['key_findings']}\n"
    
    report += "## References\n"
    for citation in citations:
        report += f"- {citation}\n"
    
    return report
