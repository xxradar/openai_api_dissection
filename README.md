# OpenAI API dissection

Walk the official [OpenAI OpenAPI spec](https://github.com/openai/openai-openapi), pick an
endpoint and method, extract its (ref-resolved) request schema, and let a model write a
ready-to-run `curl` command for it.

## Quick start
```bash
pip install -r requirements.txt      # openai, pyyaml
export OPENAI_API_KEY=sk-...
./script.sh
```
`script.sh` downloads `openapi.yaml`, converts it to `openapi.json` (once; delete the file to
refresh), lists the endpoints, asks for a number and a method, writes a self-contained JSON
description of the operation and hands it to `suggest.py`.

Optional knobs: `OPENAI_SPEC_BRANCH` (default `master`; `manual_spec` is the frozen 2025
hand-written spec), `OPENAI_SPEC_URL` (any spec URL), `SUGGEST_MODEL` (model that writes the
curl command, default `gpt-4.1`).

## Doing it by hand
### Get the spec and convert it
```bash
curl -fsSL -o openapi.yaml https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml
# mikefarah/yq:            yq eval -o=json '.' openapi.yaml > openapi.json
# kislyuk/yq (python):     yq . openapi.yaml > openapi.json
# no yq:
python3 -c 'import json,yaml,sys; json.dump(yaml.safe_load(open("openapi.yaml")), sys.stdout, default=str)' > openapi.json
```
### Base URL and endpoints
```bash
BASEURL=$(jq -r '.servers[0].url' openapi.json)
jq -r '.paths | keys[] | select(test("\\?") | not)' openapi.json | nl -w3 -s'. '
```
(The current spec lists a few `/responses...?beta=true` duplicates; the `select` hides them.
As of September 2026 there are ~180 paths, so the numbering below changes whenever the spec does.)
### Pick an endpoint and a method
```bash
NUM=12
ENDPOINT=$(jq -r '.paths | keys[] | select(test("\\?") | not)' openapi.json | sed -n "${NUM}p")
jq -r --arg path "$ENDPOINT" '.paths[$path] | keys[]' openapi.json
METHOD=post
```
### Extract the request schema
```bash
REF=$(jq -r --arg path "$ENDPOINT" --arg method "$METHOD" \
  '.paths[$path][$method].requestBody.content["application/json"].schema["$ref"] // empty' openapi.json)
SCHEMA_NAME=${REF#'#/components/schemas/'}
jq --arg name "$SCHEMA_NAME" '.components.schemas[$name]' openapi.json
```
Note that most request bodies in the current spec are `allOf` compositions of further
`$ref`s (e.g. `CreateChatCompletionRequest` pulls `model` from `CreateModelResponseProperties`),
and file-upload endpoints (`/files`, `/audio/transcriptions`, …) use `multipart/form-data`
instead of `application/json`. `script.sh` resolves the refs and handles both content types;
the one-liners above do not.

### Generate the curl command
```bash
python3 suggest.py combined.json        # file written by script.sh
```
