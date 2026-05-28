# add metadata_usage for token count to see the prices 
import os
import time
from pathlib import Path
from urllib.parse import urlparse
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY was not loaded. Check your .env file.")

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-2.5-flash"

RULES_PROMPT = """
Extract the contest rules from the provided source.
Return only valid JSON with this schema:
{
  "contest_name": "string or null",
  "eligibility": ["..."],
  "submission_requirements": ["..."],
  "deadlines": ["..."],
  "judging_criteria": ["..."],
  "prizes": ["..."],
  "prohibited_or_disqualifications": ["..."],
  "other_important_rules": ["..."],
  "source_type": "url|pdf"
}
If a section is missing, return an empty array for that section.
""".strip()


def is_url(text: str) -> bool:
    if not isinstance(text, str) or not text.strip():
        return False
    parsed = urlparse(text.strip())
    return parsed.scheme in ("http", "https") and bool(parsed.netloc)


def _extract_from_url(url: str) -> str:
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part(text=f"{RULES_PROMPT}\n\nUse this URL as the source: {url}"),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            tools=[types.Tool(url_context=types.UrlContext())],
            temperature=0.1,
        ),
    )
    return response.text


def _wait_for_operation(operation):
    while not operation.done:
        time.sleep(2)
        operation = client.operations.get(operation)
    return operation


def _extract_from_pdf(pdf_path: Path) -> str:
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")
    if pdf_path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported for local file input.")

    store = client.file_search_stores.create(
        config={
            "display_name": f"contest-rules-{pdf_path.stem}",
            "embedding_model": "models/gemini-embedding-2",
        }
    )

    operation = client.file_search_stores.upload_to_file_search_store(
        file=pdf_path,
        file_search_store_name=store.name,
        config={"display_name": pdf_path.name},
    )
    _wait_for_operation(operation)

    response = client.models.generate_content(
        model=MODEL_ID,
        contents=RULES_PROMPT,
        config=types.GenerateContentConfig(
            tools=[
                types.Tool(
                    file_search=types.FileSearch(file_search_store_names=[store.name])
                )
            ],
            temperature=0.1,
        ),
    )

    print("--- Challenge Debrief Agent Token Usage ---")
    print(f"Prompt Tokens (Input): {response.usage_metadata.prompt_token_count}")
    print(f"Candidate Tokens (Output): {response.usage_metadata.candidates_token_count}")
    print(f"Total Tokens: {response.usage_metadata.total_token_count}")

    return response.text


def run_challenge_agent(source: str) -> str:
    """
    Extract contest rules from either:
    1) a URL, or
    2) a local PDF path.
    """
    source = source.strip()

    if is_url(source):
        return _extract_from_url(source)

    pdf_path = Path(source).expanduser().resolve()
    return _extract_from_pdf(pdf_path)


def main():
    user_input = input("Enter a contest URL or a local PDF path: ").strip()
    if not user_input:
        print("No input provided.")
        return

    try:
        result = run_first_agent(user_input)
        print("\nExtracted Rules JSON:\n")
        print(result)
    except Exception as exc:
        print(f"Error: {exc}")


if __name__ == "__main__":
    main()
