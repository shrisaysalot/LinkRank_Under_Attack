# LinkRank Under Attack: Adversarial Robustness of HITS

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-36%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An empirical study and benchmark on the vulnerability of **Hyperlink-Induced Topic Search (HITS)** to adversarial link manipulation, compared against **PageRank**, **SALSA**, and **In-Degree** baselines, and evaluated against algorithmic defenses on synthetic and real web graphs (SNAP and WEBSPAM-UK2006).

---

## 👥 Group 16 (Information Retrieval Course)
- **Shrisay Shandilya**
- **Vibhor Rathi**
- **Prachi Jain**
- **Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)

---

## 📌 Project Overview
Web ranking algorithms underpin information retrieval on the hyperlinked web. While PageRank distributes probability mass globally using a damping factor ($\alpha = 0.85$), Kleinberg's HITS identifies *authorities* and *hubs* by computing the principal eigenvectors of $A^T A$ and $A A^T$. 

This project explores:
1. **The Spectral Vulnerability of HITS:** Proving and demonstrating that an attacker who injects a small hub farm of size $p$ triggers a catastrophic spectral phase transition when $p \approx 0.71 \sigma_1^2$, abruptly seizing the dominant authority vector.
2. **Comparative Robustness:** Contrasting the sharp bifurcation of HITS with the smooth, linear response of PageRank and the component-restricted structure of SALSA across $33,600$ controlled trials.
3. **Attack Topologies:** Implementing and testing attacks A1–A6 (Single Hub, Hub Farm, Bipartite Block, Proposal Inflation A4, Cross-Score A5/A5b, Greedy Gradient additions A6, and Camouflaged link farms with random dilution $r \in \{2, 5, 10\}$).
4. **Defenses & Calibration:** Implementing and benchmarking defenses D1–D5 (Randomized HITS, Subspace HITS, Bharat-Henzinger edge weighting, Hub-Contribution Capping, Wu-Davison link farm reweighting D4, and Trust-Based HITS D5), calibrated on independent graphs to prevent data leakage.
5. **Real-World WEBSPAM-UK2006 Evaluation & Attacks:** Complete ingestion of the 11,402-host, 730,774-edge WEBSPAM-UK2006 hostgraph with 10,662 human/domain spam labels, demonstrating the **Spectral Scale Barrier** ($\sigma_1^2 \approx 1.15 \times 10^5$) between global host graphs and query-dependent base sets.

---

## 🏗️ Repository Layout

