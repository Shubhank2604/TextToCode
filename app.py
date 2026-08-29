import os
import sqlite3

import google.generativeai as genai
import streamlit as st
from dotenv import load_dotenv
from sql_guard import normalize_read_only_sql, query_db


load_dotenv()

st.set_page_config(page_title="Text-to-SQL Explorer")
st.header("Text-to-SQL Explorer")

api_key = os.getenv("GOOGLE_API_KEY", "").strip()
model_name = os.getenv("GEMINI_MODEL", "gemini-pro").strip()

if not api_key:
    st.error("GOOGLE_API_KEY is not configured. Copy .env.example to .env and add your key.")
    st.stop()

genai.configure(api_key=api_key)


def get_gemini_response(question: str, prompt: str) -> str:
    model = genai.GenerativeModel(model_name)
    response = model.generate_content([prompt, question])
    return response.text.strip()


SYSTEM_PROMPT = """
Convert the user's question into exactly one SQLite SELECT query.

The database contains a STUDENT table with these columns:
NAME, CLASS, SECTION, MARKS.

Rules:
- Return SQL only, without Markdown fences or explanation.
- Generate one SELECT statement.
- Never generate INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, PRAGMA,
  ATTACH, DETACH, or any other state-changing operation.

Examples:
Question: How many records are present?
SQL: SELECT COUNT(*) FROM STUDENT

Question: Show students in the Data Science class.
SQL: SELECT * FROM STUDENT WHERE CLASS = 'Data Science'
""".strip()

question = st.text_input("Ask a question about the student database")
submit = st.button("Generate and run query")

if submit:
    if not question.strip():
        st.warning("Enter a question first.")
        st.stop()

    try:
        generated_sql = get_gemini_response(question, SYSTEM_PROMPT)
        safe_sql, rows, truncated = query_db(generated_sql, "student.db")
    except (ValueError, sqlite3.Error) as exc:
        st.error(f"Query rejected: {exc}")
    except Exception as exc:
        st.error(f"Unable to generate or execute the query: {exc}")
    else:
        st.subheader("Generated SQL")
        st.code(safe_sql, language="sql")
        st.subheader("Result")
        st.dataframe(rows, use_container_width=True)
        if truncated:
            st.caption("Showing the first 100 rows.")
