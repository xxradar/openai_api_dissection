#!/bin/bash
curl -O https://raw.githubusercontent.com/openai/openai-openapi/refs/heads/master/openapi.yaml

yq eval -o=json '.' openapi.yaml | jq . > openapi.json

BASEURL=$(jq -r '.servers[0].url' openapi.json)
echo $BASEURL

jq -r '.paths | keys[]' openapi.json | nl -w2 -s'. '

NUM=9 ENDPOINT=$(jq -r '.paths | keys[]' openapi.json | sed -n "${NUM}p")
echo $ENDPOINT

jq -r --arg path "$ENDPOINT" '.paths[$path] | keys[]' openapi.json
METHOD="post"


REF=$(jq -r --arg path "$ENDPOINT" --arg method "$METHOD" \
  '.paths[$path][$method].requestBody.content["application/json"].schema["$ref"]' openapi.json)

SCHEMA_NAME=$(echo "$REF" | sed 's|#/components/schemas/||')
SCHEMA_JSON=$(jq --arg name "$SCHEMA_NAME" '.components.schemas[$name]' openapi.json)
echo "$SCHEMA_JSON" | jq .


export COMBINED_JSON=$(jq -n \
  --arg method "$METHOD" \
  --arg endpoint "$ENDPOINT" \
  --arg baseurl "$BASEURL" \
  --argjson schema "$SCHEMA_JSON" \
  '{
    method: $method,
    endpoint: $endpoint,
    baseurl: $baseurl,
    schema: $schema
  }')



python3 test.py