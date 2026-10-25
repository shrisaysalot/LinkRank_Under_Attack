# Honest State Snapshot: LinkRank Under Attack

**Date:** 25 October 2026  
**Auditor:** Implementation Agent (Group 16)  
**Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)  
**Audit Scope:** Read-only repository audit verifying actual committed code, test runs, raw data CSVs, generated figures, and factual claims.

---

## 1. REPO STATE

### Git Branch & Remote
- **Current Branch:** `main`
- **Remotes:**
  - `origin https://github.com/shrisaysalot/LinkRank_Under_Attack.git (fetch)`
  - `origin https://github.com/shrisaysalot/LinkRank_Under_Attack.git (push)`

### Commit History (`git log --oneline`, all 7 commits)
```text
b2e3115 feat(experiments): add empirical benchmarks, cost curves, H2 takeover verification, figures, and progress report facts
c48ad2b feat(eval): implement ranking metrics, bootstrap confidence intervals, and Wilcoxon tests
da1572d feat(defenses): implement Bharat-Henzinger, Hub Capping, Wu-Davison, and Trust HITS defenses
673b103 feat(attacks): implement attacks A1-A6 with strict budget and validity constraints
19b9637 feat(data): implement synthetic generators, SNAP and WEBSPAM loaders, and Kleinberg base-set builder
3a51064 feat(rankers): implement sparse HITS, PageRank, SALSA, in-degree, randomized HITS, and subspace HITS with tests
99215d9 chore: scaffold repo structure, configuration, and dependencies
```

### Git Status & Unpushed Commits
- **Local vs Remote (`git log origin/main..HEAD`):** Empty (0 commits ahead of origin/main).
- **Working Tree Status (`git status`):** `nothing to commit, working tree clean`.
- **Shortlog (`git shortlog -sn --all`):**
  - `7 Shrisaysalot`

### Full File Tree (Depth 3) & Artifact Metadata
```text
LinkRank_Under_Attack/
├── .gitignore (476 B)
├── README.md (7,689 B)
├── requirements.txt (107 B)
├── data/
│   └── raw/
│       ├── web-NotreDame.txt.gz (3,708,538 B)
│       ├── web-Stanford.txt.gz (1,490,944 B)
│       ├── webspam-uk2006-2.0.tar.gz (153,085 B)
│       ├── wiki-Vote.txt.gz (290,339 B)
│       └── webspam-uk2006-2.0/ (extracted labels directory)
│           ├── README.txt (3,935 B)
│           ├── acknowledgments.txt (985 B)
│           ├── license.txt (14,225 B)
│           ├── webspam-uk2006-set1-labels-DomainOrTwoHumans.txt (158,580 B)
│           ├── webspam-uk2006-set1-labels.txt (405,582 B)
│           ├── webspam-uk2006-set2-labels-DomainOrTwoHumans.txt (67,762 B)
│           └── webspam-uk2006-set2-labels.txt (130,906 B)
├── docs/
│   ├── PROGRESS_REPORT_FACTS.md (23,951 B)
│   └── STATE_SNAPSHOT.md (this document)
├── figures/
│   ├── architecture.png (562,947 B, modified 17-10-2026 10:56:44)
│   ├── architecture.svg (155,956 B, modified 17-10-2026 10:56:43)
│   ├── cost_curves_rank_gain.png (431,480 B, modified 17-10-2026 10:56:41)
│   ├── defenses_tradeoff.png (180,374 B, modified 17-10-2026 10:56:43)
│   └── h2_spectral_takeover.png (368,030 B, modified 17-10-2026 10:56:42)
├── results/
│   ├── clean_baselines.csv (3,764 B, modified 17-10-2026 10:51:46)
│   ├── cost_curves.csv (237,531 B, modified 17-10-2026 10:55:54)
│   ├── defenses_eval.csv (3,303 B, modified 17-10-2026 10:56:31)
│   └── h2_experiment.csv (9,250 B, modified 17-10-2026 10:56:22)
├── scripts/
│   ├── compute_report_stats.py (1,546 B)
│   ├── download_data.py (3,079 B)
│   ├── generate_figures.py (11,014 B)
│   ├── run_clean_baselines.py (3,986 B)
│   ├── run_cost_curves.py (5,989 B)
│   ├── run_defenses.py (5,073 B)
│   └── run_h2_experiment.py (4,437 B)
├── src/
│   ├── __init__.py (91 B)
│   ├── config.py (992 B)
│   ├── attacks/
│   │   ├── __init__.py (711 B)
│   │   ├── a1_single_fake_hub.py (1,126 B)
│   │   ├── a2_hub_farm.py (1,384 B)
│   │   ├── a3_bipartite_block.py (1,942 B)
│   │   ├── a4_hub_inflation.py (2,794 B)
│   │   ├── a5_cross_score.py (2,952 B)
│   │   ├── a6_greedy_gradient.py (3,546 B)
│   │   └── base.py (1,205 B)
│   ├── data/
│   │   ├── __init__.py (580 B)
│   │   ├── base_set.py (3,861 B)
│   │   ├── loader.py (4,650 B)
│   │   └── synthetic.py (3,534 B)
│   ├── defenses/
│   │   ├── __init__.py (548 B)
│   │   ├── d2_bharat_henzinger.py (2,222 B)
│   │   ├── d3_hub_capping.py (2,945 B)
│   │   ├── d4_wu_davison.py (2,137 B)
│   │   └── d5_trust_hits.py (2,914 B)
│   ├── eval/
│   │   ├── __init__.py (566 B)
│   │   ├── metrics.py (3,595 B)
│   │   └── stats.py (1,713 B)
│   └── rankers/
│       ├── __init__.py (497 B)
│       ├── base.py (1,234 B)
│       ├── hits.py (3,714 B)
│       ├── indegree.py (1,653 B)
│       ├── pagerank.py (3,059 B)
│       ├── randomized_hits.py (3,303 B)
│       ├── salsa.py (3,702 B)
│       └── subspace_hits.py (3,409 B)
└── tests/
    ├── test_attacks.py (2,629 B)
    ├── test_data.py (2,132 B)
    └── test_rankers.py (4,485 B)
```

