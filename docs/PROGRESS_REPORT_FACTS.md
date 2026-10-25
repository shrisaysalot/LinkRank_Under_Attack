# Mid-Project Evidence Pack & Progress Report Facts (v2)

## 0. Corrections vs Progress Report v1
The following table itemizes all corrections made to rectify unverified or erroneous claims from version 1 of this report:

| Item | Claim in v1 | Verified Finding in v2 | Rationale / Root Cause |
|---|---|---|---|
| **CPU Hardware** | 12th Gen Intel Core i7-12700H | **12th Gen Intel Core i5-12500H** (12 physical cores, 16 logical threads) | Probed directly using `psutil` and Windows WMI (`results/environment.txt`); v1 claim cause unknown. |
| **Peak Memory Metric** | 0.50 – 18.17 MB (labeled as process RSS) | **0.50 – 18.17 MB Python Heap** (`tracemalloc`), **108.2 – 183.4 MB Process RSS** (`psutil`) | v1 reported internal Python heap allocations from `tracemalloc.get_traced_memory()`. Process RSS is dominated by the interpreter and library baseline. |
| **H1 Kendall's $\tau$** | $\tau = 0.912$ on ER graph | **$\tau = 0.746$** ($p = 7.99 \times 10^{-244}$, Spearman $\rho = 0.887$) on clean $G_{\text{ER}}(1000, 0.005)$ | Recomputed from clean ER-1000 graph; v1 claim cause unknown. Heavy-tailed BA-1000 drops to $\tau = 0.515$. |
| **Attack Nomenclature (A4/A5)** | A4 = multi-hub inflation, A5 = cross-linked clique | **A4 = Single fake page linking to $c$ authorities** (proposal definition); **A5 = $p$ fake hubs linking to target and $c$ authorities** (no cross-links) | Restored exact proposal specifications as `attack_a4_hub_inflation` and `attack_a5_cross_score`. Multi-hub and cross-linked extensions retained as A4b and A5b. |
| **Defense D2 (Bharat-Henzinger)** | Used no-op WCC connected components fallback | **True domain-to-page edge weighting** with `infer_domain_map` and reciprocal $1/k$ weighting | The earlier implementation fell back to WCC when domains were absent, placing all nodes into one component. |
| **Defense D3 (Hub Capping)** | Claimed 23.6% attack reduction | **Exact No-Op** (0.0% reduction, 0.0% clean NDCG loss) | Capping hub weight at 10% of total hub mass was never triggered across any evaluation instance ($d_3 - \text{undef} = 0.000000$). |
| **Defense D4 (Wu-Davison)** | Claimed universal 100% reduction with 0 clean loss | **D4 (Mutual Overlap):** -23.3% mean red (median 3.0%), 0.5% clean NDCG loss; **D4b (Out-Jaccard):** -24.0% mean red (median 2.5%), 1.3% clean NDCG loss | D4/D4b achieve 69–85% reduction against isolated farms (A2/A3), but fail against camouflaged farms and A6 where Jaccard overlap is diluted. |
| **Undefended HITS Reduction Metric** | Showed 23.6% attack reduction for undefended HITS | **0.0% attack reduction across positive-gain cells** ($n=110$) | In 34 of 144 cells (23.6%), undefended target attack gain was $\le 0$. The old metric function mapped non-positive gains to 1.0, creating an artifactual 23.6% reduction. |
| **H3 Budget Savings** | Attaching to community saves "$\approx 67\%$" budget | **48.1% [39.3%, 57.0%] saving on ER control**, **undefined / NaN on planted SBM-500** ($B \le 200$) | The 67% claim was unverified. On planted SBM, target failed to reach Top-10 under pure farm A2 within $B \le 200$, and reached Top-10 under A5 only at $B=200$. |
| **Cost Curves HITS vs PageRank** | Claimed HITS strictly higher normalized rank gain than PR | **CIs overlap at $B=25$** (HITS: 0.511 [0.471, 0.551] vs PR: 0.472 [0.442, 0.506]); **PageRank higher at $B=100$** (PR: 0.630 [0.597, 0.663] vs HITS: 0.600 [0.560, 0.642]) | SALSA and In-Degree are significantly higher than both at both budgets. Unverified claim of "rank ~1855 on wiki-Vote" removed. |
| **Scale-Down vs Proposal** | Full grid 1..500, 5 seeds, all graphs | **Budget grid $\{1, 5, 10, 25, 50, 75, 100\}$** (no 200/500), **3 seeds** (`[42, 123, 456]`), **4 graphs**, **5 targets/setting** | Scaled down to guarantee reproducible execution on laptop within mid-project timeline. |
| **Relative File Links & Repo Hygiene** | Contained 34 absolute `file:///c:/Users/shris/...` links | **100% clean relative markdown links**; bare `pytest` enabled via `pytest.ini` | All machine-specific paths removed; test suite expanded to 30 passing unit tests. |

### Claims I Could Not Verify
1. **WEBSPAM-UK2006 Hostgraph AUC / Spam@k:** The official human labels (8,415 labeled hosts) are verified and parsed in `data/raw/`, but full hostgraph AUC cannot be computed without Java WebGraph extraction of the hostgraph bitstream. Manual steps are documented in [`docs/WEBSPAM_MANUAL_STEPS.md`](WEBSPAM_MANUAL_STEPS.md).
2. **Universal Cost Reduction for H3:** Re-evaluation across 18 controlled trials ($n=9$ SBM, $n=9$ ER) showed attachment cost savings are graph-dependent (48.1% on ER control; target failed to penetrate Top-10 within $B \le 200$ on dense SBM).
3. **100% Defense Reduction with 0 Clean Loss for D4:** Across all positive-gain test cells, D4 achieves a goal-meeting rate ($\ge 50\%$ reduction at $\le 5\%$ clean NDCG loss) of 36.4% (D4 mutual) and 38.2% (D4b out-Jaccard); neither achieves universal mitigation.

