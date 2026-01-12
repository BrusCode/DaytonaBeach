from fastmcp import FastMCP
from daytona import Daytona, DaytonaConfig, CreateSandboxParams
import os

# Initialize FastMCP
mcp = FastMCP("daytona")

def get_daytona_client() -> Daytona:
    api_key = os.getenv("DAYTONA_API_KEY")
    server_url = os.getenv("DAYTONA_SERVER_URL")
    
    if not api_key:
        raise ValueError("DAYTONA_API_KEY environment variable is not set")
    if not server_url:
        raise ValueError("DAYTONA_SERVER_URL environment variable is not set")
        
    config = DaytonaConfig(api_key=api_key, server_url=server_url)
    return Daytona(config=config)

@mcp.tool()
def list_sandboxes() -> str:
    """
    List all active Daytona sandboxes.
    """
    try:
        client = get_daytona_client()
        sandboxes = client.list_sandboxes()
        return str(sandboxes)
    except Exception as e:
        return f"Error listing sandboxes: {str(e)}"

@mcp.tool()
def create_sandbox(repository_url: str) -> str:
    """
    Create a new Daytona sandbox from a Git repository URL.
    Args:
        repository_url: The URL of the Git repository to create the sandbox from.
    """
    try:
        client = get_daytona_client()
        # Assuming one of these patterns works based on common SDK usage. 
        # If parameters differ, this might need further adjustment.
        # We try to pass repository_url as a parameter if CreateSandboxParams accepts it.
        # Otherwise, we might need a specific param class but CreateSandboxParams is the standard entry.
        try:
             params = CreateSandboxParams(repositories=[repository_url])
        except TypeError:
             # Fallback if repositories arg is not list or named differently
             params = CreateSandboxParams(image=repository_url) # Some SDKs treat image as source
             
        sandbox = client.create_sandbox(params)
        return f"Sandbox created successfully: {sandbox.id}"
    except Exception as e:
        return f"Error creating sandbox: {str(e)}"

@mcp.tool()
def get_sandbox_info(sandbox_id: str) -> str:
    """
    Get detailed information about a specific sandbox.
    Args:
        sandbox_id: The ID of the sandbox to retrieve info for.
    """
    try:
        client = get_daytona_client()
        sandbox = client.get_sandbox(sandbox_id)
        return str(sandbox)
    except Exception as e:
        return f"Error getting sandbox info: {str(e)}"

@mcp.tool()
def remove_sandbox(sandbox_id: str) -> str:
    """
    Remove (delete) a Daytona sandbox.
    Args:
        sandbox_id: The ID of the sandbox to remove.
    """
    try:
        client = get_daytona_client()
        client.remove_sandbox(sandbox_id)
        return f"Sandbox {sandbox_id} removed successfully"
    except Exception as e:
        return f"Error removing sandbox: {str(e)}"

if __name__ == "__main__":
    mcp.run()
