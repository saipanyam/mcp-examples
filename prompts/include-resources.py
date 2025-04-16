import json
from mcp.server.fastmcp import FastMCP

# Initialize MCP server
mcp = FastMCP("resource-context-demo")

# Sample customer database as a resource
CUSTOMER_DB = {
    "cust_12345": {
        "name": "Acme Corporation",
        "contact": "John Doe",
        "email": "john@acmecorp.com",
        "tier": "Enterprise",
        "since": "2020-01-15"
    },
    "cust_67890": {
        "name": "Globex Industries",
        "contact": "Jane Smith",
        "email": "jane@globex.com",
        "tier": "Professional",
        "since": "2022-03-20"
    }
}

# Define a resource for customer information
@mcp.resource(
    uri="customer://profile/{id}",
    name="Customer Profile",
    description="Customer information from database"
)
async def customer_profile(id):
    """Fetch customer profile from database."""
    if id in CUSTOMER_DB:
        return json.dumps(CUSTOMER_DB[id], indent=2)
    return "Customer not found"

# Define a resource for recent orders
@mcp.resource(
    uri="customer://orders/{id}",
    name="Recent Orders",
    description="Customer's recent orders"
)
async def recent_orders(id):
    """Fetch customer's recent orders."""
    # Simulated orders data
    if id == "cust_12345":
        return """
        [
            {"order_id": "ORD-001", "date": "2023-06-10", "amount": 1250.00, "status": "Delivered"},
            {"order_id": "ORD-002", "date": "2023-08-15", "amount": 750.00, "status": "Processing"}
        ]
        """
    elif id == "cust_67890":
        return """
        [
            {"order_id": "ORD-003", "date": "2023-07-22", "amount": 500.00, "status": "Delivered"}
        ]
        """
    return "[]"

# Define a prompt that uses resource context
@mcp.prompt(
    name="customer_summary",
    description="Generate a customer summary with context from resources",
    arguments=[
        {"name": "customer_id", "description": "Customer ID", "required": True}
    ]
)
async def customer_summary(customer_id):
    """Generate a customer summary using resource context."""
    
    # This is the prompt template that will use the resources
    template = """
    Please provide a comprehensive summary for this customer:
    
    CUSTOMER PROFILE:
    {{resource:customer://profile/{customer_id}}}
    
    RECENT ORDERS:
    {{resource:customer://orders/{customer_id}}}
    
    Include the following in your summary:
    1. Key customer information
    2. Customer relationship duration
    3. Recent ordering patterns
    4. Recommendations for account management
    """
    
    # Format the template with the customer_id
    formatted_template = template.format(customer_id=customer_id)
    
    # Return the prompt with appropriate resources embedded
    return [{
        "role": "user",
        "content": {
            "type": "text",
            "text": formatted_template
        }
    }]

if __name__ == "__main__":
    mcp.run(transport='stdio')
