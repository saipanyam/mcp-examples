from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("slash-commands-demo")

@mcp.prompt(
    name="analyze_data",
    description="Analyze data from a dataset",
    arguments=[
        {"name": "dataset", "description": "Name or path of the dataset", "required": True},
        {"name": "visualization", "description": "Type of visualization to create", "required": False},
        {"name": "metrics", "description": "Statistical metrics to calculate", "required": False}
    ]
)
async def analyze_data(dataset, visualization=None, metrics=None):
    """Prompt that can be surfaced as a /analyze_data slash command."""
    
    # Default values if not provided
    viz_type = visualization or "auto"
    stats = metrics or "mean,median,correlation"
    
    prompt_template = f"""
    Please analyze the dataset: {dataset}
    
    Visualization type: {viz_type}
    
    Calculate the following metrics:
    {stats}
    
    Your analysis should include:
    1. A summary of the dataset structure
    2. Key statistical findings
    3. Patterns or trends in the data
    4. Outliers or anomalies
    5. Recommended visualizations
    
    Please format your response with clear headings and sections.
    """
    
    return [{
        "role": "user",
        "content": {"type": "text", "text": prompt_template}
    }]

@mcp.prompt(
    name="format_code",
    description="Format and improve code",
    arguments=[
        {"name": "code", "description": "Code to format", "required": True},
        {"name": "language", "description": "Programming language", "required": True},
        {"name": "style", "description": "Coding style guide to follow", "required": False}
    ]
)
async def format_code(code, language, style=None):
    """Prompt that can be surfaced as a /format_code slash command."""
    
    style_guide = style or "standard"
    
    prompt_template = f"""
    Please format and improve the following {language} code according to the {style_guide} style guide:
    
    ```{language}
    {code}
    ```
    
    Your response should include:
    1. The formatted code
    2. Explanations of major changes
    3. Suggestions for improving code quality, efficiency, or readability
    4. Any potential bugs or edge cases
    
    Please ensure the functionality remains unchanged while improving the style and structure.
    """
    
    return [{
        "role": "user",
        "content": {"type": "text", "text": prompt_template}
    }]

@mcp.prompt(
    name="summarize",
    description="Summarize text or content",
    arguments=[
        {"name": "text", "description": "Text to summarize", "required": True},
        {"name": "length", "description": "Desired summary length (short, medium, long)", "required": False},
        {"name": "focus", "description": "Aspect to focus on (main points, technical details, etc.)", "required": False}
    ]
)
async def summarize(text, length=None, focus=None):
    """Prompt that can be surfaced as a /summarize slash command."""
    
    summary_length = length or "medium"
    summary_focus = focus or "main points"
    
    prompt_template = f"""
    Please summarize the following text:
    
    {text}
    
    Summary length: {summary_length}
    Focus on: {summary_focus}
    
    Your summary should capture the essential information while maintaining accuracy.
    """
    
    return [{
        "role": "user",
        "content": {"type": "text", "text": prompt_template}
    }]

if __name__ == "__main__":
    mcp.run(transport='stdio')
