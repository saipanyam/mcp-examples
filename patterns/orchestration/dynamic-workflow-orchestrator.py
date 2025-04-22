@mcp.tool()
async def adaptive_workflow(task_description: str, available_data: dict, exchange=None) -> str:
    """Dynamically create and execute a workflow based on task description."""
    if not exchange or not hasattr(exchange, "create_message"):
        return "This tool requires a client that supports sampling."
    
    # Step 1: Use LLM to plan the workflow
    planning_request = {
        "messages": [{
            "role": "user",
            "content": {
                "type": "text",
                "text": f"""
                I need to create a workflow plan for the following task:
                
                TASK: {task_description}
                
                AVAILABLE DATA: 
                {json.dumps(available_data, indent=2)}
                
                Create a detailed execution plan with the following structure:
                1. Data sources to use
                2. Preprocessing steps needed
                3. Analysis methods to apply
                4. Visualization types to generate
                5. Format for final output
                
                For each step, specify exactly which server and tool to use.
                Available servers: data, analysis, visualization, reporting
                
                Return the workflow as a JSON object with this structure:
                {{
                    "steps": [
                        {{
                            "server": "server_name",
                            "tool": "tool_name",
                            "parameters": {{...}}
                        }}
                    ]
                }}
                """
            }
        }],
        "systemPrompt": "You are a workflow planning assistant that creates structured execution plans.",
        "maxTokens": 1000
    }
    
    # Get workflow plan from LLM
    planning_result = await exchange.create_message(planning_request)
    
    try:
        # Parse the workflow plan from LLM response
        workflow_text = planning_result.content.text
        
        # Extract JSON from the response
        import re
        json_match = re.search(r'```json\n(.*?)\n```', workflow_text, re.DOTALL)
        if json_match:
            workflow_json = json_match.group(1)
        else:
            workflow_json = workflow_text
        
        workflow = json.loads(workflow_json)
        
        # Step 2: Execute the generated workflow
        results = []
        
        for step in workflow["steps"]:
            server_name = step["server"]
            tool_name = step["tool"]
            parameters = step["parameters"]
            
            # Get server connection
            server = await get_server_connection(server_name)
            
            # Execute tool
            result = await server.call_tool(tool_name, parameters)
            results.append({
                "step": f"{server_name}.{tool_name}",
                "result": result
            })
            
            # Update parameters for next steps if needed
            if server_name == "data" and "output" in result:
                for future_step in workflow["steps"]:
                    if "data_input" in future_step["parameters"]:
                        future_step["parameters"]["data_input"] = result["output"]
        
        return f"Executed dynamic workflow with {len(workflow['steps'])} steps. Results: {json.dumps(results, indent=2)}"
    
    except Exception as e:
        return f"Error executing dynamic workflow: {str(e)}"
