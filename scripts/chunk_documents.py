
import json
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(override=True)

import nltk
from nltk.tokenize import sent_tokenize
from docling.document_converter import DocumentConverter
from docling.chunking import HybridChunker


nltk.download("punkt", quiet=True)
nltk.download("punkt_tab", quiet=True)

input_folder = Path("data/cleaned_documents")
output_file = Path("data/chunks.jsonl")
review_file = Path("data/chunks_review.jsonl")

target_words = 220
max_words = 350
min_words = 50

converter = DocumentConverter()
chunker = HybridChunker(max_tokens=500, merge_peers=True)


def needs_review(text):
    text = text.strip()

    if not text:
        return True
    if re.fullmatch(r"\d+", text):
        return True
    if len(text) < 100:
        return True
    if "[image]" in text.lower():
        return True
    if "editorial note:" in text.lower():
        return True

    return False


def group_sentences(sentences):
    groups = []
    current = []
    words = 0

    for sentence in sentences:
        count = len(sentence.split())

        if current and words + count > max_words:
            groups.append(" ".join(current))
            current = []
            words = 0

        current.append(sentence)
        words += count

        if words >= target_words:
            groups.append(" ".join(current))
            current = []
            words = 0

    if current:
        groups.append(" ".join(current))

    return groups


def sentence_aware_chunks(chunks):
    sections = []

    for chunk in chunks:
        headings = tuple(chunk.meta.headings or [])
        text = chunk.text.strip()

        if not text:
            continue

        if sections and sections[-1]["headings"] == headings:
            sections[-1]["parts"].append(text)
        else:
            sections.append({
                "headings": headings,
                "parts": [text]
            })

    results = []

    for section in sections:
        text = " ".join(section["parts"])
        sentences = sent_tokenize(text)
        groups = group_sentences(sentences)

        for group in groups:
            results.append({
                "headings": section["headings"],
                "text": group
            })

    return results


def merge_small_chunks(chunks):
    merged = []

    for chunk in chunks:
        if not merged:
            merged.append(chunk.copy())
            continue

        previous = merged[-1]

        same_heading = previous["headings"] == chunk["headings"]

        previous_words = len(previous["text"].split())
        current_words = len(chunk["text"].split())

        if (
            same_heading
            and (previous_words < min_words or current_words < min_words)
            and previous_words + current_words <= max_words
        ):
            previous["text"] += " " + chunk["text"]
        else:
            merged.append(chunk.copy())

    return merged


def process_file(file):
    document = converter.convert(str(file)).document
    original_chunks = list(chunker.chunk(document))

    chunks = sentence_aware_chunks(original_chunks)
    chunks = merge_small_chunks(chunks)

    results = []

    for chunk in chunks:
        text = chunk["text"].strip()
        headings = chunk["headings"]

        if not text:
            continue

        if headings:
            text = "\n".join(headings) + "\n" + text

        results.append(text)

    return results


def main():
    if not input_folder.exists():
        print("Could not find cleaned_documents folder.")
        return

    files = sorted(input_folder.glob("*.md"))

    if not files:
        print("No Markdown files found.")
        return

    all_chunks = []
    review_chunks = []

    for file_number, file in enumerate(files, start=1):
        print(f"Processing: {file.name}")

        chunks = process_file(file)

        for chunk_number, text in enumerate(chunks, start=1):
            record = {
                "_id": f"doc_{file_number:03d}_chunk_{chunk_number:04d}",
                "text": text,
                "source": file.name,
                "chunk_number": chunk_number
            }

            all_chunks.append(record)

            if needs_review(text):
                review_chunks.append(record)

    with open(output_file, "w", encoding="utf-8") as f:
        for chunk in all_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    with open(review_file, "w", encoding="utf-8") as f:
        for chunk in review_chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")

    print("\nChunking complete!")
    print(f"Files processed: {len(files)}")
    print(f"Total chunks: {len(all_chunks)}")
    print(f"Chunks needing review: {len(review_chunks)}")
    print(f"Saved to: {output_file}")
    print(f"Review file: {review_file}")


if __name__ == "__main__":
    main()
