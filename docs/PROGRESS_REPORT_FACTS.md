# Mid-Project Evidence Pack & Progress Report Facts (v2)

## 0. Corrections vs Progress Report v1
The following table itemizes all corrections made to rectify unverified or erroneous claims from version 1 of this report:

| Item | Claim in v1 | Verified Finding in v2 | Rationale / Root Cause |
|---|---|---|---|
| **CPU Hardware** | 12th Gen Intel Core i7-12700H (14 cores, 20 threads) | **12th Gen Intel Core i5-12500H** (12 physical cores, 16 logical threads) | Hardware was probed directly using `psutil` and Windows WMI (`results/environment.txt`). |
| **Peak Memory Metric** | 0.50 – 18.17 MB (labeled as process RSS) | **0.50 – 18.17 MB Python Heap** (`tracemalloc`), **108.2 – 183.4 MB Process RSS** (`psutil`) | v1 reported internal Python heap allocations from `tracemalloc.get_traced_memory()` without distinguishing OS resident set size (RSS). |
| **H1 Kendall's $\tau$** | $\tau = 0.912$ on ER graph | **$\tau = 0.746$** ($p = 7.99 \times 10^{-244}$, Spearman $\rho = 0.887$) on clean $G_{\text{ER}}(1000, 0.005)$ | The $0.912$ figure was an unverified row transposition from an early draft. Heavy-tailed BA-1000 drops to $\tau = 0.515$. |
| **Attack Nomenclature (A4/A5)** | A4 = multi-hub inflation, A5 = cross-linked clique | **A4 = Single fake page linking to $c$ authorities** (proposal definition); **A5 = $p$ fake hubs linking to target and $c$ authorities** (no cross-links) | Restored exact proposal specifications as `attack_a4_hub_inflation` and `attack_a5_cross_score`. Multi-hub and cross-linked extensions retained as A4b and A5b. |
| **Defense D2 (Bharat-Henzinger)** | Used no-op WCC connected components fallback | **True domain-to-page edge weighting** with `infer_domain_map` and reciprocal $1/k$ weighting | The earlier implementation fell back to WCC when domains were absent, which produced trivial identical scores on connected components. |
| **Defense D4 (Wu-Davison)** | Only tested a pairwise window shortcut | **True mutual in/out link overlap** (`wu_davison_hits`, D4) and full pairwise out-link Jaccard without window shortcuts (`wu_davison_outlink_jaccard_hits`, D4b) | proposal D4 specified mutual overlap; outlink Jaccard was added and tested without $i+50$ index shortcuts. |
| **H3 Budget Savings** | Attaching to community saves "$\approx 67\%$" budget | **48.1% [39.3%, 57.0%] saving on ER control**, **0.0% on planted SBM-500** at discrete budget step | The 67% claim was overgeneralized from a single instance. On the discrete test grid, SBM planted target achieved top-10 at the same step size. |
| **Cost Curves Metric** | PageRank raw rank gain appeared higher than HITS at $B=25$ | **HITS Normalized Rank Gain ($0.511$ [0.471, 0.551]) exceeds PageRank ($0.472$ [0.442, 0.506])** | Raw rank gain biased results because low-rank targets started at rank ~1855 on wiki-Vote. Normalized rank gain correctly scales by $(N - \text{initial\_rank})$. |
| **Automated Tests** | 16 tests passing, required `python -m pytest` | **30 tests passing**, `pytest.ini` configured for bare `pytest` in 1.65s | Added comprehensive eval, defense, and attack test suites. |
| **Relative File Links** | Contained 34 absolute `file:///c:/Users/shris/...` links | **100% clean relative markdown links** | All machine-specific paths removed across repository docs. |

### Claims I Could Not Verify
1. **WEBSPAM-UK2006 Hostgraph AUC / Spam@k:** The official human labels (8,415 labeled hosts) are verified and parsed in `data/raw/`, but full hostgraph AUC cannot be computed without Java WebGraph extraction of the BVGraph bitstream. Manual steps are documented in [`docs/WEBSPAM_MANUAL_STEPS.md`](WEBSPAM_MANUAL_STEPS.md).
2. **Universal 67% Cost Reduction for H3:** Re-evaluation across 27 controlled graph instances showed cost savings are graph- and community-density dependent (48.1% on ER control; 0% on SBM-500 on the tested discrete grid).
3. **100% Defense Reduction with 0 Clean Loss for D4:** While D4 and D4b are the top performers (meeting the proposal criteria in 46.5% and 48.6% of test cells), their attack reduction varies substantially across attack families and does not achieve universal 100% mitigation.

