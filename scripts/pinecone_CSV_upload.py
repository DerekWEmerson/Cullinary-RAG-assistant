
import os
import csv
from pinecone import Pinecone

import time
from pinecone.exceptions import PineconeException
from dotenv import load_dotenv

load_dotenv(override=True)

CSV_FILE = "data/cleaned_documents/13k-recipes.csv"
NAMESPACE = os.environ["PINECONE_NAMESPACE"]
BATCH_SIZE = 50

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.Index(os.environ["PINECONE_INDEX"])

with open(CSV_FILE, "r", encoding="utf-8-sig", newline="") as file:
    recipes = list(csv.DictReader(file))

print(f"Found {len(recipes)} recipes.")
print(f"CSV columns: {list(recipes[0].keys())}")

records = []

for i, recipe in enumerate(recipes, start=1):
    text = (
        f"Recipe: {recipe['Title']}\n"
        f"Ingredients: {recipe['Cleaned_Ingredients']}\n"
        f"Instructions: {recipe['Instructions']}"
    )

    records.append({
        "_id": f"recipe_{i:05d}",
        "text": text,
        "source": "13k-recipes.csv",
        "chunk_number": 1
    })

for start in range(0, len(records), BATCH_SIZE):
    batch = records[start:start + BATCH_SIZE]

    while True:
        try:
            index.documents.upsert(
                namespace=NAMESPACE,
                documents=batch
            )
            break

        except PineconeException as error:
            if "429" not in str(error):
                raise

            print("Rate limit reached. Waiting 60 seconds...")
            time.sleep(60)

    print(f"Uploaded {min(start + BATCH_SIZE, len(records))}/{len(records)}")

print("Recipe upload complete!")
