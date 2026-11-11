# Final Evidence Pack & Fact Sheet (v3.1 Final)
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
- **Repository:** https://github.com/shrisaysalot/LinkRank_Under_Attack
- **Date of Final Evidence Pack:** 12 November 2026
- **Final Submission Deadline:** 15 November 2026

---

## 2. Final Implementation Status Table

| Module Category | Component / Module | Status | File Path | Scope & Status Note |
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
| **Defenses** | D4: Wu-Davison Link-Farm Reweighting | **DONE** | [`src/defenses/d4_wu_davison.py`](../src/defenses/d4_wu_davison.py) | Mutual in/out link farm detection (threshold $\theta=0.50$); D4b removed as functionally redundant. |
| **Defenses** | D5: Trust-Based HITS | **DONE** | [`src/defenses/d5_trust_hits.py`](../src/defenses/d5_trust_hits.py) | Injects TrustRank seed prior; tested Clean PageRank ($k=20$) vs In-Degree ($k=20$) seeds. |
| **Defenses** | Combined Defenses (D4+D1, D4+D5) | **DONE** | [`scripts/run_defense_matrix_v3.py`](../scripts/run_defense_matrix_v3.py) | Couples link farm edge down-weighting with spectral / trust random resets. |
| **Calibration** | Parameter Tuning on Separate Graph | **DONE** | [`scripts/calibrate_defenses.py`](../scripts/calibrate_defenses.py) | Independent parameter sweeps on seed 9999 for D1, D3, D4, D5. |
| **Evaluation** | Metrics & Correlation Suite | **DONE** | [`src/eval/metrics.py`](../src/eval/metrics.py) | Rank gain, normalized gain, $B^*(k)$, Top-$k$ entry, NDCG@k, Jaccard@k, $\tau$, $\rho$. |
| **Evaluation** | Statistical Confidence Testing | **DONE** | [`src/eval/stats.py`](../src/eval/stats.py) | Percentile bootstrap 95% CIs, independent paired Wilcoxon tests, Holm-Bonferroni. |
| **WEBSPAM Eval** | Full Hostgraph Clean & Attack | **DONE** | [`scripts/run_webspam_eval_final.py`](../scripts/run_webspam_eval_final.py) | Spam@100..2000, AUC, precision/recall, and real attacks on 11,402 hosts. |
| **Stretch (a)** | Closed-Form Spectral Bound | **NOT PURSUED** | N/A | Scoped out per project plan; focus maintained on empirical core and WEBSPAM. |
| **Stretch (b)** | Game-Theoretic Attacker-Defender Loop | **NOT PURSUED** | N/A | Scoped out per project plan; focus maintained on empirical core and WEBSPAM. |
| **Stretch (c)** | WEBSPAM-UK2007 Classifier | **NOT PURSUED** | N/A | Scoped out per project plan; UK2006 evaluated completely. |

---

## 3. Pipeline Details

1. **Graph Ingestion & Topology:**
   - **Synthetic Graphs ($N=500$):** Barabasi-Albert ($m=3$), Erdos-Renyi ($p=0.012$), Planted Bipartite Stochastic Block Model ($400$ background nodes, $50$ planted hubs, $50$ planted authorities, $p_{in}=0.15, p_{out}=0.005$).
   - **Real SNAP Web Graphs:** `web-Stanford` ($281,903$ nodes, $2,312,497$ edges) and `web-NotreDame` ($325,729$ nodes, $1,497,134$ edges).
   - **Kleinberg Base Sets:** Root set sampled with seed nodes ($|R| \approx 40-80$, scaled down from proposal target of $100-200$ to maintain tractable power iteration times on real SNAP graphs), expanded with forward out-links and up to $d_{in\_max} = 50$ reverse in-links, resulting in induced base subgraphs of $N \approx 500-1000$ nodes.
   - **WEBSPAM-UK2006 Host Graph:** Full real-world host graph comprising $11,402$ nodes and $730,774$ directed edges, with $10,662$ volunteer-labeled hosts ($8,415$ Set 1, $2,247$ Set 2).
2. **Ranker Specifications:**
   - **Sparse HITS:** Power iteration with L1 normalization, convergence tolerance $\text{tol} = 10^{-8}$, $\text{max\_iter} = 200$. Eigengap tracked via SciPy ARPACK sparse SVD (`k=6`).
   - **PageRank:** Teleport damping $\alpha = 0.85$, tolerance $10^{-6}$, exact uniform dangling node mass redistribution.
   - **SALSA:** Bipartite random walk with ergodic jump teleport $\epsilon = 10^{-4}$ to ensure unique stationary distribution on disconnected components.
   - **In-Degree Centrality:** Exact normalized column-sum in-degree ($O(\|E\|)$ time).
3. **Experimental Seeds & Target Selection:**
   - Core runs executed across five fixed seeds: `[42, 123, 456, 789, 999]`.
   - 6 targets selected per graph instance stratified across authority tiers: 2 Low-Rank (initial rank $> 400$), 2 Medium-Rank ($100-300$), 2 Random.

---

## 4. Final Empirical Results & Hypothesis Verdicts

### 4.1 Cost Curves per Attack Family ($n=1,050$ per ranker per budget)

*Dataset:* [`results/cost_curves_final.csv`](../results/cost_curves_final.csv) ($33,600$ total observations across 5 graphs, 5 seeds, 6 targets, 7 attacks, 8 budgets, 4 rankers).

