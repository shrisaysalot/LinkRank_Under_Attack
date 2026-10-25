# Mid-Project Evidence Pack & Progress Report Facts

## 1. Header
- **Group Number:** 16
- **Project Title:** LinkRank Under Attack: Adversarial Robustness of HITS
- **Course:** Information Retrieval (IR)
- **Members:** Shrisay Shandilya, Vibhor Rathi, Prachi Jain
- **Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)
- **Date of Report:** 17 October 2026

---

## 2. Implementation Status Table

| Module Category | Component / Module | Status | File Path | One-Line Note |
|---|---|---|---|---|
| **Rankers** | Sparse Power Iteration HITS | **DONE** | [`src/rankers/hits.py`](../src/rankers/hits.py) | Full sparse power iteration with convergence tracking and SVD eigengap calculation. |
| **Rankers** | PageRank Baseline | **DONE** | [`src/rankers/pagerank.py`](../src/rankers/pagerank.py) | Sparse power iteration with damping $\alpha=0.85$ and exact dangling node mass redistribution. |
| **Rankers** | SALSA Baseline | **DONE** | [`src/rankers/salsa.py`](../src/rankers/salsa.py) | Bipartite random walk with ergodic teleport for disconnected components. |
| **Rankers** | In-Degree Centrality | **DONE** | [`src/rankers/indegree.py`](../src/rankers/indegree.py) | Normalized column-sum in-degree baseline ($O(\|E\|)$ time). |
| **Rankers / Defenses** | Randomized HITS (D1) | **DONE** | [`src/rankers/randomized_hits.py`](../src/rankers/randomized_hits.py) | Damped authority/hub power iteration with uniform jump reset $\epsilon=0.15$ (Ng et al. 2001). |
| **Rankers / Defenses** | Subspace HITS (D1) | **DONE** | [`src/rankers/subspace_hits.py`](../src/rankers/subspace_hits.py) | Spectral projection across top-$k$ singular vectors to prevent single-community takeover. |
| **Data Loaders** | SNAP Graph Loader | **DONE** | [`src/data/loader.py`](../src/data/loader.py) | Downloads and loads real SNAP web graphs (wiki-Vote, web-Stanford, web-NotreDame). |
| **Data Loaders** | WEBSPAM-UK2006 Loader | **PARTIAL** | [`src/data/loader.py`](../src/data/loader.py) | Official human/domain labels downloaded & parsed (8,415 hosts; explicit undecided handling); raw webgraph pending BVGraph conversion. |
| **Data Generators** | Synthetic Graph Generators | **DONE** | [`src/data/synthetic.py`](../src/data/synthetic.py) | Barabasi-Albert (scale-free), Erdos-Renyi, and SBM with planted dense bipartite communities. |
| **Data Subsets** | Kleinberg Base-Set Builder | **DONE** | [`src/data/base_set.py`](../src/data/base_set.py) | Query root set sampling ($|R| \approx 100-200$), out-link expansion, and max 50 in-link capping. |
| **Attacks** | A1: Single Fake Hub | **DONE** | [`src/attacks/a1_single_fake_hub.py`](../src/attacks/a1_single_fake_hub.py) | Injects 1 fake node with 1 direct edge to target. |
| **Attacks** | A2: Hub Farm | **DONE** | [`src/attacks/a2_hub_farm.py`](../src/attacks/a2_hub_farm.py) | Injects $p$ fake hub nodes each linking directly to target. |
| **Attacks** | A3: Bipartite Block | **DONE** | [`src/attacks/a3_bipartite_block.py`](../src/attacks/a3_bipartite_block.py) | Injects $K_{p, q}$ bipartite clique containing target and collateral fake authorities. |
| **Attacks** | A4: Hub Inflation | **DONE** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | Fake hubs link to target AND top legitimate authorities to inflate hub weights. |
| **Attacks** | A5: Cross-Score Coupling | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | Hub inflation combined with reciprocal cross-links among attacker cluster. |
| **Attacks** | A6: Greedy Gradient Edge Choice | **DONE** | [`src/attacks/a6_greedy_gradient.py`](../src/attacks/a6_greedy_gradient.py) | Ranks edge additions by $\partial \sigma_1 / \partial A_{ij} = h_i a_j$ with candidate list re-verification. |
| **Defenses** | D2: Bharat-Henzinger Edge Weighting | **DONE** | [`src/defenses/d2_bharat_henzinger.py`](../src/defenses/d2_bharat_henzinger.py) | Down-weights multiple edges between the same source and destination clusters ($1/m$). |
| **Defenses** | D3: Hub-Contribution Capping | **DONE** | [`src/defenses/d3_hub_capping.py`](../src/defenses/d3_hub_capping.py) | Caps max hub weight contribution to any authority at $10\%$ of total hub mass. |
| **Defenses** | D4: Wu-Davison Link-Farm Reweighting | **DONE** | [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) | Detects and penalizes hubs sharing suspiciously high Jaccard out-link overlap. |
| **Defenses** | D5: Trust-Based HITS | **DONE** | [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) | Injects TrustRank seed prior in jump term; cuts authority derived from zero-trust hubs. |
| **Evaluation** | Metrics & Correlation | **DONE** | [`src/eval/metrics.py`](../src/eval/metrics.py) | Rank gain, score amplification, top-k entry, NDCG@k, Jaccard@k, Kendall tau, fake share. |
| **Evaluation** | Statistical Confidence Testing | **DONE** | [`src/eval/stats.py`](../src/eval/stats.py) | Non-parametric percentile bootstrap 95% CIs and Wilcoxon signed-rank paired tests. |
| **WEBSPAM Eval** | Spam Host Classification / Spam@k | **PARTIAL** | [`src/data/loader.py`](../src/data/loader.py) | Labels loaded and categorized; full AUC / spam@k evaluation pending complete hostgraph edge dump. |
| **Stretch** | Game-Theoretic Attacker-Defender Loop | **PENDING** | - | Iterative adversarial equilibrium (scheduled for final stretch). |
| **Stretch** | Closed-Form Spectral Robustness Bound | **PENDING** | - | Derivation of exact lower bound on attacker budget $B^*$ to achieve top-1. |
| **Stretch** | WEBSPAM-UK2007 Classifier | **PENDING** | - | Multi-feature spam classifier on UK-2007 corpus. |

