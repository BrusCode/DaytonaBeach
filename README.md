# Daytona MCP Server

This is a Model Context Protocol (MCP) server for [Daytona](https://daytona.io/), allowing LLMs to interact with Daytona sandboxes.
It is built using `fastmcp` and `httpx` to interact directly with the Daytona REST API.
This server is designed for deployment on [fastmcp.cloud](https://fastmcp.cloud).

## Prerequisites

- Python 3.10+
- A Daytona API Key
- The Daytona Server URL

## Environment Variables

The server requires the following environment variables to be set:

- `DAYTONA_API_KEY`: Your Daytona API Key.
- `DAYTONA_SERVER_URL`: The URL of your Daytona server (e.g. `https://daytona.app.daytona.io`).

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

## Capabilities

### Tools
- **Sandbox Management**:
    - `list_sandboxes()`
    - `create_sandbox(repository_url)`
    - `get_sandbox_info(sandbox_id)`
    - `remove_sandbox(sandbox_id)`
- **Toolbox**:
    - `execute_command(sandbox_id, command)`
    - `list_files(sandbox_id, path)`
    - `read_file(sandbox_id, path)`
    - `write_file(sandbox_id, path, content)`

### Prompts
- **`python_agent`**: Sets the LLM context to act as a Python developer in Daytona.
- **`code_review`**: Instructs the LLM to review the code within a sandbox.

### Resources
- **`daytona://sandboxes`**: JSON list of all active sandboxes.
- **`daytona://{sandbox_id}/files/{path}`**: Direct access to file contents (e.g., `daytona://sandbox1/files/README.md`).

## Deployment on FastMCP Cloud

1.  Push this repository to GitHub.
2.  Go to [fastmcp.cloud](https://fastmcp.cloud).
3.  Import your repository.
4.  Set the `DAYTONA_API_KEY` and `DAYTONA_SERVER_URL` environment variables in the deployment settings.
5.  Deploy!