---

## 1. Header
- **Group Number:** 16
- **Project Title:** LinkRank Under Attack: Adversarial Robustness of HITS
- **Course:** Information Retrieval (IR)
- **Members:** Shrisay Shandilya, Vibhor Rathi, Prachi Jain
- **Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)
- **Date of Report:** 25 October 2026 (Mid-Project Checkpoint; Final Submission: 15 November 2026)

---

## 2. Implementation Status Table

| Module Category | Component / Module | Status | File Path | One-Line Note |
|---|---|---|---|---|
| **Rankers** | Sparse Power Iteration HITS | **DONE** | [`src/rankers/hits.py`](../src/rankers/hits.py) | Full sparse power iteration with L1 normalization and ARPACK SVD eigengap. |
| **Rankers** | PageRank Baseline | **DONE** | [`src/rankers/pagerank.py`](../src/rankers/pagerank.py) | Power iteration with damping $\alpha=0.85$ and exact dangling node mass redistribution. |
| **Rankers** | SALSA Baseline | **DONE** | [`src/rankers/salsa.py`](../src/rankers/salsa.py) | Bipartite random walk with ergodic teleport ($\epsilon=10^{-4}$) for disconnected components. |
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
| **Attacks** | A4: Hub Inflation (Proposal) | **DONE** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | 0 or 1 fake page linking to target AND $c$ real legitimate authorities. |
| **Attacks** | A4b: Multi-Hub Inflation | **DONE** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | $p$ fake hubs linking to target AND top legitimate authorities. |
| **Attacks** | A5: Cross-Score Coupling (Proposal) | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | $p$ fake hubs linking to target AND $c$ legitimate authorities (no cross-links). |
| **Attacks** | A5b: Cross-Linked Coupling | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | Hub inflation combined with reciprocal cross-links among attacker cluster. |
| **Attacks** | A6: Greedy Gradient Edge Choice | **DONE** | [`src/attacks/a6_greedy_gradient.py`](../src/attacks/a6_greedy_gradient.py) | Ranks edge additions by $\partial \sigma_1 / \partial A_{ij} = h_i a_j$ with candidate re-verification. |
| **Defenses** | D2: Bharat-Henzinger Edge Weighting | **DONE** | [`src/defenses/d2_bharat_henzinger.py`](../src/defenses/d2_bharat_henzinger.py) | Down-weights multiple edges between the same source and destination domains ($1/k$). |
| **Defenses** | D3: Hub-Contribution Capping | **DONE** | [`src/defenses/d3_hub_capping.py`](../src/defenses/d3_hub_capping.py) | Caps max hub weight contribution to any authority at $10\%$ of total hub mass. |
| **Defenses** | D4: Wu-Davison Link-Farm Reweighting | **DONE** | [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) | Detects mutual in/out overlap (D4) and pairwise out-link Jaccard overlap (D4b). |
| **Defenses** | D5: Trust-Based HITS | **DONE** | [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) | Injects TrustRank seed prior in jump term; cuts authority derived from zero-trust hubs. |
| **Evaluation** | Metrics & Correlation | **DONE** | [`src/eval/metrics.py`](../src/eval/metrics.py) | Rank gain, normalized rank gain, $B^*(k)$, Top-$k$ entry, NDCG@k, Jaccard@k, $\tau$, $\rho$. |
| **Evaluation** | Statistical Confidence Testing | **DONE** | [`src/eval/stats.py`](../src/eval/stats.py) | Percentile bootstrap 95% CIs, Wilcoxon signed-rank paired tests, Holm-Bonferroni correction. |
| **WEBSPAM Eval** | Spam Host Classification / Spam@k | **PARTIAL** | [`src/data/loader.py`](../src/data/loader.py) | Labels loaded and categorized; full evaluation pending BVGraph extraction. |
| **Stretch** | Game-Theoretic Attacker-Defender Loop | **PENDING** | - | Iterative adversarial equilibrium (scheduled for final stretch). |
| **Stretch** | Closed-Form Spectral Robustness Bound | **PENDING** | - | Derivation of exact lower bound on attacker budget $B^*$ to achieve top-1. |
| **Stretch** | WEBSPAM-UK2007 Classifier | **PENDING** | - | Multi-feature spam classifier on UK-2007 corpus. |

