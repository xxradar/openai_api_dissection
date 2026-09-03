#!/usr/bin/env python3
"""Ask a model to craft a curl command for one OpenAI API operation.

Usage:
    python3 suggest.py combined.json          # written by script.sh
    COMBINED_JSON='{...}' python3 suggest.py  # legacy: JSON in an env var

Environment:
    OPENAI_API_KEY   required
    SUGGEST_MODEL    model used to write the curl command (default: gpt-4.1)
"""

import json
import os
import sys

from openai import OpenAI

DEFAULT_MODEL = os.getenv("SUGGEST_MODEL", "gpt-4.1")
# Models the generated curl should use, per endpoint family.
DEFAULT_CHAT_MODEL = "gpt-4.1"
DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def load_combined() -> dict:
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            return json.load(f)
    raw = os.getenv("COMBINED_JSON")
    if not raw:
        sys.exit("Error: pass the combined JSON file as an argument or set COMBINED_JSON.")
    return json.loads(raw)


def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        sys.exit("Error: OPENAI_API_KEY environment variable is not set.")

    combined = load_combined()
    client = OpenAI()  # picks up OPENAI_API_KEY (and OPENAI_BASE_URL) from the environment

    instructions = (
        "You are a command-line assistant that writes ready-to-run curl commands "
        "for the OpenAI REST API.\n"
        "Rules:\n"
        "- Output ONLY the curl command in a single ```bash block, no prose.\n"
        "- The auth header MUST be written exactly as -H \"Authorization: Bearer $OPENAI_API_KEY\" "
        "(double quotes, so the shell expands the variable; never single-quote this header).\n"
        "- Build the URL from baseurl + endpoint. Replace {path_params} with realistic example IDs.\n"
        "- Use the given HTTP method. Send a body only for post/put/patch.\n"
        "- If content_type is multipart/form-data use -F fields, otherwise use -H 'Content-Type: application/json' and -d.\n"
        "- Include only the *required* body fields (plus a minimal example value for each).\n"
        f"- When a model is required use {DEFAULT_CHAT_MODEL}; for embeddings use {DEFAULT_EMBEDDING_MODEL}.\n"
        "- Single-quote only the JSON body (-d '...') and avoid nested single quotes inside it.\n"
        "- If the operation is marked deprecated, add a one-line comment saying so above the command.\n"
    )

    try:
        response = client.responses.create(
            model=DEFAULT_MODEL,
            instructions=instructions,
            input=(
                "Operation description (OpenAPI, refs already resolved):\n\n"
                + json.dumps(combined, indent=1)
            ),
            temperature=0,
        )
        print("Generated curl command:\n")
        print(response.output_text.strip())
    except Exception as e:  # noqa: BLE001
        sys.exit(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
