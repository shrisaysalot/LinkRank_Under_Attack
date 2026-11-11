# LinkRank Under Attack: Adversarial Robustness of HITS

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-36%20passed-brightgreen.svg)](tests/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An empirical study and benchmark on the vulnerability of **Hyperlink-Induced Topic Search (HITS)** to adversarial link manipulation, compared against **PageRank**, **SALSA**, and **In-Degree** baselines, and evaluated against algorithmic defenses on synthetic and real web graphs (SNAP and WEBSPAM-UK2006).

---

## 👥 Group 16 (Information Retrieval Course)
- **Shrisay Shandilya (`Shrisaysalot`):** Planned ownership in proposal: rankers, loaders, base sets. Actual execution: designed and implemented 100% of the repository codebase across all 16 commits (`main`), including rankers, synthetic generators, loaders, all 8 attacks, all 10 defenses, test suite (36 unit tests), and experimental evaluation scripts.
- **Vibhor Rathi:** Planned ownership in proposal: attacks (planned, no commits in git history).
- **Prachi Jain:** Planned ownership in proposal: defenses, evaluation (planned, no commits in git history).
- **Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)

*Git Commit History (`git shortlog -sn --all`):*
```text
    16  Shrisaysalot
```

---

## 📌 Project Overview
Web ranking algorithms underpin information retrieval on the hyperlinked web. While PageRank distributes probability mass globally using a damping factor ($\alpha = 0.85$), Kleinberg's HITS identifies *authorities* and *hubs* by computing the principal eigenvectors of $A^T A$ and $A A^T$. 

This project explores:
1. **The Spectral Vulnerability of HITS:** Evaluating the theoretical prediction that an injected hub farm triggers a spectral phase transition when $p \approx \sigma_1^2$, abruptly seizing the dominant authority vector.
2. **Comparative Robustness:** Contrasting the sharp bifurcation of HITS with the smooth, linear response of PageRank and the component-restricted structure of SALSA across $33,600$ controlled trials.
3. **Attack Topologies:** Implementing and testing attacks A1–A6 (Single Hub, Hub Farm, Bipartite Block, Proposal Inflation A4, Cross-Score A5/A5b, Greedy Gradient additions A6, and Camouflaged link farms with random dilution $r \in \{2, 5, 10\}$).
4. **Defenses & Calibration:** Implementing and benchmarking defenses D1–D5 (Randomized HITS, Subspace HITS, Bharat-Henzinger edge weighting, Hub-Contribution Capping, Wu-Davison link farm reweighting D4, and Trust-Based HITS D5), calibrated on independent graphs to prevent data leakage.
5. **Real-World WEBSPAM-UK2006 Evaluation & Attacks:** Complete ingestion of the 11,402-host, 730,774-edge WEBSPAM-UK2006 hostgraph with 10,662 human/domain spam labels, measuring real-world attack resistance and the spectral scale barrier ($\sigma_1^2 \approx 1.15 \times 10^5$) between global host graphs and query-dependent base sets.

---

## 🎯 Key Findings & Hypothesis Verdicts (Original Proposal Wording)

| Hypothesis & Original Proposal Wording | Final Verdict | Empirical Evidence ($n$, metrics, 95% CIs) |
|:---|:---:|:---|
| **H1:** *"HITS and in-degree attack costs are similar on random graphs (comparable $B^*$ for equal rank gain)."* | **NOT SUPPORTED** | $n=25$ ER instances. In-degree requires $B^*(10) = \mathbf{8.60}$ [7.60, 9.40] vs HITS $B^*(10) = \mathbf{31.40}$ [28.20, 34.20]. Ratio = $\mathbf{3.820}$ [3.439, 4.200] ($p = 5.96 \times 10^{-8}$, minimum possible for $n=25$). **New observation:** In-degree is significantly cheaper to manipulate (~3.8x fewer edges). |
| **H2:** *"Spectral takeover occurs abruptly at a critical budget $p^* \approx \sigma_1^2$, where the attacker's subgraph eigenvalue exceeds the host graph's leading eigenvalue."* | **SUPPORTED (QUALIFIED)** | $n=125$ instances across 5 graphs. Takeover occurs at $p^*(10)/\sigma_1^2 = \mathbf{0.713}$ [0.656, 0.768] and $p^*(1)/\sigma_1^2 = \mathbf{0.841}$ [0.807, 0.876]. Both CIs strictly exclude 1.0. Abrupt in 73.6% ($92/125$); non-abrupt counterexamples correlate with smaller eigengaps ($2.51$ vs $13.53$). |
| **H3:** *"Bipartite attacks (A5) achieve greater rank gain per edge than single-hub attacks (A2) in community-structured graphs (SBM) compared to random graphs (ER)."* | **NOT SUPPORTED AS A COMMUNITY EFFECT** | $n=30$ paired instances up to $B=500$. Cost saving is **33.3%** on SBM [33.3%, 33.3%] vs **36.7%** on ER [26.7%, 46.7%] ($p = 0.449$, Wilcoxon). Zero-width SBM CI is a discrete grid artifact. A5 is equally effective across topologies due to hub efficiency, not community boundaries. |
| **H4:** *"Algorithmic defenses reduce attack effectiveness by $\ge 50\%$ while preserving ranking utility (clean NDCG drop $\le 5\%$) across all graph topologies."* | **NOT SUPPORTED GLOBALLY** | $n=644$ positive undefended gain cells. No defense meets the criteria globally. D4 (Wu-Davison) achieves **32.1% overall success** (does not meet goal overall), excelling on pure farms (A2 $84.2\%$, A5 $86.7\%$) but failing against Camouflaged farms ($0.0\%$). |

---

## 🏗️ Repository Layout

```text
LinkRank_Under_Attack/
├── data/
│   └── raw/                           # Downloaded raw graphs (excluded from git)
├── docs/
│   ├── FINAL_REPORT_FACTS.md          # Comprehensive final evidence pack & fact sheet (v3.2 Final)
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

*Probed environment (copied directly from [`results/environment.txt`](results/environment.txt)):*
- **Operating System:** Windows 11 (10.0.26200)
- **Architecture:** AMD64
- **Processor:** 12th Gen Intel(R) Core(TM) i5-12500H (12 physical cores, 16 logical threads)
- **Total Visible RAM:** 15.69 GB (16,849,293,312 bytes)
- **Python:** 3.12.5 (tags/v3.12.5:ff3bc82, Aug 6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)]
- **Library Versions:**
  - `numpy`: 1.26.4
  - `scipy`: 1.12.0
  - `networkx`: 3.4.2
  - `pandas`: 3.0.5
  - `matplotlib`: 3.10.8
  - `psutil`: 7.2.2
  - `scikit-learn`: 1.5.1
  - `pytest`: 9.1.1
