# Streamlit Deployment Plan: Zomato AI Restaurant Advisor

This document details the step-by-step procedure to deploy the Streamlit frontend of the Zomato AI Restaurant Advisor on **Streamlit Community Cloud** (Streamlit Sharing).

---

## 1. Prerequisites

Before starting, ensure you have:
1. A **GitHub account** where the project repository is pushed.
2. A **Groq API Key** (or another LLM provider key if configured).
3. A **Streamlit Community Cloud account** (you can log in using your GitHub account at [share.streamlit.io](https://share.streamlit.io)).

---

## 2. Project File Structure for Deployment

Streamlit Community Cloud pulls directly from GitHub. The repository must be configured with the following files at the root level:

```text
zomato-milestone/
├── .streamlit/
│   └── config.toml             # Optional: Custom themes/port overrides
├── Docs/
│   └── deployment-plan.md      # This file
├── data/
│   └── processed/              # Parquet store files (if committed)
├── src/
│   ├── __init__.py
│   ├── app/
│   │   ├── __init__.py
│   │   └── streamlit_app.py    # MAIN ENTRY POINT FOR STREAMLIT DEPLOYMENT
│   ├── services/
│   ├── store/
│   └── ...
├── requirements.txt            # Streamlit reads this to install libraries
└── README.md
```

### Dependency Configuration (`requirements.txt`)
Your [`requirements.txt`](../requirements.txt) is already set up correctly and includes all necessary dependencies:
- `streamlit>=1.30.0`
- `fastapi>=0.100.0`
- `datasets>=2.18.0`
- `pandas>=2.1.0`
- `pyarrow>=14.0.0`
- `pydantic>=2.5.0`
- `PyYAML>=6.0.1`

---

## 3. Handling the Restaurant Database (Data Ingestion)

Since the app relies on the preprocessed Parquet database file (`data/restaurants.parquet` or `data/processed/...`), you must decide how to make this data available in the deployed container:

### Option A: Programmatic Auto-Ingestion (Recommended)
You can update `src/app/streamlit_app.py` to automatically execute the ingestion pipeline if it detects the parquet file is missing. This prevents check-in of large binary data files to GitHub.

Add the following logic at the very top of `src/app/streamlit_app.py` (before importing service layers):

```python
import os
from pathlib import Path

# Verify data file exists, else trigger offline pipeline
data_file = Path("data/restaurants.parquet")
if not data_file.exists():
    import subprocess
    print("Data file not found. Running ingestion script...")
    subprocess.run(["python", "scripts/ingest.py"], check=True)
```

### Option B: Commit Preprocessed Data to GitHub
If you prefer not to run ingestion on the Streamlit container:
1. Temporarily modify `.gitignore` to allow parquet files:
   ```diff
   - data/
   + # data/
   ```
2. Run `python scripts/ingest.py` locally to build `data/restaurants.parquet`.
3. Commit and push the `data/` folder containing the parquet files to GitHub.

---

## 4. Configuring Streamlit Secrets (LLM API Keys)

Do **NOT** push your `.env` file to GitHub. Streamlit provides a secure Secrets Manager to handle API keys.

1. In your local development, you use environment variables (e.g. `GROQ_API_KEY`).
2. When deploying on Streamlit Community Cloud, you will configure these in the **Secrets** section.
3. The keys should be formatted in TOML format:

```toml
GROQ_API_KEY = "gsk_your_actual_groq_api_key_here"
LLM_PROVIDER = "groq"
LLM_MODEL = "llama-3.3-70b-versatile"
```

Streamlit automatically exposes these keys as environment variables, so `os.getenv("GROQ_API_KEY")` in your code will work seamlessly without modifications.

---

## 5. Step-by-Step Deployment Steps

1. **Push your code to GitHub**: Make sure the latest code commits (and optionally data files) are pushed to your remote repository.
2. **Go to Streamlit Sharing**: Navigate to [share.streamlit.io](https://share.streamlit.io) and sign in with your GitHub account.
3. **Create a New App**:
   - Click the **"New app"** button in the upper-right corner.
   - If prompted, authorize Streamlit to access your GitHub repositories.
4. **Fill in App Details**:
   - **Repository**: Select your `zomato-milestone` repository.
   - **Branch**: Select your main branch (e.g. `main` or `master`).
   - **Main file path**: Set this to: `src/app/streamlit_app.py`.
5. **Add Secrets**:
   - Click the **"Advanced settings..."** button at the bottom of the form.
   - Paste your Groq credentials into the TOML secrets editor:
     ```toml
     GROQ_API_KEY = "gsk_xxxx..."
     ```
   - Click **Save**.
6. **Deploy**:
   - Click the **"Deploy!"** button.
   - Streamlit will spin up a container, install python dependencies from `requirements.txt`, run the code, and launch your application. This may take 2-4 minutes on the first build.

---

## 6. Monitoring and Logs

- If you encounter errors, you can view live console logs in the **Streamlit Console** (available in the bottom-right corner of the deployed app page).
- If the application crashes due to a database issue, make sure that `python scripts/ingest.py` has run successfully or that the Parquet data is committed to GitHub.
