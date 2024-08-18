from openai import AzureOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
    api_version="2023-03-15-preview",
    azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)