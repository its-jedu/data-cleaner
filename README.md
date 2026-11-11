# CSVH Cleaner

A Streamlit app for one-click cleaning of CSV and Excel datasets. Upload a file, get back a consistently formatted, cleaned version without losing any rows or columns.

## What it does

* **Upload**: Supports `.csv`, `.xlsx`, `.xls`
* **Standardise columns**: Names are lowercased and converted to snake_case, whitespace normalised
* **Text cleaning**: Strip leading/trailing whitespace, Title Case for name fields `next_of_kin`, `surname`, `first_name`, `middle_name`
* **Categorical consistency**: `sex`, `state`, `lga`, `entry_mode`, `marital_status`, `enrolment_status` are uppercased
* **Phone normalisation**: Telephone columns are stripped of formatting and 10-digit Nigerian numbers are padded to 11 digits with leading `0`
* **Date normalisation**: Mixed date formats and Excel serial dates in `dob`/`date`/`birth` columns are parsed and output as ISO `YYYY-MM-DD`. Compact digit strings are read as dates, not Excel serials (`07092002` → `2002-09-07`)
* **Preserve data**: No rows/columns are dropped. `enrolment_level` keeps values like `100`, `200`, `SPILL` as-is

The app shows a preview and lets you download the cleaned file as CSV or Excel.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501

## Deploy

The app is ready for Streamlit Community Cloud. Push `app.py`, `cleaner.py`, `requirements.txt` and `README.md` to GitHub, connect the repo in share.streamlit.io and deploy.

## Project structure

```
CSVH/
├─ app.py          # Streamlit UI
├─ cleaner.py      # Cleaning logic
├─ requirements.txt
├─ README.md
└─ .gitignore
```

Data files are ignored so the repo stays public and lightweight.

