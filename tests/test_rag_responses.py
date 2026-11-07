
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from rag_assistant import answer_question
from dotenv import load_dotenv

load_dotenv(override=True)

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
    "What's the difference between baking and roasting?",
]

output = Path(__file__).parent / "results" / "final_results.md"
output.parent.mkdir(parents=True, exist_ok=True)

with output.open("w", encoding="utf-8") as file:
    file.write("# Culinary RAG Assistant - Final Tests\n\n")

    for i, question in enumerate(questions, 1):
        print(f"Testing {i}/10: {question}")

        try:
            answer = answer_question(question)
        except Exception as error:
            answer = f"ERROR: {error}"
            print(answer)

        file.write(f"## Question {i}\n\n")
        file.write(f"**Question:** {question}\n\n")
        file.write(f"**Answer:**\n\n{answer}\n\n")
        file.write("---\n\n")

print(f"\nResults saved to {output}")