---

## 3. Architecture Changes vs Proposal
**None in core algorithm design; minor operational clarifications:**
1. **Link-Analysis Focus vs IR Text Processing:** The standard IR proposal template mentions text processing (tokenization, stemming, inverted index, BM25). Because this project investigates link-structure vulnerability, the analogous pipeline consists of graph ingestion, deduplication/self-loop filtering, Kleinberg query base-set expansion, sparse power iteration ranking, and link injection attacks. No text processing or document indexing is employed or required.
2. **WEBSPAM-UK2006 Hostgraph Ingestion:** While the official host label sets (set1 and set2, 8,415 hosts) were successfully retrieved, the underlying multi-gigabyte link graph is hosted in WebGraph compressed bitstream (`.graph` / `.properties`) format requiring Java extraction tools (`BV2Ascii.java`). For mid-project experiments, we evaluated on real SNAP web graphs (`wiki-Vote`, `web-Stanford`, `web-NotreDame`) and synthetic graphs, deferring complete BVGraph extraction to the final sprint.

---

## 4. Pipeline Details

### Graph Loading & Cleaning
- **SNAP Graphs:** Ingested from official SNAP `.txt.gz` archives. Headers and comments are parsed, self-loops are preserved or removed, isolated components indexed, and nodes re-mapped to contiguous zero-indexed integers ($0 \dots N-1$).
- **Base-Set Construction (Kleinberg 1999):**
  - Root Set: Sampled via localized random walks from seed nodes ($|R| \in [100, 200]$) to represent query-topical results.
  - Expansion: All outgoing neighbors added.
  - In-Link Capping: Predecessors are capped at a maximum of $50$ in-links per root node (preventing ubiquitous portal hubs from overwhelming the subgraph).
- **WEBSPAM-UK2006 Undecided Label Handling:**
  - Evaluators in WEBSPAM tagged hosts with spamicity in $[0, 1]$. Hosts with score $> 0.5$ are `spam`, $< 0.5$ are `normal`, and exactly $0.5$ are `undecided` ($176$ hosts in Set 1).
  - Explicit Strategy: In our loader (`src/data/loader.py`), undecided hosts are excluded by default (`undecided_mode="exclude"`) for rigorous binary ground-truth fidelity, with configurable options for conservative (`"spam"`), lenient (`"normal"`), or ternary (`"keep"`) evaluation.

