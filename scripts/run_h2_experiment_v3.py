"""H2 Robustness & Spectral Takeover Evaluation Script (v3).

Evaluates H2 across 5 seeds [42, 123, 456, 789, 999] and 5 graphs:
- Synthetic BA-500
- Synthetic ER-500
- Synthetic SBM-500
- SNAP web-Stanford Base Set
- SNAP web-NotreDame Base Set
Total: 125 instances (vs mid-project 60 instances).

Investigates:
- Ratio p*(10) / sigma1^2 and p*(1) / sigma1^2 with 95% bootstrap CIs
- sigma1^2 >= max in-degree property
- Abrupt spectral takeover rate (HITS vs PageRank rank step jump)
- Counterexample investigation: initial rank effect & eigengap correlation
- Numerical verification of PageRank smoothness
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
import scipy.sparse as sp
import networkx as nx

from src.data.synthetic import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm
)
from src.data.loader import load_snap_graph
from src.data.base_set import sample_root_set, build_base_set
from src.rankers import hits, pagerank
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.eval import compute_rank
from src.eval.stats import bootstrap_ci


def run_h2_robustness_v3(seeds=[42, 123, 456, 789, 999]):
    print("==================================================================")
    print("=== H2 SPECTRAL TAKEOVER EVALUATION V3 (125 INSTANCES) ===")
    print("==================================================================")
    t0 = time.time()

    print("Loading SNAP full graphs...")
    G_stan_full, _, _ = load_snap_graph("web-Stanford", max_edges=60000)
    G_nd_full, _, _ = load_snap_graph("web-NotreDame", max_edges=60000)

    graphs = {
        "Synthetic_BA_500": lambda s: generate_barabasi_albert(n=500, m=4, seed=s),
        "Synthetic_ER_500": lambda s: generate_erdos_renyi(n=500, p=0.012, seed=s),
        "Synthetic_SBM_500": lambda s: generate_planted_bipartite_sbm(460, 20, 20, seed=s)[0],
        "SNAP_web-Stanford_BaseSet": lambda s: build_base_set(
            G_stan_full, sample_root_set(G_stan_full, seed_node=int(s % 300) + 1, root_size=70), max_in_links=20
        ).graph,
        "SNAP_web-NotreDame_BaseSet": lambda s: build_base_set(
            G_nd_full, sample_root_set(G_nd_full, seed_node=int(s % 300) + 1, root_size=40), max_in_links=10
        ).graph
    }

    records = []

    for g_name, g_fn in graphs.items():
        print(f"Processing graph family: {g_name}...")
        for s in seeds:
            G = g_fn(s)
            n = G.number_of_nodes()
            nodes = list(range(n))
            A = nx.adjacency_matrix(G, nodelist=nodes, dtype=float).tocsr()

            # Singular values and eigengap
            u, sing_vals, vt = sp.linalg.svds(A, k=2)
            sing_vals = np.sort(sing_vals)[::-1]
            sigma1 = float(sing_vals[0])
            sigma2 = float(sing_vals[1])
            sigma1_sq = sigma1 ** 2
            eigengap = sigma1 - sigma2
            max_in_deg = int(A.sum(axis=0).max())
            sig_ge_indeg = bool(sigma1_sq >= max_in_deg - 1e-5)

            clean_h = hits(G, max_iter=60).scores
            clean_pr = pagerank(G, max_iter=60).scores
            order = np.argsort(clean_h)

            # 5 targets from low to high rank
            targets = [
                int(order[int(n * 0.15)]),
                int(order[int(n * 0.30)]),
                int(order[int(n * 0.50)]),
                int(order[int(n * 0.70)]),
                int(order[int(n * 0.85)])
            ]

            p_grid = sorted(list(set([
                max(1, int(round(sigma1_sq * mult)))
                for mult in np.linspace(0.1, 2.0, 24)
            ])))

            for target in targets:
                clean_h_rank = compute_rank(clean_h, target)
                clean_pr_rank = compute_rank(clean_pr, target)

                h_ranks = []
                pr_ranks = []
                p_star_10 = None
                p_star_1 = None

                for p in p_grid:
                    att_res = attack_a2_hub_farm(G, target, budget=p)
                    h_res = hits(att_res.graph, max_iter=60)
                    pr_res = pagerank(att_res.graph, max_iter=60)

                    h_r = compute_rank(h_res.scores, target)
                    pr_r = compute_rank(pr_res.scores, target)
                    h_ranks.append(h_r)
                    pr_ranks.append(pr_r)

                    if h_r <= 10 and p_star_10 is None:
                        p_star_10 = p
                    if h_r == 1 and p_star_1 is None:
                        p_star_1 = p

                h_diffs = [abs(h_ranks[i+1] - h_ranks[i]) for i in range(len(h_ranks)-1)]
                pr_diffs = [abs(pr_ranks[i+1] - pr_ranks[i]) for i in range(len(pr_ranks)-1)]
                max_h_jump = max(h_diffs) if h_diffs else 0
                max_pr_jump = max(pr_diffs) if pr_diffs else 0
                is_abrupt = bool(max_h_jump > 2 * max_pr_jump)

                records.append({
                    "graph": g_name,
                    "seed": s,
                    "num_nodes": n,
                    "target_node": target,
                    "clean_h_rank": clean_h_rank,
                    "clean_pr_rank": clean_pr_rank,
                    "clean_h_rank_pct": (clean_h_rank / n) * 100.0,
                    "sigma1": sigma1,
                    "sigma2": sigma2,
                    "sigma1_sq": sigma1_sq,
                    "eigengap": eigengap,
                    "max_in_degree": max_in_deg,
                    "sigma1_sq_ge_max_indeg": sig_ge_indeg,
                    "p_star_10": p_star_10 if p_star_10 is not None else np.nan,
                    "p_star_1": p_star_1 if p_star_1 is not None else np.nan,
                    "ratio_p_star_10_to_sigma1_sq": (p_star_10 / sigma1_sq) if p_star_10 else np.nan,
                    "ratio_p_star_1_to_sigma1_sq": (p_star_1 / sigma1_sq) if p_star_1 else np.nan,
                    "max_hits_step_jump": max_h_jump,
                    "max_pagerank_step_jump": max_pr_jump,
                    "is_hits_jump_abrupt": is_abrupt
                })

    df = pd.DataFrame(records)
    out_csv = Path("results/h2_robustness_v3.csv")
    df.to_csv(out_csv, index=False)
    print(f"\n[DONE H2] Saved {len(df)} runs to {out_csv} in {time.time()-t0:.1f}s")

    # Summary Statistics
    ge_rate = df["sigma1_sq_ge_max_indeg"].mean() * 100
    abrupt_rate = df["is_hits_jump_abrupt"].mean() * 100
    n_abrupt = df["is_hits_jump_abrupt"].sum()
    n_total = len(df)
    n_counter = n_total - n_abrupt

    p_rat10 = df["ratio_p_star_10_to_sigma1_sq"].dropna().values
    m10, l10, u10 = bootstrap_ci(p_rat10)

    p_rat1 = df["ratio_p_star_1_to_sigma1_sq"].dropna().values
    m1, l1, u1 = bootstrap_ci(p_rat1)

    print("\n--- H2 Summary Metrics ---")
    print(f"Total instances: {n_total}")
    print(f"sigma1^2 >= max in-degree property: {ge_rate:.1f}% ({df['sigma1_sq_ge_max_indeg'].sum()}/{n_total})")
    print(f"Abrupt spectral takeover rate: {abrupt_rate:.1f}% ({n_abrupt}/{n_total})")
    print(f"Counterexamples (non-abrupt): {n_counter}/{n_total} ({(n_counter/n_total)*100:.1f}%)")
    print(f"Mean max single-step rank jump: HITS={df['max_hits_step_jump'].mean():.1f}, PageRank={df['max_pagerank_step_jump'].mean():.1f}")
    print(f"p*(10) / sigma1^2 ratio: {m10:.3f} [{l10:.3f}, {u10:.3f}] (n={len(p_rat10)})")
    print(f"p*(1)  / sigma1^2 ratio: {m1:.3f} [{l1:.3f}, {u1:.3f}] (n={len(p_rat1)})")

    # WHY Counterexamples occur analysis
    counterexamples = df[~df["is_hits_jump_abrupt"]]
    abrupt_cases = df[df["is_hits_jump_abrupt"]]
    print("\n--- Counterexample Diagnostic (Why do non-abrupt cases occur?) ---")
    print(f"Abrupt Cases (n={len(abrupt_cases)}):")
    print(f"  Mean initial rank: {abrupt_cases['clean_h_rank'].mean():.1f} ({abrupt_cases['clean_h_rank_pct'].mean():.1f}% of graph)")
    print(f"  Mean eigengap (sigma1 - sigma2): {abrupt_cases['eigengap'].mean():.2f}")
    print(f"Counterexample Cases (n={len(counterexamples)}):")
    print(f"  Mean initial rank: {counterexamples['clean_h_rank'].mean():.1f} ({counterexamples['clean_h_rank_pct'].mean():.1f}% of graph)")
    print(f"  Mean eigengap (sigma1 - sigma2): {counterexamples['eigengap'].mean():.2f}")
    print("Breakdown of counterexamples by graph:")
    print(counterexamples["graph"].value_counts().to_string())

    return df


if __name__ == "__main__":
    run_h2_robustness_v3()

