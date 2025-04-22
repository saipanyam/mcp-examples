# Model Context Protocol (MCP) Examples

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

A comprehensive repository showcasing examples of implementing **Model Context Protocol (MCP)** features. This repository serves as a resource for developers to understand and build upon MCP implementations using Python.

## What is Model Context Protocol (MCP)?

The Model Context Protocol is an open protocol that standardizes how applications provide context to Large Language Models (LLMs). It defines a consistent interface for tools, resources, and prompts, enabling seamless integration between LLMs and various data sources or capabilities.

## Repository Structure

This repository is organized into several key sections:

### Patterns

- **Composability**
  - Client-orchestrated workflows
  - Proxy server implementations
  - Server-to-server communication

- **Orchestration**
  - Centralized orchestrators
  - Dynamic workflow orchestration
  - Event-driven orchestration

### Prompts

- Conditional workflows
- Dynamic arguments
- Orchestrated pipelines
- Slash commands
- Including resources in prompts

### Resources

- API integrations
- Database connections
- File system operations

### Tools

- API integration patterns
- Chunked processing
- Data processing
- Notification systems
- Semantic search implementation
- Stateful session management
- System command patterns

### Sampling

- Client implementations
- Server implementations

## Getting Started

To get started with the repository:

1. **Clone the repository**:
   ```bash
   git clone https://github.com/saipanyam/mcp-examples.git
   cd mcp-examples
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Explore the examples**:
   Browse through the different directories to understand various MCP patterns and implementations.

## Example Usage

Here's a simple example of using the client-orchestrated workflow:

```python
# Connect to specialized servers
database_client = await connect_to_server("database_server.py")
analysis_client = await connect_to_server("analysis_server.py") 
report_client = await connect_to_server("report_server.py")

# Fetch data from database server
raw_data = await database_client.call_tool("query_database", {
    "query": "SELECT * FROM sales WHERE region = 'Northeast' AND date > '2024-01-01'"
})

# Process data with analysis server
analysis_results = await analysis_client.call_tool("analyze_trends", {
    "data": raw_data,
    "metrics": ["growth_rate", "seasonality", "regional_comparison"]
})

# Generate report with report server
final_report = await report_client.call_tool("generate_sales_report", {
    "analysis": analysis_results,
    "template": "executive_summary",
    "include_visualizations": True
})
```

## Key Features

- **Modular Design**: Each example demonstrates a specific pattern or technique
- **Practical Implementation**: Ready-to-use code patterns for real-world applications
- **Comprehensive Coverage**: Covers a wide range of MCP features and capabilities
- **Best Practices**: Demonstrates recommended approaches for MCP implementation

## Use Cases

- Building multi-agent systems
- Creating orchestrated workflows between specialized LLM services
- Implementing stateful interactions with LLMs
- Developing resource-aware applications
- Creating prompt templates for consistent LLM interactions

## Contributing

Contributions to improve examples or add new ones are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