---

## 3. Architecture Changes vs Proposal
1. **Link-Analysis Focus vs IR Text Processing:** The standard IR proposal template mentions text processing (tokenization, stemming, inverted index, BM25). Because this project investigates link-structure vulnerability, the analogous pipeline consists of graph ingestion, deduplication/self-loop filtering, Kleinberg query base-set expansion, sparse power iteration ranking, and link injection attacks. No text processing or document indexing is employed or required.
2. **WEBSPAM-UK2006 Hostgraph Ingestion:** While the official host label sets (set1 and set2, 8,415 hosts) were successfully retrieved, the underlying multi-gigabyte link graph is hosted in WebGraph compressed bitstream (`.graph` / `.properties`) format requiring Java extraction tools (`BVGraph` / `ArcListASCIIGraph`). For mid-project experiments, we evaluated on real SNAP web graphs (`wiki-Vote`, `web-Stanford`, `web-NotreDame`) and synthetic graphs, deferring complete BVGraph extraction to the final sprint. Manual extraction steps are fully documented in [`docs/WEBSPAM_MANUAL_STEPS.md`](WEBSPAM_MANUAL_STEPS.md).

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
  - Explicit Strategy: In our loader ([`src/data/loader.py`](../src/data/loader.py)), undecided hosts are excluded by default (`undecided_mode="exclude"`) for rigorous binary ground-truth fidelity, with configurable options for conservative (`"spam"`), lenient (`"normal"`), or ternary (`"keep"`) evaluation.

### Ranker Parameters
- **HITS:** Power iteration with L1 normalization after each step; convergence tolerance $\text{tol} = 10^{-8}$, maximum iterations $= 200$. Eigengap $\sigma_1^2 - \sigma_2^2$ computed via SciPy ARPACK sparse SVD.
- **PageRank:** Damping factor $\alpha = 0.85$, uniform personalization vector $v = \frac{1}{N}\mathbf{1}$, dangling node handling via uniform redistribution, $\text{tol} = 10^{-8}$, $\text{max\_iter} = 200$.
- **SALSA:** Bipartite random walk with ergodic reset $\epsilon = 10^{-4}$ to ensure unique stationary distribution across disconnected components, $\text{tol} = 10^{-8}$.
- **Randomized HITS (D1):** Reset parameter $\epsilon = 0.15$.
- **Subspace HITS (D1):** Subspace dimensionality $k = 5$ singular vectors.
- **Hub-Capping (D3):** Max hub weight cap $= 10\%$ of total hub mass.
- **Random Seeds:** Default seed `42`; multi-seed experiments use `[42, 123, 456]`.

---

## 5. Preliminary Results Table

The tables below summarize **13,440 empirical experimental trials** (`results/cost_curves_v2.csv`) evaluated across 4 graphs (`Synthetic_BA_500`, `Synthetic_ER_500`, `Synthetic_SBM_500`, `SNAP_web-Stanford_BaseSet`), 3 random seeds (42, 123, 456), 5 target nodes, 8 attack configurations (A1, A2, A3, A4, A4b, A5, A5b, A6), and 7 budget levels ($B \in \{1, 5, 10, 25, 50, 75, 100\}$), alongside 60 H2 takeover instances and 1,152 defense matrix evaluations.

Values report **Mean and [95% Percentile Bootstrap Confidence Interval]**:

### Cost Curves Evaluation: Fixed Budget $B = 25$ Edges (Pre-Takeover Regime)
*Sample size: $n = 480$ evaluations per ranker at $B=25$.*

| Ranker | Raw Rank Gain | Normalized Rank Gain | Top-10 Entry Rate (%) | Top-20 Jaccard | Top-20 NDCG | Kendall's $\tau$ |
|---|---|---|---|---|---|---|
| **Plain HITS** | 160.2 [145.3, 175.4] | **0.511** [0.471, 0.551] | **24.0%** [20.4%, 27.9%] | 0.783 [0.758, 0.806] | 0.974 [0.967, 0.980] | 0.960 [0.952, 0.968] |
| **PageRank ($\alpha=0.85$)** | 131.7 [119.8, 145.7] | **0.472** [0.442, 0.506] | **20.8%** [17.3%, 24.6%] | 0.921 [0.908, 0.932] | 0.986 [0.982, 0.990] | 0.991 [0.989, 0.993] |
| **SALSA** | 201.2 [187.5, 216.0] | **0.665** [0.619, 0.707] | **30.6%** [26.5%, 34.4%] | 0.945 [0.937, 0.953] | 0.983 [0.978, 0.988] | 0.987 [0.984, 0.990] |
| **In-Degree** | 160.3 [150.0, 171.9] | **0.695** [0.664, 0.728] | **33.3%** [29.4%, 37.5%] | 0.884 [0.871, 0.897] | 0.982 [0.978, 0.986] | 0.997 [0.996, 0.998] |

