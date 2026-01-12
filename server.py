from fastmcp import FastMCP
import httpx
import os
import json

# Initialize FastMCP
mcp = FastMCP("daytona")

def get_headers() -> dict:
    api_key = os.getenv("DAYTONA_API_KEY")
    if not api_key:
        raise ValueError("DAYTONA_API_KEY environment variable is not set")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

def get_base_url() -> str:
    url = os.getenv("DAYTONA_SERVER_URL")
    if not url:
        raise ValueError("DAYTONA_SERVER_URL environment variable is not set")
    return url.rstrip('/')

@mcp.tool()
async def list_sandboxes() -> str:
    """
    List all active Daytona sandboxes.
    """
    try:
        url = f"{get_base_url()}/api/sandbox"
        headers = get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        return f"HTTP Error listing sandboxes: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error listing sandboxes: {str(e)}"

@mcp.tool()
async def create_sandbox(repository_url: str) -> str:
    """
    Create a new Daytona sandbox from a Git repository URL.
    Args:
        repository_url: The URL of the Git repository to create the sandbox from.
    """
    try:
        url = f"{get_base_url()}/api/sandbox"
        headers = get_headers()
        
        # Constructing the payload based on common Daytona API patterns
        # Adjust command/image/user if necessary based on specific API version docs
        payload = {
            "source": {
                "repository": {
                    "url": repository_url
                }
            },
            "name": repository_url.split("/")[-1].replace(".git", "") 
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            return f"Sandbox created successfully. Details: {json.dumps(response.json(), indent=2)}"
    except httpx.HTTPStatusError as e:
        return f"HTTP Error creating sandbox: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error creating sandbox: {str(e)}"

@mcp.tool()
async def get_sandbox_info(sandbox_id: str) -> str:
    """
    Get detailed information about a specific sandbox.
    Args:
        sandbox_id: The ID of the sandbox to retrieve info for.
    """
    try:
        url = f"{get_base_url()}/api/sandbox/{sandbox_id}"
        headers = get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        return f"HTTP Error getting sandbox info: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error getting sandbox info: {str(e)}"

@mcp.tool()
async def remove_sandbox(sandbox_id: str) -> str:
    """
    Remove (delete) a Daytona sandbox.
    Args:
        sandbox_id: The ID of the sandbox to remove.
    """
    try:
        url = f"{get_base_url()}/api/sandbox/{sandbox_id}"
        headers = get_headers()
        
        async with httpx.AsyncClient() as client:
            response = await client.delete(url, headers=headers)
            response.raise_for_status()
            return f"Sandbox {sandbox_id} removed successfully"
    except httpx.HTTPStatusError as e:
        return f"HTTP Error removing sandbox: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error removing sandbox: {str(e)}"

@mcp.tool()
async def execute_command(sandbox_id: str, command: str) -> str:
    """
    Execute a shell command within a Daytona sandbox.
    Args:
        sandbox_id: The ID of the sandbox to execute the command in.
        command: The command to execute.
    """
    try:
        # endpoint structure based on research: /api/toolbox/{id}/process/execute
        # Note: Some docs suggest /api/toolbox/{id}/toolbox/process/execute, we will try the shorter one first or handle 404
        url = f"{get_base_url()}/api/toolbox/{sandbox_id}/process/execute"
        headers = get_headers()
        payload = {"command": command}
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()
            result = response.json()
            # Result usually contains exitCode, stdout, stderr
            output = f"Exit Code: {result.get('exitCode', 'Unknown')}\n"
            output += f"Stdout: {result.get('stdout', '')}\n"
            output += f"Stderr: {result.get('stderr', '')}"
            return output
    except httpx.HTTPStatusError as e:
        return f"HTTP Error executing command: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error executing command: {str(e)}"

@mcp.tool()
async def read_file(sandbox_id: str, path: str) -> str:
    """
    Read the contents of a file from a Daytona sandbox.
    Args:
        sandbox_id: The ID of the sandbox.
        path: The absolute path to the file within the sandbox.
    """
    try:
        # /api/toolbox/{id}/files/download?path=...
        url = f"{get_base_url()}/api/toolbox/{sandbox_id}/files/download"
        headers = get_headers()
        params = {"path": path}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.text
    except httpx.HTTPStatusError as e:
        return f"HTTP Error reading file: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def write_file(sandbox_id: str, path: str, content: str) -> str:
    """
    Write content to a file in a Daytona sandbox.
    Args:
        sandbox_id: The ID of the sandbox.
        path: The absolute path to the file within the sandbox.
        content: The content to write.
    """
    try:
        # /api/toolbox/{id}/files/upload?path=... is common, or form data
        # Based on typical implementations, we upload as a file
        url = f"{get_base_url()}/api/toolbox/{sandbox_id}/files/upload"
        headers = get_headers()
        # Remove Content-Type json for upload if sending files/form
        upload_headers = headers.copy()
        upload_headers.pop("Content-Type", None)
        
        params = {"path": path}
        files = {"file": (path.split('/')[-1], content)}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=upload_headers, params=params, files=files)
            response.raise_for_status()
            return f"File written successfully to {path}"
    except httpx.HTTPStatusError as e:
        return f"HTTP Error writing file: {e.response.status_code} - {e.response.text}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
