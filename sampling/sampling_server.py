# sampling_server.py
from mcp.server.fastmcp import FastMCP

# Initialize the server
mcp = FastMCP("sampling-demo-server")

@mcp.tool()
async def creative_writer(topic: str, style: str = "informative", exchange=None) -> str:
    """Generate creative text about a topic using the client's LLM.
    
    Args:
        topic: The topic to write about
        style: Writing style (informative, poetic, humorous)
    """
    # Check if client supports sampling
    if not exchange or not hasattr(exchange, "client_capabilities") or not exchange.client_capabilities.sampling:
        return "This tool requires a client that supports sampling."
    
    # Create sampling request
    request = {
        "messages": [{
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Write a {style} passage about {topic}."
            }
        }],
        "systemPrompt": f"You are a creative writer specializing in {style} content.",
        "includeContext": "thisServer",
        "maxTokens": 300
    }
    
    try:
        # Request sampling from client
        result = await exchange.create_message(request)
        return f"Generated {style} content about '{topic}':\n\n{result.content.text}"
    except Exception as e:
        return f"Error during sampling: {str(e)}"

@mcp.tool()
async def summarize_text(text: str, exchange=None) -> str:
    """Summarize a text using the client's LLM.
    
    Args:
        text: Text to summarize
    """
    if not exchange or not hasattr(exchange, "client_capabilities") or not exchange.client_capabilities.sampling:
        return "This tool requires a client that supports sampling."
    
    # Create sampling request
    request = {
        "messages": [{
            "role": "user",
            "content": {
                "type": "text",
                "text": f"Please summarize the following text in 2-3 sentences:\n\n{text}"
            }
        }],
        "systemPrompt": "You are a helpful assistant that creates concise summaries.",
        "maxTokens": 150
    }
    
    try:
        result = await exchange.create_message(request)
        return f"Summary:\n\n{result.content.text}"
    except Exception as e:
        return f"Error during sampling: {str(e)}"

if __name__ == "__main__":
    # Run the server on stdio transport
    mcp.run(transport='stdio')
