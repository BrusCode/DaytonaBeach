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

if __name__ == "__main__":
    mcp.run()
