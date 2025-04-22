# mcp-examples
A repository that show cases examples of implementing Model Context Protocol features

## File System Resources in MCP

 `resources/file-system-resources.py` creates two resources:

- file://read/{path} - Reads a file's contents or lists a directory

- file://info/{path} - Returns metadata about a file or directory

## Database Resources in MCP

Here's an example using SQLite database resources. This example creates three database resources:

- db://table/{table} - Gets all records from a table

- db://record/{table}/{id} - Gets a specific record

- db://schema/{table} - Gets schema information about a table
- 
## API Resources in MCP

Here's an example using external API resources (weather, news and GitHub). This example creates multiple API-based resources:

- api://weather/current/{city} - Gets current weather for a city

- api://weather/forecast/{city}/{days} - Gets a multi-day forecast for a city

- api://news/{topic}/{count} - Gets news articles on a specific topic

- api://github/repos/{username} - Gets GitHub repositories for a user

