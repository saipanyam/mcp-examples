from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("dynamic-args-demo")

# Define a dynamic prompt
@mcp.prompt(
    name="generate_invoice",
    description="Generate a professional invoice",
    arguments=[
        {"name": "client_name", "description": "Name of the client", "required": True},
        {"name": "amount", "description": "Total invoice amount", "required": True},
        {"name": "date", "description": "Invoice date", "required": True},
        {"name": "line_items", "description": "List of items being invoiced", "required": True}
    ]
)
async def generate_invoice(client_name, amount, date, line_items):
    """Generate an invoice with dynamic arguments."""
    
    # Convert line_items string to list if needed
    if isinstance(line_items, str):
        try:
            # Handle string representation of list
            items = eval(line_items) if line_items.startswith('[') else [line_items]
        except:
            items = [line_items]
    else:
        items = line_items
    
    # Format the line items
    formatted_items = ""
    for item in items:
        if isinstance(item, dict):
            formatted_items += f"- {item.get('description', 'Item')}: ${item.get('amount', 0)}\n"
        else:
            formatted_items += f"- {item}\n"
    
    # Create invoice template
    invoice_template = f"""
    INVOICE
    =====================================
    
    Date: {date}
    Client: {client_name}
    
    Items:
    {formatted_items}
    
    Total Amount Due: ${amount}
    
    Payment Terms: Due within 30 days
    Thank you for your business!
    """
    
    return [{
        "role": "user",
        "content": {
            "type": "text",
            "text": invoice_template
        }
    }]

if __name__ == "__main__":
    mcp.run(transport='stdio')
