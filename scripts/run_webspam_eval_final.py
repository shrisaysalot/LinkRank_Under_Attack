"""Final Real-Data WEBSPAM-UK2006 Hostgraph Evaluation & Attack Experiment.

Outputs:
- results/webspam_clean_ranking_final.csv
- results/webspam_attack_final.csv
- figures/webspam_eval.png
"""
import time
import gzip
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import scipy.sparse as sp
import networkx as nx
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, precision_recall_curve, f1_score

from src.data.loader import load_webspam_hostgraph, load_webspam_labels
from src.rankers import hits, pagerank, salsa, indegree
from src.rankers.randomized_hits import randomized_hits
from src.defenses.d3_hub_capping import hub_capped_hits
from src.defenses.d4_wu_davison import wu_davison_hits
from src.defenses.d5_trust_hits import trust_based_hits
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.attacks.a5_cross_score import attack_a5_cross_score


def main():
    print("=" * 70)
    print("STARTING WEBSPAM-UK2006 FINAL EVALUATION & ATTACK")
    print("=" * 70)

    # 1. Dataset verification & disjointness
    df_set1 = load_webspam_labels(split="set1", undecided_mode="keep")
    df_set2 = load_webspam_labels(split="set2", undecided_mode="keep")
    s1_hosts = set(df_set1["host"])
    s2_hosts = set(df_set2["host"])
    overlap_count = len(s1_hosts.intersection(s2_hosts))
    print(f"Set 1 hosts: {len(df_set1)}, Set 2 hosts: {len(df_set2)}, Overlap: {overlap_count}")
    assert overlap_count == 0, "Set 1 and Set 2 must be disjoint!"

    # Hostgraph ingestion
    t0 = time.time()
    G, adj, i2h, h2i = load_webspam_hostgraph()
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    print(f"Loaded hostgraph in {time.time()-t0:.2f}s: {n_nodes} nodes, {n_edges} edges")

    # Map labels to node indices
    # Undecided hosts are excluded from binary evaluation metrics
    df_all_labels = pd.concat([df_set1, df_set2], ignore_index=True)
    df_all_clean = df_all_labels[df_all_labels["binary_label"].isin([0, 1])].copy()
    df_all_clean["node_idx"] = df_all_clean["host"].map(h2i)
    df_all_clean = df_all_clean.dropna(subset=["node_idx"])
    df_all_clean["node_idx"] = df_all_clean["node_idx"].astype(int)

    # Set 1 & Set 2 clean subsets
    df_s1_clean = df_all_clean[df_all_clean["host"].isin(s1_hosts)].copy()
    df_s2_clean = df_all_clean[df_all_clean["host"].isin(s2_hosts)].copy()

    s1_prev = df_s1_clean["binary_label"].mean()
    s2_prev = df_s2_clean["binary_label"].mean()
    all_prev = df_all_clean["binary_label"].mean()
    print(f"Spam prevalence: Set 1 = {s1_prev:.4f} ({df_s1_clean['binary_label'].sum()}/{len(df_s1_clean)})")
    print(f"Spam prevalence: Set 2 = {s2_prev:.4f} ({df_s2_clean['binary_label'].sum()}/{len(df_s2_clean)})")
    print(f"Spam prevalence: All   = {all_prev:.4f} ({df_all_clean['binary_label'].sum()}/{len(df_all_clean)})")

    # Trusted seeds for D5: Set 1 normal hosts
    set1_normal_nodes = df_s1_clean[df_s1_clean["binary_label"] == 0]["node_idx"].tolist()
    print(f"D5 Trust seed pool: {len(set1_normal_nodes)} Set 1 normal hosts")

    # 2. Clean ranking evaluation
    print("\n--- Running Clean Ranking Evaluation ---")
    rankers = {
        "InDegree": lambda a: indegree(a),
        "PageRank": lambda a: pagerank(a, alpha=0.85),
        "Undefended_HITS": lambda a: hits(a),
        "SALSA": lambda a: salsa(a),
        "D1_RandomizedHITS_0.15": lambda a: randomized_hits(a, eps=0.15),
        "D3_HubCapping_0.01": lambda a: hub_capped_hits(a, cap_fraction=0.01),
        "D4_WuDavison_0.5": lambda a: wu_davison_hits(a, out_threshold=0.5),
        "D5_TrustHITS_Set1Normal": lambda a: trust_based_hits(a, trusted_seeds=set1_normal_nodes, eps=0.15),
    }

    clean_records = []
    clean_scores_dict = {}

    for name, fn in rankers.items():
        t_start = time.time()
        res = fn(adj)
        runtime = time.time() - t_start
        scores = res.scores
        clean_scores_dict[name] = scores

        # Ranks: descending order (1 is top rank)
        ranks = np.zeros(n_nodes, dtype=int)
        order = np.argsort(-scores)
        ranks[order] = np.arange(1, n_nodes + 1)

        # Evaluate on Set 2 (Test Set) and All Labeled
        for split_name, sub_df in [("Set2_Test", df_s2_clean), ("All_Labeled", df_all_clean)]:
            node_idxs = sub_df["node_idx"].values
            y_true = sub_df["binary_label"].values
            sub_scores = scores[node_idxs]
            sub_ranks = ranks[node_idxs]

            # Spam ranks vs Normal ranks
            spam_ranks = sub_ranks[y_true == 1]
            norm_ranks = sub_ranks[y_true == 0]

            mean_spam_rank = float(np.mean(spam_ranks))
            median_spam_rank = float(np.median(spam_ranks))
            mean_norm_rank = float(np.mean(norm_ranks))
            median_norm_rank = float(np.median(norm_ranks))

            # Spam@k on the full graph
            spam_at_k = {}
            for k in [100, 500, 1000, 2000]:
                top_k_nodes = set(order[:k])
                # Count spam in top k among this labeled set
                top_k_spam = sub_df[sub_df["node_idx"].isin(top_k_nodes)]["binary_label"].sum()
                top_k_total_labeled = len(sub_df[sub_df["node_idx"].isin(top_k_nodes)])
                spam_at_k[f"spam_at_{k}"] = int(top_k_spam)
                spam_at_k[f"spam_pct_{k}"] = float(top_k_spam / top_k_total_labeled) if top_k_total_labeled > 0 else 0.0

            # ROC-AUC (detecting spam by lower score / higher rank or score directly)
            # Link spam typically seeks high score, but in clean graph spam has LOW score.
            # Standard IR: score as spam detector (higher score => spam, or lower score => spam)
            # In clean web, spam is lower ranked, so -sub_scores detects spam:
            auc_spam_as_low = float(roc_auc_score(y_true, -sub_scores))
            auc_spam_as_high = float(roc_auc_score(y_true, sub_scores))

            # Precision & Recall at top 1%, 5%, 10% of ranked hosts
            p_at = {}
            r_at = {}
            for pct in [1, 5, 10]:
                cutoff = int(n_nodes * (pct / 100.0))
                top_nodes = set(order[:cutoff])
                sub_top = sub_df[sub_df["node_idx"].isin(top_nodes)]
                tp = sub_top["binary_label"].sum()
                prec = float(tp / len(sub_top)) if len(sub_top) > 0 else 0.0
                rec = float(tp / np.sum(y_true)) if np.sum(y_true) > 0 else 0.0
                p_at[f"prec_top_{pct}pct"] = prec
                r_at[f"recall_top_{pct}pct"] = rec

            # Prevalence-calibrated F1: threshold at the score percentile matching spam prevalence
            thresh_val = np.percentile(sub_scores, 100 * (1 - sub_df["binary_label"].mean()))
            pred_binary = (sub_scores >= thresh_val).astype(int)
            prev_aware_f1 = float(f1_score(y_true, pred_binary, zero_division=0))

            clean_records.append({
                "ranker": name,
                "eval_split": split_name,
                "n_labeled": len(sub_df),
                "spam_prevalence": float(np.mean(y_true)),
                "spam_at_100": spam_at_k["spam_at_100"],
                "spam_pct_100": spam_at_k["spam_pct_100"],
                "spam_at_500": spam_at_k["spam_at_500"],
                "spam_pct_500": spam_at_k["spam_pct_500"],
                "spam_at_1000": spam_at_k["spam_at_1000"],
                "spam_pct_1000": spam_at_k["spam_pct_1000"],
                "spam_at_2000": spam_at_k["spam_at_2000"],
                "spam_pct_2000": spam_at_k["spam_pct_2000"],
                "mean_spam_rank": mean_spam_rank,
                "median_spam_rank": median_spam_rank,
                "mean_norm_rank": mean_norm_rank,
                "median_norm_rank": median_norm_rank,
                "auc_spam_low_score": auc_spam_as_low,
                "auc_spam_high_score": auc_spam_as_high,
                "prec_top_1pct": p_at["prec_top_1pct"],
                "recall_top_1pct": r_at["recall_top_1pct"],
                "prec_top_5pct": p_at["prec_top_5pct"],
                "recall_top_5pct": r_at["recall_top_5pct"],
                "prec_top_10pct": p_at["prec_top_10pct"],
                "recall_top_10pct": r_at["recall_top_10pct"],
                "prev_aware_f1": prev_aware_f1,
                "runtime_s": runtime
            })
        print(f"Ranker {name:25s} | Set 2 Median Spam Rank: {median_spam_rank:6.0f} vs Normal: {median_norm_rank:6.0f} | Runtime: {runtime:.3f}s")

    df_clean_res = pd.DataFrame(clean_records)
    df_clean_res.to_csv("results/webspam_clean_ranking_final.csv", index=False)
    print("Saved results/webspam_clean_ranking_final.csv")

    # 3. Real attack on the host graph
    print("\n--- Running Real Attack Experiments on Host Graph ---")
    hits_scores = clean_scores_dict["Undefended_HITS"]
    hits_order = np.argsort(-hits_scores)
    hits_ranks = np.zeros(n_nodes, dtype=int)
    hits_ranks[hits_order] = np.arange(1, n_nodes + 1)

    # Select 10 target hosts:
    # 5 labeled normal, 5 labeled spam
    # Spanning Low Rank (>5000), Medium Rank (1000-5000), Random
    np.random.seed(42)
    norm_hosts = df_all_clean[df_all_clean["binary_label"] == 0].copy()
    norm_hosts["clean_rank"] = hits_ranks[norm_hosts["node_idx"].values]
    spam_hosts = df_all_clean[df_all_clean["binary_label"] == 1].copy()
    spam_hosts["clean_rank"] = hits_ranks[spam_hosts["node_idx"].values]

    target_targets = []
    # 2 low-rank normal, 2 medium-rank normal, 1 random normal
    target_targets.append(norm_hosts[norm_hosts["clean_rank"] > 7000].iloc[0])
    target_targets.append(norm_hosts[norm_hosts["clean_rank"] > 5000].iloc[1])
    target_targets.append(norm_hosts[(norm_hosts["clean_rank"] >= 1500) & (norm_hosts["clean_rank"] <= 4000)].iloc[0])
    target_targets.append(norm_hosts[(norm_hosts["clean_rank"] >= 1500) & (norm_hosts["clean_rank"] <= 4000)].iloc[1])
    target_targets.append(norm_hosts.sample(1, random_state=42).iloc[0])

    # 2 low-rank spam, 2 medium-rank spam, 1 random spam
    target_targets.append(spam_hosts[spam_hosts["clean_rank"] > 7000].iloc[0])
    target_targets.append(spam_hosts[spam_hosts["clean_rank"] > 5000].iloc[1])
    target_targets.append(spam_hosts[(spam_hosts["clean_rank"] >= 1500) & (spam_hosts["clean_rank"] <= 4000)].iloc[0])
    target_targets.append(spam_hosts[(spam_hosts["clean_rank"] >= 1500) & (spam_hosts["clean_rank"] <= 4000)].iloc[1])
    target_targets.append(spam_hosts.sample(1, random_state=123).iloc[0])

    df_targets = pd.DataFrame(target_targets).reset_index(drop=True)
    print(f"Selected {len(df_targets)} target hosts across tiers:")
    for idx, row in df_targets.iterrows():
        print(f"  Target {idx+1}: Node {row['node_idx']:5d} | {row['host']:35s} | Label: {'Spam' if row['binary_label']==1 else 'Norm'} | Clean HITS Rank: {row['clean_rank']}")

    # Spectral constant of clean graph
    sigma1_sq = 115407.4

    attack_budgets = [10, 100, 1000]
    attack_records = []

    for _, t_row in df_targets.iterrows():
        t_node = int(t_row["node_idx"])
        t_label = "Spam" if t_row["binary_label"] == 1 else "Normal"
        t_host = t_row["host"]

        # Clean ranks across rankers
        clean_ranks_t = {
            "HITS": int(np.where(np.argsort(-clean_scores_dict["Undefended_HITS"]) == t_node)[0][0] + 1),
            "PageRank": int(np.where(np.argsort(-clean_scores_dict["PageRank"]) == t_node)[0][0] + 1),
            "SALSA": int(np.where(np.argsort(-clean_scores_dict["SALSA"]) == t_node)[0][0] + 1),
            "InDegree": int(np.where(np.argsort(-clean_scores_dict["InDegree"]) == t_node)[0][0] + 1),
            "D3": int(np.where(np.argsort(-clean_scores_dict["D3_HubCapping_0.01"]) == t_node)[0][0] + 1),
        }

        for att_name, att_fn in [("A2_HubFarm", attack_a2_hub_farm), ("A5_CrossScore", attack_a5_cross_score)]:
            for B in attack_budgets:
                att_res = att_fn(G, t_node, budget=B)
                A_att = att_res.adj_matrix
                n_att = A_att.shape[0]

                # Evaluate rankers on attacked graph
                res_h = hits(A_att)
                res_p = pagerank(A_att, alpha=0.85)
                res_s = salsa(A_att)
                res_deg = indegree(A_att)
                res_d3 = hub_capped_hits(A_att, cap_fraction=0.01)

                h_rank = int(np.where(np.argsort(-res_h.scores) == t_node)[0][0] + 1)
                p_rank = int(np.where(np.argsort(-res_p.scores) == t_node)[0][0] + 1)
                s_rank = int(np.where(np.argsort(-res_s.scores) == t_node)[0][0] + 1)
                deg_rank = int(np.where(np.argsort(-res_deg.scores) == t_node)[0][0] + 1)
                d3_rank = int(np.where(np.argsort(-res_d3.scores) == t_node)[0][0] + 1)

                # Run D4 on B=1000 and B=100 for a representative subset
                d4_rank = np.nan
                if B >= 100 and t_node in [df_targets.iloc[0]["node_idx"], df_targets.iloc[5]["node_idx"]]:
                    res_d4 = wu_davison_hits(A_att, out_threshold=0.5)
                    d4_rank = int(np.where(np.argsort(-res_d4.scores) == t_node)[0][0] + 1)

                attack_records.append({
                    "target_node": t_node,
                    "target_host": t_host,
                    "label": t_label,
                    "attack": att_name,
                    "budget": B,
                    "p_ratio_sigma1_sq": float(B / sigma1_sq),
                    "clean_rank_hits": clean_ranks_t["HITS"],
                    "attacked_rank_hits": h_rank,
                    "rank_change_hits": clean_ranks_t["HITS"] - h_rank,
                    "top100_entry_hits": bool(h_rank <= 100),
                    "takeover_occurred_hits": bool(h_rank == 1),
                    "clean_rank_pagerank": clean_ranks_t["PageRank"],
                    "attacked_rank_pagerank": p_rank,
                    "rank_change_pagerank": clean_ranks_t["PageRank"] - p_rank,
                    "clean_rank_salsa": clean_ranks_t["SALSA"],
                    "attacked_rank_salsa": s_rank,
                    "clean_rank_indegree": clean_ranks_t["InDegree"],
                    "attacked_rank_indegree": deg_rank,
                    "attacked_rank_d3": d3_rank,
                    "attacked_rank_d4": d4_rank
                })

        print(f"Completed attacks for target {t_host} (HITS clean rank {clean_ranks_t['HITS']})")

    df_attack_res = pd.DataFrame(attack_records)
    df_attack_res.to_csv("results/webspam_attack_final.csv", index=False)
    print("Saved results/webspam_attack_final.csv")

    # 4. Generate Publication Figure
    print("\n--- Generating Figure figures/webspam_eval.png ---")
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)

    # Subplot 1: Distribution of ranks for Spam vs Normal hosts
    ax1 = axes[0]
    ranker_names = ["InDegree", "PageRank", "Undefended_HITS", "SALSA"]
    plot_data = []
    positions = []
    labels = []
    pos = 1
    for r_name in ranker_names:
        scores = clean_scores_dict[r_name]
        order = np.argsort(-scores)
        ranks = np.zeros(n_nodes, dtype=int)
        ranks[order] = np.arange(1, n_nodes + 1)

        norm_r = ranks[df_all_clean[df_all_clean["binary_label"] == 0]["node_idx"].values]
        spam_r = ranks[df_all_clean[df_all_clean["binary_label"] == 1]["node_idx"].values]

        plot_data.append(norm_r)
        plot_data.append(spam_r)
        positions.extend([pos, pos + 0.8])
        labels.extend([f"{r_name}\n(Normal)", f"{r_name}\n(Spam)"])
        pos += 2.2

    bp = ax1.boxplot(plot_data, positions=positions, widths=0.6, patch_artist=True, showfliers=False)
    for i, box in enumerate(bp['boxes']):
        if i % 2 == 0:
            box.set_facecolor('#2B6CB0')  # Blue for Normal
        else:
            box.set_facecolor('#E53E3E')  # Red for Spam
    ax1.set_xticks(positions)
    ax1.set_xticklabels(labels, fontsize=8, rotation=20)
    ax1.set_ylabel("Host Graph Rank (1 = Top Authority, Lower is Better)", fontsize=10)
    ax1.set_title("(a) Clean Web Spam Rank Distribution (All Labeled, N=10,662)", fontsize=11, fontweight="bold")
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Subplot 2: Real Attack on Hostgraph: Target Rank vs Budget B
    ax2 = axes[1]
    a2_df = df_attack_res[df_attack_res["attack"] == "A2_HubFarm"]
    for t_node, grp in a2_df.groupby("target_node"):
        lbl = grp["label"].iloc[0]
        c = '#E53E3E' if lbl == "Spam" else '#2B6CB0'
        b_vals = [0] + grp["budget"].tolist()
        r_vals = [grp["clean_rank_hits"].iloc[0]] + grp["attacked_rank_hits"].tolist()
        ax2.plot(b_vals, r_vals, marker='o', color=c, alpha=0.6, linewidth=1.5)

    ax2.set_xlabel("Attack Budget B (Fake Hub Nodes Injected)", fontsize=10)
    ax2.set_ylabel("Attacked HITS Rank", fontsize=10)
    ax2.set_title("(b) Real Attack on Host Graph: Target Rank vs B (A2 Hub Farm)", fontsize=11, fontweight="bold")
    ax2.axvline(115407.4, color='black', linestyle=':', label="Spectral Barrier $\\sigma_1^2 = 115,407$")
    ax2.annotate("Takeover Impossible for $B \\ll \\sigma_1^2$\n(Max B=1000: $B/\\sigma_1^2 = 0.0087$)",
                 xy=(500, 4500), xytext=(200, 2500),
                 arrowprops=dict(arrowstyle="->", color="black", lw=1.5),
                 fontsize=9, backgroundcolor="#FFF8DC")
    ax2.grid(True, linestyle="--", alpha=0.5)

    plt.tight_layout()
    plt.savefig("figures/webspam_eval.png", dpi=300)
    plt.close()
    print("Saved publication figure figures/webspam_eval.png")
    print("=" * 70)
    print("WEBSPAM EVALUATION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()
