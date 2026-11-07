from pathlib import Path
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv

load_dotenv(override=True)

input_folder = Path("data/raw_documents")
output_folder = Path("data/processed_documents")
output_folder.mkdir(parents=True, exist_ok=True)

supported_extensions = {".pdf", ".txt", ".html", ".jpg"}

converter = DocumentConverter()

for source in input_folder.iterdir():
    if not source.is_file():
        continue

    # Skip unsupported file types, including CSV
    if source.suffix.lower() not in supported_extensions:
        print(f"Skipping unsupported file: {source.name}")
        continue

    output_file = output_folder / f"{source.stem}.md"

    if output_file.exists(): # Skip documents already processed
        print(f"Skipping {source.name}")
        continue

    try:
        print(f"Processing {source.name}...")
        doc = converter.convert(str(source)).document
        output_file.write_text(doc.export_to_markdown(), encoding="utf-8")
        print(f"Saved: {output_file}")

    
    except Exception as e:
        print(f"Failed to process {source.name}: {e}")