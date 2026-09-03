#!/usr/bin/env bash
#
# Dissect the OpenAI OpenAPI spec: pick an endpoint + method, extract the
# request schema, and let a model craft a ready-to-run curl command.
#
# Requirements: curl, jq, python3 (+ pyyaml, openai), OPENAI_API_KEY
# Optional: OPENAI_SPEC_URL, OPENAI_SPEC_BRANCH, SUGGEST_MODEL

set -euo pipefail

SPEC_BRANCH="${OPENAI_SPEC_BRANCH:-master}"
# NOTE: the "refs/heads/<branch>" form of the raw URL stopped working for
# the master branch; the plain "<branch>" form works for both master and
# the frozen manual_spec branch.
SPEC_URL="${OPENAI_SPEC_URL:-https://raw.githubusercontent.com/openai/openai-openapi/${SPEC_BRANCH}/openapi.yaml}"

for tool in curl jq python3; do
  command -v "$tool" >/dev/null || { echo "❌ '$tool' is required." >&2; exit 1; }
done

yaml_to_json() {
  # $1 = yaml in, $2 = json out. Works with either yq flavour, or without yq.
  if command -v yq >/dev/null && yq --version 2>&1 | grep -qi mikefarah; then
    yq eval -o=json '.' "$1" > "$2"                 # mikefarah/yq (Go)
  elif command -v yq >/dev/null && yq --help 2>&1 | grep -q 'jq'; then
    yq . "$1" > "$2"                                # kislyuk/yq (Python, jq wrapper)
  else
    python3 - "$1" "$2" <<'PY'                      # PyYAML fallback
import json, sys, yaml
with open(sys.argv[1]) as f, open(sys.argv[2], "w") as o:
    json.dump(yaml.safe_load(f), o, default=str)
PY
  fi
}

if [ -f openapi.json ]; then
  echo "✅ openapi.json already exists. Skipping download and conversion (delete it to refresh)."
else
  echo "📥 Downloading OpenAI OpenAPI spec from $SPEC_URL ..."
  curl -fsSL -o openapi.yaml "$SPEC_URL"
  echo "🔄 Converting YAML to JSON..."
  yaml_to_json openapi.yaml openapi.json
  echo "✅ Conversion complete: openapi.json created ($(jq '.paths|length' openapi.json) paths, spec $(jq -r .info.version openapi.json))."
fi

BASEURL=$(jq -r '.servers[0].url' openapi.json)
echo "Base URL: $BASEURL"

# The current spec lists some paths twice with a "?beta=true" query suffix;
# hide those duplicates from the menu.
# (while/read instead of mapfile: macOS ships bash 3.2)
ENDPOINTS=()
while IFS= read -r line; do ENDPOINTS+=("$line"); done \
  < <(jq -r '.paths | keys[] | select(test("\\?") | not)' openapi.json)

echo -e "\nAvailable Endpoints (${#ENDPOINTS[@]}):"
printf '%s\n' "${ENDPOINTS[@]}" | nl -w3 -s'. '

read -rp $'\nEnter the number of the endpoint you want to use: ' NUM
if ! [[ "$NUM" =~ ^[0-9]+$ ]] || [ "$NUM" -lt 1 ] || [ "$NUM" -gt "${#ENDPOINTS[@]}" ]; then
  echo "❌ Invalid selection." >&2; exit 1
fi
ENDPOINT="${ENDPOINTS[$((NUM-1))]}"
echo "Selected endpoint: $ENDPOINT"

echo -e "\nAvailable methods for $ENDPOINT:"
jq -r --arg path "$ENDPOINT" '.paths[$path] | to_entries[]
  | select(.key | IN("get","post","put","patch","delete"))
  | "\(.key)\(if .value.deprecated then "   (deprecated)" else "" end)"' openapi.json

read -rp $'\nEnter the method you want to use (e.g., get, post, delete): ' METHOD
METHOD_LOWER=$(echo "$METHOD" | tr '[:upper:]' '[:lower:]')
if [ "$(jq --arg p "$ENDPOINT" --arg m "$METHOD_LOWER" '.paths[$p] | has($m)' openapi.json)" != "true" ]; then
  echo "❌ Method '$METHOD_LOWER' not defined for $ENDPOINT." >&2; exit 1
fi

# Gather everything the model needs, resolving $refs so that the schema is
# self-contained (the current spec builds most request bodies from allOf/$ref).
OP_JSON=$(jq -c --arg p "$ENDPOINT" --arg m "$METHOD_LOWER" '.paths[$p][$m]' openapi.json)
COMBINED_FILE=$(mktemp "${TMPDIR:-/tmp}/openai_dissect.XXXXXX")
trap 'rm -f "$COMBINED_FILE"' EXIT

python3 - "$OP_JSON" "$METHOD_LOWER" "$ENDPOINT" "$BASEURL" "$COMBINED_FILE" <<'PY'
import json, sys
op, method, endpoint, baseurl, out = sys.argv[1:6]
op = json.loads(op)
spec = json.load(open("openapi.json"))
MAX_DEPTH = 6

def resolve(node, depth=0, seen=()):
    if depth > MAX_DEPTH:
        return {"description": "(truncated: nested too deep)"}
    if isinstance(node, dict):
        if "$ref" in node:
            ref = node["$ref"]
            if ref in seen:
                return {"description": f"(recursive ref {ref})"}
            target = spec
            for part in ref.lstrip("#/").split("/"):
                target = target[part]
            merged = {k: v for k, v in node.items() if k != "$ref"}
            merged.update(target if isinstance(target, dict) else {"value": target})
            return resolve(merged, depth + 1, seen + (ref,))
        return {k: resolve(v, depth + 1, seen) for k, v in node.items()
                if k not in ("x-oaiMeta", "x-oaiTypeLabel", "example", "examples")}
    if isinstance(node, list):
        return [resolve(v, depth + 1, seen) for v in node]
    return node

body = op.get("requestBody", {}).get("content", {})
content_type = next((ct for ct in ("application/json", "multipart/form-data") if ct in body), None)
schema = resolve(body[content_type]["schema"]) if content_type else None

json.dump({
    "method": method,
    "endpoint": endpoint,
    "baseurl": baseurl,
    "summary": op.get("summary"),
    "deprecated": op.get("deprecated", False),
    "content_type": content_type,
    "parameters": resolve(op.get("parameters", [])),   # path + query params
    "schema": schema,
}, open(out, "w"), indent=2)
PY

echo -e "\nGenerated JSON for Python script (written to $COMBINED_FILE):\n"
jq '.' "$COMBINED_FILE" | awk 'NR<=60 {print} NR==61 {print "... (truncated, see file)"}'

echo -e "\nGenerating curl command using Python..."
python3 ./suggest.py "$COMBINED_FILE"
