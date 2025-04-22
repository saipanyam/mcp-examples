# sampling_client.py
import asyncio
from typing import Optional, Dict, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

class SamplingMcpClient:
    def __init__(self, api_key: str):
        """Initialize the client with an Anthropic API key."""
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic(api_key=api_key)
    
    async def connect_to_server(self, server_path: str):
        """Connect to the MCP server."""
        # Configure server connection parameters
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )
        
        # Connect to the server
        streams = await stdio_client(server_params)
        self.stdio, self.write = streams
        self.session = ClientSession(self.stdio, self.write)
        
        # Initialize the session (includes capability negotiation)
        init_result = await self.session.initialize(
            sampling_handler=self.handle_sampling_request  # Register sampling handler
        )
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("Connected to server with tools:", [tool.name for tool in tools])
        
        return tools
    
    async def handle_sampling_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a sampling request from the server."""
        print("\nReceived sampling request from server:")
        print(f"System prompt: {request.get('systemPrompt', 'None')}")
        
        # Extract the user's message
        messages = request.get('messages', [])
        if not messages:
            return {"error": "No messages provided in sampling request"}
        
        user_message = next((m for m in messages if m.get('role') == 'user'), None)
        if not user_message or 'content' not in user_message:
            return {"error": "No user message found in sampling request"}
        
        content = user_message.get('content', {})
        text = content.get('text', '') if isinstance(content, dict) else str(content)
        
        print(f"Query: {text}")
        
        # Use Anthropic to generate the response
        try:
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=request.get('maxTokens', 500),
                messages=[{"role": "user", "content": text}],
                system=request.get('systemPrompt')
            )
            
            # Extract and return the response
            response_text = response.content[0].text
            print(f"Generated response of {len(response_text)} characters")
            
            return {
                "model": "claude-3-opus-20240229",
                "role": "assistant",
                "content": {
                    "type": "text",
                    "text": response_text
                }
            }
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return {
                "model": "error",
                "role": "assistant",
                "content": {
                    "type": "text",
                    "text": f"Error generating response: {str(e)}"
                }
            }
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the connected server."""
        if not self.session:
            return "Not connected to server."
        
        print(f"\nCalling tool: {tool_name}")
        print(f"With arguments: {arguments}")
        
        # Call the tool
        response = await self.session.call_tool(
            name=tool_name,
            arguments=arguments
        )
        
        # Extract content from response
        if hasattr(response, 'content') and response.content:
            # Usually, content is a list of content items
            content_text = []
            for item in response.content:
                if hasattr(item, 'text'):
                    content_text.append(item.text)
            
            return "\n".join(content_text)
        
        return str(response)
    
    async def cleanup(self):
        """Close the connection to the server."""
        if self.session:
            try:
                await self.session.close()
                print("Connection closed")
            except Exception as e:
                print(f"Error closing connection: {str(e)}")

async def demo_sampling():
    # Replace with your actual API key
    client = SamplingMcpClient("YOUR_ANTHROPIC_API_KEY")
    
    try:
        # Connect to the server
        await client.connect_to_server("sampling_server.py")
        
        # Call the creative writer tool
        result1 = await client.call_tool(
            "creative_writer", 
            {"topic": "space exploration", "style": "poetic"}
        )
        print("\nCreative Writing Result:")
        print(result1)
        
        # Call the text summarization tool
        long_text = """
        The Model Context Protocol (MCP) is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It defines a consistent interface for tools, resources, and prompts, enabling seamless integration between LLMs and various data sources or capabilities. MCP allows developers to build applications that can leverage the intelligence of LLMs while maintaining control over data access and execution. The protocol supports features like resource access, tool execution, prompt templates, and model sampling, all through a standardized communication format.
        """
        
        result2 = await client.call_tool(
            "summarize_text",
            {"text": long_text}
        )
        print("\nSummarization Result:")
        print(result2)
        
    finally:
        # Clean up resources
        await client.cleanup()

if __name__ == "__main__":
    asyncio.run(demo_sampling())
