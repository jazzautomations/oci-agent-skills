#!/usr/bin/env python3
"""Build synthetic chatRequest JSON locally; makes no network calls.
OCI reads belong through scripts/lib/oci_ro; inference is deliberately absent.
"""
import argparse
import json

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-format", choices=("GENERIC", "COHERE"), required=True)
    parser.add_argument("--max-tokens", type=int, default=32)
    args = parser.parse_args()
    if not 1 <= args.max_tokens <= 128:
        parser.error("--max-tokens must be between 1 and 128")
    request = {"apiFormat": args.api_format, "maxTokens": args.max_tokens, "isStream": False}
    if args.api_format == "GENERIC":
        request["messages"] = [{"role": "USER", "content": [{"type": "TEXT", "text": "Reply with OK."}]}]
    else:
        request["message"] = "Reply with OK."
    print(json.dumps(request, indent=2))

if __name__ == "__main__":
    main()