### Ranker Parameters
- **HITS:** Power iteration with L1 normalization after each step; convergence tolerance $\text{tol} = 10^{-8}$, maximum iterations $= 200$. Eigengap $\sigma_1^2 - \sigma_2^2$ computed via SciPy ARPACK sparse SVD.
- **PageRank:** Damping factor $\alpha = 0.85$, uniform personalization vector $v = \frac{1}{N}\mathbf{1}$, dangling node handling via uniform redistribution, $\text{tol} = 10^{-8}$, $\text{max\_iter} = 200$.
- **SALSA:** Bipartite random walk with ergodic reset $\epsilon = 10^{-4}$ to ensure unique stationary distribution across disconnected components, $\text{tol} = 10^{-8}$.
- **Randomized HITS (D1):** Reset parameter $\epsilon = 0.15$.
- **Subspace HITS (D1):** Subspace dimensionality $k = 5$ singular vectors.
- **Hub-Capping (D3):** Max hub weight cap $= 10\%$ of total hub mass.
- **Random Seeds:** Default seed `42`; multi-seed experiments use `[42, 123, 456, 789, 999]`.

---

## 5. Preliminary Results Table

The table below summarizes **1,512 empirical experimental trials** conducted across synthetic scale-free networks (`Synthetic_BA_500`, 500 nodes, 2,180 edges) and real SNAP web graphs (`SNAP_wiki-Vote_BaseSet`, 2,441 nodes, 78,962 edges) across 3 distinct random seeds, 3 target tiers (low-rank, medium-rank, random-rank), and 3 attack families (Hub Farm A2, Bipartite Block A3, Hub Inflation A4).

Values report **Mean and [95% Percentile Bootstrap Confidence Interval]**:

### Results at Fixed Budget $B = 25$ Edges (Pre-Takeover Regime)

| Ranker | Target Rank Gain | Top-10 Entry Rate (%) | Top-20 Entry Rate (%) | Top-20 Jaccard Similarity | NDCG@20 Fidelity | Kendall's $\tau$ | Avg Time / Run |
|---|---|---|---|---|---|---|---|
| **Plain HITS** | 59.7 [32.5, 91.2] | **0.0%** [0.0%, 0.0%] | 11.1% [3.7%, 18.5%] | 0.989 [0.981, 0.996] | 0.998 [0.996, 0.999] | 0.992 | 0.045s |
| **PageRank ($\alpha=0.85$)** | 454.8 [320.0, 590.2] | **33.3%** [20.4%, 44.4%] | 33.3% [20.4%, 44.4%] | 0.925 [0.904, 0.946] | 0.983 [0.975, 0.989] | 0.994 | 0.013s |
| **SALSA** | 381.8 [290.7, 474.5] | **16.7%** [7.4%, 26.0%] | 16.7% [7.4%, 26.0%] | 0.984 [0.975, 0.993] | 0.996 [0.993, 0.998] | 0.992 | 0.016s |
| **In-Degree** | 214.6 [173.8, 257.7] | **16.7%** [7.4%, 26.0%] | 16.7% [7.4%, 26.0%] | 0.977 [0.966, 0.986] | 0.995 [0.992, 0.997] | 0.998 | 0.009s |

### Results at Fixed Budget $B = 100$ Edges (Post-Takeover Regime)

| Ranker | Target Rank Gain | Top-10 Entry Rate (%) | Top-20 Entry Rate (%) | Top-20 Jaccard Similarity | NDCG@20 Fidelity | Kendall's $\tau$ | Avg Time / Run |
|---|---|---|---|---|---|---|---|
| **Plain HITS** | 157.3 [118.3, 199.8] | **50.0%** [37.0%, 63.0%] | **50.0%** [37.0%, 63.0%] | **0.694** [0.595, 0.778] | **0.815** [0.741, 0.880] | 0.935 | 0.048s |
| **PageRank ($\alpha=0.85$)** | 577.4 [413.1, 749.4] | **33.3%** [20.4%, 44.4%] | 33.3% [20.4%, 44.4%] | 0.864 [0.817, 0.909] | 0.931 [0.898, 0.958] | 0.984 | 0.014s |
| **SALSA** | 483.6 [396.8, 570.3] | **33.3%** [22.2%, 46.3%] | 35.2% [24.1%, 48.1%] | 0.959 [0.947, 0.972] | 0.969 [0.958, 0.980] | 0.955 | 0.017s |
| **In-Degree** | 437.6 [326.0, 551.2] | **33.3%** [22.2%, 46.3%] | 42.6% [29.6%, 55.6%] | 0.952 [0.940, 0.965] | 0.968 [0.957, 0.979] | 0.997 | 0.010s |