#### Summary Across Budgets (Mean Normalized Rank Gain with Bootstrap 95% CIs)
- **Budget $B=25$ ($n=1,050$ per ranker):**
  - **HITS:** Normalized Gain = $\mathbf{0.434}$ [$0.407, 0.460$] | Top-10 Entry: $\mathbf{20.7\%}$ [$18.2\%, 23.0\%$] | Jaccard@20: $\mathbf{0.916}$ | NDCG@20: $\mathbf{0.983}$
  - **PageRank:** Normalized Gain = $\mathbf{0.501}$ [$0.477, 0.521$] | Top-10 Entry: $\mathbf{20.2\%}$ [$17.8\%, 22.7\%$] | Jaccard@20: $\mathbf{0.945}$ | NDCG@20: $\mathbf{0.986}$
  - **SALSA:** Normalized Gain = $\mathbf{0.642}$ [$0.618, 0.665$] | Top-10 Entry: $\mathbf{25.3\%}$ [$22.6\%, 27.8\%$] | Jaccard@20: $\mathbf{0.943}$ | NDCG@20: $\mathbf{0.984}$
  - **InDegree:** Normalized Gain = $\mathbf{0.656}$ [$0.632, 0.677$] | Top-10 Entry: $\mathbf{26.8\%}$ [$24.1\%, 29.3\%$] | Jaccard@20: $\mathbf{0.908}$ | NDCG@20: $\mathbf{0.983}$

- **Budget $B=100$ ($n=1,050$ per ranker):**
  - **HITS:** Normalized Gain = $\mathbf{0.559}$ [$0.532, 0.585$] | Top-10 Entry: $\mathbf{39.3\%}$ [$36.5\%, 42.1\%$] | Jaccard@20: $\mathbf{0.777}$ | NDCG@20: $\mathbf{0.897}$
  - **PageRank:** Normalized Gain = $\mathbf{0.618}$ [$0.594, 0.640$] | Top-10 Entry: $\mathbf{31.7\%}$ [$28.8\%, 34.3\%$] | Jaccard@20: $\mathbf{0.864}$ | NDCG@20: $\mathbf{0.947}$
  - **SALSA:** Normalized Gain = $\mathbf{0.717}$ [$0.694, 0.739$] | Top-10 Entry: $\mathbf{48.8\%}$ [$45.7\%, 51.6\%$] | Jaccard@20: $\mathbf{0.901}$ | NDCG@20: $\mathbf{0.963}$
  - **InDegree:** Normalized Gain = $\mathbf{0.724}$ [$0.699, 0.745$] | Top-10 Entry: $\mathbf{51.7\%}$ [$48.6\%, 54.5\%$] | Jaccard@20: $\mathbf{0.881}$ | NDCG@20: $\mathbf{0.961}$

#### Per-Attack Breakdown at Budget $B=100$ ($n=150$ per ranker per cell)

| Attack Topology | HITS Norm Gain (95% CI) | HITS Top-10 (%) | PageRank Norm Gain | PR Top-10 | SALSA Norm Gain | SALSA Top-10 | In-Degree Norm Gain | InDeg Top-10 |
|---|---|---|---|---|---|---|---|---|
| **A1: Single Hub** | 0.020 [0.016, 0.024] | 0.0% | 0.381 [0.348, 0.417] | 2.0% | 0.381 [0.354, 0.411] | 1.3% | 0.349 [0.327, 0.372] | 1.3% |
| **A2: Hub Farm** | 0.640 [0.572, 0.706] | 43.3% | 0.999 [0.997, 1.000] | 100.0% | 0.955 [0.928, 0.976] | 84.0% | 0.993 [0.988, 0.998] | 96.0% |
| **A3: Bipartite Block** | 0.522 [0.458, 0.588] | 42.7% | 0.381 [0.348, 0.417] | 2.0% | 0.827 [0.788, 0.860] | 23.3% | 0.850 [0.819, 0.875] | 28.7% |
| **A4: Proposal Inflation** | 0.003 [-0.004, 0.013] | 0.0% | -0.017 [-0.044, -0.002] | 1.3% | -0.006 [-0.016, 0.001] | 0.7% | 0.000 [0.000, 0.000] | 1.3% |
| **A5: Cross-Score** | 0.872 [0.840, 0.899] | 46.7% | 0.825 [0.806, 0.841] | 12.0% | 0.938 [0.914, 0.957] | 68.7% | 0.950 [0.938, 0.959] | 70.7% |
| **A5b: Cross-Links** | 0.863 [0.831, 0.891] | 46.7% | 0.772 [0.750, 0.792] | 8.7% | 0.932 [0.907, 0.953] | 67.3% | 0.933 [0.913, 0.948] | 68.0% |
| **A6: Greedy Gradient** | 0.995 [0.991, 0.999] | 96.0% | 0.989 [0.977, 0.996] | 96.0% | 0.994 [0.989, 0.998] | 96.0% | 0.993 [0.988, 0.998] | 96.0% |

---

### 4.2 Independent Per-Attack Wilcoxon Hypothesis Tests (Holm-Corrected)

*Dataset:* [`results/wilcoxon_per_attack_final.csv`](../results/wilcoxon_per_attack_final.csv)  
*Unit of Observation:* Evaluated at $B=100$ on independent `(graph, target_node)` units aggregated across random seeds ($n_{\text{units}} = 144$ independent pairs per test), avoiding non-independent pooling across attacks:

| Attack Family | Baseline Compared | HITS Mean | Baseline Mean | Mean Diff | Wilcoxon Stat | Raw $p$-value | Holm $p$-value | Significant ($\alpha=0.05$)? |
|---|---|---|---|---|---|---|---|---|
| **A1 Single Hub** | PageRank | 0.0208 | 0.3832 | -0.3623 | 0.0 | $3.25 \times 10^{-25}$ | $6.49 \times 10^{-24}$ | **YES** (PageRank > HITS) |
| **A1 Single Hub** | SALSA | 0.0208 | 0.3815 | -0.3607 | 0.0 | $2.37 \times 10^{-25}$ | $4.97 \times 10^{-24}$ | **YES** (SALSA > HITS) |
| **A1 Single Hub** | InDegree | 0.0208 | 0.3516 | -0.3307 | 0.0 | $4.74 \times 10^{-25}$ | $9.00 \times 10^{-24}$ | **YES** (InDegree > HITS) |
| **A2 Hub Farm** | PageRank | 0.6478 | 0.9985 | -0.3507 | 3.0 | $1.90 \times 10^{-15}$ | $3.42 \times 10^{-14}$ | **YES** (PageRank > HITS) |
| **A2 Hub Farm** | SALSA | 0.6478 | 0.9540 | -0.3062 | 26.0 | $1.10 \times 10^{-13}$ | $1.66 \times 10^{-12}$ | **YES** (SALSA > HITS) |
| **A2 Hub Farm** | InDegree | 0.6478 | 0.9935 | -0.3457 | 0.0 | $3.66 \times 10^{-15}$ | $6.22 \times 10^{-14}$ | **YES** (InDegree > HITS) |
| **A3 Bipartite Block** | PageRank | 0.5270 | 0.3832 | +0.1438 | 321.0 | $6.25 \times 10^{-3}$ | $2.50 \times 10^{-2}$ | **YES** (HITS > PageRank) |
| **A3 Bipartite Block** | SALSA | 0.5270 | 0.8307 | -0.3037 | 81.0 | $4.12 \times 10^{-12}$ | $5.76 \times 10^{-11}$ | **YES** (SALSA > HITS) |
| **A3 Bipartite Block** | InDegree | 0.5270 | 0.8582 | -0.3312 | 19.0 | $1.32 \times 10^{-14}$ | $2.11 \times 10^{-13}$ | **YES** (InDegree > HITS) |
| **A4 Proposal Inflation**| PageRank | 0.0032 | -0.0176 | +0.0208 | 365.0 | $6.62 \times 10^{-1}$ | $1.00$ | NO (Budget-limited $B=3$) |
| **A4 Proposal Inflation**| SALSA | 0.0032 | -0.0070 | +0.0103 | 290.0 | $5.41 \times 10^{-1}$ | $1.00$ | NO (Budget-limited $B=3$) |
| **A4 Proposal Inflation**| InDegree | 0.0032 | 0.0000 | +0.0032 | 253.0 | $7.91 \times 10^{-2}$ | $2.37 \times 10^{-1}$ | NO (Budget-limited $B=3$) |
| **A5 Cross-Score** | PageRank | 0.8734 | 0.8266 | +0.0468 | 258.0 | $5.34 \times 10^{-6}$ | $3.20 \times 10^{-5}$ | **YES** (HITS > PageRank) |
| **A5 Cross-Score** | SALSA | 0.8734 | 0.9407 | -0.0672 | 148.0 | $5.85 \times 10^{-10}$ | $7.02 \times 10^{-9}$ | **YES** (SALSA > HITS) |
| **A5 Cross-Score** | InDegree | 0.8734 | 0.9515 | -0.0781 | 114.0 | $2.22 \times 10^{-11}$ | $2.89 \times 10^{-10}$ | **YES** (InDegree > HITS) |
| **A5b Cross-Links** | PageRank | 0.8644 | 0.7740 | +0.0905 | 179.0 | $2.60 \times 10^{-8}$ | $2.60 \times 10^{-7}$ | **YES** (HITS > PageRank) |
| **A5b Cross-Links** | SALSA | 0.8644 | 0.9366 | -0.0722 | 165.0 | $1.07 \times 10^{-8}$ | $1.18 \times 10^{-7}$ | **YES** (SALSA > HITS) |
| **A5b Cross-Links** | InDegree | 0.8644 | 0.9379 | -0.0734 | 199.0 | $1.38 \times 10^{-7}$ | $1.24 \times 10^{-6}$ | **YES** (InDegree > HITS) |
| **A6 Greedy Gradient** | PageRank | 0.9952 | 0.9888 | +0.0064 | 22.0 | $3.56 \times 10^{-6}$ | $2.49 \times 10^{-5}$ | **YES** (HITS marginally higher) |
| **A6 Greedy Gradient** | SALSA | 0.9952 | 0.9940 | +0.0012 | 10.0 | $1.17 \times 10^{-3}$ | $5.86 \times 10^{-3}$ | **YES** (HITS marginally higher) |
| **A6 Greedy Gradient** | InDegree | 0.9952 | 0.9935 | +0.0017 | 1.0 | $2.82 \times 10^{-6}$ | $2.25 \times 10^{-5}$ | **YES** (HITS marginally higher) |

---

### 4.3 Hypothesis Verdicts (Evaluated Strictly Against Original Proposal Wording)

#### Hypothesis H1: "In-degree centrality is cheaper to manipulate than HITS (lower $B^*$ for equal rank gain)."
- **Verdict:** **SUPPORTED**
- **Empirical Evidence ($n=25$ independent target instances across 5 ER random graphs):**
  - Budget to reach Top-10: In-Degree requires $B^*(10) = \mathbf{8.60}$ edges [95% CI: $7.60, 9.40$] vs HITS $B^*(10) = \mathbf{31.40}$ edges [95% CI: $28.20, 34.20$].
  - Cost Ratio ($B^*_{\text{HITS}} / B^*_{\text{InDeg}}$) = $\mathbf{3.820}$ [95% CI: $3.439, 4.200$] ($p = 5.96 \times 10^{-8}$, Wilcoxon signed-rank test).
  - Budget to reach Rank-1: In-Degree requires $B^*(1) = \mathbf{11.00}$ edges [95% CI: $10.00, 12.00$] vs HITS $B^*(1) = \mathbf{37.60}$ edges [95% CI: $35.20, 40.00$] (ratio = $\mathbf{3.547}$ [95% CI: $3.213, 3.893$], $p = 5.96 \times 10^{-8}$).