---

## 1. Header
- **Group Number:** 16
- **Project Title:** LinkRank Under Attack: Adversarial Robustness of HITS
- **Course:** Information Retrieval (IR)
- **Members:** Shrisay Shandilya, Vibhor Rathi, Prachi Jain
- **Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)
- **Date of Report:** 25 October 2026 (Mid-Project Checkpoint; Final Submission Planned: 15 November 2026)

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
| **Data Loaders** | WEBSPAM-UK2006 Loader | **PARTIAL** | [`src/data/loader.py`](../src/data/loader.py) | Official human/domain labels downloaded & parsed (8,415 hosts; explicit undecided handling); hostgraph bitstream pending BVGraph conversion. |
| **Data Generators** | Synthetic Graph Generators | **DONE** | [`src/data/synthetic.py`](../src/data/synthetic.py) | Barabasi-Albert (scale-free), Erdos-Renyi, and SBM with planted dense bipartite communities. |
| **Data Subsets** | Kleinberg Base-Set Builder | **DONE** | [`src/data/base_set.py`](../src/data/base_set.py) | Query root set sampling ($|R| \approx 100-200$), out-link expansion, and max 50 in-link capping. |
| **Attacks** | A1: Single Fake Hub | **DONE** | [`src/attacks/a1_single_fake_hub.py`](../src/attacks/a1_single_fake_hub.py) | Injects 1 fake node with 1 direct edge to target ($B=1$). |
| **Attacks** | A2: Hub Farm | **DONE** | [`src/attacks/a2_hub_farm.py`](../src/attacks/a2_hub_farm.py) | Injects $p$ fake hub nodes each linking directly to target. |
| **Attacks** | A3: Bipartite Block | **DONE** | [`src/attacks/a3_bipartite_block.py`](../src/attacks/a3_bipartite_block.py) | Injects $K_{p, q}$ bipartite clique containing target and collateral fake authorities. |
| **Attacks** | A4: Hub Inflation (Proposal) | **DONE** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | 0 or 1 fake page linking to target AND $c$ real legitimate authorities. |
| **Attacks** | A4b: Multi-Hub Inflation | **DONE** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | $p$ fake hubs linking to target AND top legitimate authorities. |
| **Attacks** | A5: Cross-Score Coupling (Proposal) | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | $p$ fake hubs linking to target AND $c$ legitimate authorities (no cross-links). |
| **Attacks** | A5b: Cross-Linked Coupling | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | Hub inflation combined with reciprocal cross-links among attacker cluster. |
| **Attacks** | A6: Greedy Gradient Edge Choice | **DONE** | [`src/attacks/a6_greedy_gradient.py`](../src/attacks/a6_greedy_gradient.py) | Ranks edge additions by $\partial \sigma_1 / \partial A_{ij} = h_i a_j$ with candidate re-verification. |
| **Defenses** | D2: Bharat-Henzinger Edge Weighting | **DONE** | [`src/defenses/d2_bharat_henzinger.py`](../src/defenses/d2_bharat_henzinger.py) | Down-weights multiple edges between the same source and destination domains ($1/k$). |
| **Defenses** | D3: Hub-Contribution Capping | **DONE** | [`src/defenses/d3_hub_capping.py`](../src/defenses/d3_hub_capping.py) | Exact no-op under tested parameters (10% cap never triggered on tested graphs). |
| **Defenses** | D4: Wu-Davison Link-Farm Reweighting | **DONE** | [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) | Detects mutual in/out overlap (D4) and pairwise out-link Jaccard overlap (D4b). |
| **Defenses** | D5: Trust-Based HITS | **DONE** | [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) | Injects TrustRank seed prior in jump term; cuts authority derived from zero-trust hubs. |
| **Evaluation** | Metrics & Correlation | **DONE** | [`src/eval/metrics.py`](../src/eval/metrics.py) | Rank gain, normalized rank gain, $B^*(k)$, Top-$k$ entry, NDCG@k, Jaccard@k, $\tau$, $\rho$. |
| **Evaluation** | Statistical Confidence Testing | **DONE** | [`src/eval/stats.py`](../src/eval/stats.py) | Percentile bootstrap 95% CIs, Wilcoxon signed-rank paired tests, Holm-Bonferroni correction. |
| **WEBSPAM Eval** | Spam Host Classification / Spam@k | **PARTIAL** | [`src/data/loader.py`](../src/data/loader.py) | Labels loaded and categorized; full evaluation pending BVGraph extraction. |
| **Stretch** | Game-Theoretic Attacker-Defender Loop | **NOT STARTED** | - | Iterative adversarial equilibrium (planned for final sprint). |
| **Stretch** | Closed-Form Spectral Robustness Bound | **PARTIAL** | - | Empirical threshold $p \approx 0.82 \sigma_1^2$ observed; mathematical closed-form proof and generalized bound NOT STARTED. |
| **Stretch** | WEBSPAM-UK2007 Classifier | **NOT STARTED** | - | Multi-feature spam classifier on UK-2007 corpus. |

---

