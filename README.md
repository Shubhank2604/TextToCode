# Text-to-SQL Explorer

An educational Streamlit prototype that converts natural-language questions into SQLite queries for a small student database.

## Security model

LLM output is untrusted. Before execution, the application:

- accepts exactly one statement;
- permits only `SELECT` or `WITH` queries;
- rejects state-changing SQL keywords;
- opens SQLite in read-only mode; and
- limits displayed results to 100 rows.

These controls reduce risk but do not make arbitrary model-generated SQL appropriate for a production database. A production system should additionally use a restricted database role, query timeouts, auditing, schema-level permissions, and an isolated execution service.

## Setup

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Set `GOOGLE_API_KEY` in your local `.env`, initialize the sample database, and start the application:

```bash
python sql.py
streamlit run app.py
```

Never commit `.env` or API credentials.

## Verification

```bash
python -m unittest discover -s tests -v
```

The tests exercise statement validation, common write-query bypass attempts, read-only database access, and the 100-row output limit. GitHub Actions runs them for each pull request.