```text
LinkRank_Under_Attack/
├── data/
│   └── raw/                           # Downloaded raw graphs (excluded from git)
├── docs/
│   ├── FINAL_REPORT_FACTS.md          # Comprehensive final evidence pack & fact sheet (v3.1)
│   ├── PROGRESS_REPORT_FACTS.md       # Mid-project evidence pack archive (v2.1)
│   ├── STATE_SNAPSHOT.md              # Historical repository audit
│   └── WEBSPAM_MANUAL_STEPS.md        # WEBSPAM data pipeline documentation
├── figures/                           # 300 DPI publication charts & architecture
│   ├── architecture.png               # System architecture diagram (all components built)
│   ├── architecture.svg               # Vector architecture diagram
│   ├── cost_curves_v3.png             # Cost curves per attack family with 95% CIs
│   ├── h2_takeover_v3.png             # Spectral phase transition & abruptness comparison
│   ├── defense_tradeoff_v3.png        # Defense trade-off Pareto front (security vs clean utility)
│   └── webspam_eval.png               # WEBSPAM clean rank distribution & host graph attacks
├── results/                           # Empirical CSV outputs and environment facts
│   ├── environment.txt                # Hardware, OS, Python and package versions
│   ├── cost_curves_final.csv          # Full-scale cost curves (33,600 observations)
│   ├── wilcoxon_per_attack_final.csv  # Independent paired Wilcoxon tests with Holm FWER
│   ├── h1_h3_eval_final.csv           # Controlled H1 & H3 evaluation trials
│   ├── h2_robustness_final.csv        # 125 spectral takeover instances across 5 graphs
│   ├── defense_calibration_sweeps.csv # Defense parameter sweeps on independent calibration graph
│   ├── defenses_eval_final.csv        # 7,200 defense matrix trials (positive cells n=644)
│   ├── webspam_clean_ranking_final.csv# WEBSPAM clean ranking benchmarks (Spam@100..2000, AUC)
│   └── webspam_attack_final.csv       # Real attack on WEBSPAM host graph (10 targets, B=10..1000)
├── scripts/                           # Reproducible experiment execution scripts
│   ├── download_data.py               # Download SNAP datasets & WEBSPAM labels
│   ├── download_webspam_hostgraph.py  # Download WEBSPAM hostgraph and hostnames
│   ├── run_cost_curves_v3.py          # Full-scale cost curves runner
│   ├── run_h1_h3_eval_v3.py           # Controlled H1 and H3 evaluation runner
│   ├── run_h2_experiment_v3.py        # H2 spectral takeover experiment runner
│   ├── calibrate_defenses.py          # Parameter calibration on independent graph
│   ├── run_defense_matrix_v3.py       # Full defense x attack matrix runner
│   ├── run_webspam_eval_final.py      # WEBSPAM clean ranking & real host graph attack runner
│   ├── compute_final_facts_strict.py  # Strict aggregator for FINAL_REPORT_FACTS.md
│   ├── generate_publication_figures_v3.py # 300 DPI publication figure generator
│   └── generate_figures.py            # Architecture diagram generator
├── src/                               # Core source package
│   ├── config.py                      # Fixed seeds, tolerances, default paths
│   ├── attacks/                       # Attacks A1-A6 (incl. A4, A5, A5b, A6, Camouflage)
│   ├── data/                          # Loaders (SNAP & WEBSPAM hostgraph), synthetic, base-set
│   ├── defenses/                      # Defenses D1-D5 (incl. D4, Combined D4+D1/D5)
│   ├── eval/                          # Metrics (NDCG, Jaccard, Tau, Rho) & statistics (CI, Wilcoxon)
│   └── rankers/                       # Sparse power iteration rankers (HITS, PR, SALSA, InDegree)
├── tests/                             # Pytest test suite (36 unit tests, all passing)
│   ├── test_attacks.py
│   ├── test_data.py
│   ├── test_defenses.py
│   ├── test_eval.py
│   └── test_rankers.py
├── pytest.ini
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart & Installation

```bash
# Clone the repository
git clone https://github.com/shrisaysalot/LinkRank_Under_Attack.git
cd LinkRank_Under_Attack

# Install dependencies
pip install -r requirements.txt
```

---

## 🧪 Running Unit Tests
To verify all rankers against NetworkX and ensure all attacks, loaders, and defenses adhere to specifications:

```bash
pytest -v
```

All 36 unit tests pass in under 5 seconds, verifying mathematical precision (max absolute difference vs NetworkX $< 10^{-8}$) and ensuring attacks strictly preserve clean graph structures.

---

## 📊 How to Reproduce All Final Experiments

All experimental numbers in the final report are generated by running the following scripts from the repository root:

```bash
# 1. Download real SNAP datasets & WEBSPAM hostgraph + labels
python scripts/download_data.py
python scripts/download_webspam_hostgraph.py

# 2. Run unit tests
pytest

# 3. Run H1 & H3 evaluations (n=25 ER instances, n=30 SBM/ER instances up to B=500)
python scripts/run_h1_h3_eval_v3.py

# 4. Run H2 spectral takeover experiment (125 instances across 5 graphs)
python scripts/run_h2_experiment_v3.py

# 5. Calibrate defenses on independent graph (seed 9999)
python scripts/calibrate_defenses.py

# 6. Run full defense matrix (7,200 trials across 10 defenses and 8 attacks)
python scripts/run_defense_matrix_v3.py

# 7. Run full-scale cost curves (33,600 observations across 5 graphs, 5 seeds, 7 attacks)
python scripts/run_cost_curves_v3.py

# 8. Run WEBSPAM-UK2006 clean ranking benchmark and real host graph attack
python scripts/run_webspam_eval_final.py

# 9. Re-generate all publication figures (300 DPI)
python scripts/generate_publication_figures_v3.py
python scripts/generate_figures.py
```

---

## 💻 Hardware & Library Environment

*Probed environment (from `results/environment.txt`):*
- **CPU:** 12th Gen Intel Core i5-12500H (12 physical cores, 16 logical threads)
- **OS:** Microsoft Windows 11 Home (Build 10.0.26100)
- **Python:** 3.12.5 (64-bit)
- **Libraries:** NetworkX 3.3, NumPy 1.26.4, SciPy 1.13.1, Pandas 2.2.2, Scikit-learn 1.5.1, Matplotlib 3.9.2, Pytest 9.1.1