---

## 2. TESTS

### Pytest Execution Results
We executed the test suite directly under two standard invocations:

1. **Bare `pytest -v` (FAILED):**
   - **Passed:** 0
   - **Failed / Errored:** 3 collection errors
   - **Skipped:** 0
   - **Exact Error Lines:**
     - `tests/test_attacks.py:6: in <module> from src.attacks import (...) E ModuleNotFoundError: No module named 'src'`
     - `tests/test_data.py:6: in <module> from src.data import (...) E ModuleNotFoundError: No module named 'src'`
     - `tests/test_rankers.py:6: in <module> from src.rankers import (...) E ModuleNotFoundError: No module named 'src'`
   - *Cause:* The repository lacks `pyproject.toml`, `setup.py`, or `pytest.ini` with `pythonpath = ["."]`.

2. **Module Invocation `python -m pytest -v` (PASSED):**
   - **Passed:** 16
   - **Failed:** 0
   - **Skipped:** 0
   - **Runtime:** 4.61 seconds
   - **Breakdown:**
     - `tests/test_attacks.py`: 6 tests passed (`test_a1_single_fake_hub`, `test_a2_hub_farm`, `test_a3_bipartite_block`, `test_a4_hub_inflation`, `test_a5_cross_score`, `test_a6_greedy_gradient`)
     - `tests/test_data.py`: 4 tests passed (`test_synthetic_generators`, `test_base_set_builder`, `test_snap_loader_wiki`, `test_webspam_labels_undecided`)
     - `tests/test_rankers.py`: 6 tests passed (`test_hits_vs_networkx`, `test_pagerank_vs_networkx`, `test_salsa_basic`, `test_indegree`, `test_randomized_hits_stability`, `test_subspace_hits`)

### Test Coverage Gaps
- **Defenses (D1-D5):** 0 unit tests exist (`tests/test_defenses.py` does not exist).
- **Evaluation & Metrics (`src/eval`):** 0 unit tests exist (`tests/test_eval.py` does not exist).
- **Graph loaders:** Only `wiki-Vote` is tested in `test_data.py`; `web-Stanford` and `web-NotreDame` loaders have 0 unit tests.

---

## 3. ENVIRONMENT FACTS

### Existence of `results/environment.txt`
- **File Status:** `results/environment.txt` **DOES NOT EXIST** in the repository.

### Live Environment Verification (Measured in this session)
- **CPU:** 12th Gen Intel(R) Core(TM) i5-12500H (12 physical cores, 16 logical processors)  
  *(Note discrepancy: `docs/PROGRESS_REPORT_FACTS.md` line 110 claimed "Intel Core i7-12700H", which does not match the actual host system).*
- **RAM:** Total Visible Memory: 16,454,388 KB (~15.7 GB usable, 16 GB physical).
- **OS:** Microsoft Windows 11 Home Single Language (64-bit, build 10.0.26100).
- **Python Version:** 3.12.5 (tags/v3.12.5:ff3bc82, Aug 6 2024, 20:45:27) [MSC v.1940 64 bit (AMD64)].
- **Core Library Versions:**
  - `numpy`: 1.26.4
  - `scipy`: 1.12.0
  - `networkx`: 3.4.2
  - `pandas`: 2.2.3
  - `matplotlib`: 3.10.0