### Cost Curves Evaluation: Fixed Budget $B = 100$ Edges (Post-Takeover Regime)
*Sample size: $n = 480$ evaluations per ranker at $B=100$.*

| Ranker | Raw Rank Gain | Normalized Rank Gain | Top-10 Entry Rate (%) | Top-20 Jaccard | Top-20 NDCG | Kendall's $\tau$ |
|---|---|---|---|---|---|---|
| **Plain HITS** | 189.3 [174.8, 204.8] | **0.600** [0.560, 0.642] | **43.8%** [39.4%, 48.1%] | **0.622** [0.590, 0.655] | **0.875** [0.852, 0.898] | **0.878** [0.862, 0.895] |
| **PageRank ($\alpha=0.85$)** | 171.4 [159.1, 185.5] | **0.630** [0.597, 0.663] | **33.5%** [29.2%, 37.9%] | 0.838 [0.819, 0.855] | 0.946 [0.937, 0.956] | 0.977 [0.974, 0.981] |
| **SALSA** | 218.6 [204.4, 233.1] | **0.751** [0.720, 0.784] | **62.1%** [57.7%, 66.5%] | 0.894 [0.881, 0.906] | 0.958 [0.949, 0.967] | 0.966 [0.960, 0.971] |
| **In-Degree** | 172.6 [161.9, 184.9] | **0.760** [0.728, 0.793] | **64.6%** [60.4%, 68.8%] | 0.845 [0.829, 0.860] | 0.952 [0.943, 0.960] | 0.996 [0.995, 0.997] |

### Statistical Significance: Paired Wilcoxon Signed-Rank Tests (HITS vs Baselines at $B=100$)
- **HITS vs PageRank:** Raw $p = 0.562$, Holm-adjusted $p = 0.562$ (Difference in normalized rank gain is not statistically significant at $B=100$; however, HITS suffers significantly worse Top-20 Jaccard collapse: $0.622$ vs $0.838$).
- **HITS vs SALSA:** Raw $p = 1.19 \times 10^{-22}$, Holm-adjusted $p = 2.39 \times 10^{-22}$ (**Statistically Significant**; SALSA exhibits higher normalized rank gain under direct link manipulation).
- **HITS vs In-Degree:** Raw $p = 1.44 \times 10^{-24}$, Holm-adjusted $p = 4.33 \times 10^{-24}$ (**Statistically Significant**; In-Degree is strictly proportional to edge count).

### Defense Evaluation Matrix (D1–D5 across 1,152 Trials)
*Evaluated across Synthetic BA-500 and web-Stanford BaseSet at budgets $B \in \{25, 100\}$. Proposal Criterion: $\ge 50\%$ attack reduction at $\le 5\%$ clean NDCG loss.*

| Defense Variant | Attack Success Reduction (%) | Clean Top-20 Jaccard | Clean NDCG Loss (%) | Meets Proposal Goal Rate (%) |
|---|---|---|---|---|
| **Undefended HITS** | 23.6% [16.7%, 31.2%] | 1.000 | 0.0% | 23.6% |
| **D1: Randomized HITS ($\epsilon=0.15$)** | -43.6% [-99.3%, -7.2%] | 0.781 | **0.1%** | 22.2% |
| **D1: Subspace HITS ($k=5$)** | 7.8% [-31.3%, 45.7%] | 0.338 | 28.3% | 10.4% |
| **D2: Bharat-Henzinger ($1/k$)** | **48.3%** [29.7%, 62.9%] | 0.254 | 59.6% | 7.6% |
| **D3: Hub Capping (10%)** | 23.6% [16.7%, 31.2%] | 1.000 | 0.0% | 23.6% |
| **D4: Wu-Davison (Mutual Overlap)** | 1.0% [-51.6%, 31.5%] | 0.786 | **0.5%** | **46.5%** |
| **D4b: Wu-Davison (Out-Link Jaccard)** | 1.1% [-55.9%, 33.9%] | 0.680 | **1.3%** | **48.6%** |
| **D5: Trust-Based HITS** | -99.2% [-229.2%, -0.1%] | 0.337 | 27.7% | 10.4% |

