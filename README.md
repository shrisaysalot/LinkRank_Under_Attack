# LinkRank Under Attack: Adversarial Robustness of HITS

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-35%20passed-brightgreen.svg)](tests/)
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
1. **The Spectral Vulnerability of HITS:** Proving and demonstrating that an attacker who injects a small hub farm of size $p$ triggers a catastrophic spectral phase transition when $p \ge \sigma_1^2$, abruptly seizing the dominant authority vector.
2. **Comparative Robustness:** Contrasting the sharp bifurcation of HITS with the smooth, linear response of PageRank and the component-restricted structure of SALSA across thousands of controlled trials.
3. **Attack Topologies:** Implementing and testing attacks A1–A6 (Single Hub, Hub Farm, Bipartite Block, Hub Inflation A4, Cross-Score A5/A5b, Greedy Gradient additions A6, and Camouflaged link farms with random dilution $r \in \{2, 5, 10\}$).
4. **Defenses & Calibration:** Implementing and benchmarking defenses D1–D5 (Randomized HITS, Subspace HITS, Bharat-Henzinger edge weighting, Hub-Contribution Capping, Wu-Davison link farm reweighting D4/D4b, and Trust-Based HITS D5), calibrated on independent graphs to prevent data leakage.
5. **Real-World WEBSPAM-UK2006 Evaluation:** Complete ingestion of the 11,402-host, 730,774-edge WEBSPAM-UK2006 hostgraph with 10,662 human/domain spam labels, demonstrating the spectral scale barrier ($\sigma_1^2 \approx 1.15 \times 10^5$) between global host graphs and query-dependent base sets.
6. **Stretch Objectives:** Empirical spectral bound scaling law ($R^2 = 0.94$) and an adaptive 3-round attacker-defender game loop.

---

## 🏗️ Repository Layout

```text
LinkRank_Under_Attack/
├── data/
│   └── raw/                           # Downloaded raw graphs (excluded from git)
├── docs/
│   ├── FINAL_REPORT_FACTS.md          # Comprehensive final evidence pack & fact sheet
│   ├── PROGRESS_REPORT_FACTS.md       # Mid-project evidence pack archive (v2.1)
│   ├── STATE_SNAPSHOT.md              # Historical repository audit
│   └── WEBSPAM_MANUAL_STEPS.md        # WEBSPAM data pipeline documentation
├── figures/                           # 300 DPI publication charts & architecture
│   ├── architecture.png               # System architecture diagram (all components built)
│   ├── cost_curves_v3.png             # Cost curves per attack family with 95% CIs
│   ├── h2_takeover_v3.png             # Spectral phase transition & abruptness comparison
│   ├── defense_tradeoff_v3.png        # Defense trade-off Pareto front (security vs clean utility)
│   ├── webspam_eval.png               # WEBSPAM ROC curves & spectral scale barrier
│   └── empirical_bound.png            # Stretch: empirical spectral scaling law regression
├── results/                           # Empirical CSV outputs and environment facts
│   ├── environment.txt                # Hardware, OS, Python and package versions
│   ├── clean_baselines.csv            # Clean graph baselines, eigengaps, memory
│   ├── cost_curves_v3.csv             # Full-scale cost curves (33,600 observations)
│   ├── wilcoxon_per_attack_v2.csv     # Independent paired Wilcoxon tests with Holm FWER
│   ├── h1_h3_eval_v3.csv              # Controlled H1 & H3 evaluation trials
│   ├── h2_robustness_v3.csv           # 125 spectral takeover instances across 5 graphs
│   ├── defense_calibration_sweeps.csv # Defense parameter sweeps on independent calibration graph
│   ├── defenses_eval_v3.csv           # 7,920 defense matrix trials
│   ├── webspam_eval.csv               # WEBSPAM-UK2006 spam@k, AUC, and F1 benchmarks
│   ├── empirical_bound_regression.csv # Stretch: linear and multivariate regression parameters
│   └── attacker_defender_loop.csv     # Stretch: 3-round adaptive attacker-defender game
├── scripts/                           # Reproducible experiment execution scripts
│   ├── download_data.py               # Download SNAP datasets & WEBSPAM labels
│   ├── download_webspam_hostgraph.py  # Download WEBSPAM hostgraph and hostnames
│   ├── run_clean_baselines.py         # Benchmark clean graph rankers
│   ├── run_cost_curves_v3.py          # Full-scale cost curves runner
│   ├── run_h1_h3_eval_v3.py           # Controlled H1 and H3 evaluation runner
│   ├── run_h2_experiment_v3.py        # H2 spectral takeover experiment runner
│   ├── calibrate_defenses.py          # Parameter calibration on independent graph
│   ├── run_defense_matrix_v3.py       # Full defense x attack matrix runner
│   ├── run_webspam_eval.py            # WEBSPAM real-world spam evaluation runner
│   ├── compute_stretch_empirical_bound.py # Empirical spectral bound & game loop runner
│   ├── audit_block0_fixes.py          # Block 0 audit fixes and sensitivity sweeps
│   ├── compute_final_facts.py         # Summary aggregator for final facts
│   └── generate_publication_figures_v3.py # 300 DPI publication figure generator
├── src/                               # Core source package
│   ├── config.py                      # Fixed seeds, tolerances, default paths
│   ├── attacks/                       # Attacks A1-A6 (incl. A4, A5, A5b, A6, Camouflage)
│   ├── data/                          # Loaders (SNAP & WEBSPAM hostgraph), synthetic, base-set
│   ├── defenses/                      # Defenses D1-D5 (incl. D4b, Combined D4+D1/D5)
│   ├── eval/                          # Metrics (NDCG, Jaccard, Tau, Rho) & statistics (CI, Wilcoxon)
│   └── rankers/                       # Sparse power iteration rankers (HITS, PR, SALSA, InDegree)
├── tests/                             # Pytest test suite (35 unit tests, all passing)
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

All 35 unit tests pass in under 5 seconds, verifying mathematical precision (max absolute difference vs NetworkX $< 10^{-8}$) and ensuring attacks strictly preserve clean graph structures.

---

## 📊 How to Reproduce All Final Experiments

All experimental numbers in the final report are generated by running the following scripts:

```bash
# 1. Download real SNAP datasets & WEBSPAM hostgraph + labels
python scripts/download_data.py
python scripts/download_webspam_hostgraph.py

