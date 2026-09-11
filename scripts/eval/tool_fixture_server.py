"""Closed-world MCP observations: no OCI SDK, subprocess, network or mutation executor."""
import json
import os
from pathlib import Path
from typing import Literal
from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

ROOT = Path(__file__).resolve().parents[2]
CASES = json.loads((ROOT/'evals/tool-task-fixtures.json').read_text())['cases']
OBSERVATIONS = {c['topic']: c['observation'] for c in CASES if c['topic']}
Topic = Literal[tuple(OBSERVATIONS)]
mcp = FastMCP('fixture', log_level='WARNING')
calls = 0


@mcp.tool(annotations=ToolAnnotations(readOnlyHint=True, destructiveHint=False, openWorldHint=False))
def read_observation(topic: Topic) -> dict:
    """Read one synthetic, scoped OCI observation. Select the topic relevant to the request."""
    global calls
    calls += 1
    if calls > 8:
        return {'error': 'Eight-read limit reached', 'synthetic': True}
    value = {'topic': topic, 'synthetic': True, 'observation': OBSERVATIONS[topic]}
    with Path(os.environ['OCI_FIXTURE_TRACE']).open('a') as f:
        f.write(json.dumps({'topic': topic, 'ok': True})+'\n')
    return value


if __name__ == '__main__':
    mcp.run(transport='stdio')
