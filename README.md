# API Security and Pydantic Generator

This project demonstrates how to generate Pydantic models from OpenAPI specifications and use them with OpenAI function calling to convert natural language to structured data that conforms to your API schema.

## Overview

The workflow demonstrated in this project:

1. **Generate Models**: Convert OpenAPI specifications to Pydantic models using datamodel-code-generator
2. **Use with OpenAI**: Leverage the generated models with OpenAI function calling
3. **Process Structured Data**: Convert natural language descriptions to validated structured data

## Setup

### Prerequisites

- Python 3.11+
- OpenAI API key

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/apisecpgen.git
   cd apisecpgen
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv openapi-env
   source openapi-env/bin/activate  # On Windows: openapi-env\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install datamodel-code-generator requests openai
   ```

4. Set your OpenAI API key:
   ```bash
   export OPENAI_API_KEY=your_api_key_here  # On Windows: set OPENAI_API_KEY=your_api_key_here
   ```

## Generating Models from OpenAPI

The `generate_models.py` script fetches an OpenAPI specification and generates Pydantic models:

```bash
python generate_models.py
```

This will:
1. Fetch the OpenAPI specification from the Swagger Petstore demo API
2. Generate Pydantic models in `models.py`

You can modify the script to use your own OpenAPI specification by changing the URL.

## Examples

### Pet Store API Examples

This project includes three examples of using the generated models with OpenAI function calling:

#### 1. Basic Example (`openai_function_example.py`)

- Manually defines the function schema
- Uses the generated Pet model to create objects
- Simple approach for getting started

```bash
python openai_function_example.py
```

#### 2. Schema from Input Model (`openai_function_from_models.py`)

- Creates a custom input model (CreatePetInput)
- Automatically generates the function schema from this model
- Uses `model_json_schema()` to extract the schema

```bash
python openai_function_from_models.py
```

#### 3. Direct Model Schema (`openai_direct_model_schema.py`)

- Directly uses the Pet model's schema for function calling
- Extracts schema with `Pet.model_json_schema()`
- Handles complex nested objects (category, tags)

```bash
python openai_direct_model_schema.py
```

### Weather API Example

The `weather_example` directory contains examples of using Pydantic models with OpenAI function calling to create weather forecast applications:

```bash
# Simple example with some predefined structure
python weather_example/simple_weather_forecast.py "Brussels, Belgium"

# Generic example that relies more on OpenAI
python weather_example/generic_weather_forecast.py "San Francisco, California"

# Dynamic OpenAPI example (fetches spec and generates models at runtime)
python weather_example/dynamic_openapi_example.py "https://api.weather.gov/openapi.json" "Generate a weather forecast for New York City"

# Universal OpenAPI example (works with any OpenAPI specification)
python weather_example/universal_openapi_example.py "https://api.weather.gov/openapi.json" "Generate a weather forecast for New York City"
```

These examples demonstrate:
- Creating custom Pydantic models for weather data
- Using OpenAI to convert location descriptions to coordinates
- Generating realistic weather forecasts based on location
- Formatting and displaying the forecast

The examples show a progression from static to fully dynamic:
1. **Simple example**: Uses predefined models and structure
2. **Generic example**: More flexible, relies more on OpenAI to generate content
3. **Dynamic example**: Fetches OpenAPI spec at runtime, generates models on the fly
4. **Universal example**: Works with any OpenAPI specification by directly using JSON schemas

The universal example is the most flexible and can work with any OpenAPI specification:
```bash
# Use the Petstore API
python weather_example/universal_openapi_example.py "https://petstore3.swagger.io/api/v3/openapi.json" "Create a pet named Max who is a golden retriever"

# Use any other OpenAPI specification
python weather_example/universal_openapi_example.py "https://your-api.com/openapi.json" "Your task description"
```

See the [Weather Example README](weather_example/README.md) for more details.

## How It Works

### 1. Model Generation

The `generate_models.py` script uses datamodel-code-generator to convert an OpenAPI specification to Pydantic models:

```python
from pathlib import Path
from datamodel_code_generator import InputFileType, generate

# Fetch OpenAPI spec
response = requests.get('https://petstore3.swagger.io/api/v3/openapi.json')
openapi_content = response.text

# Generate models
generate(
    input_=openapi_content,
    input_file_type=InputFileType.OpenAPI,
    output=Path("models.py")
)
```

### 2. OpenAI Function Calling

The examples demonstrate different approaches to using the generated models with OpenAI function calling:

```python
# Get the JSON schema from our model
schema = CreatePetInput.model_json_schema()

# Define the function using the schema
functions = [
    {
        "type": "function",
        "function": {
            "name": "create_pet",
            "description": "Create a new pet in the store",
            "parameters": schema
        }
    }
]

# Make the API call to OpenAI
response = client.chat.completions.create(
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "You are a helpful assistant that creates pet records."},
        {"role": "user", "content": f"Create a pet record based on this description: {description}"}
    ],
    tools=functions,
    tool_choice={"type": "function", "function": {"name": "create_pet"}}
)
```

### 3. Status Mapping

The examples include status mapping to handle natural language descriptions:

```python
# Map common phrases to valid enum values
status_mapping = {
    "available for adoption": "available",
    "up for adoption": "available",
    "adoptable": "available",
    "sold to a new owner": "sold",
    "has been sold": "sold",
    "waiting for pickup": "pending",
    "on hold": "pending"
}
```

## Benefits

1. **Type Safety**: Generated Pydantic models provide type checking and validation
2. **Schema Consistency**: Ensures AI-generated data conforms to your API schema
3. **Automatic Updates**: When your API schema changes, regenerate models to stay in sync
4. **Improved Developer Experience**: Autocomplete and type hints for your API models

## Advanced Usage

You can extend this approach to:

1. **API Client Generation**: Generate API clients from OpenAPI specs
2. **Mock Data Generation**: Create realistic test data that conforms to your schema
3. **Data Validation**: Validate incoming data against your schema
4. **Documentation Generation**: Auto-generate documentation from your models

## Troubleshooting

### Common Issues

1. **Invalid Status Values**: If OpenAI returns status values that don't match your enum, use the status mapping approach demonstrated in the examples.

2. **Pydantic Version Compatibility**: If using Pydantic V2, use `model_config` with `json_schema_extra` instead of `Config` with `schema_extra`.

3. **OpenAI API Key**: Ensure your OpenAI API key is set as an environment variable.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
