# AI Incident Investigation & Root-Cause Analysis Platform

An end-to-end platform that detects network intrusions, correlates related security events into incidents, and automatically generates human-readable root-cause-analysis (RCA) reports using an LLM — all viewable through an interactive dashboard.

Built as an applied machine learning + LLM systems project combining classical ML (classification, anomaly detection), event correlation, and generative AI report writing into a single working pipeline.

---

## What it does

Given raw network traffic data, the platform:

1. **Detects** malicious traffic using trained classifiers (attack vs. normal, and attack type)
2. **Correlates** related detected events into a single "incident" with a reconstructed timeline
3. **Generates** a structured, human-readable root-cause-analysis report for each incident using an LLM
4. **Visualizes** everything in an interactive Streamlit dashboard

```
Raw Network Traffic (NSL-KDD)
        │
        ▼
┌───────────────────┐
│   Preprocessing    │  cleaning, encoding, scaling, feature engineering
└─────────┬──────────┘
          ▼
┌───────────────────┐
│  Detection Engine   │  Random Forest (binary + multiclass) + Isolation Forest
└─────────┬──────────┘
          ▼
┌───────────────────┐
│Correlation Engine   │  groups related events into Incidents + builds timelines
└─────────┬──────────┘
          ▼
┌───────────────────┐
│  RCA Report Gen     │  LLM-generated root-cause report, grounded in real data
└─────────┬──────────┘
          ▼
┌───────────────────┐
│ Streamlit Dashboard │  upload, inspect incidents, read reports, view analytics
└───────────────────┘
```

---

## Why this project

Detection alone isn't the end goal in a real security workflow — an analyst needs to know what happened, why, and what to do next. This project builds that full chain: detection → correlation → explanation, structured the way an actual incident response pipeline works, rather than stopping at a classification label.

---

## Tech stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data processing | pandas, numpy |
| Machine learning | scikit-learn (Random Forest, Isolation Forest), imbalanced-learn (SMOTE) |
| Report generation | LLM API (Gemini / Anthropic — pluggable), with a free local fallback via Ollama |
| Dashboard | Streamlit |
| Model persistence | joblib |
| Testing | pytest |

---

## Features

- **Binary + multiclass detection** — flags traffic as attack/normal, and further classifies attack type (DoS, Probe, R2L, U2R)
- **Class-imbalance handling** — SMOTE oversampling to address the natural rarity of certain attack types
- **Anomaly detection** — an Isolation Forest layer to catch statistically unusual traffic independent of supervised labels, aimed at novel/unseen attack patterns
- **Event correlation** — groups individually flagged events into coherent incidents based on source and time proximity, rather than treating every alert in isolation
- **Grounded LLM reporting** — RCA reports are generated from structured incident data injected directly into the prompt, reducing hallucination risk compared to free-form generation
- **Multi-provider LLM support** — works with Gemini, Anthropic, or a fully local/free Ollama model, configurable via environment variables
- **Interactive dashboard** — upload data, run the full pipeline, browse incidents, and read generated reports without touching the command line

---

## Dataset

Built and evaluated on **[NSL-KDD](https://www.unb.ca/cic/datasets/nsl.html)**, a widely used benchmark intrusion-detection dataset (a cleaned successor to KDD Cup 99). It provides labeled network connection records across four attack categories (DoS, Probe, R2L, U2R) plus normal traffic.

> **Known limitation:** NSL-KDD does not include real timestamps or IP addresses. This project synthesizes timestamps (via row order) and source identifiers (via flow signature) to demonstrate the correlation logic. The correlation module is written to prefer real timestamp/IP fields when present, so it would work directly on a dataset like CICIDS2017 without modification.

---

## Project structure

```
├── config.py                  # central configuration and constants
├── data/                      # raw and processed data (not committed — see Setup)
├── src/
│   ├── preprocessing/         # loading, cleaning, feature engineering
│   ├── detection/             # model training, evaluation, inference
│   ├── correlation/           # incident grouping and timeline construction
│   └── reporting/             # LLM client, prompt templates, report generation
├── dashboard/                 # Streamlit app and pages
├── models/                    # trained model artifacts (generated, not committed)
├── reports/                   # generated RCA reports (generated, not committed)
├── notebooks/                 # exploratory data analysis
├── tests/                     # pytest suite
└── scripts/
    ├── download_data.py       # fetches NSL-KDD
    └── run_pipeline.py        # end-to-end CLI runner
```

---

## Setup

### 1. Clone and enter the repo
```bash
git clone https://github.com/gulfatima-git/AI-Incident-Investigation-and-RCA.git
cd AI-Incident-Investigation-and-RCA
```

### 2. Create a virtual environment
```bash
python -m venv .venv
# Windows
.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
Copy `.env.example` to `.env` and fill in your values:
```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your-key-here
GEMINI_MODEL=gemini-3.6-flash
```
No key? Set `LLM_PROVIDER=ollama` instead and run a local model via [Ollama](https://ollama.com) — no cost, fully offline.

### 5. Download the dataset
```bash
python scripts/download_data.py
```

### 6. Run the full pipeline
```bash
python -m scripts.run_pipeline
```

### 7. Run tests
```bash
pytest tests/
```

### 8. Launch the dashboard
```bash
streamlit run dashboard/app.py
```

---

## Dashboard walkthrough

| Page | What it does |
|---|---|
| **Upload Data** | Upload a dataset and run the full detection → correlation → reporting pipeline |
| **Detected Incidents** | Browse all incidents with severity, attack type, and event count; filter and drill in |
| **Incident Detail** | View an incident's full timeline and its generated RCA report; regenerate or download |
| **Analytics** | Charts on attack distribution, incidents over time, and top sources by incident count |

---

## Model evaluation

Evaluation prioritizes precision, recall, and F1 (macro and weighted) over raw accuracy, since the dataset is naturally imbalanced — a model that just predicts "normal" for everything would score misleadingly high on accuracy alone. Full metrics and a confusion matrix are generated per run and saved to `reports/model_evaluation.json`.

---

## Roadmap / possible extensions

- Swap in CICIDS2017 for a more modern dataset with real timestamps/IPs
- Add a retrieval step (RAG) so new incidents are compared against past ones with known resolutions
- Deploy the dashboard publicly via Streamlit Community Cloud

---

## Design notes and constraints

- **Benchmark vs. production data:** the models are trained and evaluated on NSL-KDD, a standard research benchmark, not live traffic. A production deployment would add drift monitoring and periodic retraining on top of this pipeline.
- **Human-in-the-loop reporting:** LLM-generated reports are grounded in structured incident data to constrain hallucination, but they're designed as analyst-assist output, not an autonomous remediation trigger.
- **Synthetic correlation fields:** NSL-KDD doesn't include real timestamps or IP addresses, so the correlation layer synthesizes them from row order and flow signature. The module checks for real timestamp/IP fields first, so it runs unmodified on a dataset like CICIDS2017 that does include them.

---

## Author

Built by Gul Fatima to explore applied ML and LLM-assisted systems in cybersecurity.