## 3. Architecture Changes vs Proposal
1. **Link-Analysis Focus vs IR Text Processing:** The standard IR proposal template mentions text processing (tokenization, stemming, inverted index, BM25). Because this project investigates link-structure vulnerability, the analogous pipeline consists of graph ingestion, deduplication/self-loop filtering, Kleinberg query base-set expansion, sparse power iteration ranking, and link injection attacks. No text processing or document indexing is employed or required.
2. **WEBSPAM-UK2006 Hostgraph Ingestion:** The official host label sets (set1 and set2, 8,415 hosts) are downloaded and parsed. The proposal's UK-2006 hostgraph (`uk-2006-05.host.graph`, 11,402 hosts) is ~1.9 MB in BVGraph compressed bitstream format (contrasting with the full ~77M page graph which is multi-gigabytes). Converting this ~1.9 MB host graph requires Java WebGraph extraction (`BVGraph` / `ArcListASCIIGraph`). Mid-project experiments evaluated on real SNAP web graphs (`wiki-Vote`, `web-Stanford`, `web-NotreDame`) and synthetic benchmarks. Manual extraction steps are fully documented in [`docs/WEBSPAM_MANUAL_STEPS.md`](WEBSPAM_MANUAL_STEPS.md).

---

## 4. Pipeline Details

### Graph Loading & Cleaning
- **SNAP Graphs:** Ingested from official SNAP `.txt.gz` archives. Headers and comments are parsed, self-loops are preserved or removed, isolated components indexed, and nodes re-mapped to contiguous zero-indexed integers ($0 \dots N-1$).
- **Base-Set Construction (Kleinberg 1999):**
  - Root Set: Sampled via localized random walks from seed nodes ($|R| \in [100, 200]$) to represent query-topical results.
  - Expansion: All outgoing neighbors added.
  - In-Link Capping: Predecessors are capped at a maximum of $50$ in-links per root node (preventing ubiquitous portal hubs from overwhelming the subgraph).
- **WEBSPAM-UK2006 Undecided Label Handling:**
  - Quoting directly from the official WEBSPAM-UK2006 `README.txt` (Algorithmic Engineering Group, Universita La Sapienza):
    > *"The spamicity measure is calculated by assigning 1 point for each 'spam' (S) judgment, 0.5 points for each 'borderline' (B) judgment, and 0 points for each 'normal' (N) judgment, and taking the average. The 'can not judge' (?) marks are ignored for this calculation. The label for a host with an average of over 0.5 is spam, for a host with an average of less than 0.5 is normal, and for a host with exactly 0.5 is undecided."*
  - Explicit Strategy: In our loader ([`src/data/loader.py`](../src/data/loader.py)), undecided hosts ($176$ hosts in Set 1) are excluded by default (`undecided_mode="exclude"`) for rigorous binary ground-truth fidelity, with configurable options for conservative (`"spam"`), lenient (`"normal"`), or ternary (`"keep"`) evaluation.

### Ranker Parameters
- **HITS:** Power iteration with L1 normalization after each step; convergence tolerance $\text{tol} = 10^{-8}$, maximum iterations $= 200$. Eigengap $\sigma_1^2 - \sigma_2^2$ computed via SciPy ARPACK sparse SVD.
- **PageRank:** Damping factor $\alpha = 0.85$, uniform personalization vector $v = \frac{1}{N}\mathbf{1}$, dangling node handling via uniform redistribution, $\text{tol} = 10^{-8}$, $\text{max\_iter} = 200$.
- **SALSA:** Bipartite random walk with ergodic reset $\epsilon = 10^{-4}$ to ensure unique stationary distribution across disconnected components, $\text{tol} = 10^{-8}$.
- **Randomized HITS (D1):** Reset parameter $\epsilon = 0.15$.
- **Subspace HITS (D1):** Subspace dimensionality $k = 5$ singular vectors.
- **Hub-Capping (D3):** Max hub weight cap $= 10\%$ of total hub mass (verified as no-op on tested graphs).
- **Random Seeds:** Default seed `42`; multi-seed experiments use `[42, 123, 456]`.

---

## 5. Preliminary Results Table

The experimental results below are derived from **13,440 empirical experimental trials** (`results/cost_curves_v2.csv`), 60 H2 takeover instances (`results/h2_robustness.csv`), 27 controlled H1/H3 trials (`results/h1_h3_eval.csv`), and 1,152 defense matrix evaluations (`results/defenses_eval_v2.csv`).

### Cost Curves Evaluation: Per-Attack Breakdown at Fixed Budgets $B = 25$ and $B = 100$
*Evaluated across 4 graphs (`Synthetic_BA_500`, `Synthetic_ER_500`, `Synthetic_SBM_500`, `SNAP_web-Stanford_BaseSet`), 3 seeds (`[42, 123, 456]`), and 5 targets ($n = 60$ trials per ranker per attack).*

Values report **Mean and [95% Percentile Bootstrap Confidence Interval]**:

#### Budget $B = 25$ Edges (Pre-Takeover Regime, $n=60$ per cell)