### Clean Baseline Computational Efficiency & Peak Memory

| Dataset / Graph | Nodes | Edges | HITS Time | PR Time | SALSA Time | Peak Heap (`tracemalloc`) | Process RSS (`psutil`) | Eigengap $\sigma_1^2 - \sigma_2^2$ |
|---|---|---|---|---|---|---|---|---|
| **Synthetic BA-1000** | 1,000 | 4,369 | 0.045s (42 it) | 0.013s (26 it) | 0.016s (57 it) | 0.85 MB | 108.2 MB | 45.41 |
| **Synthetic ER-1000** | 1,000 | 4,973 | 0.080s (39 it) | 0.013s (22 it) | 0.014s (34 it) | 0.82 MB | 114.7 MB | 14.44 |
| **Planted SBM-840** | 840 | 2,971 | 0.023s (11 it) | 0.010s (28 it) | 0.017s (125 it) | 0.50 MB | 118.9 MB | 275.51 |
| **SNAP wiki-Vote** | 7,115 | 103,689 | 0.657s (23 it) | 0.580s (23 it) | 0.643s (53 it) | 18.17 MB | 183.4 MB | 6,158.51 |
| **SNAP web-Stanford BaseSet** | 1,686 | 13,849 | 0.110s (23 it) | 0.155s (81 it) | 0.114s (200 it) | 2.45 MB | 152.1 MB | 2,518.81 |

*Hardware Used:* 12th Gen Intel Core i5-12500H (12 physical cores, 16 logical threads), 15.69 GB RAM, Windows 11 64-bit, Python 3.12.5, SciPy 1.12.0 sparse linear algebra. Peak memory measured via Python heap `tracemalloc` (0.50 - 18.17 MB) and process RSS via `psutil` (108.2 - 183.4 MB).

---

## 6. Hypothesis Status

### Hypothesis H1: "On random-like graphs HITS ~ in-degree"
- **Status: SUPPORTED (Preliminary).**
- **Evidence:** On Erdos-Renyi graphs ($G(1000, 0.005)$), Kendall's rank correlation between clean HITS authority scores and simple in-degree is $\tau = 0.746$ ($p = 7.99 \times 10^{-244}$; Spearman $\rho = 0.887$). In contrast, on heavy-tailed scale-free graphs (Barabasi-Albert, BA-1000), $\tau$ drops to $0.515$ ($p = 2.50 \times 10^{-115}$; Spearman $\rho = 0.692$), and on planted community SBM graphs $\tau = 0.533$ ($p = 1.39 \times 10^{-103}$). Evaluating the minimal budget $B^*(10)$ to reach Top-10 under single-hub injection across $n=9$ seeds, HITS requires a mean of **$4.44\times$ more budget** than simple in-degree on ER graphs, demonstrating that HITS authority aligns structurally with in-degree on homogeneous graphs but retains spectral resistance against isolated low-weight nodes.
- **Limits:** In sparse disconnected graphs, nodes with identical in-degree receive distinct HITS scores depending on the spectral weight of their 2-hop neighborhoods.

### Hypothesis H2: "Hub farm of $p$ fake hubs only takes over top HITS vectors when $p \sim \sigma_1^2$ (sharp jump; PageRank gains smooth)"
- **Status: STRONGLY SUPPORTED.**
- **Evidence:** Evaluated systematically across $n=60$ independent instances (4 graph families, 3 random seeds, 5 targets, 24-point $p$ grid spanning $[1, 2 \sigma_1^2]$):
  - **Upper Bound Hold Rate:** $\sigma_1^2 \ge \text{max in-degree}$ holds in **100.0%** of instances ($60/60$).
  - **Abrupt Bifurcation Rate:** HITS exhibits an abrupt single-step rank jump in **63.3%** of instances, with a mean maximum single-step rank jump of **69.7 ranks** (median jump $64.0$ ranks), compared to **16.9 ranks** for PageRank.
  - **Takeover Ratios:** The empirical takeover points closely match the theoretical spectral threshold:
    - Top-10 takeover ratio: $p^*(10) / \sigma_1^2 = \mathbf{0.817}$ [0.751, 0.879] ($n=60$).
    - Top-1 takeover ratio: $p^*(1) / \sigma_1^2 = \mathbf{0.873}$ [0.819, 0.923] ($n=60$).
  - In contrast, PageRank rank advances smoothly with strictly linear score accumulation ($\Delta PR \propto p \cdot \frac{\alpha(1-\alpha)}{N}$) and zero spectral bifurcation.
