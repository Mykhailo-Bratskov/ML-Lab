# Creating Embeddings for text prperocessing
# cosine similarity is usually used to find similar cases
# cosine similarity is basically finding angle between vectors, it goes from -1 to 1
# Models to create text embeddings: OpenAI, Word2Vec, GloV
# # Types of Embeddings: Word/Text, Document, Graph, Sentence, Image
import os 
import time
import shlex 
from dotenv import load_dotenv
from pathlib import Path
from google import genai 
from google.genai import types

# Helper functions for processing user's input
CODE_EXTENSIONS = {".py", ".js", ".ts", ".java", ".cpp", ".c", ".sql", ".html", ".css"}

def ExtractFileType(filepath: str): 
    if not os.path.exists(filepath):
        return None
    return os.path.splitext(filepath)[1].lower()

def detect_paths(message: str):
    try:
        parts = shlex.split(message)
    except ValueError:
        parts = message.split()

    paths = []

    for part in parts:
        path = Path(part).expanduser()
        if path.exists():
            paths.append(path)
    
    if len(paths) > 1:
        raise ValueError("You can only provide one path per input")
    return paths

def separate_content(query: str): 
    try:
        parts = shlex.split(query)
    except ValueError:
        parts = query.split()

    paths = detect_paths(query)
    path_strings = {str(path) for path in paths}
    text_parts = [part for part in parts if part not in path_strings]
    text = ' '.join(text_parts).strip()

    return text, paths

def infer_embbd_task(query: str, file_path: Path | None = None): 
    q = query.lower()

    if file_path and file_path.suffix.lower() in CODE_EXTENSIONS:
        return "code retrieval"

    if any(keyword in q for keyword in ["is it true", "verify", "fact check", "check if",
                                        "confirm whether", "is this correct"]):
        return "fact checking"

    if any(keyword in q for keyword in ["find", "search", "look for", "retrieve", "show me", 
                                        "where is", "which document"]):
        return "search result"

    return "question answering"


def format_query_for_embedding(query: str, file_path: Path | None = None) -> str:
    task = infer_embbd_task(query, file_path)
    return f"task: {task} | query: {query}"

# Generate embedding for document of an asymmetric retrieval task:
def format_document_for_embedding(path: Path, content: str) -> str:
    title = path.name or "none"
    return f"title: {title} | text: {content}"

# creating an agent with chunking, and embedding
# we shall use task specification to improve the output of the model
load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY was not loaded. Check your .env file.")

client = genai.Client(api_key=api_key)

def ask_file_question(file_path: Path,question: str,original_file_name: str | None = None,) -> str:
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

    formatted_question = format_query_for_embedding(question)

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

def main():
    # getting input from the user 
    first_question = True

    while True:
        if first_question:
            query_text = input("\nEnter your question and file path, or type 'quit' to exit:\n> ")
            first_question = False
        else:
            query_text = input("\nWhat's your next question? Type 'quit' to exit:\n> ")

        if query_text.lower().strip() == 'quit': 
            break

        try:
            # for an agent to know what he is working with , we both extract text from prompt
            # and also get the filetype, so that it knows how to work with it
            prompt, paths = separate_content(query_text)

            if not paths:
                print("\nNo valid file path found.")
                continue

            file_path = paths[0]
            filetype = ExtractFileType(str(file_path))
            print(f"\nYou uploaded the following file type: {filetype or 'unknown'}")

            print("\nProcessing file. This may take a moment...")

            answer = ask_file_question(file_path=file_path, question=prompt)
            print("\nAnswer:")
            print(answer)

        except Exception as e:
            print("\nAn error occurred:")
            print(e)


if __name__ == "__main__":
    main()