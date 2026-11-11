"""H1 and H3 Rigorous Evaluation Script (v3).

H1: B*(10) and B*(1) for HITS vs In-Degree on >= 5 ER instances across seeds [42, 123, 456, 789, 999].
    Computes Wilcoxon signed-rank test and 95% bootstrap CIs.
H3: A2 (pure farm) vs A5 (cross-score attaching to community) on >= 5 SBM instances plus ER control,
    with budget raised to 500 to evaluate whether A2 can overcome the planted community.
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd

from src.data.synthetic import generate_erdos_renyi, generate_planted_bipartite_sbm
from src.rankers import hits, indegree
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.attacks.a5_cross_score import attack_a5_cross_score
from src.eval import b_star_at_k, compute_rank
from src.eval.stats import bootstrap_ci, wilcoxon_test


def run_h1_evaluation(seeds=[42, 123, 456, 789, 999]):
    print("==================================================================")
    print("=== H1 EVALUATION: HITS vs In-Degree B*(10) & B*(1) on ER ===")
    print("==================================================================")
    t0 = time.time()
    budget_grid = [1, 2, 5, 10, 15, 20, 25, 30, 40, 50, 75, 100, 150, 200]
    records = []

    for s in seeds:
        G_er = generate_erdos_renyi(n=500, p=0.012, seed=s)
        h_clean = hits(G_er).scores
        order = np.argsort(h_clean)
        # Select 5 diverse target nodes across rank spectrum
        targets = [int(order[int(500 * f)]) for f in [0.15, 0.30, 0.45, 0.60, 0.75]]

        for t in targets:
            h_ranks = []
            indeg_ranks = []

            for b in budget_grid:
                att = attack_a2_hub_farm(G_er, t, budget=b)
                h_res = hits(att.graph, max_iter=60)
                indeg_res = indegree(att.graph)
                h_ranks.append(compute_rank(h_res.scores, t))
                indeg_ranks.append(compute_rank(indeg_res.scores, t))

            b_star_h10 = b_star_at_k(budget_grid, h_ranks, k=10)
            b_star_deg10 = b_star_at_k(budget_grid, indeg_ranks, k=10)
            b_star_h1 = b_star_at_k(budget_grid, h_ranks, k=1)
            b_star_deg1 = b_star_at_k(budget_grid, indeg_ranks, k=1)

            ratio_10 = (b_star_h10 / b_star_deg10) if (b_star_h10 and b_star_deg10) else np.nan
            ratio_1 = (b_star_h1 / b_star_deg1) if (b_star_h1 and b_star_deg1) else np.nan

            records.append({
                "hypothesis": "H1",
                "graph": "ER-500",
                "seed": s,
                "target_node": t,
                "b_star_hits_k10": b_star_h10,
                "b_star_indeg_k10": b_star_deg10,
                "ratio_k10": ratio_10,
                "b_star_hits_k1": b_star_h1,
                "b_star_indeg_k1": b_star_deg1,
                "ratio_k1": ratio_1
            })

    df_h1 = pd.DataFrame(records)
    print(f"H1 Completed in {time.time()-t0:.2f}s (n={len(df_h1)} instances across {len(seeds)} ER graphs)")

    valid_10 = df_h1.dropna(subset=["b_star_hits_k10", "b_star_indeg_k10"])
    m_h10, l_h10, u_h10 = bootstrap_ci(valid_10["b_star_hits_k10"].values)
    m_d10, l_d10, u_d10 = bootstrap_ci(valid_10["b_star_indeg_k10"].values)
    m_r10, l_r10, u_r10 = bootstrap_ci(valid_10["ratio_k10"].values)

    w_stat10, p_val10 = wilcoxon_test(valid_10["b_star_hits_k10"].values, valid_10["b_star_indeg_k10"].values)
    print(f"B*(10) HITS: {m_h10:.2f} [{l_h10:.2f}, {u_h10:.2f}] | In-Degree: {m_d10:.2f} [{l_d10:.2f}, {u_d10:.2f}]")
    print(f"B*(10) Cost Ratio (HITS / InDegree): {m_r10:.3f} [{l_r10:.3f}, {u_r10:.3f}] | Wilcoxon p={p_val10:.2e}")

    valid_1 = df_h1.dropna(subset=["b_star_hits_k1", "b_star_indeg_k1"])
    if len(valid_1) >= 5:
        m_h1, l_h1, u_h1 = bootstrap_ci(valid_1["b_star_hits_k1"].values)
        m_d1, l_d1, u_d1 = bootstrap_ci(valid_1["b_star_indeg_k1"].values)
        m_r1, l_r1, u_r1 = bootstrap_ci(valid_1["ratio_k1"].values)
        w_stat1, p_val1 = wilcoxon_test(valid_1["b_star_hits_k1"].values, valid_1["b_star_indeg_k1"].values)
        print(f"B*(1)  HITS: {m_h1:.2f} [{l_h1:.2f}, {u_h1:.2f}] | In-Degree: {m_d1:.2f} [{l_d1:.2f}, {u_d1:.2f}]")
        print(f"B*(1)  Cost Ratio (HITS / InDegree): {m_r1:.3f} [{l_r1:.3f}, {u_r1:.3f}] | Wilcoxon p={p_val1:.2e}")
    else:
        print(f"B*(1) reached by {len(valid_1)} instances (insufficient for Wilcoxon test at rank 1)")

    return df_h1


def run_h3_evaluation(seeds=[42, 123, 456, 789, 999]):
    print("\n==================================================================")
    print("=== H3 EVALUATION: A2 vs A5 on SBM (Planted Community) vs ER ===")
    print("==================================================================")
    t0 = time.time()
    # High budget grid up to 500 to test whether A2 ever reaches top-10 on SBM
    budget_grid = [5, 10, 25, 50, 75, 100, 150, 200, 300, 400, 500]
    records = []

    test_graphs = {
        "SBM_Planted": lambda s: generate_planted_bipartite_sbm(460, 20, 20, seed=s)[0],
        "ER_Control": lambda s: generate_erdos_renyi(500, 0.012, seed=s)
    }

    for g_name, g_fn in test_graphs.items():
        for s in seeds:
            G = g_fn(s)
            h_clean = hits(G).scores
            order = np.argsort(h_clean)
            targets = [int(order[int(500 * f)]) for f in [0.20, 0.40, 0.60]]

            for t in targets:
                a2_ranks = []
                a5_ranks = []

                for b in budget_grid:
                    att_a2 = attack_a2_hub_farm(G, t, budget=b)
                    att_a5 = attack_a5_cross_score(G, t, budget=b, c_top=3)

                    a2_ranks.append(compute_rank(hits(att_a2.graph, max_iter=60).scores, t))
                    a5_ranks.append(compute_rank(hits(att_a5.graph, max_iter=60).scores, t))

                b_star_a2 = b_star_at_k(budget_grid, a2_ranks, k=10)
                b_star_a5 = b_star_at_k(budget_grid, a5_ranks, k=10)

                cost_saving = (1.0 - (b_star_a5 / b_star_a2)) if (b_star_a2 and b_star_a5) else np.nan

                records.append({
                    "hypothesis": "H3",
                    "graph": g_name,
                    "seed": s,
                    "target_node": t,
                    "b_star_a2_k10": b_star_a2,
                    "b_star_a5_k10": b_star_a5,
                    "cost_saving_pct": cost_saving * 100.0 if not np.isnan(cost_saving) else np.nan,
                    "min_rank_a2": min(a2_ranks),
                    "min_rank_a5": min(a5_ranks)
                })

    df_h3 = pd.DataFrame(records)
    print(f"H3 Completed in {time.time()-t0:.2f}s (n={len(df_h3)} instances)")

    for g_name in ["SBM_Planted", "ER_Control"]:
        sub = df_h3[df_h3["graph"] == g_name]
        valid_s = sub["cost_saving_pct"].dropna().values
        n_a2_top10 = sub["b_star_a2_k10"].notna().sum()
        n_a5_top10 = sub["b_star_a5_k10"].notna().sum()
        print(f"\n--- {g_name} (n={len(sub)}) ---")
        print(f"  A2 reached top-10: {n_a2_top10} / {len(sub)} (min rank: {sub['min_rank_a2'].min()})")
        print(f"  A5 reached top-10: {n_a5_top10} / {len(sub)} (min rank: {sub['min_rank_a5'].min()})")
        if len(valid_s) > 0:
            m_cs, l_cs, u_cs = bootstrap_ci(valid_s)
            print(f"  A5 cost savings vs A2: {m_cs:.1f}% [{l_cs:.1f}%, {u_cs:.1f}%] (n={len(valid_s)} valid)")
        else:
            print("  Cost ratio undefined because A2 never reached top-10 even at B=500!")

    return df_h3


if __name__ == "__main__":
    df1 = run_h1_evaluation()
    df3 = run_h3_evaluation()
    combined = pd.concat([df1, df3], ignore_index=True)
    out_csv = Path("results/h1_h3_eval_v3.csv")
    combined.to_csv(out_csv, index=False)
    print(f"\nSaved combined H1/H3 evaluation to {out_csv}")