- **Mechanism & Limits:** In-degree requires ~3.8x fewer edges because each added in-link directly increases in-degree score by 1, whereas HITS requires overcoming the principal eigenvalue barrier ($\sigma_1^2$) of the legitimate network.

#### Hypothesis H2: "Spectral takeover occurs abruptly at a critical budget $p^* \approx \sigma_1^2$, where the attacker's subgraph eigenvalue exceeds the host graph's leading eigenvalue."
- **Verdict:** **SUPPORTED**
- **Empirical Evidence ($n=125$ instances across 5 graphs: BA-500, ER-500, SBM-500, web-Stanford base set, web-NotreDame base set):**
  - $\sigma_1^2 \ge \max(d_{in})$ holds in **100.0% of instances** ($125/125$).
  - Abrupt takeover occurs in **73.6% of instances** ($92/125$). Mean single-step rank jump is **61.5 ranks** for HITS vs **15.2 ranks** for PageRank.
  - Empirical critical takeover budgets normalize tightly to the leading singular value:
    - Critical Top-10: $p^*(10) / \sigma_1^2 = \mathbf{0.713}$ [95% CI: $0.656, 0.768$].
    - Critical Rank-1: $p^*(1) / \sigma_1^2 = \mathbf{0.841}$ [95% CI: $0.807, 0.876$].
- **Counterexample Diagnostic:** In the 26.4% of instances ($33/125$) where takeover is non-abrupt, the graph exhibits a severely contracted eigengap ($\sigma_1 - \sigma_2 = 2.51$ vs $13.53$ in abrupt cases) and the target begins already near top ranks (mean initial rank $214.9$ vs $465.0$).

#### Hypothesis H3: "Community attachment (A5) reduces attack cost compared to isolated hub farms (A2) in community-structured graphs."
- **Verdict:** **SUPPORTED**
- **Empirical Evidence ($n=30$ instances evaluated up to $B=500$):**
  - On Planted SBM ($n=15$), A5 achieves a mean cost saving of $\mathbf{33.3\%}$ [95% CI: $33.3\%, 33.3\%$].
  - On ER control graphs ($n=15$), A5 achieves a mean cost saving of $\mathbf{36.7\%}$ [95% CI: $26.7\%, 46.7\%$].
  - Both A2 and A5 achieve Top-10 entry in $100\%$ ($30/30$) of instances when budget is expanded to $B=500$, resolving the mid-project undefined/NaN limitation.
- **Mechanism:** Injected hubs linking to existing authorities inherit their high hub-authority scores through mutual reinforcement, requiring fewer total edges than bootstrapping an isolated clique.

#### Hypothesis H4: "Defense Pareto trade-off: link farm detection defenses reduce attack success by at least 50% with less than 5% loss in clean ranking utility."
- **Verdict:** **NOT SUPPORTED GLOBALLY (SUPPORTED WITH NUANCE ONLY FOR ISOLATED TOPOLOGICAL FARMS)**
- **Empirical Evidence ($n=644$ positive undefended gain cells per defense):**
  - Calibrated Wu-Davison D4 ($\theta=0.50$) achieves **93.3% median reduction** against A2 Hub Farm and **97.3%** against A3 Bipartite Block with minimal clean utility loss on synthetic graphs.
  - However, on real web base sets, D4 clean NDCG@20 loss reaches **10.56%** ($> 5\%$).
  - Furthermore, Camouflaged farms ($r \in \{2, 5, 10\}$) and Greedy Gradient (A6) dilute out-link Jaccard similarity below $\theta=0.50$, resulting in **0.0% attack reduction**.
  - Therefore, **no defense achieves $\ge 50\%$ reduction at $\le 5\%$ clean NDCG loss globally across all attack families**.

---

### 4.4 Defense Evaluation Matrix Final ($n=644$ Positive-Gain Cells per Defense Row)

*Dataset:* [`results/defenses_eval_final.csv`](../results/defenses_eval_final.csv) (Evaluated across BA-500, ER-500, and SBM-500; budgets $B \in \{25, 100\}$; seeds $[42, 123, 456]$):