| Attack Type | Metric | Plain HITS | PageRank ($\alpha=0.85$) | SALSA | In-Degree |
|---|---|---|---|---|---|
| **A1: Single Hub** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.016 [0.011, 0.021]<br>0.0% [0.0%, 0.0%]<br>0.851 | 0.335 [0.285, 0.393]<br>0.0% [0.0%, 0.0%]<br>0.969 | 0.389 [0.344, 0.430]<br>0.0% [0.0%, 0.0%]<br>0.990 | 0.303 [0.270, 0.335]<br>0.0% [0.0%, 0.0%]<br>0.918 |
| **A2: Hub Farm** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.316 [0.230, 0.413]<br>13.3% [5.0%, 23.3%]<br>0.837 | **0.982** [0.973, 0.990]<br>**100.0%** [100.0%, 100.0%]<br>0.794 | 0.950 [0.918, 0.976]<br>86.7% [78.3%, 95.0%]<br>0.892 | 0.982 [0.973, 0.989]<br>91.7% [85.0%, 96.7%]<br>0.839 |
| **A3: Bipartite Block** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.139 [0.095, 0.190]<br>0.0% [0.0%, 0.0%]<br>0.854 | 0.335 [0.285, 0.393]<br>0.0% [0.0%, 0.0%]<br>0.963 | 0.806 [0.760, 0.845]<br>11.7% [3.3%, 20.0%]<br>0.923 | 0.813 [0.761, 0.856]<br>18.3% [8.3%, 28.3%]<br>0.854 |
| **A4: Proposal Inflation** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.014 [-0.004, 0.043]<br>0.0% [0.0%, 0.0%]<br>0.900 | -0.011 [-0.023, -0.002]<br>0.0% [0.0%, 0.0%]<br>0.970 | -0.007 [-0.022, 0.002]<br>0.0% [0.0%, 0.0%]<br>0.997 | 0.000 [0.000, 0.000]<br>0.0% [0.0%, 0.0%]<br>0.978 |
| **A4b: Multi-Hub Inflation** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | **0.872** [0.820, 0.916]<br>26.7% [16.7%, 38.3%]<br>0.733 | 0.421 [0.370, 0.481]<br>0.0% [0.0%, 0.0%]<br>0.936 | 0.745 [0.531, 0.864]<br>18.3% [8.3%, 28.3%]<br>0.954 | 0.835 [0.785, 0.879]<br>23.3% [13.3%, 35.0%]<br>0.871 |
| **A5: Proposal Cross-Score** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | **0.872** [0.820, 0.916]<br>26.7% [16.7%, 38.3%]<br>0.733 | 0.421 [0.370, 0.481]<br>0.0% [0.0%, 0.0%]<br>0.936 | 0.745 [0.531, 0.864]<br>18.3% [8.3%, 28.3%]<br>0.954 | 0.835 [0.785, 0.879]<br>23.3% [13.3%, 35.0%]<br>0.871 |
| **A5b: Cross-Score Links** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | **0.863** [0.813, 0.906]<br>25.0% [15.0%, 36.7%]<br>0.737 | 0.378 [0.323, 0.442]<br>0.0% [0.0%, 0.0%]<br>0.945 | 0.733 [0.520, 0.852]<br>18.3% [8.3%, 28.3%]<br>0.956 | 0.812 [0.759, 0.855]<br>18.3% [8.3%, 28.3%]<br>0.883 |
| **A6: Greedy Gradient** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | **0.998** [0.998, 0.999]<br>**100.0%** [100.0%, 100.0%]<br>0.622 | 0.916 [0.889, 0.941]<br>66.7% [55.0%, 78.3%]<br>0.852 | 0.960 [0.911, 0.987]<br>91.7% [85.0%, 96.7%]<br>0.895 | 0.982 [0.973, 0.989]<br>91.7% [85.0%, 96.7%]<br>0.858 |

#### Budget $B = 100$ Edges (Post-Takeover Regime, $n=60$ per cell)

| Attack Type | Metric | Plain HITS | PageRank ($\alpha=0.85$) | SALSA | In-Degree |
|---|---|---|---|---|---|
| **A1: Single Hub** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.016 [0.011, 0.021]<br>0.0% [0.0%, 0.0%]<br>0.851 | 0.335 [0.285, 0.393]<br>0.0% [0.0%, 0.0%]<br>0.969 | 0.389 [0.344, 0.430]<br>0.0% [0.0%, 0.0%]<br>0.990 | 0.303 [0.270, 0.335]<br>0.0% [0.0%, 0.0%]<br>0.918 |
| **A2: Hub Farm** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.576 [0.473, 0.687]<br>50.0% [38.3%, 63.3%]<br>0.438 | **0.998** [0.996, 1.000]<br>**100.0%** [100.0%, 100.0%]<br>0.634 | 0.958 [0.929, 0.983]<br>88.3% [80.0%, 95.0%]<br>0.844 | 0.996 [0.992, 0.999]<br>100.0% [100.0%, 100.0%]<br>0.831 |
| **A3: Bipartite Block** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.548 [0.438, 0.661]<br>50.0% [38.3%, 63.3%]<br>0.415 | 0.335 [0.285, 0.393]<br>0.0% [0.0%, 0.0%]<br>0.960 | 0.852 [0.792, 0.902]<br>33.3% [21.7%, 45.0%]<br>0.772 | 0.893 [0.858, 0.924]<br>41.7% [28.3%, 55.0%]<br>0.742 |
| **A4: Proposal Inflation** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.014 [-0.004, 0.043]<br>0.0% [0.0%, 0.0%]<br>0.900 | -0.011 [-0.023, -0.002]<br>0.0% [0.0%, 0.0%]<br>0.970 | -0.007 [-0.022, 0.002]<br>0.0% [0.0%, 0.0%]<br>0.997 | 0.000 [0.000, 0.000]<br>0.0% [0.0%, 0.0%]<br>0.978 |
| **A4b: Multi-Hub Inflation** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.883 [0.831, 0.928]<br>50.0% [38.3%, 63.3%]<br>0.607 | 0.817 [0.791, 0.842]<br>23.3% [13.3%, 35.0%]<br>0.841 | 0.939 [0.865, 0.976]<br>91.7% [85.0%, 96.7%]<br>0.877 | 0.968 [0.959, 0.977]<br>91.7% [85.0%, 96.7%]<br>0.816 |
| **A5: Proposal Cross-Score** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.883 [0.831, 0.928]<br>50.0% [38.3%, 63.3%]<br>0.607 | 0.817 [0.791, 0.842]<br>23.3% [13.3%, 35.0%]<br>0.841 | 0.939 [0.865, 0.976]<br>91.7% [85.0%, 96.7%]<br>0.877 | 0.968 [0.959, 0.977]<br>91.7% [85.0%, 96.7%]<br>0.816 |
| **A5b: Cross-Score Links** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | 0.883 [0.831, 0.928]<br>50.0% [38.3%, 63.3%]<br>0.547 | 0.758 [0.725, 0.790]<br>21.7% [11.7%, 31.7%]<br>0.850 | 0.943 [0.881, 0.974]<br>91.7% [85.0%, 96.7%]<br>0.894 | 0.959 [0.945, 0.971]<br>91.7% [85.0%, 96.7%]<br>0.810 |
| **A6: Greedy Gradient** | Norm Gain<br>Top-10 Rate (%)<br>Top-20 Jaccard | **0.999** [0.998, 0.999]<br>**100.0%** [100.0%, 100.0%]<br>0.614 | 0.992 [0.985, 0.998]<br>100.0% [100.0%, 100.0%]<br>0.638 | 0.997 [0.993, 0.999]<br>100.0% [100.0%, 100.0%]<br>0.898 | 0.996 [0.992, 0.999]<br>100.0% [100.0%, 100.0%]<br>0.850 |

