@mcp.prompt(
    name="ticket_response",
    description="Generate a customer support response",
    arguments=[
        {"name": "issue_type", "description": "Type of customer issue", "required": True},
        {"name": "severity", "description": "Severity level", "required": True},
        {"name": "customer_tier", "description": "Customer tier level", "required": False}
    ]
)
async def ticket_response(issue_type, severity, customer_tier="standard"):
    template = f"""
    Generate a professional response for a {severity} {issue_type} issue 
    for a {customer_tier}-tier customer.
    
    The response should include:
    - Appropriate greeting
    - Acknowledgment of the issue
    - Explanation of next steps
    - Expected resolution timeline
    - Closing with appropriate tone
    """
    
    return [{
        "role": "user",
        "content": {"type": "text", "text": template}
    }]
