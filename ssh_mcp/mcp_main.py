"""SSH MCP server for managing SSH connections and executing commands on remote hosts."""
import logging
import os
import traceback
from io import StringIO

import paramiko
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from paramiko import RSAKey

from ssh_client import SSHClient, SSHConfig
from secret_service import get_secret_last_version
from vm_service import get_vm_info

logging.basicConfig(level=logging.INFO)

mcp = FastMCP(
    name="ssh-mcp",
    instructions="A Model Context Protocol for managing and interacting with multiple virtual machines over SSH",
)


def get_ssh_client(port, user, ip_address, ssh_key) -> SSHClient:
    """Get or create SSH client instance."""
    try:
        config = SSHConfig(port, user, ip_address, ssh_key)
        _ssh_client = SSHClient(config)
    except Exception:
        traceback.print_exc()
        raise
    return _ssh_client


@mcp.tool()
async def execute_ssh_command(
    command: str, 
    timeout: int = 60,
    max_length: int = 10000
) -> str:
    """Execute a command on a remote host via SSH.

    Args:
        command: The shell command to execute on the remote host
        timeout: SSH connection and command timeout in seconds (default: 30, max: 300)
        max_length: Maximum length of stdout/stderr output in characters (default: 1000, max: 10,000,000)

    Returns:
        Formatted string containing command output or error information
    """

    headers = get_http_headers()
    logging.info(f'http headers {headers}')

    if 'project_id' not in headers:
        return "Ошибка, project_id не передан в metadata"

    if 'secret_id' not in headers:
        return "Ошибка, secret_id не передан в metadata"

    if 'token' not in headers:
        return "Ошибка, token не передан в metadata"

    hostname, user_name, ip_address = get_vm_info(headers)

    ssh_key=get_secret_last_version(
        secret_id=headers['secret_id'],
        token=headers['token'],
        project_id=headers['project_id']
    )

    try:
        client = get_ssh_client(22, user_name, ip_address, ssh_key)
        result = client.execute_command('server', command, timeout, max_length)

        if result["success"]:
            output = f"""
                SUCCESS:
                Exit Code: {result["exit_code"]}
                
                STDOUT:
                {result["stdout"]}
            """

            if result["stderr"]:
                output += f"\n\nSTDERR:\n{result['stderr']}"

            return output
        else:
            return f"ERROR: Failed to execute command\nError: {result['error']}"

    except Exception as e:
        traceback.print_exc()
        return f"ERROR: Failed to execute command: {str(e)}"




@mcp.tool()
async def get_host_info() -> str:
    """Get detailed information about a specific SSH host.

    Args:
        None

    Returns:
        Formatted string containing host configuration details
    """
    headers = get_http_headers()
    logging.info(f'http headers {headers}')

    if 'vm_id' not in headers:
        return "Ошибка, vm_id не передан в metadata"
    if 'token' not in headers:
        return "Ошибка, token не передан в metadata"

    try:

        hostname, user_name, ip_address = get_vm_info(headers)

        output = f"Host Information for '{hostname}':\n" + "=" * 35 + "\n\n"
        output += f"Host ip: {ip_address}\n"
        output += f"User: {user_name}\n"

        return output

    except Exception as e:
        traceback.print_exc()
        return f"ERROR: Failed to get host information: {str(e)}"


@mcp.tool()
async def test_ssh_connection(timeout: int = 30) -> str:
    """Test SSH connection to a remote host without executing any commands.

    Args:
        timeout: SSH connection timeout in seconds (default: 30, max: 300)

    Returns:
        String indicating whether the connection was successful or failed
    """
    headers = get_http_headers()
    logging.info(f'http headers {headers}')

    if 'project_id' not in headers:
        return "Ошибка, project_id не передан в metadata"

    if 'secret_id' not in headers:
        return "Ошибка, secret_id не передан в metadata"

    if 'token' not in headers:
        return "Ошибка, token не передан в metadata"

    hostname, user_name, ip_address = get_vm_info(headers)

    ssh_key = get_secret_last_version(
        secret_id=headers['secret_id'],
        token=headers['token'],
        project_id=headers['project_id']
    )

    try:
        client = get_ssh_client(22, user_name, ip_address, ssh_key)
        host_config = client.config.get_host_config('server')

        if not host_config:
            return f"ERROR: Host '{hostname}' not found in configuration."

        # Validate timeout parameter
        command_timeout = min(max(timeout, 1), 300)  # 1s to 5 minutes

        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(
                hostname=host_config.get("hostname", hostname),
                port=host_config.get("port", 22),
                username=host_config.get("user", os.getenv("USER")),
                pkey=RSAKey.from_private_key(StringIO(host_config.get("identityfile")[0])),
                timeout=command_timeout,
            )

            return f"SUCCESS: Connection to {hostname} successful"

        except Exception as e:
            print(traceback.format_exc())
            return f"ERROR: Connection to {hostname} failed: {str(e)}"
        finally:
            ssh_client.close()
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

    except Exception as e:
        traceback.print_exc()
        return f"ERROR: Failed to test connection: {str(e)}"


def run():
    """Run the SSH MCP server."""
    transport = os.getenv("MCP_TRANSPORT", "sse")
    if transport == "sse":
        mcp.run(transport="sse", host="0.0.0.0", port=os.getenv('PORT', 8000))
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http")
    else:
        mcp.run(transport="stdio")

run()
