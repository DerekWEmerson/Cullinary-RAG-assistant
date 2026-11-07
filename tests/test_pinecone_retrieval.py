
import os
import requests
from dotenv import load_dotenv

load_dotenv(override=True)

host = os.environ["PINECONE_HOST"]
namespace = os.environ["PINECONE_NAMESPACE"]

questions = [
    "What's the difference between sautéing and pan-frying?",
    "How do I keep chicken from drying out when I cook it?",
    "What temperature should I cook chicken to?",
    "What can I use instead of buttermilk?",
    "How many tablespoons are in a cup?",
    "Why does my bread dough need to be kneaded?",
    "How do I stop food from sticking to the pan?",
    "What's the best way to cook vegetables without losing their nutrients?",
    "Why does meat turn brown when I cook it?",
    "What's the difference between baking and roasting?"
]
top_k = 5

headers = {
    "Api-Key": os.environ["PINECONE_API_KEY"],
    "X-Pinecone-API-Version": "2026-07",
    "Content-Type": "application/json"
}

url = f"{host}/namespaces/{namespace}/documents/search"

for question in questions:
    payload = {
        "top_k": top_k,
        "score_by": [
            {
                "type": "embed",
                "field": "text",
                "query": question
            }
        ],
        "include_fields": ["text", "source", "chunk_number"]
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    if response.status_code != 200:
        print("Status:", response.status_code)
        print("Response:", response.text)

    response.raise_for_status()

    data = response.json()
    matches = data.get("matches", [])

    print(f"\nQuestion: {question}")
    print(f"Results found: {len(matches)}")

    for i, match in enumerate(matches, start=1):
        print(f"\nResult {i}")
        print(f"Score: {match.get('_score', 'N/A')}")
        print(f"Source: {match.get('source', 'Unknown')}")
        print(f"Chunk: {match.get('chunk_number', 'Unknown')}")
        print(f"Text: {match.get('text', 'No text returned')}")
        print("-" * 50)