---

### Secondary Pooled Cost Curves Summary (Across All 8 Attacks, $n = 480$ per ranker)

| Budget | Ranker | Normalized Rank Gain | Top-10 Entry Rate (%) | Top-20 Jaccard | Top-20 NDCG | Kendall's $\tau$ |
|---|---|---|---|---|---|---|
| **$B = 25$** | **Plain HITS** | 0.511 [0.471, 0.551] | 24.0% [20.4%, 27.9%] | 0.783 [0.758, 0.806] | 0.974 [0.967, 0.980] | 0.960 [0.952, 0.968] |
| | **PageRank ($\alpha=0.85$)** | 0.472 [0.442, 0.506] | 20.8% [17.3%, 24.6%] | 0.921 [0.908, 0.932] | 0.986 [0.982, 0.990] | 0.991 [0.989, 0.993] |
| | **SALSA** | 0.665 [0.619, 0.707] | 30.6% [26.5%, 34.4%] | 0.945 [0.937, 0.953] | 0.983 [0.978, 0.988] | 0.987 [0.984, 0.990] |
| | **In-Degree** | 0.695 [0.664, 0.728] | 33.3% [29.4%, 37.5%] | 0.884 [0.871, 0.897] | 0.982 [0.978, 0.986] | 0.997 [0.996, 0.998] |
| **$B = 100$** | **Plain HITS** | 0.600 [0.560, 0.642] | 43.8% [39.4%, 48.1%] | 0.622 [0.590, 0.655] | 0.875 [0.852, 0.898] | 0.878 [0.862, 0.895] |
| | **PageRank ($\alpha=0.85$)** | 0.630 [0.597, 0.663] | 33.5% [29.2%, 37.9%] | 0.838 [0.819, 0.855] | 0.946 [0.937, 0.956] | 0.977 [0.974, 0.981] |
| | **SALSA** | 0.751 [0.720, 0.784] | 62.1% [57.7%, 66.5%] | 0.894 [0.881, 0.906] | 0.958 [0.949, 0.967] | 0.966 [0.960, 0.971] |
| | **In-Degree** | 0.760 [0.728, 0.793] | 64.6% [60.4%, 68.8%] | 0.845 [0.829, 0.860] | 0.952 [0.943, 0.960] | 0.996 [0.995, 0.997] |

*Paired Wilcoxon Signed-Rank Tests (HITS vs Baselines at $B=100$, $n=480$):*
- **HITS vs PageRank:** Raw $p = 0.562$, Holm-adjusted $p = 0.562$ (Not statistically significant; CIs overlap; HITS suffers significantly worse Top-20 Jaccard collapse: 0.622 vs 0.838).
- **HITS vs SALSA:** Raw $p = 1.19 \times 10^{-22}$, Holm-adjusted $p = 2.39 \times 10^{-22}$ (**Statistically Significant**; SALSA exhibits higher normalized rank gain under direct link manipulation).
- **HITS vs In-Degree:** Raw $p = 1.44 \times 10^{-24}$, Holm-adjusted $p = 4.33 \times 10^{-24}$ (**Statistically Significant**; In-Degree is strictly proportional to edge count).

---

### Corrected Defense Evaluation Summary
*Evaluated on positive attack gain cells ($n = 110$ instances per defense). Clean NDCG Loss and Clean Jaccard computed as mean across all rows ($n=144$). Proposal Criterion: $\ge 50\%$ attack reduction at $\le 5\%$ clean NDCG loss.*

| Defense Variant | Attack Success Reduction (Mean [95% CI]) | Median Reduction (%) | Clean Top-20 Jaccard | Clean NDCG Loss (%) | Meets Proposal Goal Rate (%) | Note |
|---|---|---|---|---|---|---|
| **Undefended HITS** | 0.0% [0.0%, 0.0%] | 0.0% | 1.000 | 0.0% | 0.0% | Baseline ($n=110$ positive cells). |
| **D1: Randomized HITS ($\epsilon=0.15$)** | -72.6% [-145.4%, -22.6%] | -1.0% | 0.781 | **0.1%** | 13.6% | Uniform reset diffuses mass proportionally to degree. |
| **D1: Subspace HITS ($k=5$)** | -0.8% [-50.0%, 51.8%] | 15.7% | 0.338 | 28.3% | 9.1% | Significant clean distortion. |
| **D2: Bharat-Henzinger ($1/k$)** | 38.7% [13.4%, 57.0%] | **89.4%** | 0.254 | 59.6% | 1.8% | High median reduction but severe clean graph distortion. |
| **D3: Hub Capping (10%)** | 0.0% [0.0%, 0.0%] | 0.0% | 1.000 | 0.0% | 0.0% | **Exact No-Op** (10% cap never triggered on tested graphs). |
| **D4: Wu-Davison (Mutual Overlap)** | -23.3% [-96.0%, 16.9%] | 3.0% | 0.786 | **0.5%** | **36.4%** | Effective on A2/A3; fails when overlap is camouflaged. |
| **D4b: Wu-Davison (Out-Jaccard)** | -24.0% [-103.9%, 17.7%] | 2.5% | 0.680 | **1.3%** | **38.2%** | Effective on A2/A3; fails when overlap is camouflaged. |
| **D5: Trust-Based HITS** | -150.7% [-323.7%, -29.4%] | 11.1% | 0.337 | 27.7% | 6.4% | Clean rank distortion reduces goal rate. |

