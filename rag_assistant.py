import os
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)


HOST = os.environ["PINECONE_HOST"]
NAMESPACE = os.environ["PINECONE_NAMESPACE"]
TOP_K = 5

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def retrieve(question):
    url = f"{HOST}/namespaces/{NAMESPACE}/documents/search"

    headers = {
        "Api-Key": os.environ["PINECONE_API_KEY"],
        "X-Pinecone-API-Version": "2026-07",
        "Content-Type": "application/json",
    }

    payload = {
        "top_k": TOP_K,
        "score_by": [
            {"type": "embed", "field": "text", "query": question}
        ],
        "include_fields": ["text", "source", "chunk_number"],
    }

    response = requests.post(
        url, headers=headers, json=payload, timeout=60
    )

    if response.status_code == 429:
        raise RuntimeError(
            f"Pinecone rate limit:\n{response.text[:2000]}"
        )

    response.raise_for_status()
    matches = response.json().get("matches", [])

    if "recipe" not in question.lower():
        matches.sort(
            key=lambda match: (
                match.get("source") == "13k-recipes.csv",
                -match.get("_score", 0)
            )
        )

    return matches


def answer_question(question):
    matches = retrieve(question)

    if not matches:
        return "No relevant documents found."

    context = []
    sources = []

    for i, match in enumerate(matches, start=1):
        source = match.get("source", "Unknown")
        chunk = match.get("chunk_number", "Unknown")
        content = match.get("text", "")

        context.append(f"[{i}] {content}")
        sources.append(f"[{i}] {source} (chunk {chunk})")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful culinary assistant. "
                    "Answer using only the provided context. "
                    "Cite evidence using [1], [2], etc. "
                    "If the context does not contain the answer, "
                    "say you don't have enough information."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n\n"
                    f"Context:\n{chr(10).join(context)}"
                ),
            },
        ],
    )

    answer = response.choices[0].message.content

    return answer + "\n\nSources:\n" + "\n".join(sources)


def main():
    print("\nCulinary RAG Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("You: ").strip()

        if question.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if not question:
            continue

        try:
            print("\nAssistant:")
            print(answer_question(question))
            print()
        except Exception as error:
            print(f"\nError: {error}\n")


if __name__ == "__main__":
    main()
