from fastmcp import FastMCP
from daytona_sdk import Daytona, CreateWorkspaceParams, DaytonaConfig
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
def list_workspaces() -> str:
    """
    List all active Daytona workspaces.
    """
    try:
        client = get_daytona_client()
        workspaces = client.list_workspaces()
        return str(workspaces)
    except Exception as e:
        return f"Error listing workspaces: {str(e)}"

@mcp.tool()
def create_workspace(repository_url: str) -> str:
    """
    Create a new Daytona workspace from a Git repository URL.
    Args:
        repository_url: The URL of the Git repository to create the workspace from.
    """
    try:
        client = get_daytona_client()
        params = CreateWorkspaceParams(repository_url=repository_url)
        workspace = client.create_workspace(params)
        return f"Workspace created successfully: {workspace.id}"
    except Exception as e:
        return f"Error creating workspace: {str(e)}"

@mcp.tool()
def get_workspace_info(workspace_id: str) -> str:
    """
    Get detailed information about a specific workspace.
    Args:
        workspace_id: The ID of the workspace to retrieve info for.
    """
    try:
        client = get_daytona_client()
        workspace = client.get_workspace(workspace_id)
        return str(workspace)
    except Exception as e:
        return f"Error getting workspace info: {str(e)}"

@mcp.tool()
def remove_workspace(workspace_id: str) -> str:
    """
    Remove (delete) a Daytona workspace.
    Args:
        workspace_id: The ID of the workspace to remove.
    """
    try:
        client = get_daytona_client()
        client.remove_workspace(workspace_id)
        return f"Workspace {workspace_id} removed successfully"
    except Exception as e:
        return f"Error removing workspace: {str(e)}"

if __name__ == "__main__":
    mcp.run()
