import os

import openai
from dotenv import find_dotenv, load_dotenv

_ = load_dotenv(find_dotenv())

CLOUDFLARE_ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID")
CLOUDFLARE_API_KEY = os.getenv("CLOUDFLARE_API_KEY")
CLOUDFLARE_GATEWAY_ID = os.getenv("CLOUDFLARE_GATEWAY_ID")

openai_client = openai.OpenAI(
    api_key=CLOUDFLARE_API_KEY,
    base_url=f"https://gateway.ai.cloudflare.com/v1/{CLOUDFLARE_ACCOUNT_ID}/{CLOUDFLARE_GATEWAY_ID}/workers-ai/v1/",
)

def get_embedding(input: str):
    response = openai_client.embeddings.create(
        model="@cf/baai/bge-small-en-v1.5", input=input
    )
    return response.model_dump()