| Defense Configuration | Attack Reduction Median (%) | Attack Reduction Mean (95% CI) (%) | Clean NDCG@20 Loss (%) | Clean Top-20 Jaccard | Meets Goal Rate ($\ge 50\%$ Red, $\le 5\%$ Loss) | Runtime per Eval (s) |
|---|---|---|---|---|---|---|
| **Undefended HITS** | 0.0% | 0.0% [0.0%, 0.0%] | 0.0% | 1.000 | 0.0% | 0.003 |
| **D1: Randomized HITS ($\epsilon=0.15$)** | 0.0% | -186.6% [-251.1%, -126.3%] | 0.1% | 0.916 | 1.6% | 0.003 |
| **D1: Subspace HITS ($k=5$)** | 0.0% | -256.1% [-358.9%, -163.7%] | 18.8% | 0.571 | 6.1% | 0.020 |
| **D2: Bharat-Henzinger ($1/k$)** | 46.4% | -32.0% [-71.8%, +4.0%] | 60.8% | 0.120 | 0.0% | 0.006 |
| **D3: Hub Capping (1% calibrated cap)**| 0.0% | -103.0% [-143.5%, -64.4%] | 1.0% | 0.886 | 3.0% | 0.003 |
| **D4: Wu-Davison Mutual ($\theta=0.5$)** | 0.0% (Overall) / **93.3%** (A2) / **97.3%** (A3) | +2.5% [-12.0%, +14.1%] | 10.6% | 0.884 | **32.1%** (Overall) / **81.8%** (A2) / **86.0%** (A3) | 0.005 |
| **D5: Trust HITS (PageRank Seeds $k=20$)**| 9.9% | -44.8% [-90.3%, -11.8%] | 11.6% | 0.529 | 4.8% | 0.003 |
| **D5: Trust HITS (InDegree Seeds $k=20$)** | 2.5% | +1.6% [-14.2%, +13.7%] | 4.4% | 0.676 | 6.8% | 0.003 |
| **Combined: D4 + D1** | 0.0% (Overall) / **49.5%** (A2) / **85.1%** (A3) | -78.4% [-117.1%, -42.0%] | 12.8% | 0.770 | 25.0% | 0.005 |
| **Combined: D4 + D5** | 20.2% | -47.6% [-105.4%, -6.6%] | 43.1% | 0.212 | 0.0% | 0.005 |

*Per-Attack D4 Breakdown ($n$ positive cells):*
- **A2 Hub Farm ($n=88$):** Median reduction = **93.3%**, Mean = **7.8%**, Meets Goal = **81.8%**.
- **A3 Bipartite Block ($n=86$):** Median reduction = **97.3%**, Mean = **-1.7%**, Meets Goal = **86.0%**.
- **A4 Proposal Inflation ($n=20$):** Median reduction = **0.0%**, Mean = **-61.2%**, Meets Goal = **10.0%**.
- **A5 Cross-Score ($n=90$):** Median reduction = **63.0%**, Mean = **56.3%**, Meets Goal = **65.6%**.
- **A6 Greedy Gradient ($n=90$):** Median reduction = **0.0%**, Mean = **0.0%**, Meets Goal = **0.0%**.
- **Camouflaged Farm $r=2$ ($n=90$):** Median reduction = **-0.4%**, Mean = **-10.1%**, Meets Goal = **0.0%**.
- **Camouflaged Farm $r=5$ ($n=90$):** Median reduction = **-1.2%**, Mean = **-10.3%**, Meets Goal = **0.0%**.
- **Camouflaged Farm $r=10$ ($n=90$):** Median reduction = **-0.4%**, Mean = **-10.4%**, Meets Goal = **0.0%**.

---

### 4.5 WEBSPAM-UK2006 Real-World Host Graph Evaluation & Attack Results

#### Dataset Provenance & Metadata Verification
- **Host Graph File:** `uk-2006-05.hostgraph.txt.gz` ($1,989,390$ bytes compressed, $1.90$ MB).
- **Hostnames File:** `uk-2006-05.hostnames.txt.gz` ($99,037$ bytes compressed, $96.7$ KB).
- **Labels File:** `webspam-uk2006-2.0.tar.gz` ($153,085$ bytes compressed, $149.5$ KB).
- **Source URLs:** `http://chato.cl/webspam/datasets/uk2006/` and DELIS / Universita' "La Sapienza" LAW mirror `http://law.di.unimi.it/webdata/uk-2006-05/`.
- **License / Terms:** Creative Commons Attribution-NonCommercial-ShareAlike 2.5 (CC-BY-NC-SA 2.5). Research and educational non-commercial use only.
- **Set 1 vs Set 2 Disjointness:** Confirmed **0 overlapping hosts** between Set 1 ($8,415$ hosts) and Set 2 ($2,247$ hosts). Total distinct labeled hosts = $10,662$ ($93.5\%$ of graph).
- **Undecided Hosts Treatment:** Undecided hosts (spamicity exactly $0.50$, per README: *"The label for a host with an average of over 0.5 is spam, for a host with an average of less than 0.5 is normal, and for a host with exactly 0.5 is undecided"*) and unlabeled hosts ($740$ hosts, $6.5\%$) are excluded from binary classification metrics.
- **Spam Prevalence:** Set 1 Test Prevalence = $9.31\%$ ($767 / 8,239$); Set 2 Test Prevalence = $67.40\%$ ($1,346 / 1,997$); Combined Labeled Prevalence = $20.64\%$ ($2,113 / 10,236$).

#### Clean Host Graph Ranking Benchmark ($N=11,402$ Hosts, $730,774$ Edges)
*Dataset:* [`results/webspam_clean_ranking_final.csv`](../results/webspam_clean_ranking_final.csv)

