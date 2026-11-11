"""WEBSPAM-UK2006 Real-World Link Spam Evaluation Script.

Evaluates HITS, PageRank, SALSA, In-Degree, and Defenses (D1, D2, D3, D4, D4b, D5)
on the real-world WEBSPAM-UK2006 host graph (11,402 hosts, 730,774 edges).
"""
import sys
from pathlib import Path
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, f1_score, precision_recall_curve
import networkx as nx

from src.data.loader import load_webspam_hostgraph, load_webspam_labels
from src.rankers import hits, pagerank, salsa, indegree
from src.defenses import (
    randomized_hits,
    hub_capped_hits,
    wu_davison_hits,
    wu_davison_outlink_jaccard_hits,
    trust_based_hits,
    bharat_henzinger_hits
)


def run_webspam_evaluation():
    print("==================================================================")
    print("=== WEBSPAM-UK2006 REAL-WORLD SPAM EVALUATION ===")
    print("==================================================================")

    # 1. Load Host Graph
    print("Loading WEBSPAM hostgraph...")
    t0 = time.time()
    G, adj, n2h, h2n = load_webspam_hostgraph()
    n_nodes = len(n2h)
    n_edges = G.number_of_edges()
    print(f"Loaded hostgraph: {n_nodes} nodes, {n_edges} edges in {time.time()-t0:.2f}s")

    # 2. Load Labels
    df_set1 = load_webspam_labels("set1", undecided_mode="keep")
    df_set2 = load_webspam_labels("set2", undecided_mode="keep")

    print("\n--- Label Reconciliations ---")
    print(f"Set 1 total: {len(df_set1)} | normal: {(df_set1['binary_label']==0).sum()}, spam: {(df_set1['binary_label']==1).sum()}, undecided: {(df_set1['binary_label']==-1).sum()}")
    print(f"Set 2 total: {len(df_set2)} | normal: {(df_set2['binary_label']==0).sum()}, spam: {(df_set2['binary_label']==1).sum()}, undecided: {(df_set2['binary_label']==-1).sum()}")

    # Merge labels with host nodes
    # Map to node_id
    host_labels = {}
    for _, row in df_set1.iterrows():
        h = row["host"]
        if h in h2n:
            host_labels[h2n[h]] = {"split": "set1", "label": row["binary_label"], "spamicity": row["spamicity"]}

    for _, row in df_set2.iterrows():
        h = row["host"]
        if h in h2n:
            host_labels[h2n[h]] = {"split": "set2", "label": row["binary_label"], "spamicity": row["spamicity"]}

    print(f"Total labeled nodes in graph: {len(host_labels)} / {n_nodes} ({len(host_labels)/n_nodes*100:.1f}%)")
    unlabeled_count = n_nodes - len(host_labels)
    print(f"Unlabeled hosts in graph: {unlabeled_count}")

    # Create node label array: 0=normal, 1=spam, -1=undecided, -2=unlabeled
    node_binary_label = np.full(n_nodes, -2, dtype=int)
    node_spamicity = np.full(n_nodes, np.nan, dtype=float)
    node_split = np.full(n_nodes, "unlabeled", dtype=object)

    for nid, d in host_labels.items():
        node_binary_label[nid] = d["label"]
        node_spamicity[nid] = d["spamicity"]
        node_split[nid] = d["split"]

    # Gold standard trust seeds: Set 1 normal hosts with 0 spamicity
    set1_normal_seeds = [
        nid for nid, d in host_labels.items()
        if d["split"] == "set1" and d["label"] == 0 and d["spamicity"] == 0.0
    ]
    print(f"Extracted {len(set1_normal_seeds)} authentic normal seeds from Set 1 for Trust-Based HITS (D5)")

    # 3. Define Algorithms to Run
    algorithms = {}

    print("\nRunning Algorithms on Whole Hostgraph...")
    # Baselines
    t_start = time.time()
    algorithms["InDegree"] = indegree(adj)
    print(f"  InDegree computed in {time.time()-t_start:.2f}s")

    t_start = time.time()
    algorithms["PageRank"] = pagerank(adj)
    print(f"  PageRank computed in {time.time()-t_start:.2f}s")

    t_start = time.time()
    algorithms["Undefended_HITS"] = hits(adj, max_iter=100)
    print(f"  Undefended HITS computed in {time.time()-t_start:.2f}s (iter: {algorithms['Undefended_HITS'].iterations})")

    t_start = time.time()
    algorithms["SALSA"] = salsa(adj, max_iter=100)
    print(f"  SALSA computed in {time.time()-t_start:.2f}s (iter: {algorithms['SALSA'].iterations})")

    # Defenses
    t_start = time.time()
    algorithms["D1_RandomizedHITS_0.15"] = randomized_hits(adj, eps=0.15, max_iter=100)
    print(f"  D1 Randomized HITS (eps=0.15) computed in {time.time()-t_start:.2f}s")

    t_start = time.time()
    algorithms["D3_HubCapping_0.01"] = hub_capped_hits(adj, cap_fraction=0.01, max_iter=100)
    print(f"  D3 Hub Capping (cap=0.01) computed in {time.time()-t_start:.2f}s")

    t_start = time.time()
    algorithms["D4_WuDavison_Mutual"] = wu_davison_hits(adj, max_iter=100)
    print(f"  D4 Wu-Davison Mutual computed in {time.time()-t_start:.2f}s")

    t_start = time.time()
    algorithms["D4b_WuDavison_OutJaccard"] = wu_davison_outlink_jaccard_hits(adj, max_iter=100)
    print(f"  D4b Wu-Davison OutJaccard computed in {time.time()-t_start:.2f}s")

    t_start = time.time()
    # D5 with Genuine Set-1 Normal Seeds (first 200 high-degree normal seeds)
    # Select seeds among set1_normal_seeds sorted by in-degree
    indeg_scores = algorithms["InDegree"].scores
    sorted_normal_seeds = sorted(set1_normal_seeds, key=lambda n: -indeg_scores[n])[:200]
    algorithms["D5_TrustHITS_Set1Seeds"] = trust_based_hits(adj, trusted_seeds=sorted_normal_seeds, eps=0.15, max_iter=100)
    print(f"  D5 Trust-Based HITS (200 Set-1 seeds) computed in {time.time()-t_start:.2f}s")

    # 4. Evaluation Metrics
    # We evaluate spam@k for k in [10, 20, 50, 100]
    # And AUC / F1 on labeled hosts (evaluating both on Set 2 test set, and All labeled)
    ks = [10, 20, 50, 100]
    eval_results = []

    print("\n--- Algorithm Performance & Spam Vulnerability ---")
    for name, res in algorithms.items():
        scores = res.scores
        ranking = np.argsort(-scores)

        # Compute spam@k on top-k nodes
        spam_at_k = {}
        for k in ks:
            top_k_nodes = ranking[:k]
            top_k_labels = [node_binary_label[n] for n in top_k_nodes]
            # Labeled counts
            n_spam = sum(1 for l in top_k_labels if l == 1)
            n_normal = sum(1 for l in top_k_labels if l == 0)
            n_undecided = sum(1 for l in top_k_labels if l == -1)
            n_unlabeled = sum(1 for l in top_k_labels if l == -2)
            n_evaluable = n_spam + n_normal
            # Fraction spam among labeled, and fraction spam among all k
            pct_spam_all = (n_spam / k) * 100.0
            pct_spam_labeled = (n_spam / n_evaluable * 100.0) if n_evaluable > 0 else 0.0
            spam_at_k[k] = {
                "n_spam": n_spam,
                "n_normal": n_normal,
                "n_undecided": n_undecided,
                "n_unlabeled": n_unlabeled,
                "pct_spam_all": pct_spam_all,
                "pct_spam_labeled": pct_spam_labeled
            }

        # Compute AUC and best F1 using Hub/Auth ratio and inverse score as spam predictor
        # In link spam, ratio = hub_score / (auth_score + 1e-9) is classic spamicity flag
        hub_scores = getattr(res, "hub_scores", None)
        if hub_scores is not None and len(hub_scores) == n_nodes:
            spam_predictor = hub_scores / (scores + 1e-12)
        else:
            spam_predictor = -scores  # Lower authority score correlates with spam

        # Evaluation on Set 2 (Strict Test Split, excluding undecided)
        test_mask = (node_split == "set2") & (node_binary_label >= 0)
        y_test = node_binary_label[test_mask]
        s_test = spam_predictor[test_mask]

        if len(y_test) > 0 and len(np.unique(y_test)) == 2:
            auc_test = roc_auc_score(y_test, s_test)
            # Best F1
            prec, rec, thresholds = precision_recall_curve(y_test, s_test)
            f1_scores = 2 * (prec * rec) / (prec + rec + 1e-12)
            best_f1_test = np.max(f1_scores)
        else:
            auc_test = 0.5
            best_f1_test = 0.0

        # Evaluation on All Labeled (Set 1 + Set 2, excluding undecided)
        all_mask = (node_binary_label >= 0)
        y_all = node_binary_label[all_mask]
        s_all = spam_predictor[all_mask]
        auc_all = roc_auc_score(y_all, s_all) if len(np.unique(y_all)) == 2 else 0.5
        prec, rec, _ = precision_recall_curve(y_all, s_all)
        best_f1_all = np.max(2 * (prec * rec) / (prec + rec + 1e-12))

        record = {
            "algorithm": name,
            "runtime_s": getattr(res, "elapsed_time", 0.0),
            "spam@10": spam_at_k[10]["n_spam"],
            "spam@10_pct": spam_at_k[10]["pct_spam_all"],
            "spam@20": spam_at_k[20]["n_spam"],
            "spam@20_pct": spam_at_k[20]["pct_spam_all"],
            "spam@50": spam_at_k[50]["n_spam"],
            "spam@50_pct": spam_at_k[50]["pct_spam_all"],
            "spam@100": spam_at_k[100]["n_spam"],
            "spam@100_pct": spam_at_k[100]["pct_spam_all"],
            "test_set2_auc": auc_test,
            "test_set2_f1": best_f1_test,
            "all_labeled_auc": auc_all,
            "all_labeled_f1": best_f1_all,
            "top10_details": f"Spam:{spam_at_k[10]['n_spam']}, Norm:{spam_at_k[10]['n_normal']}, Undec:{spam_at_k[10]['n_undecided']}, Unlab:{spam_at_k[10]['n_unlabeled']}",
            "top20_details": f"Spam:{spam_at_k[20]['n_spam']}, Norm:{spam_at_k[20]['n_normal']}, Undec:{spam_at_k[20]['n_undecided']}, Unlab:{spam_at_k[20]['n_unlabeled']}"
        }
        eval_results.append(record)
        print(f"[{name:25s}] Spam@10: {spam_at_k[10]['n_spam']:2d} ({spam_at_k[10]['pct_spam_all']:4.1f}%) | "
              f"Spam@20: {spam_at_k[20]['n_spam']:2d} ({spam_at_k[20]['pct_spam_all']:4.1f}%) | "
              f"Spam@50: {spam_at_k[50]['n_spam']:2d} ({spam_at_k[50]['pct_spam_all']:4.1f}%) | "
              f"Spam@100: {spam_at_k[100]['n_spam']:2d} ({spam_at_k[100]['pct_spam_all']:4.1f}%) | "
              f"AUC(Set2): {auc_test:.3f} | F1(Set2): {best_f1_test:.3f}")

    eval_df = pd.DataFrame(eval_results)
    out_csv = Path("results/webspam_eval.csv")
    eval_df.to_csv(out_csv, index=False)
    print(f"\nSaved WEBSPAM evaluation results to {out_csv}")
    return eval_df


if __name__ == "__main__":
    run_webspam_evaluation()

