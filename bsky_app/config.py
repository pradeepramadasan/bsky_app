import os
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load environment variables
load_dotenv('x.env')

# Initialize Azure OpenAI client
azure_client = AzureOpenAI(
    azure_endpoint=os.getenv('ENDPOINT_URL'),
    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
    api_version="2024-12-01-preview"
)

# GPT-4o deployment configuration
gpt4o_deployment = os.getenv('GPT4O_DEPLOYMENT_NAME')
assert gpt4o_deployment, "GPT4O deployment name missing in environment variables"

config_list_gpt4o = [{
    "model": gpt4o_deployment,
    "api_key": os.getenv('AZURE_OPENAI_API_KEY'),
    "base_url": os.getenv('ENDPOINT_URL'),
    "api_type": "azure",
    "api_version": "2024-12-01-preview"
}]

# Bluesky credentials
BLUESKY_USERNAME = os.getenv('BSKYUNAME')
BLUESKY_PASSWORD = os.getenv('BSKYPASSWD')