# 2. Run clean baseline benchmarks (runtime, peak memory, eigengap)
python scripts/run_clean_baselines.py

# 3. Run H1 & H3 evaluations (n=25 ER instances, n=30 SBM/ER instances)
python scripts/run_h1_h3_eval_v3.py

# 4. Run H2 spectral takeover experiment (125 instances across 5 graphs)
python scripts/run_h2_experiment_v3.py

# 5. Calibrate defenses on independent graph (seed 9999)
python scripts/calibrate_defenses.py

# 6. Run full defense matrix v3 (7,920 trials across 11 defenses and 8 attacks)
python scripts/run_defense_matrix_v3.py

# 7. Run WEBSPAM-UK2006 real-spam evaluation (11,402 hosts, 730k edges)
python scripts/run_webspam_eval.py

# 8. Run Stretch: empirical spectral bound regression & 3-round game loop
python scripts/compute_stretch_empirical_bound.py

# 9. Run full-scale cost curves v3 (33,600 observations across 5 graphs, 5 seeds, 7 attacks)
python scripts/run_cost_curves_v3.py

# 10. Generate 300 DPI publication figures & print final summary facts
python scripts/generate_publication_figures_v3.py
python scripts/compute_final_facts.py
```

---

## 📈 Key Findings & Hypothesis Verdicts

1. **Spectral Takeover (Hypothesis H2 Strongly Supported):**
   - The theoretical condition $\sigma_1^2 \ge \text{max in-degree}$ holds in **100.0%** of evaluated instances ($n=125$).
   - Takeover occurs abruptly in **73.6%** of instances, with a mean single-step rank jump of **61.5 ranks** for HITS vs **15.2 ranks** for PageRank.
   - Empirical takeover ratios: $p^*(10) / \sigma_1^2 = 0.713$ [0.656, 0.766]; $p^*(1) / \sigma_1^2 = 0.841$ [0.808, 0.873].
   - **Counterexample Diagnostic:** Non-abrupt takeover cases occur when the graph has a small eigengap ($\sigma_1 - \sigma_2 = 2.51$ vs $13.53$ in abrupt cases) and the target begins already near top ranks.
2. **HITS vs In-Degree Baseline (Hypothesis H1 Strongly Supported):**
   - On Erdos-Renyi graphs ($n=25$), In-Degree is significantly cheaper to manipulate than HITS: $B^*(10)$ is **8.60** [7.60, 9.40] for In-Degree vs **31.40** [28.20, 34.40] for HITS (ratio = **3.82**, Wilcoxon $p = 5.96 \times 10^{-8}$).
3. **Community Attachment (Hypothesis H3 Supported):**
   - Attaching fake hubs to top legitimate authorities (A5 Cross-Score) reduces the required budget to penetrate Top-10 by **33.3%** [33.3%, 33.3%] on planted SBM graphs and **36.7%** [26.7%, 46.7%] on ER control graphs compared to isolated hub farms (A2).
4. **Defense Trade-Offs (Hypothesis H4 Supported with Nuance):**
   - **Wu-Davison (D4 and D4b)** with calibrated threshold $\theta = 0.5$ effectively suppresses isolated link farms: **93.3% median reduction** against A2, **97.3%** against A3, and **63.0%** against A5.
   - However, **Camouflaged Link Farms ($r \in \{2, 5, 10\}$)** and **Greedy Gradient (A6)** evade D4/D4b ($0.0\%$ reduction) by diluting pairwise out-link Jaccard overlap below the threshold.
   - **Hub Capping (D3)** at $1\%$ binds and provides $25.8\%$ reduction, whereas $10\%$ capping is a complete no-op across all networks.
5. **Real-World Web Graph Scale Barrier:**
   - On the full WEBSPAM-UK2006 hostgraph, $\sigma_1^2 \approx 115,407$, rendering local farm injections ($B \le 100$) ineffective at hijacking global eigenvectors ($B \ll \sigma_1^2$), whereas query-dependent base sets ($\sigma_1^2 \approx 10-50$) remain acutely vulnerable.

---

## 📋 Final Implementation Status Table

| Module | Status | Details |
|---|---|---|
| **HITS, PageRank, SALSA, InDegree** | **DONE** | Sparse power iteration, $\text{tol}=10^{-8}$, exact convergence tracking. |
| **Randomized HITS & Subspace HITS (D1)** | **DONE** | Damped power iteration ($\epsilon=0.15$) and top-$k$ singular subspace projection ($k=5$). |
| **Data Loaders (SNAP & WEBSPAM Hostgraph)** | **DONE** | Parses wiki-Vote, web-Stanford, web-NotreDame, and full 11,402-node WEBSPAM hostgraph. |
| **Base Set Builder (Kleinberg 1999)** | **DONE** | Root set sampling, out-link expansion, max 20-25 in-link capping. |
| **Synthetic Generators (BA, ER, SBM)** | **DONE** | Scale-free, random, and planted dense bipartite community graphs. |
| **Attacks A1–A6 & Camouflaged Farms** | **DONE** | A1, A2, A3, A4, A5, A5b, A6, and Camouflaged farms ($r=2, 5, 10$). |
| **Defenses D1–D5 & Combined Defenses** | **DONE** | D1-rand, D1-sub, D2 (domain-map), D3 (1% cap), D4 (mutual), D4b (Jaccard), D5 (trust), Combined D4+D1/D5. |
| **Defense Calibration Module** | **DONE** | Independent parameter sweeps on seed 9999 for D1, D3, D4, D5. |
| **Statistical Testing & CIs** | **DONE** | Percentile bootstrap 95% CIs (1,000 resamples), independent paired Wilcoxon tests, Holm-Bonferroni FWER. |
| **WEBSPAM-UK2006 Evaluation** | **DONE** | Full hostgraph evaluation: spam@k ($k=10, 20, 50, 100$), ROC-AUC, F1, spectral barrier analysis. |
| **Stretch: Empirical Spectral Bound** | **DONE** | Empirical scaling law $p^*(10) \propto \sigma_1^2$ regression ($R^2 = 0.94$ for top-1) with 95% CI bands. |
| **Stretch: Attacker-Defender Game Loop** | **DONE** | 3-round adaptive evasion via camouflage and defender re-tuning on calibration graph. |

For detailed tables, numerical evidence, and the complete fact sheet, see [`docs/FINAL_REPORT_FACTS.md`](docs/FINAL_REPORT_FACTS.md).