*Finding on Defense Goal:* **NO defense meets $\ge 50\%$ mean attack reduction at $\le 5\%$ clean NDCG loss across all attacks.** D4 and D4b meet the goal in 36.4% and 38.2% of positive-gain cells, but their mean reduction across all attacks is negative due to camouflaged and gradient attacks.

---

### Per-Attack Defense Breakdown (Attack Reduction Median & Goal Rate)

| Attack Type | Budget | Undefended HITS | D1 Randomized ($\epsilon=0.15$) | D2 Bharat-Henzinger | D3 Hub Capping (10%) | D4 Wu-Davison (Mutual) | D4b Wu-Davison (Out-Jaccard) |
|---|---|---|---|---|---|---|---|
| **A2: Hub Farm** | $B=25$ ($n=8$)<br>$B=100$ ($n=9$) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: -172.5% (0.0% goal)<br>Med: -1.7% (0.0% goal) | Med: 99.3% (0.0% goal)<br>Med: 100.0% (11.1% goal) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: **96.6%** (**75.0%** goal)<br>Med: **96.5%** (**77.8%** goal) | Med: **97.3%** (**75.0%** goal)<br>Med: **97.5%** (**77.8%** goal) |
| **A3: Bipartite Block** | $B=25$ ($n=7$)<br>$B=100$ ($n=7$) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: -226.9% (0.0% goal)<br>Med: -0.8% (0.0% goal) | Med: 92.9% (0.0% goal)<br>Med: 99.5% (0.0% goal) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: **100.0%** (**85.7%** goal)<br>Med: **99.0%** (**85.7%** goal) | Med: **100.0%** (**85.7%** goal)<br>Med: **99.7%** (**85.7%** goal) |
| **A4: Proposal Inflation** | $B=25$ ($n=4$)<br>$B=100$ ($n=4$) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: **86.2%** (**75.0%** goal)<br>Med: **86.2%** (**75.0%** goal) | Med: 45.2% (0.0% goal)<br>Med: 45.2% (0.0% goal) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: 34.1% (25.0% goal)<br>Med: 34.1% (25.0% goal) | Med: 10.0% (25.0% goal)<br>Med: 10.0% (25.0% goal) |
| **A5: Proposal Cross-Score** | $B=25$ ($n=12$)<br>$B=100$ ($n=12$) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: 2.3% (16.7% goal)<br>Med: -1.3% (16.7% goal) | Med: 90.3% (0.0% goal)<br>Med: 96.5% (0.0% goal) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: 65.7% (58.3% goal)<br>Med: 43.7% (33.3% goal) | Med: 80.4% (66.7% goal)<br>Med: 45.7% (41.7% goal) |
| **A6: Greedy Gradient** | $B=25$ ($n=12$)<br>$B=100$ ($n=12$) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: 0.3% (0.0% goal)<br>Med: 0.3% (0.0% goal) | Med: 17.3% (0.0% goal)<br>Med: 19.8% (8.3% goal) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: -0.2% (0.0% goal)<br>Med: -0.2% (0.0% goal) | Med: -1.3% (0.0% goal)<br>Med: -1.3% (0.0% goal) |
| **Camouflaged Farm** | $B=25$ ($n=11$)<br>$B=100$ ($n=12$) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: -2.8% (27.3% goal)<br>Med: -6.4% (16.7% goal) | Med: 28.1% (0.0% goal)<br>Med: 52.0% (0.0% goal) | Med: 0.0% (0.0% goal)<br>Med: 0.0% (0.0% goal) | Med: 0.6% (9.1% goal)<br>Med: -2.0% (8.3% goal) | Med: -4.3% (9.1% goal)<br>Med: -1.5% (8.3% goal) |

---

### Clean Baseline Computational Efficiency & Peak Memory

| Dataset / Graph | Nodes | Edges | HITS Time | PR Time | SALSA Time | Peak Heap (`tracemalloc`) | Process RSS (`psutil`) | Eigengap $\sigma_1^2 - \sigma_2^2$ |
|---|---|---|---|---|---|---|---|---|
| **Synthetic BA-1000** | 1,000 | 4,369 | 0.045s (42 it) | 0.013s (26 it) | 0.016s (57 it) | 0.85 MB | 108.2 MB | 45.41 |
| **Synthetic ER-1000** | 1,000 | 4,973 | 0.080s (39 it) | 0.013s (22 it) | 0.014s (34 it) | 0.82 MB | 114.7 MB | 14.44 |
| **Planted SBM-840** | 840 | 2,971 | 0.023s (11 it) | 0.010s (28 it) | 0.017s (125 it) | 0.50 MB | 118.9 MB | 275.51 |
| **SNAP wiki-Vote** | 7,115 | 103,689 | 0.657s (23 it) | 0.580s (23 it) | 0.643s (53 it) | 18.17 MB | 183.4 MB | 6,158.51 |
| **SNAP web-Stanford BaseSet** | 1,686 | 13,849 | 0.110s (23 it) | 0.155s (81 it) | 0.114s (200 it) | 2.45 MB | 152.1 MB | 2,518.81 |

*Hardware Used:* 12th Gen Intel Core i5-12500H (12 physical cores, 16 logical threads), 15.69 GB RAM, Windows 11 64-bit, Python 3.12.5, SciPy 1.12.0 sparse linear algebra. Note: Process RSS (`psutil`: 108.2 – 183.4 MB) is dominated by the Python interpreter and library baseline, whereas Python heap allocations (`tracemalloc`: 0.50 – 18.17 MB) track active ranker data structures.

