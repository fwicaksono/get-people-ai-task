# GET-PEOPLE-AI-TASK

An AI-powered talent analysis system designed to identify ideal successors by matching success patterns derived from High Performers.

## 📖 Project Overview

This project simulates a real-world HR analytics workflow. It moves beyond subjective decision-making by using data-driven **Success Patterns** to find “Hidden Gems” within an organization who share the same traits as top-performing employees.

### Key Features

* **Dynamic Benchmarking** – Select specific High Performers (Stars) to create a custom “Ideal Profile” baseline.
* **AI-Powered Job Context** – Generates professional Job Descriptions & Requirements using Gemini AI based on role context.
* **Smart Scoring Engine** – Calculates match rates using a weighted multi-variable formula (Cognitive, Motivation, Leadership, etc.).
* **Interactive Dashboard** – Visualizes gaps, strengths, and match distributions.

---

## 🛠️ Installation & Setup (Supabase Version)

Follow these steps to run the application locally using **Supabase PostgreSQL**.

---

## ✅ Prerequisites

* Python 3.9+
* Supabase project (Free tier supported)
* Supabase credentials:

  * Project URL
  * Anon Key
  * Database password
* Google Gemini API Key

---

## 🔧 Step 1: Setup Environment Variables

Create a file named `.env` in the root directory and paste:

```
SUPA_HOST=your-project.supabase.co
SUPA_PORT=5432
DBNAME=postgres
SUPA_USER=postgres
PASSWORD=Your_Supabase_DB_Password
DATABASE_URL=postgresql://postgres:Your_Supabase_DB_Password@db.your-project.supabase.co:5432/postgres
GEMINI_API_KEY=Paste_Your_Gemini_API_Key_Here
```

---

## 🔧 Step 2: Install Dependencies

```
pip install -r requirements.txt
```

(Recommended:
`python -m venv venv` → `source venv/bin/activate`)

---

## 🚀 Step 3: Run the Application

```
streamlit run main.py
```

Visit:
`http://localhost:8501`

---

## 📂 Project Structure

```
ai-talent-match/
├── .env
├── requirements.txt
├── main.py
├── app_layout.py
├── query.py
├── prompt.py
└── config.py
```

---

## 🔍 How to Use (Demo Scenario)

1. **Define Role:** e.g., *Data Analyst*, Level *Senior*
2. **Add Context:** e.g., “Tableau Dashboarding”, “ETL APIs”
3. **Select Benchmark:**

   * Method A: Input Employee ID, e.g., `EMP1005`
   * Method B: Leave EMPTY → system uses average of all High Performers
4. **Analyze:** Click **Analyze & Match** to view:

   * Ranking Table
   * Radar Charts
   * AI Insights

---


