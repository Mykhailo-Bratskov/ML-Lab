# Agentic AI (Draft)

A simple draft project for asking questions about files and contest rules using **Google Gemini**.

## Project Structure

- `agents/`
- `agents/first_agent.py` - contest-rules extractor (URL or PDF)
- `agents/terminal_agent.py` - terminal/CLI file Q&A flow
- `agents/code_agent.py` - placeholder for code-focused agent
- `agents/research_agent.py` - placeholder for research agent
- `agents/review_agent.py` - placeholder for review agent
- `utils/`
- `utils/prompt_input.py` - prompt and contest-rule input helpers
- `utils/metadata_extraction.py` - metadata extraction utilities
- `utils/token_counter.py` - token counting helper
- `utils/debug_file.py` - small env debug utility
- `app/main.py` - app entrypoint placeholder

## Requirements

- Python 3.10+
- A valid Google Gemini API key

Install dependencies:

```bash
pip install streamlit google-genai python-dotenv pandas edfio
```

## Setup

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

## Run

- Contest rules extraction agent:

```bash
python agents/first_agent.py
```

- Terminal file Q&A agent:

```bash
python agents/terminal_agent.py
```
