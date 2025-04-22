```
NUM=9

ENDPOINT=$(jq -r '.paths | keys_unsorted[]' openapi.json | sed -n "${NUM}p")
DESCRIPTION=$(jq -r --arg ep "$ENDPOINT" '.paths[$ep].post.description' openapi.json)


echo "$DESCRIPTION"
```