### Clean Baseline Computational Efficiency & Peak Memory

| Dataset / Graph | Nodes | Edges | HITS Time | PR Time | SALSA Time | Peak RAM (MB) | Eigengap $\sigma_1^2 - \sigma_2^2$ |
|---|---|---|---|---|---|---|---|
| **Synthetic BA-1000** | 1,000 | 4,369 | 0.045s (42 it) | 0.013s (26 it) | 0.016s (57 it) | 0.85 MB | 45.41 |
| **Synthetic ER-1000** | 1,000 | 4,973 | 0.080s (39 it) | 0.013s (22 it) | 0.014s (34 it) | 0.82 MB | 14.44 |
| **Planted SBM-840** | 840 | 2,971 | 0.023s (11 it) | 0.010s (28 it) | 0.017s (125 it) | 0.50 MB | 275.51 |
| **SNAP wiki-Vote** | 7,115 | 103,689 | 0.657s (23 it) | 0.580s (23 it) | 0.643s (53 it) | 18.17 MB | 6,158.51 |
| **SNAP web-Stanford BaseSet** | 1,686 | 13,849 | 0.110s (23 it) | 0.155s (81 it) | 0.114s (200 it) | 2.45 MB | 2,518.81 |

*Hardware Used:* 12th Gen Intel Core i5-12500H (12 physical cores, 16 logical processors), 16 GB RAM, Windows 11 64-bit, Python 3.12.5, SciPy 1.12.0 sparse linear algebra. Peak memory measured via Python heap tracemalloc (0.50 - 18.17 MB) and process RSS via psutil (108 - 183 MB).

---

## 6. Hypothesis Status

### Hypothesis H1: "On random-like graphs HITS ~ in-degree"
- **Status: SUPPORTED (Preliminary).**
- **Evidence:** On Erdos-Renyi graphs ($G(1000, 0.005)$), Kendall's rank correlation between clean HITS authority scores and simple in-degree is $\tau = 0.746$ ($p = 7.99 \times 10^{-244}$; Spearman $\rho = 0.887$). In contrast, on heavy-tailed scale-free graphs (Barabasi-Albert, BA-1000), $\tau$ drops to $0.515$ ($p = 2.50 \times 10^{-115}$; Spearman $\rho = 0.692$), and on planted community SBM graphs $\tau = 0.533$ ($p = 1.39 \times 10^{-103}$), confirming that HITS authority aligns closely with in-degree on homogeneous random graphs but diverges on heavy-tailed graphs with dense local communities. (Note: Progress Report v1 erroneously cited $\tau=0.912$ due to an uncorrected row transposition).
- **Limits:** In sparse disconnected graphs, nodes with identical in-degree receive distinct HITS scores depending on whether their in-neighbors link to other high-degree nodes.

### Hypothesis H2: "Hub farm of $p$ fake hubs only takes over top HITS vectors when $p \sim \sigma_1^2$ (sharp jump; PageRank gains smooth)"
- **Status: STRONGLY SUPPORTED.**
- **Evidence:** Evaluated on a 300-node network with clean dominant singular value $\sigma_1 = 7.279$ ($\sigma_1^2 = 52.98$):
  - At $p = 26$ ($p / \sigma_1^2 = 0.49$): Target HITS rank is $218 / 300$, authority score $= 0.0008$ (completely suppressed).
  - At $p = 52$ ($p / \sigma_1^2 = 0.98 \approx 1$): Target HITS rank jumps abruptly from $218 \to 1$, with authority score surging from $0.0008 \to 0.0955$, and at $p=79$ reaching $0.8996$ ($90\%$ of total network authority mass).
  - In contrast, PageRank rank advances smoothly ($235 \to 6 \to 1$) with strictly linear score accumulation ($\Delta PR \propto p \cdot \frac{\alpha(1-\alpha)}{N}$).
  - Across the cost curve experiments: at $B=25$, HITS Top-10 entry is $0.0\%$; at $B=100$, it leaps to $50.0\%$ with catastrophic top-20 Jaccard collapse ($0.989 \to 0.694$).
- **Limits:** Tested on synthetic scale-free and SNAP base sets. Validation on the full web-Stanford network will establish exact scaling of $\sigma_1^2$ with graph diameter.