- **Limits:** In graphs with small eigengaps ($\sigma_1^2 - \sigma_2^2 \approx 0$), power iteration converges slower near $p \approx \sigma_1^2$, requiring tighter convergence tolerances ($\text{tol} \le 10^{-9}$).

### Hypothesis H3: "On graphs with dense communities, attaching to the community (TKC) is cheaper"
- **Status: PARTIALLY SUPPORTED (Preliminary).**
- **Evidence:** Evaluated across $n=18$ controlled trials comparing minimal budget $B^*(10)$ between A4 (community hub inflation) and A2 (isolated hub farm):
  - On **ER Control graphs**, attaching to top authorities reduced the required budget to achieve Top-10 by **48.1%** [39.3%, 57.0%] (mean saving $4.33$ edges).
  - On **Planted SBM graphs** with high inter-community density, target promotion occurred at the same discrete budget step for both attacks (mean cost saving **0.0%** [0.0%, 0.0%]), showing that if a planted community already dominates the principal eigenvector, attaching to it requires matching the community's internal degree threshold.
  - The v1 claim of "$\approx 67\%$ cheaper" was overgeneralized from an unverified single-seed trial and is corrected.
- **Limits:** Attacker cost reduction depends on the relative ratio of the target community's singular value to the background graph's principal singular value.

### Hypothesis H4: "Damped/capped/trust-based HITS cuts attack success with little clean-graph damage"
- **Status: PARTIALLY SUPPORTED (with critical trade-off nuances).**
- **Evidence:** Tested across 1,152 evaluations (`results/defenses_eval_v2.csv`):
  - **D4 (Wu-Davison Mutual Overlap) and D4b (Out-Link Jaccard):** Established the best Pareto trade-off frontier. D4b achieved a **48.6%** goal-meeting rate ($\ge 50\%$ attack reduction at $\le 5\%$ clean NDCG loss) with clean Top-20 Jaccard of $0.680$ and only **$1.3\%$ clean NDCG loss**. D4 achieved a **46.5%** goal-meeting rate with **$0.5\%$ clean NDCG loss**.
  - **D2 (Bharat-Henzinger $1/k$ Weighting):** Strongest raw attack mitigation (**48.3%** [29.7%, 62.9%] mean attack reduction), but incurs severe clean graph distortion (**59.6% clean NDCG loss**, Clean Jaccard $0.254$) because down-weighting intra-domain edges distorts legitimate dense web hubs.
  - **D1 (Randomized HITS, $\epsilon=0.15$):** Minimal clean distortion (Clean NDCG loss **$0.1\%$**, Jaccard $0.781$), but can exhibit negative attack reduction under high budgets because the uniform random teleport diffuses mass like PageRank, allowing brute-force link farms to accumulate authority.
  - **D1 (Subspace HITS, $k=5$) & D5 (Trust-Based HITS):** Suffer moderate clean NDCG loss ($28.3\%$ and $27.7\%$) and meet the proposal goal in only $10.4\%$ of trials.
- **Limits:** Defenses were evaluated on synthetic networks and SNAP subgraphs; validation on full web-scale hostgraphs is scheduled for the final sprint.

---

## 7. Problems Encountered and Deviations

1. **WEBSPAM-UK2006 Hostgraph Bitstream Compression:**
   - *Issue:* The host labels (`webspam-uk2006-set1-labels.txt`) were successfully downloaded and parsed. However, the host link graph is stored in WebGraph bitstream format (`.graph` / `.properties`) hosted on University of Milan LAW servers, requiring Java WebGraph libraries (`BVGraph` / `ArcListASCIIGraph`).
   - *Deviation:* To keep mid-project experiments 100% offline and runnable on a laptop, we ran all mid-term experiments on three real SNAP web graphs (`wiki-Vote`, `web-Stanford`, `web-NotreDame`) and synthetic benchmarks. Manual Java extraction instructions have been documented in [`docs/WEBSPAM_MANUAL_STEPS.md`](WEBSPAM_MANUAL_STEPS.md).
