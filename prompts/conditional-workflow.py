from mcp.server.fastmcp import FastMCP
import json

# Initialize MCP server
mcp = FastMCP("workflow-guide-demo")

# Define a function to analyze sentiment
def analyze_sentiment(text):
    """Simple sentiment analysis simulation."""
    # In a real system, you'd use a proper sentiment analysis tool
    negative_words = ["bad", "terrible", "awful", "horrible", "disappointed", "issue", "problem"]
    positive_words = ["good", "great", "excellent", "amazing", "love", "happy", "satisfied"]
    
    text_lower = text.lower()
    neg_count = sum(text_lower.count(word) for word in negative_words)
    pos_count = sum(text_lower.count(word) for word in positive_words)
    
    if neg_count > pos_count:
        return "negative"
    elif pos_count > neg_count:
        return "positive"
    else:
        return "neutral"

@mcp.prompt(
    name="support_triage",
    description="Triage customer support messages with guided workflow",
    arguments=[
        {"name": "customer_message", "description": "Message from the customer", "required": True},
        {"name": "customer_id", "description": "Customer ID", "required": False},
        {"name": "product_id", "description": "Product ID", "required": False}
    ]
)
async def support_triage(customer_message, customer_id=None, product_id=None):
    """Guided workflow for triaging customer support messages."""
    
    # Analyze the message to determine intent and sentiment
    sentiment = analyze_sentiment(customer_message)
    
    # Check for keywords to determine the type of issue
    message_lower = customer_message.lower()
    
    # Determine the intent/category
    if any(word in message_lower for word in ["bill", "charge", "payment", "refund", "subscription"]):
        intent = "billing_issue"
    elif any(word in message_lower for word in ["broken", "error", "bug", "doesn't work", "crash"]):
        intent = "technical_problem"
    elif any(word in message_lower for word in ["how to", "how do i", "guide", "tutorial"]):
        intent = "help_request"
    else:
        intent = "general_inquiry"
    
    # Build context object
    context = {
        "sentiment": sentiment,
        "intent": intent,
        "customer_id": customer_id,
        "product_id": product_id
    }
    
    # Create conditional response based on the analysis
    if intent == "billing_issue":
        if sentiment == "negative":
            prompt_template = f"""
            CUSTOMER SUPPORT TRIAGE - BILLING ISSUE (URGENT)
            
            Customer Message: "{customer_message}"
            
            Context: {json.dumps(context, indent=2)}
            
            This appears to be an urgent billing issue with a dissatisfied customer. Please:
            
            1. Address their concern with empathy and understanding
            2. Explain our billing policies clearly and concisely
            3. Offer a specific solution to resolve their issue
            4. If appropriate, suggest a courtesy adjustment or refund
            5. Provide next steps and expected timeline
            
            Remember: The goal is to turn this negative experience into a positive one.
            """
        else:
            prompt_template = f"""
            CUSTOMER SUPPORT TRIAGE - BILLING INQUIRY
            
            Customer Message: "{customer_message}"
            
            Context: {json.dumps(context, indent=2)}
            
            This appears to be a billing question. Please:
            
            1. Provide clear information about our billing policies
            2. Address their specific question directly
            3. Offer additional helpful information they might need
            4. End with an invitation to contact billing@example.com for further assistance
            """
    
    elif intent == "technical_problem":
        prompt_template = f"""
        CUSTOMER SUPPORT TRIAGE - TECHNICAL ISSUE
        
        Customer Message: "{customer_message}"
        
        Context: {json.dumps(context, indent=2)}
        
        This appears to be a technical problem. Please:
        
        1. Express understanding of their frustration
        2. Ask for any additional details needed (error messages, steps to reproduce)
        3. Provide troubleshooting steps for common issues
        4. Explain how to contact technical support if the issue persists
        5. Offer to escalate to our development team if necessary
        """
    
    elif intent == "help_request":
        prompt_template = f"""
        CUSTOMER SUPPORT TRIAGE - HELP REQUEST
        
        Customer Message: "{customer_message}"
        
        Context: {json.dumps(context, indent=2)}
        
        This appears to be a request for help or guidance. Please:
        
        1. Provide clear step-by-step instructions
        2. Include relevant links to documentation if applicable
        3. Explain in user-friendly terms
        4. Ask if they need clarification on any part of your explanation
        """
    
    else:
        prompt_template = f"""
        CUSTOMER SUPPORT TRIAGE - GENERAL INQUIRY
        
        Customer Message: "{customer_message}"
        
        Context: {json.dumps(context, indent=2)}
        
        This appears to be a general inquiry. Please:
        
        1. Answer their question as clearly and concisely as possible
        2. Provide relevant additional information they might find helpful
        3. Direct them to appropriate resources if needed
        4. End with an invitation to ask any follow-up questions
        """
    
    return [{
        "role": "user",
        "content": {"type": "text", "text": prompt_template}
    }]

if __name__ == "__main__":
    mcp.run(transport='stdio')
