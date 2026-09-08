#!/usr/bin/env python3
"""Probe installed Claude Code activation against a loopback mock API, with Read only."""

import argparse
import json
import os
import shutil
import subprocess
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


def probe():
    executable = shutil.which("claude")
    if not executable:
        raise RuntimeError("Claude Code is unavailable")
    version = subprocess.check_output([executable, "--version"], text=True).strip()
    report = {
        "host": version,
        "transport": "loopback mock API; no model or OCI calls",
        "cases": [],
    }
    for filename in ("match.tf", "other.txt", "control.txt"):
        captured = []
        with tempfile.TemporaryDirectory(prefix="oci-paths-probe-") as directory:
            root = Path(directory)
            plugin = root / "plugin"
            (plugin / ".claude-plugin").mkdir(parents=True)
            (plugin / ".claude-plugin/plugin.json").write_text(
                '{"name":"oci-probe","version":"0.0.1"}'
            )
            skill = plugin / "skills/oci-paths-probe"
            skill.mkdir(parents=True)
            skill.joinpath("SKILL.md").write_text(
                '---\nname: oci-paths-probe\ndescription: PATHS_PROBE_DESCRIPTION. Use when: probing activation. Not for: OCI operations.\npaths: ["**/*.tf"]\n---\nPATHS_PROBE_BODY\n'
            )
            if filename == "control.txt":
                skill.joinpath("SKILL.md").write_text(
                    skill.joinpath("SKILL.md")
                    .read_text()
                    .replace('paths: ["**/*.tf"]\n', "")
                )
            root.joinpath(filename).write_text("fixture\n")

            class Handler(BaseHTTPRequestHandler):
                def log_message(self, *args):
                    pass

                def do_POST(self):
                    body = json.loads(
                        self.rfile.read(int(self.headers["Content-Length"]))
                    )
                    captured.append(body)
                    messages = body.get("messages", [])
                    seen = any(
                        "tool_result" in json.dumps(message) for message in messages
                    )
                    content = (
                        [{"type": "text", "text": "Probe complete."}]
                        if seen
                        else [
                            {
                                "type": "tool_use",
                                "id": "probe_read",
                                "name": "Read",
                                "input": {"file_path": str(root / filename)},
                            }
                        ]
                    )
                    response = {
                        "id": "msg_probe",
                        "type": "message",
                        "role": "assistant",
                        "model": "claude-sonnet-4-6",
                        "content": content,
                        "stop_reason": "end_turn" if seen else "tool_use",
                        "stop_sequence": None,
                        "usage": {"input_tokens": 1, "output_tokens": 1},
                    }
                    self.send_response(200)
                    if body.get("stream"):
                        self.send_header("Content-Type", "text/event-stream")
                        self.end_headers()
                        events = [
                            (
                                "message_start",
                                {
                                    "type": "message_start",
                                    "message": {
                                        **response,
                                        "content": [],
                                        "stop_reason": None,
                                    },
                                },
                            )
                        ]
                        for i, block in enumerate(content):
                            events.append(
                                (
                                    "content_block_start",
                                    {
                                        "type": "content_block_start",
                                        "index": i,
                                        "content_block": {**block, "input": {}}
                                        if block["type"] == "tool_use"
                                        else block,
                                    },
                                )
                            )
                            if block["type"] == "tool_use":
                                events.append(
                                    (
                                        "content_block_delta",
                                        {
                                            "type": "content_block_delta",
                                            "index": i,
                                            "delta": {
                                                "type": "input_json_delta",
                                                "partial_json": json.dumps(
                                                    block["input"]
                                                ),
                                            },
                                        },
                                    )
                                )
                            events.append(
                                (
                                    "content_block_stop",
                                    {"type": "content_block_stop", "index": i},
                                )
                            )
                        events += [
                            (
                                "message_delta",
                                {
                                    "type": "message_delta",
                                    "delta": {
                                        "stop_reason": response["stop_reason"],
                                        "stop_sequence": None,
                                    },
                                    "usage": {"output_tokens": 1},
                                },
                            ),
                            ("message_stop", {"type": "message_stop"}),
                        ]
                        for event, payload in events:
                            self.wfile.write(
                                f"event: {event}\ndata: {json.dumps(payload)}\n\n".encode()
                            )
                    else:
                        self.send_header("Content-Type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(response).encode())

            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            env = {
                k: v
                for k, v in os.environ.items()
                if not k.startswith(("ANTHROPIC_", "CLAUDE_", "CLAUDECODE"))
            }
            env.update(
                ANTHROPIC_BASE_URL=f"http://127.0.0.1:{server.server_port}",
                ANTHROPIC_API_KEY="local-probe-only",
                CLAUDE_CONFIG_DIR=str(root / "config"),
                CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1",
            )
            try:
                result = subprocess.run(
                    [
                        executable,
                        "-p",
                        f"Read {filename} and say done.",
                        "--plugin-dir",
                        str(plugin),
                        "--tools",
                        "Read,Skill",
                        "--allowedTools",
                        "Read",
                        "--strict-mcp-config",
                        "--mcp-config",
                        '{"mcpServers":{}}',
                        "--settings",
                        '{"disableAllHooks":true}',
                        "--no-session-persistence",
                        "--output-format",
                        "json",
                    ],
                    cwd=root,
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=45,
                )
            finally:
                server.shutdown()
                server.server_close()
            texts = [json.dumps(body) for body in captured if body.get("messages")]
            report["cases"].append(
                {
                    "file": filename,
                    "exit_code": result.returncode,
                    "requests": len(texts),
                    "description_visible": [
                        "PATHS_PROBE_DESCRIPTION" in text for text in texts
                    ],
                    "body_visible": ["PATHS_PROBE_BODY" in text for text in texts],
                }
            )
    matching, other, control = report["cases"]
    if (
        not matching["requests"]
        or not other["requests"]
        or not any(control["description_visible"])
    ):
        report["finding"] = "unsettled: mock API did not observe both cases"
    elif any(matching["description_visible"]) and not any(other["description_visible"]):
        report["finding"] = "gates activation"
    elif all(matching["description_visible"]) and all(other["description_visible"]):
        report["finding"] = "does not gate description availability in this host"
    else:
        report["finding"] = "unsettled: inspect visibility arrays"
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = probe()
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text)
    print(text, end="")
