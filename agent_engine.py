import os
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY was not loaded. Check your .env file.")

client = genai.Client(api_key=api_key)


CODE_EXTENSIONS = {
    ".py", ".js", ".ts", ".java", ".cpp", ".c",
    ".sql", ".html", ".css"
}


def infer_embedding_task(question: str, file_path: Path | None = None) -> str:
    q = question.lower()

    if file_path and file_path.suffix.lower() in CODE_EXTENSIONS:
        return "code retrieval"

    if any(keyword in q for keyword in [
        "is it true",
        "verify",
        "fact check",
        "check if",
        "confirm whether",
        "is this correct",
    ]):
        return "fact checking"

    if any(keyword in q for keyword in [
        "find",
        "search",
        "look for",
        "retrieve",
        "show me",
        "where is",
        "which document",
    ]):
        return "search result"

    return "question answering"


def format_query_for_embedding(question: str, file_path: Path | None = None) -> str:
    task = infer_embedding_task(question, file_path)
    return f"task: {task} | query: {question}"


def ask_file_question(
    file_path: Path,
    question: str,
    original_file_name: str | None = None,
) -> str:
    display_name = original_file_name or file_path.name

    file_search_store = client.file_search_stores.create(
        config={
            "display_name": f"store-for-{file_path.stem}",
            "embedding_model": "models/gemini-embedding-2",
        }
    )

    operation = client.file_search_stores.upload_to_file_search_store(
        file=file_path,
        file_search_store_name=file_search_store.name,
        config={
            "display_name": display_name,
            "chunking_config": {
                "white_space_config": {
                    "max_tokens_per_chunk": 512,
                    "max_overlap_tokens": 64,
                }
            },
        },
    )

    while not operation.done:
        time.sleep(3)
        operation = client.operations.get(operation)

    formatted_question = format_query_for_embedding(question, file_path)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=formatted_question,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[file_search_store.name]
                    )
                )
            ]
        ),
    )

    return response.text