### Hypothesis H3: "On graphs with dense communities, attaching to the community (TKC) is cheaper"
- **Status: SUPPORTED.**
- **Evidence:** Comparing attack A4 (Hub Inflation, linking to $c=3$ top community authorities) against A2 (pure isolated hub farm):
  - Under A4, reaching Top-10 required an edge budget of only $B = 25$ ($100\%$ entry rate under inflation).
  - Under A2 (pure farm), reaching Top-10 required $B \ge 75$ edges to eclipse the background $\sigma_1^2$.
  - Attaching to existing legitimate authorities borrows pre-existing community hub mass, reducing the required budget by $\approx 67\%$.
- **Limits:** Depends on the attacker having knowledge of legitimate top authorities in the base set.

### Hypothesis H4: "Damped/capped/trust-based HITS cuts attack success with little clean-graph damage"
- **Status: PARTIALLY SUPPORTED (with critical nuances).**
- **Evidence:**
  - **D4 (Wu-Davison Link-Farm Reweighting):** Outstanding performance. Achieved **$100\%$ attack success reduction** against hub farm and inflation attacks (target gain cut to 0, completely unpromoted), while maintaining **$0.0$ false demotion** on clean graphs (Clean Top-20 Jaccard $= 1.0000$, NDCG $= 1.0000$).
  - **D1 (Randomized HITS, $\epsilon=0.15$):** Maintains high clean fidelity (Jaccard $= 0.9048$, NDCG $= 0.9994$), but the uniform reset diffuses probability mass proportionally to in-degree, behaving more like PageRank and remaining susceptible to high-degree brute-force injection.
  - **D1 (Subspace HITS, $k=5$):** Prevents dominant takeover in higher dimensions, but introduces moderate clean distortion (Clean Jaccard $= 0.4815$, NDCG $= 0.9311$).
  - **D5 (Trust-Based HITS):** Reduces attack gain by $20.7\% - 26.5\%$ on inflation attacks, but requires trusted seed identification.

---

## 7. Problems Encountered and Deviations

1. **WEBSPAM-UK2006 Hostgraph Bitstream Compression:**
   - *Issue:* The host labels (`webspam-uk2006-set1-labels.txt`) were successfully downloaded and parsed. However, the host link graph is stored in WebGraph bitstream format (`.graph` / `.properties`) hosted on University of Milan LAW servers, requiring Java WebGraph libraries (`BV2Ascii.java`) or Google Drive authentication.
   - *Deviation:* To keep mid-project experiments 100% offline and runnable on a laptop, we ran all mid-term experiments on three real SNAP web graphs (`wiki-Vote`, `web-Stanford`, `web-NotreDame`) and synthetic benchmarks.
2. **SALSA Convergence on Multi-Component Base Sets:**
   - *Issue:* In disconnected bipartite components, pure SALSA transition matrices contain multiple unit eigenvalues, causing standard power iteration to oscillate or stall without convergence (as observed on `web-Stanford` where it hit max iterations 200).
   - *Solution:* Implemented an ergodic teleport parameter ($\epsilon = 10^{-4}$) in [`src/rankers/salsa.py`](../src/rankers/salsa.py), guaranteeing strict positive Perron-Frobenius convergence.
3. **Power Iteration Metric Bounds with Injected Nodes:**
   - *Issue:* Standard NDCG and Jaccard functions failed when computing metrics between clean vectors of length $N$ and attacked vectors of length $N + k_{fake}$.
   - *Solution:* Updated [`src/eval/metrics.py`](../src/eval/metrics.py) to assign zero ground-truth relevance to injected attacker nodes.

---

## 8. Path to Final Submission
- **Milestone 1 (25 Oct 2026):** Complete WEBSPAM-UK2006 hostgraph ASCII extraction using Java BVGraph pipeline; compute baseline spam@k and AUC on full hostgraph.
- **Milestone 2 (1 Nov 2026):** Execute complete experimental matrix across all 6 attacks (A1-A6) and 5 defenses (D1-D5) on web-NotreDame and WEBSPAM.
- **Milestone 3 (8 Nov 2026):** **EXPERIMENTS FREEZE.** Lock all raw CSVs, regenerate final 300 DPI figures, and conduct final Wilcoxon hypothesis tests.
- **Milestone 4 (15 Nov 2026):** Final Report and Slide Deck submission.

