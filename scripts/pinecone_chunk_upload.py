
import json
import os
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv(override=True)

HOST = os.environ["PINECONE_HOST"]
NAMESPACE = os.environ["PINECONE_NAMESPACE"]
INPUT_FILE = Path("data/chunks.jsonl")
BATCH_SIZE = 25

url = f"{HOST}/namespaces/{NAMESPACE}/documents/upsert"

headers = {
    "Api-Key": os.environ["PINECONE_API_KEY"],
    "X-Pinecone-API-Version": "2026-07",
    "Content-Type": "application/json",
}

# Load all chunks
with INPUT_FILE.open("r", encoding="utf-8") as file:
    documents = [
        json.loads(line)
        for line in file
        if line.strip()
    ]

# Check for duplicate IDs
ids = [doc["_id"] for doc in documents]

if len(ids) != len(set(ids)):
    raise ValueError("Duplicate document IDs detected.")

print(f"Loaded {len(documents)} documents.")
print(f"Namespace: {NAMESPACE}\n")

uploaded = 0

# Upload documents in batches
for start in range(0, len(documents), BATCH_SIZE):
    batch = documents[start:start + BATCH_SIZE]

    for attempt in range(3):
        try:
            response = requests.post(
                url,
                headers=headers,
                json={"documents": batch},
                timeout=120,
            )

            response.raise_for_status()

            result = response.json()
            count = result.get("upserted_count", 0)

            if count != len(batch):
                raise RuntimeError(
                    f"Expected {len(batch)} documents, "
                    f"but Pinecone accepted {count}."
                )

            uploaded += count
            print(f"Uploaded {uploaded}/{len(documents)}")
            break

        except (requests.RequestException, RuntimeError) as error:
            print(f"Upload error: {error}")

            if attempt == 2:
                raise

            time.sleep(2 ** (attempt + 1))

    # Small delay between batches
    time.sleep(0.5)

print("\nUPLOAD COMPLETE")
print(f"Documents submitted: {uploaded}")
print(f"Namespace: {NAMESPACE}")
