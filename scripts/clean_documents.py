from pathlib import Path
import re
import html
from dotenv import load_dotenv

load_dotenv(override=True)

input_folder = Path("data/processed_documents")
output_folder = Path("data/cleaned_documents")

output_folder.mkdir(parents=True, exist_ok=True)


def clean_markdown(text):
    # Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Fix HTML entities like &amp;
    text = html.unescape(text)

    # Remove trailing whitespace from lines
    text = "\n".join(line.rstrip() for line in text.split("\n"))

    # Remove excessive blank lines (keep at most two)
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove leading/trailing blank space
    text = text.strip()

    # Remove stray PDF bullet glyphs
    text = re.sub(r"(?m)^(\s*-\s*)\uf0b7\s*", r"\1", text)

    return text + "\n"


for source in input_folder.glob("*.md"):

    output_file = output_folder / source.name

    text = source.read_text(encoding="utf-8")
    cleaned = clean_markdown(text)

    output_file.write_text(cleaned, encoding="utf-8")

    print(f"Cleaned: {source.name}")

print("Cleaning complete!")