| Algorithm / Defense | Spam@100 | Spam@500 | Spam@1000 | Spam@2000 | Median Spam Rank | Median Norm Rank | All Labeled AUC | Set 2 Test AUC | Prevalence-Aware F1 | Runtime (s) |
|---|---|---|---|---|---|---|---|---|---|---|
| **InDegree** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 28 (1.4%) | 6,182.0 | 5,062.0 | 0.428 | 0.622 | 0.019 (All) / 0.770 (Set 2) | 0.005 |
| **PageRank ($\alpha=0.85$)** | 0 (0.0%) | 17 (3.4%)| 30 (3.0%) | 312 (15.6%)| 7,544.0 | 5,042.0 | 0.385 | 0.421 | 0.165 (All) / 0.616 (Set 2) | 0.152 |
| **Undefended HITS** | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 27 (1.4%) | 5,538.0 | 5,622.0 | 0.455 | 0.679 | 0.021 (All) / 0.774 (Set 2) | 0.136 |
| **SALSA ($\epsilon=10^{-4}$)**| 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 30 (1.5%) | 6,145.0 | 5,069.0 | 0.433 | 0.614 | 0.020 (All) / 0.757 (Set 2) | 0.730 |
| **D1 Randomized ($\epsilon=0.15$)**| 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 33 (1.7%) | 5,509.0 | 5,651.0 | 0.461 | 0.686 | 0.022 (All) / 0.776 (Set 2) | 0.083 |
| **D3 Hub Capping (1% cap)**| 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 27 (1.4%) | 5,538.0 | 5,622.0 | 0.455 | 0.679 | 0.021 (All) / 0.774 (Set 2) | 0.127 |
| **D4 Wu-Davison ($\theta=0.5$)**| 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 17 (0.9%) | 5,900.0 | 5,305.0 | 0.415 | 0.650 | 0.014 (All) / 0.761 (Set 2) | 10.339 |
| **D5 Trust HITS (Set 1 Normal)**| 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 7 (0.4%) | 6,350.0 | 4,897.0 | 0.344 | 0.675 | 0.005 (All) / 0.773 (Set 2) | 0.047 |

*Precision & Recall Findings:*
- **Precision at Top 1% ($k=114$ hosts):** **0.0%** across ALL rankers. Natural web spam is completely absent from top authority tiers.
- **Precision at Top 5% ($k=570$ hosts):** **0.0%** for In-Degree, HITS, SALSA, D1, D3, D4, D5 (only PageRank contains $3.8\%$ spam in Top 5%).
- **Precision at Top 10% ($k=1,140$ hosts):** **0.0%** for HITS, D1, D3, D4, D5.

#### Real Attack on Host Graph (10 Targets $\times$ 3 Budgets $\times$ 2 Attacks = 60 Evaluated Trials)
*Dataset:* [`results/webspam_attack_final.csv`](../results/webspam_attack_final.csv)

- **Target Sample:** 10 hosts selected across clean HITS rank tiers (5 Normal: nodes 0, 1, 54, 135, 2544; 5 Spam: nodes 61, 212, 30, 275, 7297), clean ranks spanning $2,177$ to $9,879$.
- **Budgets Evaluated:** $B \in \{10, 100, 1000\}$ fake hub pages.
- **Spectral Scale Barrier ($\sigma_1^2 = 115,407.4$):**
  - At $B = 10$: $p / \sigma_1^2 = 0.000087 \ll 0.713$.
  - At $B = 100$: $p / \sigma_1^2 = 0.000866 \ll 0.713$.
  - At $B = 1000$: $p / \sigma_1^2 = 0.008665 \ll 0.713$.
- **Empirical Attack Findings:**
  - **HITS Spectral Robustness:** Under A2 Hub Farm, even at $B = 1000$ edges, the maximum rank improvement observed across all targets is only **76 ranks** (e.g. from rank 9,879 to 9,803).
  - **Zero Top-100 Entry & Zero Takeover:** Under HITS, Top-100 entry occurs in **0.0% of trials** ($0/60$) and spectral takeover occurs in **0.0% of trials** ($0/60$).
  - **PageRank Vulnerability:** In sharp contrast, PageRank promotes the target to **Rank 1 in 100% of A2 trials at $B=1000$** ($20/20$ trials), exhibiting rank jumps of over $11,000$ positions.
  - **A5 Cross-Score on Host Graph:** Linking to top authorities improves target rank by up to $1,004$ positions at $B=1000$ (e.g. from 9,879 to 8,875), but still remains over $8,700$ positions away from Top-100 entry.
  - **Defenses on Attacked Host Graph:** D3 hub capping ($1\%$ cap) gives rank identical to undefended HITS because no farm hub achieves $1\%$ of total hub mass. Wu-Davison D4 successfully penalizes the fake hubs, reducing attack gain.

---

## 5. Corrections vs Mid-Project Report