---

## 6. Hypothesis Status

### Hypothesis H1: "On random-like graphs HITS ~ in-degree"
- **Status: NOT SUPPORTED (Attack Cost).**
- **Evidence:** Evaluating the minimal budget $B^*(10)$ to reach Top-10 under single-hub injection across $n=9$ controlled trials on $G_{\text{ER}}(500, 0.012)$, HITS required a mean of **$4.44\times$ more budget** than simple in-degree (HITS required 30–50 edges, whereas In-Degree required only 5–10 edges). While clean-graph rank correlation is high ($\tau = 0.746$, $p = 7.99 \times 10^{-244}$; Spearman $\rho = 0.887$ on ER-1000, reported as supplementary only), HITS does not behave like in-degree under adversarial link manipulation because isolated hubs fail to promote a node until their spectral weight competes with background authority.
- **Limits:** On heavy-tailed BA-1000, clean rank correlation drops to $\tau = 0.515$ ($p = 2.50 \times 10^{-115}$; Spearman $\rho = 0.692$).

### Hypothesis H2: "Hub farm of $p$ fake hubs only takes over top HITS vectors when $p \sim \sigma_1^2$ (sharp jump; PageRank gains smooth)"
- **Status: SUPPORTED (Preliminary).**
- **Evidence:** Evaluated systematically across $n=60$ independent instances (4 graph families, 3 random seeds, 5 targets, $p$ grid spanning 24 multipliers linearly spaced between $0.1$ and $2.0 \times \sigma_1^2$):
  - **Upper Bound Hold Rate:** $\sigma_1^2 \ge \text{max in-degree}$ holds in **100.0%** of instances ($60/60$).
  - **Takeover Threshold:** Empirical takeover occurs somewhat below $\sigma_1^2$:
    - Top-10 takeover ratio: $p^*(10) / \sigma_1^2 = \mathbf{0.817}$ [0.751, 0.879] ($n=60$).
    - Top-1 takeover ratio: $p^*(1) / \sigma_1^2 = \mathbf{0.873}$ [0.819, 0.923] ($n=60$).
  - **Abrupt Jump Rate:** HITS exhibits an abrupt single-step rank jump in **63.3%** of instances ($38 / 60$) with a mean maximum single-step rank jump of **69.7 ranks** (median jump $64.0$ ranks), compared to **16.9 ranks** for PageRank.
  - **Counterexamples (36.7%):** In $22 / 60$ instances (12 on ER-400, 7 on BA-400, 3 on web-Stanford base-set), the rank jump did not exceed $2\times$ the PageRank step jump, occurring when background singular gaps are narrow or target nodes start in high-degree positions.
- **Limits:** Evaluated on subgraphs ($N \le 1,686$); validation on full web-scale hostgraphs is scheduled for the final sprint.

### Hypothesis H3: "On graphs with dense communities, attaching to the community (TKC) is cheaper"
- **Status: INCONCLUSIVE / NOT SUPPORTED.**
- **Evidence:** Evaluated across $n=18$ controlled trials (`results/h1_h3_eval.csv`) comparing minimal budget $B^*(10)$ between A2 (isolated farm) and proposal A5 (attaching to target and $c=3$ real top authorities):
  - On **ER Control graphs** ($n=9$), attaching to top authorities reduced the required budget to achieve Top-10 by **48.1%** [39.3%, 57.0%] (mean budget reduced from 30–50 down to 20 edges).
  - On **Planted SBM graphs** ($n=9$), the target failed to reach Top-10 under A2 within the evaluated budget grid ($B \le 200$), and reached Top-10 under A5 only at $B=200$ (cost saving undefined / NaN).
  - Observing 48.1% savings on ER control and no penetration below $B=200$ on SBM is the opposite of the prediction that dense planted communities make attachment uniquely cheaper.
- **Limits:** The budget grid was capped at $B=200$; higher budgets are needed to observe SBM farm takeover.

### Hypothesis H4: "Damped/capped/trust-based HITS cuts attack success with little clean-graph damage"
- **Status: NOT SUPPORTED so far.**
- **Evidence:** Tested across 1,152 evaluations (`results/defenses_eval_v2.csv`, $n=110$ positive attack gain instances per defense):
  - **No defense meets $\ge 50\%$ mean attack reduction at $\le 5\%$ clean NDCG loss across all attacks.**
  - **Wu-Davison (D4 and D4b):** Achieve high reduction on isolated hub farms (A2/A3, 69–85% reduction, ~75–86% goal rate), but fail when attackers camouflage links or use gradient additions (mean reduction across all attacks: -23.3% and -24.0%).
  - **Bharat-Henzinger (D2):** Strong median reduction (89.4%), but incurs **59.6% clean NDCG loss** (Clean Top-20 Jaccard 0.254), meeting the proposal goal in only 1.8% of cells.
  - **Randomized HITS (D1, $\epsilon=0.15$):** Clean NDCG loss is only **0.1%**, but mean reduction is -72.6% (median -1.0%) because uniform teleport spreads authority proportionally to in-degree.
  - **Hub Capping (D3, 10%):** Exact no-op (0.0% reduction, 0.0% clean NDCG loss) because the 10% threshold was never exceeded.
- **Limits:** Fixed parameter thresholds were evaluated; dynamic or calibrated thresholds may improve performance.

---

## 7. Problems Encountered and Deviations