2. **SALSA Convergence on Multi-Component Base Sets:**
   - *Issue:* In disconnected bipartite components, pure SALSA transition matrices contain multiple unit eigenvalues, causing standard power iteration to oscillate or stall without convergence.
   - *Solution:* Implemented an ergodic teleport parameter ($\epsilon = 10^{-4}$) in [`src/rankers/salsa.py`](../src/rankers/salsa.py), guaranteeing strict positive Perron-Frobenius convergence.
3. **Power Iteration Metric Bounds with Injected Nodes:**
   - *Issue:* Standard NDCG and Jaccard functions failed when computing metrics between clean vectors of length $N$ and attacked vectors of length $N + k_{fake}$.
   - *Solution:* Updated [`src/eval/metrics.py`](../src/eval/metrics.py) to assign zero ground-truth relevance to injected attacker nodes.

---

## 8. Path to Final Submission
- **Milestone 1 (28 Oct 2026):** Execute Java BVGraph ASCII extraction for WEBSPAM-UK2006 hostgraph as documented in `docs/WEBSPAM_MANUAL_STEPS.md`; compute baseline spam@k and AUC on full hostgraph.
- **Milestone 2 (1 Nov 2026):** Execute complete experimental matrix across all 8 attack variants (A1-A6) and 8 defense variants on `web-NotreDame` and WEBSPAM.
- **Milestone 3 (8 Nov 2026):** **EXPERIMENTS FREEZE.** Lock all raw CSVs, regenerate final 300 DPI publication figures, and conduct final Wilcoxon hypothesis tests.
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

# 2. Run automated test suite (all 30 tests must pass in < 4s)
pytest -v

# 3. Download SNAP web datasets and WEBSPAM-UK2006 labels
python scripts/download_data.py

# 4. Run clean baselines evaluation across synthetic and real SNAP graphs
python scripts/run_clean_baselines.py

# 5. Run Tier B experiments (cost curves v2, H2 robustness, H1/H3 eval, defenses v2)
python scripts/run_tier_b_experiments.py

# 6. Compute exact statistical facts, bootstrap CIs, and Wilcoxon p-values
python scripts/compute_facts_v2.py

# 7. Generate all 300 DPI publication figures and system architecture diagram
python scripts/generate_figures.py
```

### Manifest of Generated Artifacts for the 4-Page PDF

#### Figures (`figures/`)
- [`figures/cost_curves_rank_gain.png`](../figures/cost_curves_rank_gain.png): 300 DPI dual-panel chart of Normalized Rank Gain and Top-10 Entry Rate vs Attacker Budget on Synthetic BA-500 and SNAP web-Stanford base set across HITS, PageRank, SALSA, and In-degree.
- [`figures/h2_spectral_takeover.png`](../figures/h2_spectral_takeover.png): 300 DPI dual-panel chart of Target Authority and Target Rank vs Farm Size $p$, with the theoretical threshold $\sigma_1^2$ annotated illustrating the abrupt bifurcation of HITS vs smooth PageRank.
- [`figures/defenses_tradeoff.png`](../figures/defenses_tradeoff.png): 300 DPI Pareto plot showing Attack Success Reduction (%) vs Clean Graph NDCG Loss across defenses D1-D5.
- [`figures/architecture.png`](../figures/architecture.png) and [`figures/architecture.svg`](../figures/architecture.svg): End-to-end system architecture diagram clearly highlighting BUILT vs PENDING components.

#### Raw Data Tables (`results/`)
- [`results/environment.txt`](../results/environment.txt): Exact hardware and Python environment specification.
- [`results/clean_baselines.csv`](../results/clean_baselines.csv): Runtime, peak heap memory (`tracemalloc`), process RSS (`psutil`), iterations, and eigengap across 5 benchmark graphs.
- [`results/cost_curves_v2.csv`](../results/cost_curves_v2.csv): Complete 13,440-row dataset with ranks, gains, amplifications, Jaccard, NDCG, and Kendall tau.
- [`results/h2_robustness.csv`](../results/h2_robustness.csv): 60-instance spectral takeover measurements verifying $\sigma_1^2 \ge \text{max in-degree}$ and jump abruptness.
- [`results/h1_h3_eval.csv`](../results/h1_h3_eval.csv): Controlled $B^*(10)$ evaluations on ER and planted SBM graphs.
- [`results/defenses_eval_v2.csv`](../results/defenses_eval_v2.csv): 1,152-row defense evaluation matrix across 8 defense variants.
