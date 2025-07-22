import os
from openai import OpenAI

def main():
    # Retrieve the OpenAI API key from the environment variable
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable is not set.")
        return

    # Retrieve the JSON payload from the COMBINED_JSON environment variable
    combined_json = os.getenv("COMBINED_JSON")
    if not combined_json:
        print("Error: COMBINED_JSON environment variable is not set.")
        return

    # Initialize the OpenAI API client
    # Explicitly set only the api_key to avoid any unexpected configuration issues
    client = OpenAI()
    client.api_key = api_key

    # Construct the prompt for the model
    prompt = (
        "You are a command-line assistant.\n\n"
        "I will provide you with a JSON object: \n\n"
        f"{combined_json}\n\n"
        "Craft a curl command based on this. \n" 
        "The Bearer token is in $OPENAI_API_KEY\n"
        "Do not use placeholders, use the actual values.\n"
        "verify closly there are no quoting issues.\n"
        "Always suggest - if required - model gpt-4o \n"
        "For embedding related suggestions use text-embedding-ada-002. \n"
        "Only use required parameters in payloads.\n"
    )

    try:
        # Make a request to the OpenAI Chat Completions API
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates curl commands."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )

        # Extract and print the generated curl command
        curl_command = response.choices[0].message.content.strip()
        print("Generated curl command:")
        print(curl_command)

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
