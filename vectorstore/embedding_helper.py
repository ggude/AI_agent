from openai import OpenAI
from config import OPENAI_API_KEY

api_key = OPENAI_API_KEY
client = OpenAI(api_key=api_key)

def get_openai_embedding(text):
    response = client.embeddings.create(model="text-embedding-3-small", input=text)
    return response.data[0].embedding