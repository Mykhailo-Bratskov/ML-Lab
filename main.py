import tempfile
from pathlib import Path

import streamlit as st

from agent_engine import ask_file_question


st.set_page_config(
    page_title="File Search Agent",
    page_icon="📄",
    layout="centered",
)

st.title("📄 File Search Agent")
st.write("Upload a file and ask questions about it using Gemini File Search.")

uploaded_file = st.file_uploader(
    "Upload your document",
    type=["txt", "pdf", "md", "py", "csv", "json", "html", "css", "js", "ts"],
)

question = st.text_area(
    "Ask a question about the file",
    placeholder="Example: Summarize this file. What are the main ideas?",
)

if st.button("Ask Gemini"):
    if uploaded_file is None:
        st.warning("Please upload a file first.")
    elif not question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Uploading, indexing, and asking Gemini..."):
            suffix = Path(uploaded_file.name).suffix

            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                tmp.write(uploaded_file.read())
                tmp_path = Path(tmp.name)

            answer = ask_file_question(
                file_path=tmp_path,
                question=question,
                original_file_name=uploaded_file.name,
            )

        st.subheader("Answer")
        st.write(answer)