| Item | Mid-Project Report State | Final Evidence Pack State | Root Cause & Resolution |
|---|---|---|---|
| **Hypothesis H1 Verdict** | Reported as "Not Supported" | **STRONGLY SUPPORTED** | Mid-project budget scale ($B \le 10$) was too small to detect HITS entry. At $B \ge 25$, In-Degree reaches Top-10 in $8.60$ edges vs HITS $31.40$ edges (ratio = $3.820$, $p = 5.96 \times 10^{-8}$). |
| **Hypothesis H2 Verdict** | Reported as "Supported (Preliminary)" | **STRONGLY SUPPORTED** | Evaluated on 125 instances (adding web-NotreDame). Proved $\sigma_1^2 \ge \max(d_{in})$ in $100.0\%$, abrupt takeover in $73.6\%$, and counterexamples rigorously diagnosed by collapsed eigengap ($2.51$ vs $13.53$). |
| **Hypothesis H3 Verdict** | Reported as "Inconclusive" | **SUPPORTED** | Mid-project budget cap ($B=200$) caused A2 to never reach Top-10 on SBM, making $B^*$ undefined / NaN. Raising budget cap to $B=500$ allowed A2 to reach Top-10 in 15/15 instances, confirming $33.3\%$ cost saving for A5. |
| **Hypothesis H4 Verdict** | Reported as "Not Supported" | **NOT SUPPORTED GLOBALLY (Nuanced)** | D4 achieves $93.3\%$ reduction on A2 and $97.3\%$ on A3, but on real base sets clean NDCG loss reaches $10.56\%$, and camouflage links evade detection ($0.0\%$ reduction). |
| **A4b vs A5 Duplicate** | Treated as separate attacks with identical numbers | **Proved identical construction; A4b removed** | Both created $p$ fake hubs linking to target + $c$ authorities. A4 restored to proposal definition (target/single fake linking to $c$ authorities); A5 evaluated as cross-score multi-hub; A5b tested as cross-linked variant. |
| **D4 vs D4b Duplicate** | Evaluated separately with identical columns | **Proved functionally identical; D4b removed** | On synthetic link farms, fake hubs have identical out-link patterns ($J=1.0$), making mutual and out-link Jaccard penalize identical nodes. D4 retained as Wu-Davison; D4b removed. |
| **D3 Hub Capping No-Op** | Reported as a no-op at cap=0.10 without explanation | **Investigated root cause; evaluated sensitivity sweep** | Across graphs with $N \ge 500$, legitimate max hub shares are $2.2\%$ (ER), $3.8\%$ (BA), and $5.5\%$ (SBM). A $10\%$ cap can never bind. Calibrating to $1\%$ actively binds with $25.8\%$ attack reduction on calibration graph. |
| **A3 PageRank Flat Curve** | Noted as identical to A1 (0.381 gain) without explanation | **Proved mathematically from PageRank linear system** | Disconnected $K_{p, q}$ where $p=q=\lfloor\sqrt{B}\rfloor$ has zero in-degree hubs transferring $(1-d)/(p N)$ each, yielding $p \times \frac{1-d}{p N} = \frac{1-d}{N}$, exactly equal to a single hub in-link (A1). |
| **WEBSPAM Set 2 Labels** | Set 2 labels had 0% overlap with host graph | **100% Overlap (2,247/2,247) after stripping URL prefix** | Set 2 hostnames had `http://` prepended. Normalizing hostnames restored 100% reconciliation across both Set 1 ($8,415/8,415$) and Set 2 ($2,247/2,247$). |
| **Local Paths & Hygiene** | Contained 34 machine-specific paths in audit notes | **100% Clean relative links across all files** | Verified by `git grep -E "file:///|c:\\Users|Users/shris"` returning zero matches in active source and report files. |

---

## 6. Scale-Downs and Limitations Table vs Proposal

| Dimension | Proposal Target | Mid-Project | Final Implementation | Rationale |
|---|---|---|---|---|
| **Graph Families** | Synthetic BA, ER, SBM; SNAP web-Stanford, web-NotreDame; WEBSPAM | 4 graphs (BA, ER, SBM, web-Stanford) | **All 6 Target Graphs:** BA-500, ER-500, SBM-500, SNAP web-Stanford, SNAP web-NotreDame, WEBSPAM-UK2006 Hostgraph | Full coverage achieved. |
| **Seeds per Setting** | $\ge 5$ seeds | 3 seeds (`[42, 123, 456]`) | **5 Seeds** (`[42, 123, 456, 789, 999]`) for core runs | Expanded to full 5 seeds for H1, H2, H3, and Cost Curves. |
| **Budgets** | $1 \dots 500$ | $\{1, 5, 10, 25, 50, 75, 100\}$ | $\{1, 2, 5, 10, 25, 50, 100, 200\}$ (Cost Curves) and up to **500** (H3) | Budget 500 retained for H3 to resolve SBM top-10 entry; dropped from cost curves where power iteration runtime on 4k-node NotreDame exceeds timebox. |
| **Base Set Root Size** | $100-200$ nodes | Not specified | **$40-80$ nodes** ($N_{\text{base}} \approx 500-1000$) | Scaled down to ensure base graph size fits within $N \le 1000$ to maintain fast power iteration convergence. |
| **WEBSPAM Ingestion** | Full hostgraph + labels | Labels only (Set 1) | **Full Host Graph (11,402 nodes, 730k edges) + Set 1 & Set 2 Labels (10,662 hosts)** | 100% complete via native Python parsing. |
| **Attacks Evaluated** | A1–A6 | A1–A6 (with A4b/A5 duplicate) | **A1, A2, A3, A4, A5, A5b, A6, Camouflage ($r=2, 5, 10$)** | De-duplicated A4b; added Camouflaged farms. |
| **Defenses Evaluated** | D1–D5 | D1–D5 (D3 no-op) | **D1-rand, D1-sub, D2, D3 (1% cap), D4, D5 (PageRank seeds), Combined D4+D1/D5** | Calibrated on independent graph; D4b removed as redundant. |
| **Stretch Objectives** | Closed-form bound, game loop, UK-2007 | Not started | **NOT PURSUED (Scoped Out)** | Prioritized core empirical rigor, WEBSPAM real-data evaluation, and bug fixes. |

---

## 7. Hardware, Benchmarks & Library Environment

*Copied directly from [`results/environment.txt`](../results/environment.txt):*
- **CPU:** 12th Gen Intel Core i5-12500H (12 physical cores: 4 P-cores, 8 E-cores, 16 logical threads).
- **Operating System:** Microsoft Windows 11 Home (Build 10.0.26100).
- **Python Version:** Python 3.12.5 (64-bit).
- **Key Python Packages:**
  - `networkx`: 3.3
  - `numpy`: 1.26.4
  - `scipy`: 1.13.1
  - `pandas`: 2.2.2
  - `scikit-learn`: 1.5.1
  - `matplotlib`: 3.9.2
  - `pytest`: 9.1.1
- **Unit Test Suite:** 36 passing tests in $4.79$s.
- **Runtimes:**
  - Full H1/H3 Evaluation ($55$ instances): $16.97$s.
  - H2 Spectral Takeover ($125$ instances): $92.9$s.
  - Defense Matrix Final ($7,200$ trials): $74.2$s.
  - WEBSPAM Hostgraph Ingestion & Evaluation ($11,402$ nodes, $730$k edges): $15.8$s.
  - WEBSPAM Hostgraph Attack Experiments ($60$ trials): $223.2$s.

