import os
from pinecone import Pinecone
from dotenv import load_dotenv

load_dotenv(override=True)

pc = Pinecone(api_key=os.environ["PINECONE_API_KEY"])
index = pc.describe_index(os.environ["PINECONE_INDEX"])

print(index.to_dict())