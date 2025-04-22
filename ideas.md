```
NUM=9

ENDPOINT=$(jq -r '.paths | keys_unsorted[]' openapi.json | sed -n "${NUM}p")

METHOD="post"


DESCRIPTION=$(jq -r --arg ep "$ENDPOINT" '.paths[$ep].'$METHOD'.description' openapi.json)


echo "$DESCRIPTION"
```
