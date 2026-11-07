from pathlib import Path
from docling.document_converter import DocumentConverter
from dotenv import load_dotenv

load_dotenv(override=True)

source = Path("data/raw_documents/Cooking-Methods-Manual.pdf") 
output_folder = Path("data/processed_documents")
output_folder.mkdir(parents=True, exist_ok=True) # Makes folder if doesn't exist.

converter = DocumentConverter()
doc = converter.convert(source).document

output_file = output_folder / f"{source.stem}.md"
output_file.write_text(doc.export_to_markdown(), encoding="utf-8")

print(f"Saved to {output_file}")