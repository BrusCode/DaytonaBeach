# Daytona MCP Server

This is a Model Context Protocol (MCP) server for [Daytona](https://daytona.io/), allowing LLMs to interact with Daytona workspaces.
It is built using `fastmcp` and designed for deployment on [fastmcp.cloud](https://fastmcp.cloud).

## Prerequisites

- Python 3.10+
- A Daytona API Key
- The Daytona Server URL

## Environment Variables

The server requires the following environment variables to be set:

- `DAYTONA_API_KEY`: Your Daytona API Key.
- `DAYTONA_SERVER_URL`: The URL of your Daytona server.

## Installation & Local Usage

1.  Clone this repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Run the server:
    ```bash
    fastmcp run server.py
    ```

## Tools

The server exposes the following tools to the LLM:

- **`list_workspaces()`**: Lists all active Daytona workspaces.
- **`create_workspace(repository_url: str)`**: Creates a new workspace from a Git repository URL.
- **`get_workspace_info(workspace_id: str)`**: Retrieves detailed info about a workspace.
- **`remove_workspace(workspace_id: str)`**: Deletes a workspace.

## LLM Verification Prompt

To verify the server is working with an LLM, you can use the following prompt:

> "Please list my active Daytona workspaces. If I don't have any, create one from https://github.com/daytonaio/sample-repo.git"

## Deployment on FastMCP Cloud

1.  Push this repository to GitHub.
2.  Go to [fastmcp.cloud](https://fastmcp.cloud).
3.  Import your repository.
4.  Set the `DAYTONA_API_KEY` and `DAYTONA_SERVER_URL` environment variables in the deployment settings.
5.  Deploy!
