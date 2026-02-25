# Securing LLM Agents Without Sacrificing Generative Utility



> Paper currently under revision. Citation details will be updated upon publication.

---

## Overview

This repository contains all experimental code, analysis scripts, and research data for the study on prompt injection security in LLM-powered game NPCs. The research tests three security configurations (WEAK, STRONG, OPTIMAL) against adversarial attacks across 750 controlled trials using Google Gemini 2.5 Flash, with the fictional NPC "Aethelgard the Eternal" as the testbed.

Key findings include a 33.6× security improvement from WEAK to OPTIMAL configurations, the discovery of the "Stone Wall" phenomenon in over-restricted configurations, and identification of a security sweet spot in the 250–1000 character response range.

---

## Repository Structure

```
repo/
├── Py_code/
│   ├── AiNpcTest_1.py            # Adversarial trial runner: conducts attacks, saves results, runs basic analysis
│   ├── AiNpcTest_2.py            # Adversarial trial runner: conducts attacks and saves raw data only
│   └── Data analysis code/
│       ├── data_process1.py      # Core EDA and visualizations
│       ├── ling_process1.py      # LFI computation and visualization
│       ├── ling_process2.py      # Security sweet spot analysis
│       ├── compute_statistics.py # All significance tests and confidence intervals
│       ├── lfi_sensitivity.py    # LFI weighting sensitivity analysis
│       └── maxlfi.py             # Peak LFI diagnostic utility
│
└── research_data/
    ├── Data analysis results/
    │   ├── Figures/              # All generated charts and plots
    │   ├── comprehensive_linguistic_forensics.csv
    │   ├── lfi_sensitivity_full.csv
    │   ├── lfi_sensitivity_summary.csv
    │   ├── segmented_security_report.csv
    │   ├── stats_asr_by_category.csv
    │   ├── stats_asr_by_config.csv
    │   ├── summary_categories.csv
    │   └── summary_lore.csv
    └── Raw data/
        └── raw_data.csv          # Full 750-trial experimental dataset
```

---

## Setup

### Prerequisites

- Python 3.9+
- A Google Gemini API key (for `Py_code/` scripts only)

### Installation

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME
pip install -r requirements.txt
```

### API Key Configuration

The NPC experiment scripts require a Gemini API key. Copy the example env file and add your key:

```bash
cp .env.example .env
```

Then edit `.env`:

```
GEMINI_API_KEY=your_api_key_here
```

> **Note:** The data analysis scripts in `Data analysis code/` do not require an API key and can be run directly on the provided dataset.

---

## Running the Experiments

### `AiNpcTest_1.py`

Conducts adversarial attacks across all configurations, saves results to CSV and Excel, and runs basic statistical analysis:

```bash
cd Py_code
python AiNpcTest_1.py
```

### `AiNpcTest_2.py`

Conducts the same adversarial attacks and saves raw data files, without running analysis:

```bash
cd Py_code
python AiNpcTest_2.py
```

---

## Running the Analysis

All analysis scripts are in `Py_code/Data analysis code/`. Before running, open each script and replace `XXX` in the `DATA_FILE` variable with the path to `research_data/Raw data/raw_data.csv`.

Run scripts in this recommended order:

| Script | Purpose | Output |
|---|---|---|
| `data_process1.py` | Core EDA, ASR by configuration and category | `summary_lore.csv`, `summary_categories.csv`, figures |
| `compute_statistics.py` | Fisher's exact tests, Wilson CIs, Mann-Whitney U, point-biserial correlations | `stats_asr_by_config.csv`, `stats_asr_by_category.csv` |
| `ling_process1.py` | LFI computation and fragmentation visualization | `comprehensive_linguistic_forensics.csv`, figures |
| `ling_process2.py` | Security sweet spot and length segment analysis | `segmented_security_report.csv`, figures |
| `lfi_sensitivity.py` | Sensitivity analysis of LFI weighting schemes | `lfi_sensitivity_full.csv`, `lfi_sensitivity_summary.csv` |
| `maxlfi.py` | Identifies the peak LFI response in the dataset | Console output |

Pre-computed results are already available in `research_data/Data analysis results/`.

---

## Key Concepts

**Attack Success Rate (ASR):** Proportion of adversarial prompts that successfully elicited the secret phrase from the NPC.

**Linguistic Fragmentation Index (LFI):** A novel metric measuring internal resistance during security failures, computed via weighted pattern matching across four marker types (underscores, Base64-like strings, German semantic markers, syntactic glitches).

**Stone Wall Phenomenon:** Observed in the STRONG configuration, which achieved perfect security (0% ASR) but collapsed to highly repetitive, identical responses — eliminating generative utility.

**Security Sweet Spot:** Response lengths of 250–1000 characters showed the lowest vulnerability across configurations.

---

## Requirements

See `requirements.txt`. Key dependencies:

- `google-generativeai` — Gemini API client (experiment scripts only)
- `pandas`, `numpy` — Data processing
- `scipy` — Statistical tests
- `matplotlib`, `seaborn` — Visualizations
- `python-dotenv` — API key management

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Citation

> Citation will be added upon publication.

---

## Contact

For questions about this research, please open an issue in this repository.
