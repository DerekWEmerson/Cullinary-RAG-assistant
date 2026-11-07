# Culinary RAG Assistant

**A source-grounded culinary question-answering assistant built with Python, Pinecone, Docling, and OpenAI.**

The Culinary RAG Assistant answers questions about cooking techniques, food science, ingredient substitutions, and recipes by retrieving relevant information from a curated culinary knowledge base. Rather than relying solely on a language model's general knowledge, it supplies retrieved passages as context and returns source references alongside its answers.

This project demonstrates an end-to-end retrieval-augmented generation (RAG) workflow: document ingestion, text cleaning, structure-aware chunking, vector search, answer generation, and repeatable evaluation.

## Highlights

- **Multi-format ingestion:** Converts PDF, HTML, TXT, and JPG source material into Markdown with Docling.
- **Custom chunking:** Combines Docling's `HybridChunker` with sentence grouping, heading preservation, and small-chunk merging.
- **Quality review:** Flags potentially problematic chunks for manual inspection without silently discarding them.
- **Structured and unstructured data:** Supports culinary reference documents and a separate CSV recipe-ingestion path.
- **Semantic retrieval:** Searches a Pinecone index using text-based embedding queries and retrieves up to five matching records.
- **Grounded responses:** Uses OpenAI's `gpt-4o-mini` to answer from retrieved context, with numbered citations and a source list.
- **Evaluation scripts:** Includes a fixed set of ten culinary questions for retrieval inspection and end-to-end response testing.

## How it works

```text
PDF / HTML / TXT / JPG             Recipe CSV
          |                            |
     Docling conversion           CSV parsing
          |                            |
     Markdown cleaning            Recipe records
          |                            |
  Hybrid + sentence-aware               |
        chunking                        |
          |                            |
  JSONL records + review file           |
          |                            |
          +--------> Pinecone <---------+
                         |
                   Semantic search
                         |
                 Top 5 retrieved records
                         |
                Context + user question
                         |
                  OpenAI gpt-4o-mini
                         |
                Answer + source citations
```

### Document processing

1. `docling_all.py` converts supported source files to Markdown, skipping files already processed.
2. `clean_documents.py` normalizes whitespace, line endings, HTML entities, and stray bullet characters.
3. `chunk_documents.py` uses Docling's `HybridChunker`, then groups sentences into readable sections while retaining headings. It also generates `chunks_review.jsonl` to identify records needing review.
4. `pinecone_chunk_upload.py` validates record IDs and uploads document chunks in batches with retries.
5. `pinecone_CSV_upload.py` transforms CSV recipe rows into searchable records and uploads them separately, retrying on Pinecone rate limits.

### Retrieval and generation

When a user asks a question, `rag_assistant.py` sends it to Pinecone's document search endpoint, requests up to five matches, and passes their text to `gpt-4o-mini`. The prompt instructs the model to use only the retrieved context, cite numbered passages, and acknowledge when the available information is insufficient. The response includes a source list with document names and chunk numbers.

For non-recipe questions, retrieved recipe records are deprioritized so reference material can take precedence.

## Tech stack

| Component | Technology |
| --- | --- |
| Application | Python, command-line interface |
| Document extraction | Docling |
| Chunking | Docling `HybridChunker`, NLTK |
| Vector search and storage | Pinecone |
| Answer generation | OpenAI `gpt-4o-mini` |
| HTTP requests | Requests |
| Configuration | `python-dotenv` |

## Getting started

**Requirements:** Python, an OpenAI API key, and access to a Pinecone index configured for document search with integrated embedding. The application expects an existing, populated Pinecone index; installing the code alone does not provision or populate one.

1. Clone this repository and enter its root directory.
2. Create and activate a virtual environment.
3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in your configuration:

   ```dotenv
   OPENAI_API_KEY=
   PINECONE_API_KEY=
   PINECONE_HOST=
   PINECONE_NAMESPACE=
   PINECONE_INDEX=
   ```

   Use the host, namespace, and index associated with **your own** Pinecone setup. Keep `.env` private; never commit API keys.

5. From the repository root, launch the assistant:

   ```bash
   python rag_assistant.py
   ```