### Peak-Memory Measurement Method
- **Documented Method:** The codebase uses Python's standard library `tracemalloc` (`tracemalloc.start()`, `tracemalloc.get_traced_memory()`), **NOT** process RSS (`psutil`).
- **File Reference:** Verified directly in [`scripts/run_clean_baselines.py:10,51,57-58`](../scripts/run_clean_baselines.py#L10).
- **Implication:** Memory figures in `results/clean_baselines.csv` track Python heap allocations created during the ranker execution call, not total OS page table footprint (RSS).

---

## 4. MODULE STATUS TABLE

| Module | File Path | Status | Tested? | Note |
|---|---|---|---|---|
| **HITS** | [`src/rankers/hits.py`](../src/rankers/hits.py) | **DONE** | Yes (`test_rankers.py`) | Sparse power iteration, L1 normalization, tolerance $10^{-8}$, SVD eigengap calculation via `scipy.sparse.linalg.svds`. Verified against NetworkX. |
| **PageRank** | [`src/rankers/pagerank.py`](../src/rankers/pagerank.py) | **DONE** | Yes (`test_rankers.py`) | Sparse power iteration, $\alpha=0.85$, uniform teleport, exact dangling node mass redistribution. Verified against NetworkX. |
| **SALSA** | [`src/rankers/salsa.py`](../src/rankers/salsa.py) | **DONE** | Yes (`test_rankers.py`) | Bipartite random walk with ergodic jump $\epsilon=10^{-4}$ for multi-component stability. Authority and hub scores verified to sum to 1. |
| **In-Degree** | [`src/rankers/indegree.py`](../src/rankers/indegree.py) | **DONE** | Yes (`test_rankers.py`) | Column-sum in-degree normalized by total in-degree. |
| **Randomized HITS (D1)** | [`src/rankers/randomized_hits.py`](../src/rankers/randomized_hits.py) | **DONE** | Yes (`test_rankers.py`) | Ng et al. (2001) reset $\epsilon=0.15$ with uniform teleport prior. |
| **Subspace HITS (D1)** | [`src/rankers/subspace_hits.py`](../src/rankers/subspace_hits.py) | **DONE** | Yes (`test_rankers.py`) | SVD projection across top-$k$ singular vectors ($k=5$). |
| **SNAP Loaders** | [`src/data/loader.py`](../src/data/loader.py) | **PARTIAL** | Yes (wiki-Vote only) | `load_snap_graph` can load `wiki-Vote`, `web-Stanford`, and `web-NotreDame`. Only `wiki-Vote` tested; Stanford/NotreDame untested in test suite. |
| **WEBSPAM Labels Loader** | [`src/data/loader.py`](../src/data/loader.py) | **DONE** | Yes (`test_data.py`) | Parses Set 1 & Set 2 labels; explicit handling for 176 undecided hosts (`exclude`, `spam`, `normal`, `keep`). |
| **WEBSPAM Host Graph Loader** | [`src/data/loader.py`](../src/data/loader.py) | **NOT STARTED** | No | No function exists to load the host graph. Compressed BVGraph `.graph` bitstream files are not downloaded. |
| **Synthetic Generators** | [`src/data/synthetic.py`](../src/data/synthetic.py) | **DONE** | Yes (`test_data.py`) | BA ($m=4$), ER ($p=0.005$), SBM with planted dense bipartite core. |
| **Base-Set Builder** | [`src/data/base_set.py`](../src/data/base_set.py) | **DONE** | Yes (`test_data.py`) | Kleinberg (1999) expansion: random-walk root set ($|R|=100-200$), forward expansion, predecessor cap (max 50). |
| **Attack A1 (Single Fake Hub)** | [`src/attacks/a1_single_fake_hub.py`](../src/attacks/a1_single_fake_hub.py) | **DONE** | Yes (`test_attacks.py`) | Adds 1 fake node pointing to target ($B=1$). |
| **Attack A2 (Hub Farm)** | [`src/attacks/a2_hub_farm.py`](../src/attacks/a2_hub_farm.py) | **DONE** | Yes (`test_attacks.py`) | Adds $p=B$ fake nodes, each pointing to target. |
| **Attack A3 (Bipartite Block)** | [`src/attacks/a3_bipartite_block.py`](../src/attacks/a3_bipartite_block.py) | **DONE** | Yes (`test_attacks.py`) | Injects $K_{p, q}$ where $p \times q \le B$, target is one authority, adds $p + q - 1$ nodes. |
| **Attack A4 (Hub Inflation)** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | **PARTIAL / MISALIGNED** | Yes (`test_attacks.py`) | Implements multi-hub inflation (proposal's A5) instead of 0-fake-hub inflation. |
| **Attack A5 (Cross-Score)** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | **PARTIAL / MISALIGNED** | Yes (`test_attacks.py`) | Implements farm with top authorities AND inter-hub cross links ($h_i \to h_j$). Not in cost curves CSV. |
| **Attack A6 (Greedy Gradient)** | [`src/attacks/a6_greedy_gradient.py`](../src/attacks/a6_greedy_gradient.py) | **DONE** | Yes (`test_attacks.py`) | Ranks candidate edges by $\partial \sigma_1 / \partial A_{ij} = h_i a_j$ with re-verification. Not in cost curves CSV. |
| **Defense D1 (Randomized/Subspace)** | [`src/rankers/randomized_hits.py`](../src/rankers/randomized_hits.py), [`subspace_hits.py`](../src/rankers/subspace_hits.py) | **DONE** | Yes (in `test_rankers.py`) | Randomized reset $\epsilon=0.15$; spectral projection $k=5$. |
| **Defense D2 (Bharat-Henzinger)** | [`src/defenses/d2_bharat_henzinger.py`](../src/defenses/d2_bharat_henzinger.py) | **BROKEN** | No | Domain fallback groups by weakly connected components. On any connected graph, all nodes are placed in `"comp_0"`, giving every edge identical weight $1/\|E\|$, resulting in exactly 0% attack reduction. |
| **Defense D3 (Hub Capping)** | [`src/defenses/d3_hub_capping.py`](../src/defenses/d3_hub_capping.py) | **DONE** | No | Caps each hub's authority contribution at `cap_fraction * sum(h)` (default 10%). |
| **Defense D4 (Wu-Davison)** | [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) | **PARTIAL** | No | Uses out-link Jaccard between hubs with a 50-hub comparison shortcut; penalizes clean hubs. |
| **Defense D5 (Trust-Based HITS)** | [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) | **DONE** | No | Trusted seed prior (default top 5% in-degree nodes as proxy). |
| **Metrics: Rank Gain** | [`src/eval/metrics.py`](../src/eval/metrics.py) | **DONE** | No | `rank_gain()` computes $r_{\text{clean}} - r_{\text{attacked}}$. |
| **Metrics: Normalized Rank Gain** | - | **NOT STARTED** | No | Not implemented in `metrics.py` (only raw integer rank gain). |
| **Metrics: Top-10 / Top-20 Entry** | [`scripts/run_cost_curves.py`](../scripts/run_cost_curves.py) | **DONE** | No | Inline binary indicator `int(att_rank <= 10)` in experiment script. |
| **Metrics: B*(k)** | - | **NOT STARTED** | No | Inversion script to compute minimum budget $B^*(k)$ not implemented. |
| **Metrics: Kendall's Tau** | [`src/eval/metrics.py`](../src/eval/metrics.py) | **DONE** | No | `scipy.stats.kendalltau` on common nodes. |
| **Metrics: Spearman's Rho** | - | **NOT STARTED** | No | Not implemented in `metrics.py`. |
| **Metrics: Jaccard@k** | [`src/eval/metrics.py`](../src/eval/metrics.py) | **DONE** | No | Top-$k$ set overlap fraction ($k=20$). |
| **Metrics: NDCG@k** | [`src/eval/metrics.py`](../src/eval/metrics.py) | **DONE** | No | Discounted cumulative gain; fake nodes mapped to relevance 0. |
| **Metrics: Fake Share** | [`src/eval/metrics.py`](../src/eval/metrics.py) | **DONE** | No | Fraction of top-$k$ nodes that are fake attacker nodes. |
| **Metrics: Eigengap** | [`src/rankers/hits.py`](../src/rankers/hits.py) | **DONE** | No | $\sigma_1^2 - \sigma_2^2$ via SciPy sparse SVD. |
| **Stats: Bootstrap CI** | [`src/eval/stats.py`](../src/eval/stats.py) | **DONE** | No | Percentile bootstrap (1,000 resamples, 95% CI). |
| **Stats: Wilcoxon Signed-Rank** | [`src/eval/stats.py`](../src/eval/stats.py) | **DONE** | No | Paired non-parametric test with zero-difference filtering. |
| **Stats: Holm Correction** | - | **NOT STARTED** | No | No multiple hypothesis testing correction in `stats.py` or codebase. |
| **Figures Script** | [`scripts/generate_figures.py`](../scripts/generate_figures.py) | **DONE** | No | Generates 4 figures (cost curves, H2 bifurcation, defense trade-off, architecture diagram). |

---

## 5. ATTACK DEFINITIONS CHECK

### Implementation vs Proposal Specification for A4 and A5

1. **Attack A4 (Hub Inflation):**
   - **Proposal Definition:** The target node itself or ONE fake page links to the $c$ highest-authority real pages ($c$ edges added, 0 or 1 fake node, no farm of fake hubs).
   - **Actual Code ([`src/attacks/a4_hub_inflation.py:53-79`](../src/attacks/a4_hub_inflation.py#L53)):
     ```python
     cost_per_hub = 1 + c_eff if c_eff > 0 else 1
     num_hubs = max(1, budget // cost_per_hub)
     # Injects num_hubs fake nodes!
     # Each fake node links to target AND to c_eff legitimate top authorities.
     ```
   - **Verdict:** **MISMATCH.** The code implements a **multi-hub farm** linking to both the target and real authorities. This is precisely what the proposal described as **A5**, NOT A4. The 0-fake-hub inflation (target out-linking to real authorities) is missing.

2. **Attack A5 (Cross-Score Coupling):**
   - **Proposal Definition:** $p$ fake hubs each link to $c$ real top authorities AND to the target.
   - **Actual Code ([`src/attacks/a5_cross_score.py:51-80`](../src/attacks/a5_cross_score.py#L51)):
     ```python
     # 1. Primary links: fake hubs -> target
     # 2. Inflation links: fake hubs -> real top authorities
     # 3. Cross links among fake hubs (h1 -> h2) to amplify internal scores
     ```
   - **Verdict:** **MISMATCH.** The code adds mutual cross-links between fake hubs ($h_i \to h_j$) on top of inflation links.

### How Budget $B$ is Counted Across Attacks
- **Edge-Only Budgeting:** In **ALL** attacks (A1-A6), the parameter `budget` enforces a ceiling strictly on the **number of added EDGES** (`len(added_edges) <= budget`).
- **Node Cost Inconsistency:** Nodes are treated as "free" in the budget constraint:
  - In A1: 1 edge, 1 node added.
  - In A2: $B$ edges, $B$ nodes added.
  - In A3: $B$ edges, $\approx 2\sqrt{B}$ nodes added ($p$ hubs, $q-1$ collateral authorities).
  - In A4: $B$ edges, $\approx B / (c + 1)$ nodes added.
  - In A5: $B$ edges, $\approx B / (c + 2)$ nodes added.
  - In A6: $B$ edges, $0$ to $B$ nodes added (prefers existing nodes, falls back to new nodes).
- **Consistency Summary:** Budget $B$ is uniformly counted as **edges only** across the codebase.

---

## 6. EXPERIMENTS ACTUALLY RUN

### Results CSV Inventory

| File | Script | Graphs Used | Attacks | Rankers | Defenses | Seeds | Targets / Graph | Budgets | Rows | Date Generated | Reflects Current Code? |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `clean_baselines.csv` | `run_clean_baselines.py` | 5 (`Synthetic_BA_1000`, `Synthetic_ER_1000`, `Synthetic_Planted_SBM`, `SNAP_wiki-Vote`, `SNAP_web-Stanford_BaseSet`) | None (Clean) | 6 (HITS, PageRank, SALSA, InDegree, RandomizedHITS, SubspaceHITS) | Evaluated as rankers | 1 (42) | Whole graph | None | 30 | 17-10-2026 10:51:46 | Yes |
| `cost_curves.csv` | `run_cost_curves.py` | 2 (`Synthetic_BA_500`, `SNAP_wiki-Vote_BaseSet`) | 3 (A2, A3, A4) | 4 (HITS, PageRank, SALSA, InDegree) | None | 3 (`42, 123, 456`) | 3 tiers (med, low, rand; 10 unique targets) | 7 (`1, 5, 10, 25, 50, 100, 200`) | 1,512 | 17-10-2026 10:55:54 | Yes |
| `defenses_eval.csv` | `run_defenses.py` | 1 (`Synthetic_BA_400`) | 2 (A2, A4) at $B \in \{25, 50\}$ (4 settings) | HITS baseline | 6 (D1-rand, D1-sub, D2, D3, D4, D5) | 1 (42) | 1 target (30th percentile node) | 2 (`25, 50`) | 28 | 17-10-2026 10:56:31 | Yes |
| `h2_experiment.csv` | `run_h2_experiment.py` | 1 (`Synthetic_BA_300`) | 1 (A2 Hub Farm) | 4 (HITS, PageRank, SALSA, InDegree) | None | 1 (42) | 1 target (20th percentile node) | 66 points ($p \in [1, 96]$) | 66 | 17-10-2026 10:56:22 | Yes |

### Comparison to Proposal Commitments
- **Graph Combinations:**
  - **Proposed:** $\ge 30$ (graph, base set, target) combinations $\times 5$ seeds ($= 150$ settings minimum).
  - **Actually Run in `cost_curves.csv`:** 2 graphs $\times 1$ base set $\times 3$ target tiers $= 6$ combinations $\times 3$ seeds $= 18$ settings.
  - **Omissions:** `web-Stanford` base-set (absent from cost curves), `web-NotreDame` base-set (absent), `WEBSPAM-UK2006` (absent), seeds 789 and 999 (absent).
- **Attacks in Cost Curves:**
  - **Proposed:** All 6 attacks (A1-A6).
  - **Actually Run:** Only 3 attacks (A2, A3, A4). A1, A5, and A6 are absent from `cost_curves.csv`.
- **Budget Grid:**
  - **Proposed:** Dense grid $1 \dots 500$.
  - **Actually Run:** 7 discrete points: `[1, 5, 10, 25, 50, 100, 200]`. Maximum budget evaluated is $200$, not $500$.

---

## 7. HYPOTHESIS STATUS (H1-H4)

### Hypothesis H1: "On random-like graphs HITS ~ in-degree"
- **Status: PARTIALLY SUPPORTED (Evidence Thin & Data Discrepancy Found).**
- **Experiment:** Verified in this session on clean synthetic graphs using `scipy.stats.kendalltau` between HITS authority scores and in-degree.
- **Numbers:**
  - On $G_{\text{ER}}(1000, 0.005, \text{seed}=42)$: Kendall's $\tau = \mathbf{0.7461}$ ($p = 7.99 \times 10^{-244}$).
  - On $G_{\text{BA}}(1000, 4, \text{seed}=42)$: Kendall's $\tau = \mathbf{0.5154}$ ($p = 2.50 \times 10^{-115}$).
  - On Planted SBM (840 nodes, seed=42): Kendall's $\tau = \mathbf{0.5329}$ ($p = 1.39 \times 10^{-103}$).
- **Audit Finding:** In `docs/PROGRESS_REPORT_FACTS.md` line 118, it claimed $\tau = 0.912$ on ER and $\tau = 0.481$ on BA. No CSV contains these numbers. Live recomputation yields $\tau = 0.7461$ and $\tau = 0.5154$. While the qualitative trend holds ($\tau_{\text{ER}} > \tau_{\text{BA}}$), the report's headline number $0.912$ is unverified.
- **Evidence Breadth:** 1 graph per topology, single random seed (seed 42), 0 real web graphs evaluated.

### Hypothesis H2: "Hub farm of $p$ fake hubs only takes over top HITS vectors when $p \sim \sigma_1^2$ (sharp jump; PageRank gains smooth)"
- **Status: SUPPORTED (on 1 synthetic graph; SNAP validation pending).**
- **Experiment:** Evaluated in `scripts/run_h2_experiment.py` recorded in `results/h2_experiment.csv`.
- **Numbers:** Evaluated on a 300-node Barabasi-Albert graph ($\sigma_1 = 7.279, \sigma_1^2 = 52.98$):
  - At $p = 26$ ($p / \sigma_1^2 = 0.49$): Target HITS rank is $218 / 300$, score $= 0.0008$.
  - At $p = 52$ ($p / \sigma_1^2 = 0.98$): Target HITS rank jumps abruptly to $1$, score surges to $0.0955$.
  - At $p = 79$ ($p / \sigma_1^2 = 1.49$): Target HITS score reaches $0.8996$ ($90\%$ of total network authority mass).
  - PageRank rank progression over the same range is smooth: $235 \to 6 \to 1$.
- **In Cost Curves ($N=500$ & wiki-Vote):**
  - At $B=25$: Plain HITS Top-10 entry is $0.0\%$ [0.0%, 0.0%].
  - At $B=100$: Plain HITS Top-10 entry leaps to $50.0\%$ [37.0%, 63.0%].
- **Limits / Thinness:** The bifurcation curve was generated on **exactly 1 synthetic graph** (300 nodes, 1 seed, 1 target). It has not been verified on `web-Stanford` or `web-NotreDame`.

### Hypothesis H3: "On graphs with dense communities, attaching to the community (TKC) is cheaper"
- **Status: PARTIALLY SUPPORTED (Evidence Thin).**
- **Experiment:** Comparison of attack A4 (inflation by linking to top authorities) vs A2 (pure isolated hub farm) in `results/cost_curves.csv`.
- **Numbers:**
  - In `results/cost_curves.csv`, on `Synthetic_BA_500` at $B=25$: A4 achieved Top-10 entry in $100\%$ of trials, whereas A2 achieved $0\%$ Top-10 entry until $B \ge 75$.
- **Limits / Thinness:** Evaluated on only 2 graphs across 3 seeds. Furthermore, because A4 was implemented as multi-hub inflation rather than the proposal's 0-fake-hub attack, H3 has only been tested for a multi-hub variant.

### Hypothesis H4: "Damped/capped/trust-based HITS cuts attack success with little clean-graph damage"
- **Status: PARTIALLY SUPPORTED (Very Thin Evidence & D2 Broken).**
- **Experiment:** Evaluated in `scripts/run_defenses.py` recorded in `results/defenses_eval.csv`.
- **Numbers:**
  - Evaluated on **only 1 graph** (Synthetic BA-400, 1 seed, 1 target) across 4 attack conditions (`A2_B25`, `A2_B50`, `A4_B25`, `A4_B50`).
  - D4 (Wu-Davison): 100.0% attack success reduction on this single graph; clean graph false demotion $= 0.0$ ($1.0 - \text{Jaccard@20}$).
  - D1 (Randomized HITS, $\epsilon=0.15$): Attack reduction $0.0\%$ (target still gained rank), clean Jaccard $= 0.9048$, clean NDCG $= 0.9994$.
  - D1 (Subspace HITS, $k=5$): Attack reduction $39.3\% - 68.9\%$, clean Jaccard $= 0.4815$, clean NDCG $= 0.9311$.
  - D3 (Hub Capping, $10\%$): Attack reduction $0.0\%$ on A2, $1.9\%$ on A4.
  - D5 (Trust HITS): Attack reduction $20.7\% - 26.5\%$ on A4, negative reduction on A2 (clean rank was distorted).
  - D2 (Bharat-Henzinger): **0.0% attack reduction** across all conditions (broken WCC fallback).
- **Limits / Thinness:** Evidence is extremely thin: exactly 1 synthetic graph, 1 target, 0 real web graphs, no statistical confidence intervals.

---

## 8. DEFENSE STATUS

### Implementation Summary (One Sentence Each)
- **D1 (Randomized HITS / Subspace HITS):** Implemented in [`src/rankers/randomized_hits.py`](../src/rankers/randomized_hits.py) as a power iteration with uniform restart teleport ($\epsilon=0.15$), and in [`src/rankers/subspace_hits.py`](../src/rankers/subspace_hits.py) via top-$k$ SVD projection ($k=5$).
- **D2 (Bharat-Henzinger):** Implemented in [`src/defenses/d2_bharat_henzinger.py`](../src/defenses/d2_bharat_henzinger.py) by scaling edge weights inversely by inter-domain edge counts ($1 / C[d_u, d_v]$), falling back to weakly connected components when domain metadata is absent.
- **D3 (Hub Capping):** Implemented in [`src/defenses/d3_hub_capping.py`](../src/defenses/d3_hub_capping.py) by clamping each hub's authority contribution at $\text{cap\_fraction} \times \sum h$ (default $10\%$) during each power iteration step.
- **D4 (Wu-Davison):** Implemented in [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) by penalizing edges from pairs of hubs whose outgoing target sets exhibit Jaccard similarity $> 0.5$.
- **D5 (Trust-Based HITS):** Implemented in [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) by injecting a personalized seed prior (top 5% in-degree nodes as proxy) into authority and hub restarts with weight $\epsilon=0.15$.

### D4 Signal Analysis & Clean-Graph Flag Rate
- **Signal Used:** D4 uses **OUT-LINK Jaccard similarity between hubs** (overlap of outgoing targets: $|Out(u) \cap Out(v)| / |Out(u) \cup Out(v)|$). It does **NOT** use the in-link/out-link overlap metric from the original Wu & Davison (2005) paper.
- **Implementation Shortcut:** Line 44 of `d4_wu_davison.py` checks only `min(len(hub_list), i + 50)` neighbors in the node list, omitting all hub pairs separated by more than 50 positions.
- **Clean-Graph Flag Rate:** Measured live in this audit on clean `Synthetic_BA_400`:
  - **3 legitimate hub pairs are flagged and penalized** on the unattacked graph.
  - The reported "0.0 false demotion" in `defenses_eval.csv` occurred solely because `false_demotion` was defined as `1.0 - clean_top20_jaccard`, and the 3 penalized hubs did not cause any top-20 authority to leave the top 20.
- **Re-checking Against Harder Attacks:**
  - D4 has **NOT** been evaluated against camouflaged farms, A1, A3, A5, or A6.
  - It has only been evaluated against A2 and A4 at budgets 25 and 50 on 1 synthetic graph.

### Threshold Selection
- All defense parameters (`cap_fraction=0.10`, `overlap_threshold=0.5`, `penalty_factor=0.2`, `eps=0.15`, `k=5`) are hardcoded defaults. No threshold tuning, sweep, or sensitivity ablation exists in the codebase.

### Defense $\times$ Attack Matrix
- **Status:** **PARTIAL / INCOMPLETE.**
- Only 4 combinations exist in `results/defenses_eval.csv`: $\{A2_{25}, A2_{50}, A4_{25}, A4_{50}\} \times \{D1_{\text{rand}}, D1_{\text{sub}}, D2, D3, D4, D5\}$.
- The full planned $6 \times 5$ matrix across multiple graphs and budgets does not exist.

---

## 9. WEBSPAM-UK2006

### Downloaded Files & Sizes (`data/raw/`)
1. `data/raw/webspam-uk2006-2.0.tar.gz` (153,085 bytes / ~153 KB)
2. `data/raw/webspam-uk2006-2.0/webspam-uk2006-set1-labels.txt` (405,582 bytes)
3. `data/raw/webspam-uk2006-2.0/webspam-uk2006-set1-labels-DomainOrTwoHumans.txt` (158,580 bytes)
4. `data/raw/webspam-uk2006-2.0/webspam-uk2006-set2-labels.txt` (130,906 bytes)
5. `data/raw/webspam-uk2006-2.0/webspam-uk2006-set2-labels-DomainOrTwoHumans.txt` (67,762 bytes)

### Host Graph Status
- **Is the host graph downloaded or loaded?** **NO.** The host graph is completely absent from `data/raw/`.
- **Do Spam@k, AUC, or F1 results exist?** **NO.** No classification or ranking evaluation on WEBSPAM exists in any script or CSV.
- **What is blocking:**
  1. The host link graph (`uk-2006-05.host.graph` and `.properties`, ~1-2 GB compressed) is stored on the University of Milan LAW repository in WebGraph BVGraph bitstream format.
  2. Ingestion requires downloading the WebGraph Java `.jar` dependencies (`webgraph-*.jar`, `fastutil-*.jar`, `dsiutils-*.jar`) and running `BV2Ascii` or using a specialized bitstream reader.
  3. No download script exists for the host graph bitstream.
- **Does `docs/WEBSPAM_MANUAL_STEPS.md` exist?** **NO.** The file does not exist anywhere in the repository.

### Verified Label Counts (Direct File Audit)

| File | Total Hosts | Normal (Non-Spam) | Spam | Undecided |
|---|---|---|---|---|
| `webspam-uk2006-set1-labels.txt` | 8,415 | 7,472 | 767 | 176 |
| `webspam-uk2006-set1-labels-DomainOrTwoHumans.txt` | 5,622 | 4,948 | 674 | 0 |
| `webspam-uk2006-set2-labels.txt` | 2,247 | 651 | 1,346 | 250 |
| `webspam-uk2006-set2-labels-DomainOrTwoHumans.txt` | 1,851 | 601 | 1,250 | 0 |

---

## 10. STRETCH OBJECTIVES

| Stretch Objective | Status | Evidence |
|---|---|---|
| **Game-Theoretic Attacker-Defender Loop** | **NOT STARTED** | No code, classes, or scripts exist in `src/` or `scripts/`. Grep returns only planned mentions in `PROGRESS_REPORT_FACTS.md` ("scheduled for final stretch"). |
| **Empirical / Closed-Form Eigengap Bound** | **PARTIAL** | Empirical threshold $p \approx \sigma_1^2$ is measured in `run_h2_experiment.py` and plotted in `figures/h2_spectral_takeover.png`. However, the mathematical closed-form proof and generalized $B^*(k)$ function are **NOT STARTED** (no proof document or bound calculation script exists). |
| **WEBSPAM-UK2007 + Multi-Feature Classifier** | **NOT STARTED** | No UK-2007 data downloaded, no feature extraction scripts, no classifier models trained or evaluated. |

---

## 11. DOCS AND FIGURES

### Documentation Inventory
1. [`README.md`](../README.md) (7,689 bytes):
   - Clean markdown.
   - Contains 0 `file:///` links and 0 local absolute paths.
2. [`docs/PROGRESS_REPORT_FACTS.md`](../docs/PROGRESS_REPORT_FACTS.md) (23,951 bytes):
   - **Audit Issue:** Contains **34 hardcoded local `file:///c:/Users/shris/OneDrive/...` links**.
   - Contains an unverified Kendall tau figure for H1 ($\tau=0.912$ vs real $\approx 0.746$).
   - Contains inaccurate hardware specs (Core i7-12700H vs real Core i5-12500H).
3. `docs/WEBSPAM_MANUAL_STEPS.md`: **Does not exist.**
4. No v1 / v2 versions of docs exist.

### Figures Inventory (`figures/`)

| File Name | Shows | CI Bands Present? | Generated from Current CSVs? |
|---|---|---|---|
| `architecture.png` (563 KB) | System pipeline diagram (Ingestion, Base-Set, Attacks, Defenses, Rankers, Eval) | N/A (Diagram) | Yes (`generate_figures.py`) |
| `architecture.svg` (156 KB) | Vector SVG version of architecture diagram | N/A (Diagram) | Yes (`generate_figures.py`) |
| `cost_curves_rank_gain.png` (431 KB) | Dual-panel plot of Target Rank Gain vs Budget for HITS, PageRank, SALSA, InDegree on BA-500 and wiki-Vote | **No (plots mean $\pm$ standard deviation, not bootstrap 95% CI)** | Yes (from `results/cost_curves.csv`) |
| `h2_spectral_takeover.png` (368 KB) | Target Authority and Target Rank vs Farm Size $p$ annotated with theoretical $\sigma_1^2$ line | No (deterministic single-run trajectory) | Yes (from `results/h2_experiment.csv`) |
| `defenses_tradeoff.png` (180 KB) | Scatter plot of Attack Success Reduction (%) vs Clean Graph False Demotion across 7 defense variants | No (points without error bars) | Yes (from `results/defenses_eval.csv`) |

---

## 12. KNOWN PROBLEMS AND UNVERIFIED CLAIMS

1. **Bare `pytest` Import Failure:** Running bare `pytest -v` fails on test collection (`ModuleNotFoundError: No module named 'src'`). Running `python -m pytest` is mandatory unless `PYTHONPATH=.` is set or a `pyproject.toml` is added.
2. **D2 Bharat-Henzinger Logic Flaw:** In `src/defenses/d2_bharat_henzinger.py`, when `domain_map` is not provided (the default), it falls back to weakly connected components. On any connected graph, every node belongs to `"comp_0"`. Consequently, all edges receive identical weight $1/|E|$, which scales the adjacency matrix by a constant and has zero effect on HITS scores. This explains why D2 achieved 0.0% attack reduction in `defenses_eval.csv`.
3. **D4 Wu-Davison Window Shortcut & Signal Deviation:**
   - Evaluates out-link Jaccard between hubs instead of in/out link overlap.
   - Truncates pairwise comparisons to the next 50 nodes in the list (`i + 50`), creating an arbitrary index-order dependency.
   - Clean-graph test in this audit flagged 3 legitimate hub pairs on BA-400.
4. **H1 Correlation Number Unverified:** The progress report states Kendall's $\tau = 0.912$ on ER(1000, 0.005). Recomputing in this audit on ER(1000, 0.005) yields $\tau \approx 0.7461$. The 0.912 figure was likely pasted from an attacked PageRank row in `cost_curves.csv`.
5. **Hardware Specification Discrepancy:** `PROGRESS_REPORT_FACTS.md` lists an Intel Core i7-12700H; the actual physical machine is an Intel Core i5-12500H.
6. **Attack Nomenclature / Definition Mismatch:**
   - `a4_hub_inflation.py` implements multi-hub inflation with edges to target and real top authorities (the proposal's A5).
   - `a5_cross_score.py` implements a farm with top authorities plus inter-hub cross-links ($h_i \to h_j$).
   - The proposal's original A4 (0 fake hubs, target linking directly to $c$ authorities) is not implemented.
7. **Missing Unit Tests:** Zero unit tests exist for defenses (`src/defenses`), evaluation metrics (`src/eval/metrics.py`), or statistical confidence intervals (`src/eval/stats.py`).
8. **Missing Environment Documentation:** `results/environment.txt` does not exist.
9. **Missing WEBSPAM Host Graph:** The host graph was never downloaded; `docs/WEBSPAM_MANUAL_STEPS.md` does not exist.
10. **Hardcoded Machine Paths in Documentation:** 34 occurrences of `../...` in `docs/PROGRESS_REPORT_FACTS.md`.

---

## 13. REMAINING WORK AND TIME ESTIMATE

### Remaining Tasks vs Proposal Timeline

| Priority | Task | Importance / Why Needed | Realistic Effort Estimate | Human Intervention Needed? |
|---|---|---|---|---|
| **P0** | **Download & Extract WEBSPAM-UK2006 Host Graph** | Required for Milestone 1 / Milestone 3; blocks all real-world spam host evaluations (Spam@k, AUC, F1). | ~60 min compute (download + extract) + 45 min agent work | **YES:** User must obtain `.graph` and `.properties` files from LAW / Milan and provide Java runtime for `BV2Ascii`. |
| **P1** | **Fix D2 Bharat-Henzinger & D4 Wu-Davison Defenses** | D2 is currently a no-op (0% reduction); D4 uses out-link Jaccard and has a 50-hub truncation shortcut. | ~45 min agent work + 10 min testing | **No** (pure code fix: domain parser for SNAP/WEBSPAM, full pairwise or min-hash for D4). |
| **P2** | **Expand Attack Cost Curves Matrix (Milestone 2)** | Currently only 2 graphs, 3 attacks, 3 seeds, budget $\le 200$. Need A1, A5, A6, `web-Stanford`, `web-NotreDame`, 5 seeds, and budgets up to 500. | ~90 min compute + 30 min agent work | **No** (unattended overnight script run). |
| **P3** | **Execute Full Defense $\times$ Attack Matrix (Milestone 2)** | Defenses currently evaluated on only 1 synthetic graph and 4 conditions. Need all 5 defenses $\times$ all 6 attacks across multiple graphs. | ~60 min compute + 30 min agent work | **No** (unattended script run). |
| **P4** | **Create WEBSPAM Host Graph Loader & Evaluation Script** | Compute Spam@k, AUC, and precision/recall across clean and attacked rankings. | ~45 min agent work + 20 min compute | **No** (once host graph ASCII edge list is available). |
| **P5** | **Add Missing Unit Tests (`test_defenses.py`, `test_eval.py`)** | Ensure zero regression and establish CI safety. | ~30 min agent work | **No**. |
| **P6** | **Fix Repo Hygiene (pytest config, docs cleanup)** | Add `pytest.ini` so bare `pytest` works; replace 34 `file:///` local paths in docs with relative links; create `results/environment.txt`. | ~20 min agent work | **No**. |
| **P7** | **Stretch: Mathematical Bound & Closed-Form Proof** | Complete theoretical derivation of $B^*(k)$ vs $\sigma_2$ for the final report. | ~90 min agent / human theoretical analysis | **YES:** Theoretical alignment with team. |
| **P8** | **Stretch: Game-Theoretic Loop & UK-2007 Classifier** | Optional stretch items for bonus evaluation. | ~120 min compute + 60 min agent work | **YES:** Decision whether to attempt or drop for 8 Nov freeze. |

---

## 14. TOP 5 THINGS I SHOULD KNOW

1. **WEBSPAM host graph is completely absent:** Only the 153 KB label files are in `data/raw/`. The actual host graph is not downloaded, no loader exists, and `docs/WEBSPAM_MANUAL_STEPS.md` was never created. Without manual intervention to acquire the WebGraph bitstream and convert it (via Java `BV2Ascii`), WEBSPAM host graph evaluation will fail the 8 Nov experiments freeze.
2. **Defenses were evaluated on a single 400-node synthetic graph with 1 target:** The claim of "100% attack reduction / 0.0 false demotion" in `PROGRESS_REPORT_FACTS.md` reflects a single run on a 400-node synthetic graph under simple farms. Furthermore, D4 uses out-link Jaccard (with an artificial 50-hub window) instead of the paper's in/out link overlap, and on clean graphs it does penalize legitimate hubs. D2 Bharat-Henzinger is functionally broken (produces 0.0% attack reduction due to a WCC fallback).
3. **Attack definitions A4 and A5 deviate from the proposal:** `a4_hub_inflation.py` adds multiple fake hubs pointing to both target and top real authorities (which matches the proposal's A5), while `a5_cross_score.py` adds mutual cross-links between fake hubs. The proposal's original A4 (0 fake hubs, target linking to real authorities) is not implemented.
4. **Experimental coverage is ~12% of the proposal plan:** In `cost_curves.csv`, only 2 graphs (`Synthetic_BA_500`, `SNAP_wiki-Vote_BaseSet`), 3 attacks (A2, A3, A4), 3 seeds (42, 123, 456), and budgets up to 200 were executed. A1, A5, A6 and graphs `web-Stanford`, `web-NotreDame`, and `WEBSPAM` were omitted.
5. **Bare `pytest` fails and documentation contains 34 hardcoded local `file:///` paths:** Running bare `pytest` crashes with `ModuleNotFoundError: No module named 'src'` (it must be run as `python -m pytest`). Additionally, `PROGRESS_REPORT_FACTS.md` contains 34 machine-specific `file:///c:/Users/shris/...` paths, an incorrect CPU model, and an unverified H1 correlation figure ($\tau = 0.912$ vs actual $\approx 0.746$).
