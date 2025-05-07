#!/bin/bash

set -e

# Step 1: Get OpenAPI spec
echo "Downloading OpenAI OpenAPI spec..."
curl -s -O https://raw.githubusercontent.com/openai/openai-openapi/refs/heads/master/openapi.yaml

# Step 2: Convert YAML to JSON
echo "Converting YAML to JSON..."
yq eval -o=json '.' openapi.yaml | jq . > openapi.json

# Step 3: Extract base URL
BASEURL=$(jq -r '.servers[0].url' openapi.json)
echo "Base URL: $BASEURL"

# Step 4: Display endpoints
echo -e "\nAvailable Endpoints:"
jq -r '.paths | keys[]' openapi.json | nl -w2 -s'. '

# Step 5: Prompt for endpoint selection
read -p $'\nEnter the number of the endpoint you want to use: ' NUM
ENDPOINT=$(jq -r '.paths | keys[]' openapi.json | sed -n "${NUM}p")
echo "Selected endpoint: $ENDPOINT"

# Step 6: Show methods available for the selected endpoint
echo -e "\nAvailable methods for $ENDPOINT:"
jq -r --arg path "$ENDPOINT" '.paths[$path] | keys[]' openapi.json

# Step 7: Prompt for method selection
read -p $'\nEnter the method you want to use (e.g., get, post, delete): ' METHOD
METHOD_LOWER=$(echo "$METHOD" | tr '[:upper:]' '[:lower:]')

# Step 8: Extract parameter schema
REF=$(jq -r --arg path "$ENDPOINT" --arg method "$METHOD_LOWER" \
  '.paths[$path][$method].requestBody.content["application/json"].schema["$ref"] // empty' openapi.json)

if [ -n "$REF" ]; then
  SCHEMA_NAME=$(echo "$REF" | sed 's|#/components/schemas/||')
  SCHEMA_JSON=$(jq --arg name "$SCHEMA_NAME" '.components.schemas[$name]' openapi.json)
else
  SCHEMA_JSON=null
fi

# Step 9: Combine metadata
export COMBINED_JSON=$(jq -n \
  --arg method "$METHOD_LOWER" \
  --arg endpoint "$ENDPOINT" \
  --arg baseurl "$BASEURL" \
  --argjson schema "$SCHEMA_JSON" \
  '{
    method: $method,
    endpoint: $endpoint,
    baseurl: $baseurl,
    schema: $schema
  }')

echo -e "\nGenerated JSON for Python script:\n"
echo "$COMBINED_JSON" | jq .

# Step 10: Call Python generator
echo -e "\nGenerating curl command using Python..."
python3 ./suggest.py 
