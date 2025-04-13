# How to get openapi calls
## Get the openapi spec file
```
curl -O https://raw.githubusercontent.com/openai/openai-openapi/refs/heads/master/openapi.yaml
```
## convert if necessary
```
yq eval -o=json '.' openapi.yaml | jq . > openapi.json
```
## Extract the BASEURL
```
BASEURL=$(jq -r '.servers[0].url' openapi.json)
```
```
echo $BASEURL
```
## Extract the Endpoints
```
jq -r '.paths | keys[]' openapi.json | nl -w2 -s'. '
```
```
 1. /assistants
 2. /assistants/{assistant_id}
 3. /audio/speech
 4. /audio/transcriptions
 5. /audio/translations
 6. /batches
 7. /batches/{batch_id}
 8. /batches/{batch_id}/cancel
 9. /chat/completions
10. /chat/completions/{completion_id}
11. /chat/completions/{completion_id}/messages
12. /completions
13. /embeddings
14. /files
15. /files/{file_id}
16. /files/{file_id}/content
17. /fine_tuning/checkpoints/{permission_id}/permissions
18. /fine_tuning/jobs
19. /fine_tuning/jobs/{fine_tuning_job_id}
20. /fine_tuning/jobs/{fine_tuning_job_id}/cancel
21. /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints
22. /fine_tuning/jobs/{fine_tuning_job_id}/events
23. /images/edits
24. /images/generations
25. /images/variations
26. /models
27. /models/{model}
28. /moderations
29. /organization/admin_api_keys
30. /organization/admin_api_keys/{key_id}
31. /organization/audit_logs
32. /organization/costs
33. /organization/invites
34. /organization/invites/{invite_id}
35. /organization/projects
36. /organization/projects/{project_id}
37. /organization/projects/{project_id}/api_keys
38. /organization/projects/{project_id}/api_keys/{key_id}
39. /organization/projects/{project_id}/archive
40. /organization/projects/{project_id}/rate_limits
41. /organization/projects/{project_id}/rate_limits/{rate_limit_id}
42. /organization/projects/{project_id}/service_accounts
43. /organization/projects/{project_id}/service_accounts/{service_account_id}
44. /organization/projects/{project_id}/users
45. /organization/projects/{project_id}/users/{user_id}
46. /organization/usage/audio_speeches
47. /organization/usage/audio_transcriptions
48. /organization/usage/code_interpreter_sessions
49. /organization/usage/completions
50. /organization/usage/embeddings
51. /organization/usage/images
52. /organization/usage/moderations
53. /organization/usage/vector_stores
54. /organization/users
55. /organization/users/{user_id}
56. /realtime/sessions
57. /realtime/transcription_sessions
58. /responses
59. /responses/{response_id}
60. /responses/{response_id}/input_items
61. /threads
62. /threads/runs
63. /threads/{thread_id}
64. /threads/{thread_id}/messages
65. /threads/{thread_id}/messages/{message_id}
66. /threads/{thread_id}/runs
67. /threads/{thread_id}/runs/{run_id}
68. /threads/{thread_id}/runs/{run_id}/cancel
69. /threads/{thread_id}/runs/{run_id}/steps
70. /threads/{thread_id}/runs/{run_id}/steps/{step_id}
71. /threads/{thread_id}/runs/{run_id}/submit_tool_outputs
72. /uploads
73. /uploads/{upload_id}/cancel
74. /uploads/{upload_id}/complete
75. /uploads/{upload_id}/parts
76. /vector_stores
77. /vector_stores/{vector_store_id}
78. /vector_stores/{vector_store_id}/file_batches
79. /vector_stores/{vector_store_id}/file_batches/{batch_id}
80. /vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel
81. /vector_stores/{vector_store_id}/file_batches/{batch_id}/files
82. /vector_stores/{vector_store_id}/files
83. /vector_stores/{vector_store_id}/files/{file_id}
84. /vector_stores/{vector_store_id}/files/{file_id}/content
85. /vector_stores/{vector_store_id}/search
```
## Pick an endpoint
```
NUM=9 ENDPOINT=$(jq -r '.paths | keys[]' openapi.json | sed -n "${NUM}p")
```
```
echo $ENDPOINT
```

## Pick a method
```
jq -r --arg path "$ENDPOINT" '.paths[$path] | keys[]' openapi.json
```
```
METHOD="post"
```

## extract the REF
```
REF=$(jq -r --arg path "$ENDPOINT" --arg method "$METHOD" \
  '.paths[$path][$method].requestBody.content["application/json"].schema["$ref"]' openapi.json)
```
## extract the SCHEMA
```
SCHEMA_NAME=$(echo "$REF" | sed 's|#/components/schemas/||')
```
```
SCHEMA_JSON=$(jq --arg name "$SCHEMA_NAME" '.components.schemas[$name]' openapi.json)
```
```
echo "$SCHEMA_JSON" | jq .
```
## Extract
```
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
```
```
echo "$COMBINED_JSON" | jq .
```
## Python code
```
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
```
