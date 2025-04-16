import asyncio
from typing import Dict, List, Optional, Any
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from anthropic import Anthropic

class ContentPipelineClient:
    def __init__(self, api_key: str):
        """Initialize the client with an Anthropic API key."""
        self.session: Optional[ClientSession] = None
        self.anthropic = Anthropic(api_key=api_key)
    
    async def connect_to_server(self, server_path: str):
        """Connect to the MCP server containing the content pipeline prompt."""
        # Set up server connection parameters
        server_params = StdioServerParameters(
            command="python",
            args=[server_path],
            env=None
        )
        
        # Connect to the server
        stdio_transport = await stdio_client(server_params)
        self.stdio, self.write = stdio_transport
        self.session = ClientSession(self.stdio, self.write)
        
        # Initialize the session
        await self.session.initialize()
        
        # List available prompts
        response = await self.session.list_prompts()
        prompts = response.prompts
        print("Connected to server with prompts:", [prompt.name for prompt in prompts])
    
    async def run_content_pipeline(self, topic: str, content_type: str):
        """Run the multi-step content pipeline for the specified topic and content type."""
        if not self.session:
            return "Not connected to server."
        
        print(f"\n--- Starting Content Pipeline for '{topic}' ({content_type}) ---\n")
        
        # Get the content_pipeline prompt with our arguments
        prompt_result = await self.session.get_prompt("content_pipeline", {
            "topic": topic,
            "content_type": content_type
        })
        
        # Extract the messages chain from the prompt
        messages = prompt_result.messages
        
        # Initialize conversation with first message
        conversation = []
        current_role = None
        full_responses = []
        
        print("Beginning multi-step content creation process...")
        
        # Process the chained messages
        for i, msg in enumerate(messages):
            role = msg.role
            content = msg.content.text if hasattr(msg.content, 'text') else str(msg.content)
            
            # Add message to conversation
            conversation.append({
                "role": role,
                "content": content
            })
            
            # If this is an assistant message, we don't need to send it to the API
            # It's used as a placeholder to maintain conversation flow
            if role == "assistant":
                continue
                
            # Get LLM response for this step of the conversation
            print(f"\nStep {i+1}: {content[:60]}...\n")
            
            response = self.anthropic.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=1500,
                messages=conversation
            )
            
            # Add the response to the conversation
            response_text = response.content[0].text
            conversation.append({
                "role": "assistant",
                "content": response_text
            })
            
            # Save the full response
            step_name = ""
            if "research" in content.lower():
                step_name = "RESEARCH"
            elif "outline" in content.lower():
                step_name = "OUTLINE"
            elif "draft" in content.lower() and "polish" not in content.lower():
                step_name = "DRAFT"
            elif "polish" in content.lower():
                step_name = "FINAL POLISH"
                
            full_responses.append(f"--- {step_name} ---\n\n{response_text}")
            
            print(f"Completed {step_name if step_name else 'step'}")
        
        print("\n--- Content Pipeline Complete ---\n")
        
        return "\n\n".join(full_responses)

# Example usage
async def main():
    # Replace with your actual API key
    client = ContentPipelineClient("your_anthropic_api_key")
    
    try:
        # Connect to the server with our content pipeline prompt
        await client.connect_to_server("content_pipeline_server.py")
        
        # Run the content pipeline
        result = await client.run_content_pipeline(
            topic="Artificial Intelligence in Healthcare", 
            content_type="blog post"
        )
        
        print("\n=== FINAL RESULT ===\n")
        print(result)
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
