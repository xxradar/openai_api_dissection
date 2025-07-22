# OpenAI API Dissection Tool

This tool helps you dissect the OpenAI API specification and generate curl commands for specific endpoints.

## Prerequisites

- Python 3.x
- `yq` command-line tool
- `jq` command-line tool
- `curl`
- OpenAI API key

## How to get OpenAPI calls

### Step 1: Get the OpenAPI spec file
```
curl -O https://raw.githubusercontent.com/openai/openai-openapi/refs/heads/master/openapi.yaml
```
### Step 2: Convert if necessary
```
yq . openapi.yaml >openapi.json
```
### Step 3: Extract the Base URL
```
BASEURL=$(jq -r '.servers[0].url' openapi.json)
```
```
echo $BASEURL
```
### Step 4: Extract the Endpoints
```
jq -r '.paths | keys[]' openapi.json | nl -w2 -s'. '
```
```
Available Endpoints:
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
14. /evals
15. /evals/{eval_id}
16. /evals/{eval_id}/runs
17. /evals/{eval_id}/runs/{run_id}
18. /evals/{eval_id}/runs/{run_id}/output_items
19. /evals/{eval_id}/runs/{run_id}/output_items/{output_item_id}
20. /files
21. /files/{file_id}
22. /files/{file_id}/content
23. /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions
24. /fine_tuning/checkpoints/{fine_tuned_model_checkpoint}/permissions/{permission_id}
25. /fine_tuning/jobs
26. /fine_tuning/jobs/{fine_tuning_job_id}
27. /fine_tuning/jobs/{fine_tuning_job_id}/cancel
28. /fine_tuning/jobs/{fine_tuning_job_id}/checkpoints
29. /fine_tuning/jobs/{fine_tuning_job_id}/events
30. /images/edits
31. /images/generations
32. /images/variations
33. /models
34. /models/{model}
35. /moderations
36. /organization/admin_api_keys
37. /organization/admin_api_keys/{key_id}
38. /organization/audit_logs
39. /organization/certificates
40. /organization/certificates/activate
41. /organization/certificates/deactivate
42. /organization/certificates/{certificate_id}
43. /organization/costs
44. /organization/invites
45. /organization/invites/{invite_id}
46. /organization/projects
47. /organization/projects/{project_id}
48. /organization/projects/{project_id}/api_keys
49. /organization/projects/{project_id}/api_keys/{key_id}
50. /organization/projects/{project_id}/archive
51. /organization/projects/{project_id}/certificates
52. /organization/projects/{project_id}/certificates/activate
53. /organization/projects/{project_id}/certificates/deactivate
54. /organization/projects/{project_id}/rate_limits
55. /organization/projects/{project_id}/rate_limits/{rate_limit_id}
56. /organization/projects/{project_id}/service_accounts
57. /organization/projects/{project_id}/service_accounts/{service_account_id}
58. /organization/projects/{project_id}/users
59. /organization/projects/{project_id}/users/{user_id}
60. /organization/usage/audio_speeches
61. /organization/usage/audio_transcriptions
62. /organization/usage/code_interpreter_sessions
63. /organization/usage/completions
64. /organization/usage/embeddings
65. /organization/usage/images
66. /organization/usage/moderations
67. /organization/usage/vector_stores
68. /organization/users
69. /organization/users/{user_id}
70. /realtime/sessions
71. /realtime/transcription_sessions
72. /responses
73. /responses/{response_id}
74. /responses/{response_id}/input_items
75. /threads
76. /threads/runs
77. /threads/{thread_id}
78. /threads/{thread_id}/messages
79. /threads/{thread_id}/messages/{message_id}
80. /threads/{thread_id}/runs
81. /threads/{thread_id}/runs/{run_id}
82. /threads/{thread_id}/runs/{run_id}/cancel
83. /threads/{thread_id}/runs/{run_id}/steps
84. /threads/{thread_id}/runs/{run_id}/steps/{step_id}
85. /threads/{thread_id}/runs/{run_id}/submit_tool_outputs
86. /uploads
87. /uploads/{upload_id}/cancel
88. /uploads/{upload_id}/complete
89. /uploads/{upload_id}/parts
90. /vector_stores
91. /vector_stores/{vector_store_id}
92. /vector_stores/{vector_store_id}/file_batches
93. /vector_stores/{vector_store_id}/file_batches/{batch_id}
94. /vector_stores/{vector_store_id}/file_batches/{batch_id}/cancel
95. /vector_stores/{vector_store_id}/file_batches/{batch_id}/files
96. /vector_stores/{vector_store_id}/files
97. /vector_stores/{vector_store_id}/files/{file_id}
98. /vector_stores/{vector_store_id}/files/{file_id}/content
99. /vector_stores/{vector_store_id}/search
```
### Step 5: Pick an endpoint
```
NUM=9 ENDPOINT=$(jq -r '.paths | keys[]' openapi.json | sed -n "${NUM}p")
```
```
echo $ENDPOINT
```

### Step 6: Pick a method
```
jq -r --arg path "$ENDPOINT" '.paths[$path] | keys[]' openapi.json
```
```
METHOD="post"
```

### Step 7: Extract the parameter reference
```
REF=$(jq -r --arg path "$ENDPOINT" --arg method "$METHOD" \
  '.paths[$path][$method].requestBody.content["application/json"].schema["$ref"]' openapi.json)
```
### Step 8: Extract the schema
```
SCHEMA_NAME=$(echo "$REF" | sed 's|#/components/schemas/||')
```
```
SCHEMA_JSON=$(jq --arg name "$SCHEMA_NAME" '.components.schemas[$name]' openapi.json)
```
```
echo "$SCHEMA_JSON" | jq .
```
### Step 9: Create a JSON summary
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
### Step 10: Generate curl command using Python
```
python3 suggest.py
```

## Quick Start

For an automated interactive experience, simply run:

```bash
./script.sh
```

This script will:
1. Download the OpenAI OpenAPI specification
2. Convert it to JSON format
3. Present available endpoints for selection
4. Allow you to choose an HTTP method
5. Extract the required schema
6. Generate a curl command using the OpenAI API

Make sure to set your OpenAI API key as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```