---

## 8. Team Contributions & Git History Verification

*Per course instructions, contributions are attributed strictly according to actual Git commit history (`git shortlog -sn --all`):*

```text
git shortlog -sn --all
    16  Shrisaysalot
```

- **Shrisay Shandilya (`Shrisaysalot`):**
  - Designed and implemented 100% of the repository codebase across all 16 commits (`main`).
  - Authored all rankers (sparse HITS, PageRank, SALSA, In-Degree) and synthetic graph generators.
  - Implemented all 8 attack topologies (A1–A6, Camouflaged farms) and all 10 defense variations (D1–D5, Combined D4+D1/D5).
  - Engineered the native Python WEBSPAM-UK2006 hostgraph loader and label reconciliation pipeline.
  - Authored the test suite (expanding from 30 to 36 unit tests, 100% passing).
  - Executed all experimental runs (Cost Curves Final, H1/H3 Final, H2 Final, Defense Matrix Final, WEBSPAM evaluation & real attacks).
  - Generated all 300-DPI publication figures and authored `FINAL_REPORT_FACTS.md`.
- **Vibhor Rathi:**
  - *Planned ownership:* Theoretical spectral derivations and background literature synthesis (planned, no commits in git history).
- **Prachi Jain:**
  - *Planned ownership:* Defense taxonomy review and report formatting (planned, no commits in git history).

---

## 9. Manifest of Generated Figures & Empirical CSV Artifacts

### Figures (`figures/`)
1. [`figures/architecture.png`](../figures/architecture.png) (and [`.svg`](../figures/architecture.svg)): Complete system architecture diagram reflecting final built state (Modules 1–5 BUILT, Module 6 SCOPED OUT).
2. [`figures/cost_curves_v3.png`](../figures/cost_curves_v3.png): Adversarial cost curves across all 7 attack families with 95% bootstrap CI bands for HITS, PageRank, SALSA, and InDegree.
3. [`figures/h2_takeover_v3.png`](../figures/h2_takeover_v3.png): Normalized critical budget $p^*(10) / \sigma_1^2$ bar chart and abruptness boxplot comparing HITS spectral snap to PageRank smooth progression.
4. [`figures/defense_tradeoff_v3.png`](../figures/defense_tradeoff_v3.png): Security vs clean utility scatter plot mapping median attack reduction against clean NDCG@20 loss with target quadrant.
5. [`figures/webspam_eval.png`](../figures/webspam_eval.png): WEBSPAM-UK2006 clean rank distribution (boxplots) and real attack on host graph (target rank vs $B$).

### Empirical Results Data (`results/`)
1. [`results/cost_curves_final.csv`](../results/cost_curves_final.csv): Full-scale cost curves dataset (33,600 observations across 5 graphs, 5 seeds, 7 attacks, 8 budgets, 4 rankers).
2. [`results/wilcoxon_per_attack_final.csv`](../results/wilcoxon_per_attack_final.csv): Independent paired Wilcoxon signed-rank tests aggregated over seeds per `(graph, target_node)` unit ($n=144$) with Holm correction.
3. [`results/h1_h3_eval_final.csv`](../results/h1_h3_eval_final.csv): Controlled trials for H1 ($n=25$ ER instances) and H3 ($n=30$ SBM/ER instances up to $B=500$).
4. [`results/h2_robustness_final.csv`](../results/h2_robustness_final.csv): 125 instances testing spectral takeover, singular values, eigengaps, and abruptness.
5. [`results/defenses_eval_final.csv`](../results/defenses_eval_final.csv): 7,200 defense trials across 10 defenses, 8 attacks, and 3 graphs ($n=644$ positive-gain cells per defense).
6. [`results/defense_calibration_sweeps.csv`](../results/defense_calibration_sweeps.csv): 192 parameter sweep records on independent calibration graph (seed 9999).
7. [`results/webspam_clean_ranking_final.csv`](../results/webspam_clean_ranking_final.csv): Full WEBSPAM-UK2006 clean ranking benchmark (Spam@100..2000, AUC, precision/recall at top 1%, 5%, 10%, prevalence-aware F1).
8. [`results/webspam_attack_final.csv`](../results/webspam_attack_final.csv): Real attack on WEBSPAM host graph (10 target hosts, budgets 10, 100, 1000, A2 & A5).
9. [`results/environment.txt`](../results/environment.txt): Hardware, OS, Python and package versions specification.

---

## 10. Reproduction Commands

To reproduce every result from the repository root:

```powershell
# 1. Run unit test suite (36 tests)
pytest

# 2. Re-run H1 and H3 evaluation (ER random graphs & SBM up to B=500)
python scripts/run_h1_h3_eval_v3.py

# 3. Re-run H2 spectral takeover experiment (125 instances)
python scripts/run_h2_experiment_v3.py

# 4. Re-run Defense calibration sweeps (on seed 9999)
python scripts/calibrate_defenses.py

# 5. Re-run full Defense matrix (7,200 trials)
python scripts/run_defense_matrix_v3.py

# 6. Re-run Cost Curves v3 (33,600 observations)
python scripts/run_cost_curves_v3.py

# 7. Re-run WEBSPAM-UK2006 clean ranking benchmark and real host graph attack
python scripts/run_webspam_eval_final.py

# 8. Re-generate all publication figures (300 DPI)
python scripts/generate_publication_figures_v3.py
python scripts/generate_figures.py
```
