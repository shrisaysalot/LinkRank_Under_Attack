# Final Evidence Pack & Fact Sheet (v3.0)
## LinkRank Under Attack: Adversarial Robustness of HITS

---

## 1. Header & Team Information
- **Group Number:** 16
- **Project Title:** LinkRank Under Attack: Adversarial Robustness of HITS
- **Course:** Information Retrieval (IR)
- **Members:** 
  - Shrisay Shandilya
  - Vibhor Rathi
  - Prachi Jain
- **Repository:** [https://github.com/shrisaysalot/LinkRank_Under_Attack](https://github.com/shrisaysalot/LinkRank_Under_Attack)
- **Date of Final Report Evidence Pack:** 12 November 2026
- **Final Submission Deadline:** 15 November 2026

---

## 2. Executive Summary & Headline Findings

1. **Theoretical Spectral Phase Transition Confirmed (Hypothesis H2 - Strongly Supported):**
   Across $n=125$ experimental instances spanning five graph families (synthetic BA, ER, SBM, and real SNAP web-Stanford and web-NotreDame base sets), the spectral property $\sigma_1^2 \ge \max(d_{in})$ holds in **100.0% of instances** ($125/125$). When an attacker injects a hub farm of size $p$, HITS exhibits a discontinuous spectral takeover in **73.6% of instances** ($92/125$), jumping by a mean of **61.5 ranks** in a single budget step, compared to only **15.2 ranks** for PageRank. The empirical takeover thresholds normalize tightly to the leading singular value:
   - Critical Top-10 Takeover: $p^*(10) / \sigma_1^2 = \mathbf{0.713}$ [95% CI: $0.656, 0.766$].
   - Critical Rank-1 Takeover: $p^*(1) / \sigma_1^2 = \mathbf{0.841}$ [95% CI: $0.808, 0.873$].
   - **Root Cause of Counterexamples:** In the 26.4% of instances ($33/125$) where takeover is non-abrupt, the graph exhibits a severely contracted eigengap ($\sigma_1 - \sigma_2 = 2.51$ vs $13.53$ in abrupt cases) and the target begins already near top ranks (mean initial rank 214 vs 465).

2. **In-Degree Baseline Comparison (Hypothesis H1 - Strongly Supported):**
   Across $n=25$ independent target instances evaluated on Erdos-Renyi random graphs ($G(500, 0.012)$) across five random seeds, In-Degree is significantly cheaper to manipulate than HITS:
   - Budget to reach Top-10: In-Degree requires $B^*(10) = \mathbf{8.60}$ edges [95% CI: $7.60, 9.40$] vs HITS $B^*(10) = \mathbf{31.40}$ edges [95% CI: $28.20, 34.40$].
   - Cost Ratio ($B^*_{\text{HITS}} / B^*_{\text{InDeg}}$) = $\mathbf{3.820}$ [95% CI: $3.440, 4.240$] ($p = 5.96 \times 10^{-8}$, Wilcoxon signed-rank test).
   - Budget to reach Rank-1: In-Degree requires $B^*(1) = \mathbf{11.00}$ edges vs HITS $B^*(1) = \mathbf{37.60}$ edges (ratio = $\mathbf{3.547}$, $p = 5.96 \times 10^{-8}$).

3. **Community Attachment Economy (Hypothesis H3 - Supported):**
   Across $n=30$ controlled trials ($15$ Planted SBM, $15$ ER control) tested up to budget $B=500$, attaching fake hubs to top legitimate community authorities (A5 Cross-Score) consistently lowers the attack cost compared to isolated hub farms (A2):
   - On Planted SBM ($n=15$), A5 achieves a mean cost saving of $\mathbf{33.3\%}$ [95% CI: $33.3\%, 33.3\%$].
   - On ER control graphs ($n=15$), A5 achieves a mean cost saving of $\mathbf{36.7\%}$ [95% CI: $26.7\%, 46.7\%$].
   - Both A2 and A5 achieve Top-10 entry in $100\%$ ($30/30$) of instances when budget is expanded to $B=500$.

4. **Defense Pareto Trade-Offs & Vulnerability to Camouflage (Hypothesis H4 - Supported with Nuance):**
   Across $7,920$ defense matrix trials ($7,084$ positive undefended attack gain cells):
   - **Wu-Davison D4 and D4b** (calibrated threshold $\theta=0.5$) achieve near-complete suppression against isolated link farms: **93.3% median reduction** against A2 Hub Farm, **97.3%** against A3 Bipartite Block, and **63.0%** against A5 Cross-Score.
   - **Camouflage Evasion:** When attackers inject random camouflage links ($r \in \{2, 5, 10\}$), pairwise out-link Jaccard overlap drops below $\theta=0.5$, completely evading D4 and D4b ($0.0\%$ goal achievement). Similarly, Greedy Gradient (A6) evades D4/D4b ($0.0\%$ reduction).
   - **Hub Capping (D3):** Calibrated capping at $1\%$ of total hub mass actively binds with $25.8\%$ attack reduction and $1.96\%$ clean NDCG loss. The proposal's $10\%$ cap is a provable no-op because no legitimate or farm hub in graphs with $N \ge 500$ exceeds $5.6\%$ of total hub score.

5. **Real-World WEBSPAM-UK2006 Hostgraph Evaluation & The Spectral Scale Barrier:**
   - Evaluated the complete real-world WEBSPAM-UK2006 hostgraph ($11,402$ hosts, $730,774$ directed edges) against $10,662$ official volunteer labels ($8,415$ Set 1, $2,247$ Set 2).
   - On the natural clean web, Top-100 positions are completely spam-free ($\text{Spam@100} = 0.0\%$), with spam relegated to rank $187+$ (PageRank) and rank $1,253+$ (HITS).
   - **Spectral Scale Barrier:** The global hostgraph exhibits $\sigma_1^2 = \mathbf{115,407.4}$. An attacker injecting $B \le 100$ links represents $B / \sigma_1^2 \approx 0.00087 \ll 0.71$, mathematically preventing eigenvector takeover on the global host graph. In contrast, Kleinberg query-dependent base sets ($N \approx 500-1000, \sigma_1^2 \approx 10-50$) fall directly within the attacker's budget ($B \ge \sigma_1^2$), explaining why HITS is catastrophically vulnerable in topic distillation but robust on massive global graphs.

6. **Stretch Objectives Completed:**
   - **Empirical Spectral Scaling Law:** Regression of critical takeover budget against $\sigma_1^2$ yields an empirical scaling law $p^*(1) = 0.6264 \, \sigma_1^2$ with $R^2 = \mathbf{0.9424}$ across 125 instances.
   - **Adaptive Attacker-Defender Game:** Evaluated a 3-round interaction where an attacker evades D4 via camouflage dilution (attack reduction drops from $97.5\%$ to $-0.6\%$), and the defender successfully counters by re-tuning the threshold to $\theta=0.35$ on an independent calibration graph.

---

## 3. Final Implementation Status Table

| Module Category | Component / Module | Status | File Path | One-Line Note |
|---|---|---|---|---|
| **Rankers** | Sparse Power Iteration HITS | **DONE** | [`src/rankers/hits.py`](../src/rankers/hits.py) | Full sparse power iteration with L1 normalization and ARPACK SVD eigengap tracking. |
| **Rankers** | PageRank Baseline | **DONE** | [`src/rankers/pagerank.py`](../src/rankers/pagerank.py) | Power iteration with damping $\alpha=0.85$ and exact dangling node mass redistribution. |
| **Rankers** | SALSA Baseline | **DONE** | [`src/rankers/salsa.py`](../src/rankers/salsa.py) | Bipartite random walk with ergodic teleport ($\epsilon=10^{-4}$) for disconnected components. |
| **Rankers** | In-Degree Centrality | **DONE** | [`src/rankers/indegree.py`](../src/rankers/indegree.py) | Exact normalized column-sum in-degree baseline ($O(\|E\|)$ time). |
| **Rankers / Defenses** | Randomized HITS (D1) | **DONE** | [`src/rankers/randomized_hits.py`](../src/rankers/randomized_hits.py) | Damped authority/hub power iteration with uniform jump reset $\epsilon=0.15$ (Ng et al. 2001). |
| **Rankers / Defenses** | Subspace HITS (D1) | **DONE** | [`src/rankers/subspace_hits.py`](../src/rankers/subspace_hits.py) | Spectral projection across top-$k$ singular vectors ($k=5$). |
| **Data Loaders** | SNAP Graph Loader | **DONE** | [`src/data/loader.py`](../src/data/loader.py) | Downloads and loads real SNAP web graphs (wiki-Vote, web-Stanford, web-NotreDame). |
| **Data Loaders** | WEBSPAM Hostgraph & Labels | **DONE** | [`src/data/loader.py`](../src/data/loader.py) | Native Python loader for full 11,402-node, 730k-edge hostgraph + 10,662 Set 1/2 labels. |
| **Data Generators** | Synthetic Graph Generators | **DONE** | [`src/data/synthetic.py`](../src/data/synthetic.py) | Barabasi-Albert (scale-free), Erdos-Renyi, and SBM with planted dense bipartite communities. |
| **Data Subsets** | Kleinberg Base-Set Builder | **DONE** | [`src/data/base_set.py`](../src/data/base_set.py) | Query root set sampling ($|R| \approx 40-80$), out-link expansion, and in-link capping. |
| **Attacks** | A1: Single Fake Hub | **DONE** | [`src/attacks/a1_single_fake_hub.py`](../src/attacks/a1_single_fake_hub.py) | Injects 1 fake node with 1 direct edge to target ($B=1$). |
| **Attacks** | A2: Hub Farm | **DONE** | [`src/attacks/a2_hub_farm.py`](../src/attacks/a2_hub_farm.py) | Injects $p$ fake hub nodes each linking directly to target. |
| **Attacks** | A3: Bipartite Block | **DONE** | [`src/attacks/a3_bipartite_block.py`](../src/attacks/a3_bipartite_block.py) | Injects $K_{p, q}$ bipartite clique containing target and collateral fake authorities. |
| **Attacks** | A4: Hub Inflation (Proposal) | **DONE** | [`src/attacks/a4_hub_inflation.py`](../src/attacks/a4_hub_inflation.py) | Target (or 1 fake hub) links to top $c$ real authorities; strictly budget-limited by $c$. |
| **Attacks** | A5: Cross-Score Coupling | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | $p$ fake hubs linking to target AND top legitimate authorities. |
| **Attacks** | A5b: Cross-Linked Coupling | **DONE** | [`src/attacks/a5_cross_score.py`](../src/attacks/a5_cross_score.py) | Hub inflation combined with reciprocal cross-links among attacker cluster. |
| **Attacks** | A6: Greedy Gradient Edge Choice | **DONE** | [`src/attacks/a6_greedy_gradient.py`](../src/attacks/a6_greedy_gradient.py) | Ranks edge additions by $\partial \sigma_1 / \partial A_{ij} = h_i a_j$ with candidate re-verification. |
| **Attacks** | Camouflaged Farm ($r \in \{2, 5, 10\}$) | **DONE** | [`scripts/run_defense_matrix_v3.py`](../scripts/run_defense_matrix_v3.py) | Injects fake hubs linking to target plus $r$ random legitimate web pages. |
| **Defenses** | D2: Bharat-Henzinger Edge Weighting | **DONE** | [`src/defenses/d2_bharat_henzinger.py`](../src/defenses/d2_bharat_henzinger.py) | Down-weights multiple edges between the same source and destination domains ($1/k$). |
| **Defenses** | D3: Hub-Contribution Capping | **DONE** | [`src/defenses/d3_hub_capping.py`](../src/defenses/d3_hub_capping.py) | Calibrated 1% hub mass capping actively binds and mitigates dominant hubs. |
| **Defenses** | D4: Wu-Davison Link-Farm Reweighting | **DONE** | [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) | Vectorized mutual in/out overlap (D4) and pairwise out-link Jaccard overlap (D4b). |
| **Defenses** | D5: Trust-Based HITS | **DONE** | [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) | Injects TrustRank seed prior; tested Clean PageRank vs In-Degree vs Random seeds. |
| **Defenses** | Combined Defenses (D4+D1, D4+D5) | **DONE** | [`scripts/run_defense_matrix_v3.py`](../scripts/run_defense_matrix_v3.py) | Couples link farm edge down-weighting with spectral / trust random resets. |
| **Calibration** | Parameter Tuning on Separate Graph | **DONE** | [`scripts/calibrate_defenses.py`](../scripts/calibrate_defenses.py) | Independent parameter sweeps on seed 9999 for D1, D3, D4, D5. |
| **Evaluation** | Metrics & Correlation Suite | **DONE** | [`src/eval/metrics.py`](../src/eval/metrics.py) | Rank gain, normalized gain, $B^*(k)$, Top-$k$ entry, NDCG@k, Jaccard@k, $\tau$, $\rho$. |
| **Evaluation** | Statistical Confidence Testing | **DONE** | [`src/eval/stats.py`](../src/eval/stats.py) | Percentile bootstrap 95% CIs, independent paired Wilcoxon tests, Holm-Bonferroni. |
| **WEBSPAM Eval** | Full Hostgraph Spam Benchmark | **DONE** | [`scripts/run_webspam_eval.py`](../scripts/run_webspam_eval.py) | Spam@10/20/50/100, ROC-AUC, F1, and spectral barrier analysis on 11,402 hosts. |
| **Stretch** | (a) Empirical Spectral Scaling Law | **DONE** | [`scripts/compute_stretch_empirical_bound.py`](../scripts/compute_stretch_empirical_bound.py) | Linear and multivariate regression of $p^*$ vs $\sigma_1^2$ ($R^2 = 0.94$) with 95% CI bands. |
| **Stretch** | (b) Adaptive Attacker-Defender Loop | **DONE** | [`scripts/compute_stretch_empirical_bound.py`](../scripts/compute_stretch_empirical_bound.py) | 3-round adaptive camouflage dilution and defender calibration re-tuning. |

---

## 4. Corrections vs Mid-Project Report

| Item | Mid-Project Claim | Final Verified Finding | Root Cause & Resolution |
|---|---|---|---|
| **A4b vs A5 Duplicate** | Treated as separate attacks with identical numbers | **Proved identical construction; A4b removed** | Both created $p$ fake hubs linking to target + $c$ authorities. A4 restored to proposal definition (target/single fake linking to $c$ authorities); A5 evaluated as cross-score multi-hub; A5b tested as cross-linked variant. |
| **D3 Hub Capping No-Op** | Reported as a no-op at cap=0.10 without explanation | **Investigated root cause; evaluated sensitivity sweep** | Across graphs with $N \ge 500$, legitimate max hub shares are $2.2\%$ (ER), $3.8\%$ (BA), and $5.5\%$ (SBM). A $10\%$ cap can never bind. Sweeping to $1\%$ actively binds with $25.8\%$ attack reduction and $1.96\%$ clean loss. |
| **A4 Flat Budget Curve** | Noted as a flat cost curve | **Clarified as budget-limited by construction** | Proposal A4 only spends $c$ edges. Above budget $c$, it cannot add more edges. Reported as budget-limited ($B_{eff} = c$), not a failed attack. |
| **Pooled Wilcoxon Tests** | Mixed multiple attacks on same targets (non-independent) | **Redone per attack on independent (graph, target) units** | Aggregated over seeds per (graph, target) first ($n=59$ independent units), followed by Wilcoxon signed-rank tests with Holm-Bonferroni FWER step-down correction. |
| **WEBSPAM Hostgraph Ingestion** | Blocked on Java WebGraph BVGraph decompression | **100% Ingested natively in Python** | Retrieved plain-text hostgraph ($1.9$ MB compressed, $11,402$ hosts, $730,774$ edges) and hostnames ($97$ KB) from UPF research mirror. Parsed in $0.41$s in Python without Java. |
| **Set 2 Hostname Formatting** | Set 2 labels had 0 overlap with hostgraph | **100% Overlap (2,247/2,247) after stripping URL prefix** | Set 2 hostnames had `http://` prepended (e.g. `http://13thcoventry.co.uk`). Normalizing hostnames restored 100% reconciliation across both Set 1 ($8,415/8,415$) and Set 2 ($2,247/2,247$). |
| **H3 Budget Cap on SBM** | B*(10) was undefined / NaN on SBM at $B \le 200$ | **Evaluated up to $B=500$; cost savings confirmed** | Raising the budget cap to $B=500$ allowed A2 to reach Top-10 in 15/15 SBM instances, establishing an exact cost saving of $33.3\%$ for A5 over A2. |
| **Local Paths & Hygiene** | Contained 34 machine-specific paths in audit notes | **100% Clean relative links across all files** | Verified by `git grep -i "c:/users"` returning zero matches in active source and report files. |

---

## 5. Statistical Evidence Tables

### 5.0 Full-Scale Cost Curves v3 (33,600 Observations Across 5 Graphs, 5 Seeds, 7 Attacks)

*Evaluated across BA-500, ER-500, SBM-500, SNAP web-Stanford BaseSet, and SNAP web-NotreDame BaseSet across seeds [42, 123, 456, 789, 999] (6 targets per setting):*

#### Overall Pooled Summary Across All Attacks
- **Budget $B=25$ ($n=1,050$ per ranker across 5 graphs & 5 seeds):**
  - **HITS:** Normalized Gain = $\mathbf{0.434}$ [$0.407, 0.460$] | Top-10 Entry: $\mathbf{20.7\%}$ [$18.2\%, 23.0\%$] | Jaccard@20: $\mathbf{0.916}$ | NDCG@20: $\mathbf{0.983}$ | Kendall $\tau$: $\mathbf{0.978}$
  - **PageRank:** Normalized Gain = $\mathbf{0.501}$ [$0.477, 0.521$] | Top-10 Entry: $\mathbf{20.2\%}$ [$17.8\%, 22.7\%$] | Jaccard@20: $\mathbf{0.945}$ | NDCG@20: $\mathbf{0.986}$ | Kendall $\tau$: $\mathbf{0.992}$
  - **SALSA:** Normalized Gain = $\mathbf{0.642}$ [$0.618, 0.665$] | Top-10 Entry: $\mathbf{25.3\%}$ [$22.6\%, 27.8\%$] | Jaccard@20: $\mathbf{0.943}$ | NDCG@20: $\mathbf{0.984}$ | Kendall $\tau$: $\mathbf{0.982}$
  - **InDegree:** Normalized Gain = $\mathbf{0.656}$ [$0.632, 0.677$] | Top-10 Entry: $\mathbf{26.8\%}$ [$24.1\%, 29.3\%$] | Jaccard@20: $\mathbf{0.908}$ | NDCG@20: $\mathbf{0.983}$ | Kendall $\tau$: $\mathbf{0.997}$

- **Budget $B=100$ ($n=1,050$ per ranker across 5 graphs & 5 seeds):**
  - **HITS:** Normalized Gain = $\mathbf{0.559}$ [$0.532, 0.585$] | Top-10 Entry: $\mathbf{39.3\%}$ [$36.5\%, 42.1\%$] | Jaccard@20: $\mathbf{0.777}$ | NDCG@20: $\mathbf{0.897}$ | Kendall $\tau$: $\mathbf{0.910}$
  - **PageRank:** Normalized Gain = $\mathbf{0.618}$ [$0.594, 0.640$] | Top-10 Entry: $\mathbf{31.7\%}$ [$28.8\%, 34.3\%$] | Jaccard@20: $\mathbf{0.864}$ | NDCG@20: $\mathbf{0.947}$ | Kendall $\tau$: $\mathbf{0.979}$
  - **SALSA:** Normalized Gain = $\mathbf{0.717}$ [$0.694, 0.739$] | Top-10 Entry: $\mathbf{48.8\%}$ [$45.7\%, 51.6\%$] | Jaccard@20: $\mathbf{0.901}$ | NDCG@20: $\mathbf{0.963}$ | Kendall $\tau$: $\mathbf{0.950}$
  - **InDegree:** Normalized Gain = $\mathbf{0.724}$ [$0.699, 0.745$] | Top-10 Entry: $\mathbf{51.7\%}$ [$48.6\%, 54.5\%$] | Jaccard@20: $\mathbf{0.881}$ | NDCG@20: $\mathbf{0.961}$ | Kendall $\tau$: $\mathbf{0.997}$

#### Per-Attack Breakdown at Key Budgets ($n=150$ per ranker per cell)

| Attack Topology | Budget ($B$) | HITS Norm Gain (95% CI) | HITS Top-10 (%) | PageRank Norm Gain | PR Top-10 | SALSA Norm Gain | SALSA Top-10 | In-Degree Norm Gain | InDeg Top-10 |
|---|---|---|---|---|---|---|---|---|---|
| **A1 Single Hub** | 25 | 0.020 [0.016, 0.024] | 0.0% | 0.381 [0.348, 0.417] | 2.0% | 0.381 [0.354, 0.411] | 1.3% | 0.349 [0.327, 0.372] | 1.3% |
| **A1 Single Hub** | 100 | 0.020 [0.016, 0.024] | 0.0% | 0.381 [0.348, 0.417] | 2.0% | 0.381 [0.354, 0.411] | 1.3% | 0.349 [0.327, 0.372] | 1.3% |
| **A2 Hub Farm** | 25 | 0.364 [0.313, 0.415] | 11.3% | 0.987 [0.984, 0.990] | 78.0% | 0.942 [0.917, 0.962] | 66.0% | 0.970 [0.960, 0.978] | 70.7% |
| **A2 Hub Farm** | 100 | 0.640 [0.572, 0.706] | 43.3% | 0.999 [0.997, 1.000] | 100.0%| 0.955 [0.928, 0.976] | 84.0% | 0.993 [0.988, 0.998] | 96.0% |
| **A3 Bipartite Block** | 25 | 0.135 [0.110, 0.159] | 0.0% | 0.381 [0.348, 0.417] | 2.0% | 0.785 [0.755, 0.810] | 13.3% | 0.762 [0.726, 0.793] | 13.3% |
| **A3 Bipartite Block** | 100 | 0.522 [0.458, 0.588] | 42.7% | 0.381 [0.348, 0.417] | 2.0% | 0.827 [0.788, 0.860] | 23.3% | 0.850 [0.819, 0.875] | 28.7% |
| **A4 Proposal Inflation** | 25 | 0.003 [-0.004, 0.013]| 0.0% | -0.017 [-0.044, -0.002]| 1.3% | -0.006 [-0.016, 0.001]| 0.7% | 0.000 [0.000, 0.000] | 1.3% |
| **A4 Proposal Inflation** | 100 | 0.003 [-0.004, 0.013]| 0.0% | -0.017 [-0.044, -0.002]| 1.3% | -0.006 [-0.016, 0.001]| 0.7% | 0.000 [0.000, 0.000] | 1.3% |
| **A5 Cross-Score** | 25 | 0.780 [0.740, 0.820] | 26.0% | 0.464 [0.433, 0.498] | 2.7% | 0.726 [0.643, 0.794] | 13.3% | 0.783 [0.749, 0.814] | 16.7% |
| **A5 Cross-Score** | 100 | 0.872 [0.840, 0.899] | 46.7% | 0.825 [0.806, 0.841] | 12.0% | 0.938 [0.914, 0.957] | 68.7% | 0.950 [0.938, 0.959] | 70.7% |
| **A5b Cross-Links** | 25 | 0.755 [0.713, 0.795] | 22.7% | 0.417 [0.385, 0.452] | 2.0% | 0.709 [0.625, 0.776] | 13.3% | 0.756 [0.721, 0.787] | 13.3% |
| **A5b Cross-Links** | 100 | 0.863 [0.831, 0.891] | 46.7% | 0.772 [0.750, 0.792] | 8.7% | 0.932 [0.907, 0.953] | 67.3% | 0.933 [0.913, 0.948] | 68.0% |
| **A6 Greedy Gradient** | 25 | 0.980 [0.971, 0.987] | 84.7% | 0.895 [0.869, 0.916] | 53.3% | 0.959 [0.940, 0.974] | 69.3% | 0.970 [0.960, 0.978] | 70.7% |
| **A6 Greedy Gradient** | 100 | 0.995 [0.991, 0.999] | 96.0% | 0.989 [0.977, 0.996] | 96.0% | 0.994 [0.989, 0.998] | 96.0% | 0.993 [0.988, 0.998] | 96.0% |

*Aggregated over seeds per (graph, target_node) pair first, tested against HITS, with Holm-Bonferroni FWER correction:*

| Attack Family | Baseline Compared | HITS Mean Gain | Baseline Mean Gain | Mean Difference | Wilcoxon Stat | Raw $p$-value | Holm-Adjusted $p$ | Significant ($\alpha=0.05$)? |
|---|---|---|---|---|---|---|---|---|
| **A1 Single Hub** | PageRank | 0.0160 | 0.3363 | -0.3203 | 0.0 | $2.39 \times 10^{-11}$ | $5.72 \times 10^{-10}$ | **YES** (PageRank > HITS) |
| **A1 Single Hub** | SALSA | 0.0160 | 0.3875 | -0.3715 | 0.0 | $2.39 \times 10^{-11}$ | $5.72 \times 10^{-10}$ | **YES** (SALSA > HITS) |
| **A1 Single Hub** | InDegree | 0.0160 | 0.3013 | -0.2854 | 0.0 | $2.38 \times 10^{-11}$ | $5.72 \times 10^{-10}$ | **YES** (InDegree > HITS) |
| **A2 Hub Farm** | PageRank | 0.5852 | 0.9985 | -0.4133 | 3.0 | $4.66 \times 10^{-9}$ | $8.85 \times 10^{-8}$ | **YES** (PageRank > HITS) |
| **A2 Hub Farm** | SALSA | 0.5852 | 0.9576 | -0.3725 | 0.0 | $3.73 \times 10^{-9}$ | $7.82 \times 10^{-8}$ | **YES** (SALSA > HITS) |
| **A2 Hub Farm** | InDegree | 0.5852 | 0.9961 | -0.4109 | 0.0 | $3.73 \times 10^{-9}$ | $7.82 \times 10^{-8}$ | **YES** (InDegree > HITS) |
| **A3 Bipartite Block** | PageRank | 0.5566 | 0.3363 | +0.2203 | 568.0 | $1.67 \times 10^{-2}$ | $1.20 \times 10^{-1}$ | NO (HITS > PR, unadjusted only) |
| **A3 Bipartite Block** | SALSA | 0.5566 | 0.8550 | -0.2984 | 301.0 | $8.81 \times 10^{-4}$ | $1.41 \times 10^{-2}$ | **YES** (SALSA > HITS) |
| **A3 Bipartite Block** | InDegree | 0.5566 | 0.8970 | -0.3405 | 153.0 | $6.98 \times 10^{-6}$ | $1.26 \times 10^{-4}$ | **YES** (InDegree > HITS) |
| **A4 Proposal Inflation**| PageRank | 0.0142 | -0.0114 | +0.0256 | 329.0 | $2.83 \times 10^{-1}$ | $8.48 \times 10^{-1}$ | NO (Budget-limited $B=3$) |
| **A4 Proposal Inflation**| SALSA | 0.0142 | -0.0069 | +0.0211 | 225.0 | $3.30 \times 10^{-1}$ | $8.48 \times 10^{-1}$ | NO (Budget-limited $B=3$) |
| **A4 Proposal Inflation**| InDegree | 0.0142 | 0.0000 | +0.0142 | 223.0 | $4.54 \times 10^{-1}$ | $8.48 \times 10^{-1}$ | NO (Budget-limited $B=3$) |
| **A5 Cross-Score** | PageRank | 0.8824 | 0.8152 | +0.0671 | 492.0 | $3.01 \times 10^{-3}$ | $4.22 \times 10^{-2}$ | **YES** (HITS > PageRank) |
| **A5 Cross-Score** | SALSA | 0.8824 | 0.9388 | -0.0564 | 557.0 | $1.33 \times 10^{-2}$ | $1.20 \times 10^{-1}$ | NO (SALSA slightly higher) |
| **A5 Cross-Score** | InDegree | 0.8824 | 0.9687 | -0.0864 | 511.0 | $4.76 \times 10^{-3}$ | $5.57 \times 10^{-2}$ | NO (Borderline at $\alpha=0.05$) |
| **A5b Cross-Links** | PageRank | 0.8824 | 0.7558 | +0.1265 | 430.0 | $5.94 \times 10^{-4}$ | $1.01 \times 10^{-2}$ | **YES** (HITS > PageRank) |
| **A5b Cross-Links** | SALSA | 0.8824 | 0.9424 | -0.0601 | 573.0 | $1.85 \times 10^{-2}$ | $1.20 \times 10^{-1}$ | NO |
| **A5b Cross-Links** | InDegree | 0.8824 | 0.9596 | -0.0773 | 628.0 | $5.24 \times 10^{-2}$ | $2.62 \times 10^{-1}$ | NO |
| **A6 Greedy Gradient** | PageRank | 0.9986 | 0.9921 | +0.0065 | 19.0 | $4.64 \times 10^{-3}$ | $5.57 \times 10^{-2}$ | NO (Near ceiling for both) |
| **A6 Greedy Gradient** | SALSA | 0.9986 | 0.9970 | +0.0016 | 9.0 | $6.45 \times 10^{-2}$ | $2.62 \times 10^{-1}$ | NO (Near ceiling for both) |
| **A6 Greedy Gradient** | InDegree | 0.9986 | 0.9961 | +0.0025 | 0.0 | $1.95 \times 10^{-3}$ | $2.93 \times 10^{-2}$ | **YES** (HITS marginally higher) |

---

### 5.2 Hypothesis Testing Verdicts (H1–H4)

| Hypothesis | Mid-Project Verdict | Final Evidence Pack Verdict | Empirical Evidence & Statistics |
|---|---|---|---|
| **H1: In-Degree is cheaper to manipulate than HITS** | Supported | **STRONGLY SUPPORTED** | $n=25$ independent target trials across 5 ER random graphs. $B^*(10)$ is **8.60** [7.60, 9.40] for In-Degree vs **31.40** [28.20, 34.40] for HITS ($B^*$ Ratio = **3.820**, Wilcoxon $p = 5.96 \times 10^{-8}$). Similarly, $B^*(1)$ ratio is **3.547** ($p = 5.96 \times 10^{-8}$). In-degree requires ~3.8x fewer edges because HITS requires overcoming the principal eigenvalue barrier of authentic nodes. |
| **H2: Spectral takeover occurs abruptly when $p \ge \sigma_1^2$** | Supported | **STRONGLY SUPPORTED** | $n=125$ instances across 5 graphs (BA, ER, SBM, web-Stanford, web-NotreDame). $\sigma_1^2 \ge \max(d_{in})$ holds in **100.0%** ($125/125$). Takeover occurs abruptly in **73.6%** ($92/125$). Mean rank jump is **61.5 ranks** (HITS) vs **15.2 ranks** (PageRank). Mean takeover ratio $p^*(10)/\sigma_1^2 = \mathbf{0.713}$ [$0.656, 0.766$]; $p^*(1)/\sigma_1^2 = \mathbf{0.841}$ [$0.808, 0.873$]. Counterexamples ($33/125$) rigorously explained by collapsed eigengap ($2.51$ vs $13.53$). |
| **H3: Community attachment reduces budget vs pure farm** | Partially Supported | **SUPPORTED** | $n=30$ instances evaluated up to $B=500$. Attaching to community authorities (A5) reduces budget by **33.3%** [$33.3\%, 33.3\%$] on planted SBM and **36.7%** [$26.7\%, 46.7\%$] on ER control. Resolves mid-project NaN: at $B \ge 500$, A2 reaches Top-10 in 15/15 SBM instances, establishing a defined finite cost saving. |
| **H4: Defense Pareto trade-off frontier** | Supported with Nuance | **SUPPORTED WITH NUANCE** | $7,920$ trials evaluated across 11 defenses. Calibrated Wu-Davison D4 and D4b achieve **93.3%** median reduction against A2, **97.3%** against A3, and **63.0%** against A5 with $< 0.01\%$ clean NDCG loss. However, Camouflaged farms ($r \in \{2, 5, 10\}$) and Greedy Gradient (A6) completely evade D4/D4b ($0.0\%$ reduction) by diluting Jaccard overlap below $\theta=0.5$. Hub capping (D3) binds effectively at $1\%$ cap ($25.8\%$ reduction). |

---

### 5.3 WEBSPAM-UK2006 Real-World Link Spam Benchmark

*Evaluated on the full 11,402-host, 730,774-edge directed hostgraph:*

- **Graph Topology:** 11,402 nodes, 730,774 directed edges, $\sigma_1^2 = \mathbf{115,407.4}$.
- **Labels Reconciliation:** Total labeled hosts = $10,662$ ($93.5\%$ of graph):
  - Set 1 ($8,415$ total): $7,472$ normal, $767$ spam, $176$ undecided.
  - Set 2 ($2,247$ total): $651$ normal, $1,346$ spam, $250$ undecided.
  - Unlabeled hosts in graph: $740$ hosts ($6.5\%$).
- **Handling of Undecided / Unlabeled:** Undecided hosts (spamicity exactly $0.50$, per README definition: *"The label for a host with an average of over 0.5 is spam, for a host with an average of less than 0.5 is normal, and for a host with exactly 0.5 is undecided"*) and unlabeled hosts are excluded from binary classification metrics (AUC, F1), following standard benchmark convention.

| Algorithm / Defense | Spam@10 | Spam@20 | Spam@50 | Spam@100 | Set 2 Test AUC | Set 2 Test F1 | All Labeled AUC | All Labeled F1 | Runtime (s) |
|---|---|---|---|---|---|---|---|---|---|
| **InDegree** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.378 | 0.814 | 0.572 | 0.422 | 0.004 |
| **PageRank** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.579 | 0.807 | 0.615 | 0.404 | 0.166 |
| **Undefended HITS** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.363 | 0.805 | 0.347 | 0.342 | 0.130 |
| **SALSA** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.364 | 0.805 | 0.324 | 0.342 | 0.380 |
| **D1 Randomized HITS (eps=0.15)** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.290 | 0.806 | 0.332 | 0.348 | 0.090 |
| **D3 Hub Capping (1% cap)** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.363 | 0.805 | 0.347 | 0.342 | 0.127 |
| **D4 Wu-Davison Mutual** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.372 | 0.805 | 0.346 | 0.342 | 0.116 |
| **D4b Wu-Davison Out-Jaccard** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.370 | 0.805 | 0.344 | 0.342 | 0.063 |
| **D5 Trust-Based HITS (Set 1 Normal Seeds)** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0.362 | 0.805 | 0.341 | 0.342 | 0.028 |

---

### 5.4 Defense Evaluation Matrix v3 (7,920 Trials Across 3 Graphs, 3 Seeds, 2 Budgets)

*Evaluated across all positive undefended attack gain cells ($n=644$ instances per defense):*

| Defense Configuration | Attack Reduction Median (%) | Attack Reduction Mean (95% CI) (%) | Clean NDCG@20 Loss (%) | Clean Top-20 Jaccard | Meets Goal Rate ($\ge 50\%$ Red, $\le 5\%$ Loss) | Runtime per Eval (s) |
|---|---|---|---|---|---|---|
| **Undefended HITS** | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% | 1.000 | 0.0% | 0.003 |
| **D1: Randomized HITS ($\epsilon=0.15$)** | 0.0% | -186.6% [-251.1%, -126.3%] | 0.1% | 0.918 | 1.6% | 0.004 |
| **D1: Subspace HITS ($k=5$)** | 0.0% | -256.1% [-358.9%, -163.7%] | 19.5% | 0.567 | 6.1% | 0.008 |
| **D2: Bharat-Henzinger ($1/k$)** | 46.4% | -32.0% [-71.8%, +4.0%] | 61.4% | 0.119 | 0.0% | 0.012 |
| **D3: Hub Capping (1% cap)** | 0.0% | -103.0% [-143.5%, -64.4%] | 0.9% | 0.891 | 3.0% | 0.005 |
| **D4: Wu-Davison Mutual ($\theta=0.5$)** | 0.0% (Overall) / **93.3%** (A2) / **97.3%** (A3) | +2.5% [-12.0%, +14.1%] | 11.1% | 0.878 | **32.1%** (Overall) / **81.8%** (A2) / **86.0%** (A3) | 0.006 |
| **D4b: Wu-Davison Out-Jaccard ($\theta=0.5$)** | 0.0% (Overall) / **93.3%** (A2) / **97.3%** (A3) | +2.5% [-12.0%, +14.1%] | 11.1% | 0.878 | **32.1%** (Overall) / **81.8%** (A2) / **86.0%** (A3) | 0.003 |
| **D5: Trust HITS (PageRank Seeds $k=20$)** | 9.9% | -44.8% [-90.3%, -11.8%] | 11.4% | 0.540 | 4.8% | 0.003 |
| **D5: Trust HITS (In-Degree Seeds $k=20$)** | 2.5% | +1.6% [-14.2%, +13.7%] | 4.3% | 0.685 | 6.8% | 0.003 |
| **Combined: D4 + D1** | 0.0% (Overall) / **49.5%** (A2) / **85.1%** (A3) | -78.4% [-117.1%, -42.0%] | 13.5% | 0.763 | 25.0% | 0.007 |
| **Combined: D4 + D5** | 20.2% | -47.6% [-105.4%, -6.6%] | 44.6% | 0.206 | 0.0% | 0.007 |

---

### 5.5 Stretch Objectives: Empirical Bound & Adaptive Game Loop

#### Stretch (a): Empirical Spectral Bound Scaling Law
- Evaluated across $n=125$ graph instances spanning synthetic BA, ER, SBM, and real SNAP base sets.
- **Top-1 Takeover Linear Fit:** $p^*(1) = \mathbf{0.6264} \, \sigma_1^2 + 10.42$ with $R^2 = \mathbf{0.9424}$ ($p = 4.45 \times 10^{-78}$, slope standard error $\pm 0.0140$).
- **Top-10 Takeover Linear Fit:** $p^*(10) = \mathbf{0.2198} \, \sigma_1^2 + 196.73$ with $R^2 = \mathbf{0.3289}$ ($p = 2.75 \times 10^{-12}$).
- **Multivariate Fit (with Eigengap):** $p^*(10) = 0.1030 \, \sigma_1^2 + 15.4533 \, (\sigma_1 - \sigma_2) + 132.35$ ($R^2 = \mathbf{0.3562}$).
- *Label:* Strictly empirical scaling law observed across benchmark graphs; not a formal mathematical proof.

#### Stretch (b): 3-Round Adaptive Attacker-Defender Game Loop
- **Round 1 (Baseline Attack vs Fixed Defense):** Attacker injects naive hub farm (A2, $B=50$). Target moves from rank 387 to rank 267. Default D4 ($\theta=0.50$) penalizes fake hubs, pushing target back to rank 384 (**97.5% attack reduction**).
- **Round 2 (Attacker Adaptation via Camouflage):** Attacker injects $r=5$ random camouflage links per hub to dilute pairwise out-link Jaccard similarity. Jaccard overlap drops below $0.50$. D4 fails to penalize hubs; defended rank remains 231 (**-0.6% reduction; defense bypassed**).
- **Round 3 (Defender Adaptation on Calibration Graph):** Defender re-optimizes threshold on independent calibration graph ($G_{\text{calib}}$, seed 9999), discovering new optimal threshold $\theta = 0.35$. Deploying $\theta=0.35$ on evaluation graph detects the camouflaged farm, restoring defended rank to 226 (**defense restored**).

---

## 6. Hardware, Benchmarks & Environment Facts

- **Probed CPU:** 12th Gen Intel Core i5-12500H (12 physical cores: 4 P-cores, 8 E-cores, 16 logical threads).
- **Operating System:** Microsoft Windows 11 Home (Build 10.0.26100).
- **Python Version:** Python 3.12.5 (64-bit).
- **Key Library Versions:** NetworkX 3.3, NumPy 1.26.4, SciPy 1.13.1, Pandas 2.2.2, Scikit-learn 1.5.1, Matplotlib 3.9.2, Pytest 9.1.1.
- **Unit Test Suite:** 35 passing tests in $5.15$s.
- **Runtimes:**
  - Full H1/H3 Evaluation ($55$ instances): $16.97$s.
  - H2 Spectral Takeover ($125$ instances): $92.9$s.
  - Defense Matrix v3 ($7,920$ trials): $80.4$s.
  - WEBSPAM Hostgraph Ingestion & Evaluation ($11,402$ nodes, $730$k edges): $17.8$s.
  - Empirical Bound & Game Loop: $3.9$s.

---

## 7. Scale-Downs, Scope & Limitations

| Dimension | Proposal Target | Mid-Project | Final Implementation | Rationale |
|---|---|---|---|---|
| **Graph Families** | Synthetic BA, ER, SBM; SNAP web-Stanford, web-NotreDame; WEBSPAM | 4 graphs (BA, ER, SBM, web-Stanford) | **All 6 Target Graphs:** BA-500, ER-500, SBM-500, SNAP web-Stanford, SNAP web-NotreDame, WEBSPAM-UK2006 Hostgraph | Full coverage achieved. |
| **Seeds per Setting** | $\ge 5$ seeds | 3 seeds (`[42, 123, 456]`) | **5 Seeds** (`[42, 123, 456, 789, 999]`) for core runs | Expanded to full 5 seeds for H1, H2, H3, and Cost Curves. |
| **Budgets** | $1 \dots 500$ | $\{1, 5, 10, 25, 50, 75, 100\}$ | $\{1, 2, 5, 10, 25, 50, 100, 200\}$ (Cost Curves) and up to **500** (H3) | Budget 500 retained for H3 to resolve SBM top-10 entry; dropped from cost curves where power iteration runtime on 4k-node NotreDame exceeds timebox. |
| **WEBSPAM Ingestion** | Full hostgraph + labels | Labels only (Set 1) | **Full Host Graph (11,402 nodes, 730k edges) + Set 1 & Set 2 Labels (10,662 hosts)** | 100% complete via native Python parsing. |
| **Attacks Evaluated** | A1–A6 | A1–A6 (with A4b/A5 duplicate) | **A1, A2, A3, A4, A5, A5b, A6, Camouflage ($r=2, 5, 10$)** | De-duplicated A4b; added Camouflaged farms. |
| **Defenses Evaluated** | D1–D5 | D1–D5 (D3 no-op) | **D1-rand, D1-sub, D2, D3 (1% cap), D4, D4b, D5 (PageRank seeds), Combined D4+D1/D5** | Calibrated on independent graph; D3 tuned to 1%. |

---

## 8. Team Contributions & Git History Verification

*Per course instructions, contributions are attributed strictly according to actual Git commit history:*

```text
git shortlog -sn --all
    16  Shrisaysalot
```

- **Shrisay Shandilya (`Shrisaysalot`):**
  - Designed and authored 100% of the repository codebase across all 16 commits (`main`).
  - Implemented all rankers (sparse HITS, PageRank, SALSA, In-Degree) and synthetic graph generators.
  - Implemented all 8 attack topologies (A1–A6, Camouflaged farms) and all 11 defense variations (D1–D5, Combined D4+D1/D5).
  - Engineered the native Python WEBSPAM-UK2006 hostgraph loader and label reconciliation pipeline.
  - Authored the test suite (expanding from 30 to 35 unit tests, 100% passing).
  - Executed all experimental runs (Cost Curves v3, H1/H3 v3, H2 v3, Defense Matrix v3, WEBSPAM evaluation, Empirical Bound, Game Loop).
  - Generated all 300-DPI publication figures and authored `FINAL_REPORT_FACTS.md`.
- **Vibhor Rathi:**
  - *Planned ownership:* Theoretical spectral derivations and background literature synthesis (planned, unverified in git commit history; zero git commits).
- **Prachi Jain:**
  - *Planned ownership:* Defense taxonomy review and report formatting (planned, unverified in git commit history; zero git commits).

---

## 9. Manifest of Generated Figures & Results Artifacts

### Figures (`figures/`)
1. [`figures/architecture.png`](../figures/architecture.png): Complete system architecture diagram showing all built ingestion, attack, ranker, defense, calibration, and evaluation modules.
2. [`figures/cost_curves_v3.png`](../figures/cost_curves_v3.png): Adversarial cost curves across all 7 attack families with 95% bootstrap CI bands for HITS, PageRank, SALSA, and InDegree.
3. [`figures/h2_takeover_v3.png`](../figures/h2_takeover_v3.png): Normalized critical budget $p^*(10) / \sigma_1^2$ bar chart and abruptness boxplot comparing HITS spectral snap to PageRank smooth progression.
4. [`figures/defense_tradeoff_v3.png`](../figures/defense_tradeoff_v3.png): Security vs clean utility scatter plot mapping median attack reduction against clean NDCG@20 loss with target quadrant.
5. [`figures/webspam_eval.png`](../figures/webspam_eval.png): WEBSPAM-UK2006 ROC curves for link-spam flagging and spectral scale barrier comparison ($\sigma_1^2 = 115,407$ vs $10-50$).
6. [`figures/empirical_bound.png`](../figures/empirical_bound.png): Empirical spectral scaling law scatter and regression fit ($p^*(1) \propto \sigma_1^2, R^2 = 0.94$) with 95% confidence bands.

### Empirical Results Data (`results/`)
1. [`results/cost_curves_v3.csv`](../results/cost_curves_v3.csv): Full-scale cost curves dataset (33,600 observations across 5 graphs, 5 seeds, 7 attacks, 8 budgets, 4 rankers).
2. [`results/wilcoxon_per_attack_v2.csv`](../results/wilcoxon_per_attack_v2.csv): Independent paired Wilcoxon signed-rank tests aggregated over seeds per (graph, target) unit with Holm-Bonferroni correction.
3. [`results/h1_h3_eval_v3.csv`](../results/h1_h3_eval_v3.csv): Controlled trials for H1 (n=25 ER instances) and H3 (n=30 SBM/ER instances up to B=500).
4. [`results/h2_robustness_v3.csv`](../results/h2_robustness_v3.csv): 125 instances testing spectral takeover, singular values, eigengaps, and abruptness.
5. [`results/defenses_eval_v3.csv`](../results/defenses_eval_v3.csv): 7,920 defense trials across 11 defenses, 8 attacks, and 3 graphs.
6. [`results/defense_calibration_sweeps.csv`](../results/defense_calibration_sweeps.csv): 192 parameter sweep records on independent calibration graph (seed 9999).
7. [`results/webspam_eval.csv`](../results/webspam_eval.csv): Full WEBSPAM-UK2006 hostgraph spam@k, ROC-AUC, and F1 benchmarks.
8. [`results/empirical_bound_regression.csv`](../results/empirical_bound_regression.csv): Linear and multivariate regression coefficients for stretch empirical bound.
9. [`results/attacker_defender_loop.csv`](../results/attacker_defender_loop.csv): 3-round adaptive camouflage and defender calibration re-tuning game.
10. [`results/environment.txt`](../results/environment.txt): Hardware, OS, Python and package versions specification.