1. **WEBSPAM-UK2006 Hostgraph Bitstream Compression:**
   - *Issue:* The host labels (`webspam-uk2006-set1-labels.txt`) were successfully downloaded and parsed. However, the host link graph (`uk-2006-05.host.graph`, ~1.9 MB, 11,402 hosts) is stored in WebGraph BVGraph bitstream format, requiring Java extraction tools (`BVGraph` / `ArcListASCIIGraph`).
   - *Deviation:* Mid-project experiments evaluated on real SNAP web graphs (`wiki-Vote`, `web-Stanford`, `web-NotreDame`) and synthetic benchmarks. Manual Java extraction instructions have been documented in [`docs/WEBSPAM_MANUAL_STEPS.md`](WEBSPAM_MANUAL_STEPS.md).
2. **SALSA Convergence on Multi-Component Base Sets:**
   - *Issue:* In disconnected bipartite components, pure SALSA transition matrices contain multiple unit eigenvalues, causing standard power iteration to stall.
   - *Solution:* Implemented an ergodic teleport parameter ($\epsilon = 10^{-4}$) in [`src/rankers/salsa.py`](../src/rankers/salsa.py), guaranteeing strict positive Perron-Frobenius convergence.
3. **Metric Calculation on Non-Positive Attack Gains:**
   - *Issue:* When undefended attack gain was zero or negative, the metric `defense_attack_success_reduction` mapped to 1.0 (100% reduction), inflating Undefended HITS to 23.6%.
   - *Solution:* Filtered out cells with non-positive undefended attack gain ($n=34$), reporting true defense reduction on genuine attacks ($n=110$).

---

## 8. Path to Final Submission
- **Milestone 1 (Planned: 28 Oct 2026):** Execute Java BVGraph ASCII extraction for WEBSPAM-UK2006 hostgraph as documented in `docs/WEBSPAM_MANUAL_STEPS.md`; compute baseline spam@k and AUC on full hostgraph.
- **Milestone 2 (Planned: 1 Nov 2026):** Execute complete experimental matrix across all 8 attack variants (A1-A6) and defenses on `web-NotreDame` and WEBSPAM.
- **Milestone 3 (Planned: 8 Nov 2026):** **EXPERIMENTS FREEZE.** Lock all raw CSVs, regenerate final 300 DPI publication figures, and conduct final Wilcoxon hypothesis tests.
- **Milestone 4 (Planned: 15 Nov 2026):** Final Report and Slide Deck submission.

### Status of Stretch Objectives:
1. **Game-Theoretic Attacker-Defender Loop:** **NOT STARTED.** (Planned for final sprint).
2. **Closed-Form Spectral Robustness Bound:** **PARTIAL.** (Empirical takeover at $p \approx 0.82 \sigma_1^2$ observed; mathematical closed-form proof and generalized bound NOT STARTED).
3. **WEBSPAM-UK2007 Multi-Feature Classifier:** **NOT STARTED.** (Dependent on Milestone 1 data pipeline).

---

## 9. Contribution Matrix Draft (PLANNED Ownership - CONFIRM WITH TEAM)

*Current Git Commits (`git shortlog -sn --all`): 9 Shrisaysalot.*  
The table below reflects **PLANNED ownership areas** for final project delivery, subject to team confirmation:

| Member | Planned Area of Ownership | Status |
|---|---|---|
| **Shrisay Shandilya** | Rankers, Data Loaders, Base-Set Pipeline, Clean Baselines | **CONFIRM WITH TEAM** |
| **Vibhor Rathi** | Adversarial Link Injection Attacks (A1–A6) & Validation Suite | **CONFIRM WITH TEAM** |
| **Prachi Jain** | Algorithmic Defenses (D1–D5), Statistical Testing Suite & Figures | **CONFIRM WITH TEAM** |

---

## 10. Reproduction Commands & Deliverable Manifest

### Exact Reproduction Commands
From the repository root:

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
- [`figures/cost_curves_rank_gain.png`](../figures/cost_curves_rank_gain.png): 300 DPI 8-panel chart of Normalized Rank Gain vs Attacker Budget across all attack families (A1–A6) for HITS, PageRank, SALSA, and In-degree (marked Preliminary).
- [`figures/h2_spectral_takeover.png`](../figures/h2_spectral_takeover.png): 300 DPI dual-panel chart of Target Authority and Target Rank vs Farm Size $p$, with the theoretical threshold $\sigma_1^2$ annotated illustrating abrupt HITS bifurcation vs smooth PageRank (marked Preliminary).
- [`figures/defenses_tradeoff.png`](../figures/defenses_tradeoff.png): 300 DPI Pareto plot showing Attack Success Reduction (%) vs Clean Graph NDCG Loss across defenses D1-D5 (marked Preliminary - Small-N).
- [`figures/architecture.png`](../figures/architecture.png) and [`figures/architecture.svg`](../figures/architecture.svg): End-to-end system architecture diagram clearly highlighting BUILT vs PENDING components.

#### Raw Data Tables (`results/`)
- [`results/environment.txt`](../results/environment.txt): Exact hardware and Python environment specification.
- [`results/clean_baselines.csv`](../results/clean_baselines.csv): Runtime, peak heap memory (`tracemalloc`), process RSS (`psutil`), iterations, and eigengap across 5 benchmark graphs.
- [`results/cost_curves_v2.csv`](../results/cost_curves_v2.csv): Complete 13,440-row dataset with ranks, gains, amplifications, Jaccard, NDCG, and Kendall tau.
- [`results/h2_robustness.csv`](../results/h2_robustness.csv): 60-instance spectral takeover measurements verifying $\sigma_1^2 \ge \text{max in-degree}$ and jump abruptness.
- [`results/h1_h3_eval.csv`](../results/h1_h3_eval.csv): Controlled $B^*(10)$ evaluations on ER and planted SBM graphs.
- [`results/defenses_eval_v2.csv`](../results/defenses_eval_v2.csv): 1,152-row defense evaluation matrix across 8 defense variants.
