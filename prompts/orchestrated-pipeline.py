from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("chain-interactions-demo")

@mcp.prompt(
    name="content_pipeline",
    description="Chain multiple interactions for content creation",
    arguments=[
        {"name": "topic", "description": "Topic to write about", "required": True},
        {"name": "content_type", "description": "Type of content (article, blog, social)", "required": True}
    ]
)
async def content_pipeline(topic, content_type):
    """Chain multiple interactions for content creation workflow."""
    
    # Step 1: Research prompt
    research_prompt = f"""
    I need comprehensive research on the topic: {topic}
    
    Please provide:
    1. Key facts and statistics
    2. Current trends
    3. Major challenges
    4. Expert opinions
    5. Relevant examples or case studies
    
    This research will be used to create {content_type} content.
    """
    
    # Step 2: Outline prompt (will be shown after assistant responds to research)
    outline_prompt = f"""
    Based on the research you just provided about {topic}, please create a detailed outline for a {content_type}.
    
    The outline should include:
    - An engaging title
    - Introduction (key hooks and overview)
    - 3-5 main sections with subpoints
    - Each section should address a specific aspect of {topic}
    - Conclusion with key takeaways
    
    Format the outline with clear headings and bullet points.
    """
    
    # Step 3: Draft prompt (will be shown after assistant creates outline)
    draft_prompt = f"""
    Using the outline you just created, please write a complete first draft of the {content_type} about {topic}.
    
    Follow these guidelines:
    - Maintain a conversational but authoritative tone
    - Include relevant facts from the research
    - Use engaging subheadings
    - Add appropriate transitions between sections
    - Include a strong introduction and conclusion
    """
    
    # Step 4: Final polish prompt (will be shown after draft is created)
    polish_prompt = f"""
    Review and polish the {content_type} draft you just created.
    
    Focus on:
    - Improving clarity and flow
    - Strengthening weak sections
    - Enhancing the introduction and conclusion
    - Adding a call-to-action if appropriate
    - Checking for consistency in tone and style
    - Ensuring factual accuracy
    
    Provide the final polished version of the {content_type}.
    """
    
    # Return the messages for the multi-step workflow
    return [
        {
            "role": "user",
            "content": {"type": "text", "text": research_prompt}
        },
        {
            "role": "assistant",
            "content": {"type": "text", "text": "I'll research this topic thoroughly for you."}
        },
        {
            "role": "user",
            "content": {"type": "text", "text": outline_prompt}
        },
        {
            "role": "assistant",
            "content": {"type": "text", "text": "Based on the research, here's a detailed outline."}
        },
        {
            "role": "user",
            "content": {"type": "text", "text": draft_prompt}
        },
        {
            "role": "assistant",
            "content": {"type": "text", "text": "Here's a draft based on the outline."}
        },
        {
            "role": "user",
            "content": {"type": "text", "text": polish_prompt}
        }
    ]

if __name__ == "__main__":
    mcp.run(transport='stdio')
