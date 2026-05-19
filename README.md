# Agentic AI (Draft)

A simple draft project for asking questions about a file using **Google Gemini File Search**.

This repository currently includes two interfaces:
- `main.py`: a Streamlit web app
- `terminal_agent.py`: a terminal/CLI version

Both flows upload a file to a Gemini file search store, index it with embeddings, and answer your question using `gemini-2.5-flash`.

## Features

- Upload or pass a local file
- Ask natural language questions about file content
- Basic query task shaping (`code retrieval`, `fact checking`, `search result`, `question answering`)
- Chunking configuration for file indexing

## Project Structure

- `main.py` - Streamlit UI for file upload + question input
- `agent_engine.py` - core Gemini file search logic used by Streamlit app
- `terminal_agent.py` - standalone terminal agent flow
- `debug_File.py` - small env debug utility for printing the API key

## Requirements

- Python 3.10+
- A valid Google Gemini API key

Install dependencies:

```bash
pip install streamlit google-genai python-dotenv
```

## Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run

### Option 1: Streamlit app

```bash
streamlit run main.py
```

Then open the local Streamlit URL, upload a supported file, and ask your question.

### Option 2: Terminal app

```bash
python terminal_agent.py
```

When prompted, enter your question together with a file path.

Example:

```text
Summarize this file C:\path\to\document.pdf
```

Type `quit` to exit.

## Notes

- This is an early draft and may need stronger error handling and cleanup (for example, lifecycle management of file search stores).
- Supported file types in the Streamlit uploader include: `txt`, `pdf`, `md`, `py`, `csv`, `json`, `html`, `css`, `js`, `ts`.