async def list_files(sandbox_id: str, path: str = ".") -> str:
    """
    List files and directories in a Daytona sandbox.
    Args:
        sandbox_id: The ID of the sandbox.
        path: The directory path to list (default is current directory ".").
    """
    try:
        # Initial approach: Execute 'ls -R' (recursive) or just 'ls -la' to give agent visibility
        # Native API for listing files: fs modules usually exist but simple ls via execute_command is robust for agents
        # Let's try to map it to a structured output if possible, or just raw text from ls
        cmd = f"ls -la {path}"
        return await execute_command(sandbox_id, cmd)
    except Exception as e:
        return f"Error listing files: {str(e)}"

# --- Prompts ---

@mcp.prompt()
def python_agent() -> str:
    """
    Returns a system prompt for an agent specialized in Python development within Daytona.
    """
    return """You are an expert Python developer working inside a Daytona Sandbox.
Your goal is to satisfy the user's coding requests efficiently.

Capabilities:
- You can list files to explore the codebase.
- You can read and write files directly.
- You can execute shell commands to run tests, linters, or scripts.

Guidelines:
1. Always explore the file structure first to understand the context.
2. When creating new files, ensure standard project structure (setup.py, requirements.txt).
3. Verify your code by running it or creating simple tests.
"""

@mcp.prompt()
def code_review() -> str:
    """
    Returns a prompt for performing a code review on the repository in the sandbox.
    """
    return """You are a senior software engineer tasked with reviewing the code in this Daytona Sandbox.
    
Please:
1. List the files to understand the project structure.
2. Read key files (README, main logic, tests).
3. specific suggestions for improvements regarding:
    - Code quality and PEP 8 compliance.
    - Potential bugs or security issues.
    - Performance optimizations.
    - Test coverage.
"""

# --- Resources ---

@mcp.resource("daytona://sandboxes")
async def list_sandboxes_resource() -> str:
    """
    A dynamic resource that lists all active sandboxes in JSON format.
    """
    try:
        url = f"{get_base_url()}/api/sandbox"
        headers = get_headers()
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@mcp.resource("daytona://{sandbox_id}/files/{path}")
async def read_file_resource(sandbox_id: str, path: str) -> str:
    """
    Directly access a file's content via a URI.
    Example: daytona://my-sandbox/files/README.md
    """
    try:
        # Reuse read_file logic or call endpoint
        # Note: path in URI might need decoding if it contains slashes that conflict with pattern
        # Ideally, use execute_tool, but direct impl is cleaner for resource
        
        # Path adjustment: generic handlers might pass path with slashes
        decoded_path = path # fastmcp handles basic matching, but deep paths might catch partial
        # Simple fix: assume path is relative to repo root
        
        url = f"{get_base_url()}/api/toolbox/{sandbox_id}/files/download"
        headers = get_headers()
        params = {"path": decoded_path}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            return response.text
    except Exception as e:
        return f"Error reading resource {sandbox_id}/{path}: {str(e)}"

if __name__ == "__main__":
    mcp.run()
