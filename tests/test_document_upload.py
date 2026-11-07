import json
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

HOST = os.environ["PINECONE_HOST"]
NAMESPACE = os.environ["PINECONE_NAMESPACE"]

with open("data/chunks.jsonl", encoding="utf-8") as f:
    document = json.loads(next(f))

url = f"{HOST}/namespaces/{NAMESPACE}/documents/upsert"

headers = {
    "Api-Key": os.environ["PINECONE_API_KEY"],
    "X-Pinecone-API-Version": "2026-07",
    "Content-Type": "application/json",
}

response = requests.post(
    url,
    headers=headers,
    json={"documents": [document]},
    timeout=60,
)

print("Status:", response.status_code)
print("Response:", response.text)