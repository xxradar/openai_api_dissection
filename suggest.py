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
    client = OpenAI()

    # Construct the prompt for the model
    prompt = (
        "You are a command-line assistant.\n\n"
        "I will provide you with a JSON object containing API endpoint information:\n\n"
        f"{combined_json}\n\n"
        "Generate a curl command based on this information:\n" 
        "- Use Bearer token from $OPENAI_API_KEY\n"
        "- Use actual values, not placeholders\n"
        "- Verify closely there are no quoting issues\n"
        "- For chat completions, suggest model 'gpt-4o'\n"
        "- For embeddings, use model 'text-embedding-ada-002'\n"
        "- Include only required parameters in the payload\n"
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