6. Ask a culinary question, such as *Why does bread dough need to be kneaded?* Type `exit` or `quit` to close the program.

> **Note:** Running the assistant requires searchable data already uploaded to the configured Pinecone index. Pinecone and OpenAI usage may incur charges.

## Rebuilding the knowledge base

The data preparation scripts are separate from the interactive assistant. If you have suitable source documents and permission to use them, place them in `data/raw_documents/` and run the following commands **from the repository root** (assuming the scripts are in `scripts/`):

```bash
python scripts/docling_all.py
python scripts/clean_documents.py
python scripts/chunk_documents.py
python scripts/pinecone_chunk_upload.py
```

This produces cleaned Markdown and JSONL chunk records before uploading them to Pinecone. Review `data/chunks_review.jsonl` before treating the resulting corpus as production-ready.

For the separate recipe ingestion workflow, `pinecone_CSV_upload.py` expects a file at `data/cleaned_documents/13k-recipes.csv` with `Title`, `Cleaned_Ingredients`, and `Instructions` columns:

```bash
python scripts/pinecone_CSV_upload.py
```

**Caution:** Both Pinecone upload scripts write records to the configured index and namespace. Do not run them unless you intend to modify that index. The original source corpus and recipe CSV are not automatically downloaded by this repository.

## Testing and evaluation

The project includes several scripts for inspecting individual stages of the pipeline:

| Script | Purpose |
| --- | --- |
| `tests/test_docling.py` | Convert a sample PDF to Markdown; requires the named sample file locally |
| `tests/test_document_upload.py` | Submit one chunk to Pinecone; **writes to the index** |
| `tests/test_pinecone_retrieval.py` | Inspect retrieved matches for ten predefined culinary questions |
| `tests/test_rag_responses.py` | Generate answers for the same ten questions and save them to `tests/results/final_results.md` |
| `scripts/check_index.py` | Display Pinecone index metadata |

Run the end-to-end response test from the repository root:

```bash
python tests/test_rag_responses.py
```

The saved results make it possible to review answer relevance, grounding, and source references. **The test script records outputs; it does not automatically calculate an accuracy score.** Any reported evaluation score should be supported by a separate documented grading rubric.

## Project structure

```text
.
├── rag_assistant.py
├── requirements.txt
├── .env.example
├── scripts/
│   ├── docling_all.py
│   ├── clean_documents.py
│   ├── chunk_documents.py
│   ├── pinecone_chunk_upload.py
│   ├── pinecone_CSV_upload.py
│   └── check_index.py
├── tests/
│   ├── test_docling.py
│   ├── test_document_upload.py
│   ├── test_pinecone_retrieval.py
│   ├── test_rag_responses.py
│   └── results/
│       └── final_results.md
└── data/
    ├── raw_documents/
    ├── processed_documents/
    ├── cleaned_documents/
    ├── chunks.jsonl
    └── chunks_review.jsonl
```

The tree shows the **intended repository organization**. Generated files and source datasets may be excluded from version control; the corresponding directories may need to be created locally. If your uploaded filenames or locations differ, update the paths in this README accordingly.

## Design decisions and trade-offs

- **Readable, source-aware chunks:** Headings are retained and sentence boundaries are respected, improving the usefulness of retrieved context. Word-count thresholds and token limits are heuristics, not guarantees of ideal retrieval quality.
- **Separate recipe ingestion:** Structured CSV recipes are converted directly to text records rather than being routed through the document-extraction pipeline.
- **Simple, inspectable retrieval:** A fixed `top_k=5` and explicit search payload make the pipeline easy to understand and debug.
- **Transparent evidence:** Answers include both in-text citation markers and source names/chunk numbers. These references identify retrieved records; they are not independent verification of every claim.
- **Practical evaluation:** A repeatable question set enables qualitative comparisons as prompts, chunking, and retrieval settings change.

## Future improvements

Potential extensions include a web interface, automated retrieval and answer-quality metrics, improved recipe-versus-reference ranking, configurable retrieval settings, and broader evaluation coverage.

## Project status

The command-line RAG assistant and its ten-question response test have been run successfully. This repository showcases a working learning/portfolio project, not a hosted production service.
