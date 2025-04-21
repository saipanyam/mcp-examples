from mcp.server.fastmcp import FastMCP
import httpx

mcp = FastMCP("api-integration-server")

@mcp.tool()
async def github_search(query: str, result_type: str = "repositories") -> str:
    """Search GitHub for repositories, users, or issues.
    
    Args:
        query: Search query
        result_type: Type of results to return (repositories, users, issues)
    """
    allowed_types = ["repositories", "users", "issues"]
    if result_type not in allowed_types:
        return f"Invalid result_type. Must be one of: {', '.join(allowed_types)}"
    
    # Build GitHub API URL
    url = f"https://api.github.com/search/{result_type}"
    params = {"q": query, "per_page": 5}
    
    # Make API request
    async with httpx.AsyncClient() as client:
        headers = {"Accept": "application/vnd.github.v3+json"}
        response = await client.get(url, params=params, headers=headers)
        
        if response.status_code != 200:
            return f"Error: GitHub API returned status code {response.status_code}"
        
        data = response.json()
        
        # Format results
        results = []
        for item in data["items"]:
            if result_type == "repositories":
                results.append(f"- {item['full_name']}: {item['description'] or 'No description'} ({item['stargazers_count']} stars)")
            elif result_type == "users":
                results.append(f"- {item['login']}: {item['html_url']}")
            elif result_type == "issues":
                results.append(f"- {item['title']} ({item['state']}): {item['html_url']}")
        
        return f"Found {data['total_count']} results. Here are the top {len(results)}:\n\n" + "\n".join(results)
