import os
from dotenv import load_dotenv
from pydantic_ai.providers.google import GoogleProvider

# Load your .env file
load_dotenv()

# 1. Initialize the provider (it will use GOOGLE_API_KEY from your .env)
provider = GoogleProvider()

# 2. Access the underlying Google GenAI client to list models
# Note: This is an async call in the client
async def list_available_models():
    # .models.list() returns a generator of model objects
    models = provider.client.models.list()
    
    print("Available Models:")
    for model in models:
        # Each model object has a 'name' attribute (e.g., 'models/gemini-1.5-flash')
        print(f"- {model.name}")

# Run the check
import asyncio
asyncio.run(list_available_models())