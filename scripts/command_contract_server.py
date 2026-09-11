"""Optional offline MCP for OCI command contracts. No cloud or process executor."""
from typing import Annotated
import json

from mcp.server.fastmcp import FastMCP
from mcp.types import CallToolResult, TextContent, ToolAnnotations
from pydantic import Field

from read_contract import check, describe

mcp = FastMCP('oci-command-contract', log_level='WARNING')
OFFLINE = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)


@mcp.tool(annotations=OFFLINE)
def describe_read_command(leaf: Annotated[str, Field(max_length=200)]) -> dict:
    """Describe a known OCI read leaf: required flags, aliases, enums and pagination. Offline metadata only."""
    return describe(leaf)


@mcp.tool(annotations=OFFLINE)
def check_read_command(command: Annotated[str, Field(max_length=16384)]) -> CallToolResult:
    """Check one INERT proposed OCI read command. Fix reported syntax issues before proposing it. Never executes it."""
    result = check(command)
    return CallToolResult(isError=not result['valid'],
                          content=[TextContent(type='text', text=json.dumps(result))])


if __name__ == '__main__':
    mcp.run(transport='stdio')