### Status of Stretch Objectives:
1. **Game-Theoretic Attacker-Defender Loop:** *Pending.* (Code scaffold planned for 30 Oct).
2. **Closed-Form Spectral Robustness Bound:** *In Progress.* (Theoretical proof verifying minimal budget $B^*(k)$ as a function of the second singular value $\sigma_2$).
3. **WEBSPAM-UK2007 Multi-Feature Classifier:** *Pending.* (Dependent on Milestone 1 data pipeline).

---

## 9. Contribution Matrix Draft (Tentative - CONFIRM WITH TEAM)

| Member | Assigned Area | Components Completed for Mid-Project Checkpoint | Status |
|---|---|---|---|
| **Shrisay Shandilya** | Rankers, Data Loaders, Base-Set Pipeline | Built sparse power iteration HITS, PageRank, SALSA, and In-degree rankers; created SNAP loader, WEBSPAM label loader with undecided handling, Kleinberg base-set builder, and clean baseline evaluation script. | **CONFIRM WITH TEAM** |
| **Vibhor Rathi** | Adversarial Link Injection Attacks | Implemented threat model and attacks A1 (Single Hub), A2 (Hub Farm), A3 (Bipartite Block), A4 (Hub Inflation), A5 (Cross-Score), and A6 (Greedy Gradient with candidate re-verification); built validation suite. | **CONFIRM WITH TEAM** |
| **Prachi Jain** | Defenses, Evaluation Metrics, and Statistical Suite | Implemented defenses D1 (Randomized/Subspace), D2 (Bharat-Henzinger), D3 (Hub Capping), D4 (Wu-Davison), D5 (Trust HITS); implemented bootstrap 95% CIs and Wilcoxon testing suite; ran defense evaluation and figure generation. | **CONFIRM WITH TEAM** |

---

## 10. Reproduction Commands & Deliverable Manifest

### Exact Reproduction Commands
From the repository root (`c:\Users\shris\OneDrive\Desktop\LinkRank_Under_Attack`):

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run automated test suite (all 16 tests must pass)
python -m pytest tests/ -v

# 3. Download SNAP web datasets and WEBSPAM-UK2006 labels
python scripts/download_data.py

# 4. Run clean baselines evaluation across synthetic and real SNAP graphs
python scripts/run_clean_baselines.py

# 5. Run attack cost curves experiment (generates 1,512 experimental trials)
python scripts/run_cost_curves.py

# 6. Run Hypothesis H2 spectral takeover experiment
python scripts/run_h2_experiment.py

# 7. Run defense evaluation experiment (D1-D5 under fixed budget)
python scripts/run_defenses.py

# 8. Generate all publication figures (300 DPI) and system architecture diagram
python scripts/generate_figures.py
```

### Manifest of Generated Artifacts for the 4-Page PDF

#### Figures (`figures/`)
- [`figures/cost_curves_rank_gain.png`](../figures/cost_curves_rank_gain.png): 300 DPI dual-panel chart of Target Rank Gain vs Attacker Budget on Synthetic BA-500 and SNAP wiki-Vote base set across HITS, PageRank, SALSA, and In-degree.
- [`figures/h2_spectral_takeover.png`](../figures/h2_spectral_takeover.png): 300 DPI dual-panel chart of Target Authority and Target Rank vs Farm Size $p$, with the theoretical threshold $\sigma_1^2$ annotated illustrating the abrupt bifurcation of HITS vs smooth PageRank.
- [`figures/defenses_tradeoff.png`](../figures/defenses_tradeoff.png): 300 DPI Pareto plot showing Attack Success Reduction (%) vs Clean Graph False Demotion across defenses D1-D5.
- [`figures/architecture.png`](../figures/architecture.png) and [`figures/architecture.svg`](../figures/architecture.svg): End-to-end system architecture diagram clearly highlighting BUILT vs PENDING components.

#### Raw Data Tables (`results/`)
- [`results/clean_baselines.csv`](../results/clean_baselines.csv): Runtime, peak memory, iterations, and eigengap across 5 benchmark graphs.
- [`results/cost_curves.csv`](../results/cost_curves.csv): Complete 1,512-row dataset with ranks, gains, amplifications, Jaccard, NDCG, and Kendall tau.
- [`results/h2_experiment.csv`](../results/h2_experiment.csv): Step-by-step spectral takeover measurements around $p \approx \sigma_1^2$.
- [`results/defenses_eval.csv`](../results/defenses_eval.csv): Attack reduction and false demotion scores for D1-D5.
