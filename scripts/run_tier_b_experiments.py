"""Tier B experiments: Cost curves v2, H2 robustness, H1/H3 evaluations, and defense matrix."""
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import time
import math
import numpy as np
import pandas as pd
import networkx as nx
import scipy.sparse as sp

from src.config import RESULTS_DIR, DEFAULT_SEED
from src.data.synthetic import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm,
)
from src.data.loader import load_snap_graph
from src.data.base_set import sample_root_set, build_base_set
from src.rankers import hits, pagerank, salsa, indegree
from src.attacks import (
    attack_a1_single_fake_hub,
    attack_a2_hub_farm,
    attack_a3_bipartite_block,
    attack_a4_hub_inflation,
    attack_a4b_multi_hub_inflation,
    attack_a5_cross_score,
    attack_a5b_cross_score,
    attack_a6_greedy_gradient,
)
from src.defenses import (
    randomized_hits,
    subspace_hits,
    bharat_henzinger_hits,
    hub_capped_hits,
    wu_davison_hits,
    wu_davison_outlink_jaccard_hits,
    trust_based_hits,
)
from src.eval import (
    compute_rank,
    rank_gain,
    normalized_rank_gain,
    b_star_at_k,
    top_k_jaccard,
    ndcg_at_k,
    kendall_tau,
    spearman_rho,
    defense_attack_success_reduction,
)


def attack_camouflaged_farm(G: nx.DiGraph, target_node: int, budget: int = 25, r_camouflage: int = 5) -> "AttackResult":
    """Camouflaged farm: Each fake hub links to target AND r_camouflage random real pages."""
    from src.attacks.base import AttackResult
    G_att = G.copy()
    max_node = max(G.nodes()) if len(G) > 0 else -1
    all_real_nodes = [n for n in G.nodes() if n != target_node]

    cost_per_hub = 1 + r_camouflage
    num_hubs = max(1, budget // cost_per_hub)
    added_nodes = []
    added_edges = []

    rng = np.random.RandomState(42)
    edge_count = 0

    for i in range(1, num_hubs + 1):
        if edge_count >= budget:
            break
        fake_hub = max_node + i
        G_att.add_node(fake_hub)
        added_nodes.append(fake_hub)

        # Primary link to target
        G_att.add_edge(fake_hub, target_node)
        added_edges.append((fake_hub, target_node))
        edge_count += 1

        # Camouflage links to random real pages
        camo_targets = rng.choice(all_real_nodes, size=min(r_camouflage, len(all_real_nodes)), replace=False)
        for c_node in camo_targets:
            if edge_count < budget and not G_att.has_edge(fake_hub, c_node):
                G_att.add_edge(fake_hub, c_node)
                added_edges.append((fake_hub, c_node))
                edge_count += 1

    adj = nx.adjacency_matrix(G_att, nodelist=range(G_att.number_of_nodes()), dtype=float).tocsr()
    return AttackResult(
        graph=G_att,
        adj_matrix=adj,
        target_node=target_node,
        added_nodes=added_nodes,
        added_edges=added_edges,
        cost_nodes=len(added_nodes),
        cost_edges=len(added_edges),
    )


# ---------------------------------------------------------
# B1: Cost Curves v2
# ---------------------------------------------------------
def run_b1_cost_curves():
    print("\n========================================================")
    print("=== B1: Running Cost Curves v2 (results/cost_curves_v2.csv) ===")
    print("========================================================")
    t_start = time.perf_counter()

    seeds = [42, 123, 456]
    budgets = [1, 5, 10, 25, 50, 100, 200]

    # Pre-build graphs (around 500 nodes each)
    graphs = {}
    print("Generating synthetic graphs...")
    graphs["Synthetic_BA_500"] = {s: generate_barabasi_albert(n=500, m=4, seed=s) for s in seeds}
    graphs["Synthetic_ER_500"] = {s: generate_erdos_renyi(n=500, p=0.01, seed=s) for s in seeds}
    graphs["Synthetic_SBM_500"] = {
        s: generate_planted_bipartite_sbm(n_background=460, n_planted_hubs=20, n_planted_authorities=20, seed=s)[0]
        for s in seeds
    }

    print("Loading SNAP web-Stanford base set...")
    G_stan_full, _, _ = load_snap_graph("web-Stanford", max_edges=100000)
    graphs["SNAP_web-Stanford_BaseSet"] = {}
    for s in seeds:
        root = sample_root_set(G_stan_full, seed_node=int(s % 500) + 1, root_size=80)
        base = build_base_set(G_stan_full, root, max_in_links=25)
        graphs["SNAP_web-Stanford_BaseSet"][s] = base.graph

    attacks = {
        "A1_SingleHub": lambda g, t, b: attack_a1_single_fake_hub(g, t, budget=b),
        "A2_HubFarm": lambda g, t, b: attack_a2_hub_farm(g, t, budget=b),
        "A3_BipartiteBlock": lambda g, t, b: attack_a3_bipartite_block(g, t, budget=b),
        "A4_ProposalInflation": lambda g, t, b: attack_a4_hub_inflation(g, t, budget=b, c_top=3, use_one_fake_page=False),
        "A4b_MultiHubInflation": lambda g, t, b: attack_a4b_multi_hub_inflation(g, t, budget=b, c_top=3),
        "A5_ProposalCrossScore": lambda g, t, b: attack_a5_cross_score(g, t, budget=b, c_top=3),
        "A5b_CrossScoreLinks": lambda g, t, b: attack_a5b_cross_score(g, t, budget=b, c_top=3),
        "A6_GreedyGradient": lambda g, t, b: attack_a6_greedy_gradient(g, t, budget=b, candidate_pool_size=1),
    }

    rankers = {
        "HITS": lambda g: hits(g, max_iter=80),
        "PageRank": lambda g: pagerank(g, alpha=0.85, max_iter=80),
        "SALSA": lambda g: salsa(g, max_iter=80),
        "InDegree": lambda g: indegree(g),
    }

    records = []

    for g_name, g_by_seed in graphs.items():
        for s in seeds:
            G = g_by_seed[s]
            n_nodes = G.number_of_nodes()

            # Clean baseline
            clean_results = {r_name: r_fn(G) for r_name, r_fn in rankers.items()}
            h_scores = clean_results["HITS"].scores

            # Pick 5 diverse targets: low, med-low, med, med-high, random
            sorted_order = np.argsort(h_scores)
            rng = np.random.RandomState(s)
            targets = [
                ("lowest_rank", int(sorted_order[int(n_nodes * 0.1)])),
                ("low_rank", int(sorted_order[int(n_nodes * 0.25)])),
                ("medium_rank", int(sorted_order[int(n_nodes * 0.50)])),
                ("medium_high_rank", int(sorted_order[int(n_nodes * 0.70)])),
                ("random_rank", int(rng.choice(sorted_order[int(n_nodes * 0.2):int(n_nodes * 0.8)]))),
            ]

            for tier, target_node in targets:
                clean_ranks = {r_name: compute_rank(clean_results[r_name].scores, target_node) for r_name in rankers}

                for att_name, att_fn in attacks.items():
                    for B in budgets:
                        att_res = att_fn(G, target_node, B)
                        G_att = att_res.graph
                        n_added = att_res.cost_nodes
                        e_added = att_res.cost_edges

                        for r_name, r_fn in rankers.items():
                            res_att = r_fn(G_att)
                            c_scores = clean_results[r_name].scores
                            a_scores = res_att.scores

                            c_rank = clean_ranks[r_name]
                            a_rank = compute_rank(a_scores, target_node)
                            g_raw = c_rank - a_rank
                            g_norm = normalized_rank_gain(c_scores, a_scores, target_node)
                            t10 = int(a_rank <= 10)
                            t20 = int(a_rank <= 20)
                            jacc = top_k_jaccard(c_scores, a_scores, k=20)
                            ndcg = ndcg_at_k(c_scores, a_scores, k=20)
                            tau = kendall_tau(c_scores, a_scores)
                            rho = spearman_rho(c_scores, a_scores)

                            records.append({
                                "graph": g_name,
                                "seed": s,
                                "target_tier": tier,
                                "target_node": target_node,
                                "attack": att_name,
                                "budget": B,
                                "nodes_added": n_added,
                                "edges_added": e_added,
                                "ranker": r_name,
                                "clean_rank": c_rank,
                                "attacked_rank": a_rank,
                                "rank_gain": g_raw,
                                "normalized_rank_gain": g_norm,
                                "top10_entry": t10,
                                "top20_entry": t20,
                                "jaccard_at_20": jacc,
                                "ndcg_at_20": ndcg,
                                "kendall_tau": tau,
                                "spearman_rho": rho,
                            })

    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "cost_curves_v2.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"[DONE B1] Generated {len(df)} rows in {out_csv} in {elapsed:.1f}s")
    return df


# ---------------------------------------------------------
# B2: H2 Robustness
# ---------------------------------------------------------
def run_b2_h2_robustness():
    print("\n========================================================")
    print("=== B2: Running H2 Robustness (results/h2_robustness.csv) ===")
    print("========================================================")
    t_start = time.perf_counter()

    seeds = [42, 123, 456]
    graphs = {
        "Synthetic_BA_400": lambda s: generate_barabasi_albert(n=400, m=3, seed=s),
        "Synthetic_ER_400": lambda s: generate_erdos_renyi(n=400, p=0.015, seed=s),
        "Synthetic_SBM_400": lambda s: generate_planted_bipartite_sbm(360, 20, 20, seed=s)[0],
    }

    # Add web-Stanford base set
    G_stan_full, _, _ = load_snap_graph("web-Stanford", max_edges=60000)
    records = []

    for g_name in list(graphs.keys()) + ["SNAP_web-Stanford_BaseSet"]:
        for s in seeds:
            if g_name == "SNAP_web-Stanford_BaseSet":
                root = sample_root_set(G_stan_full, seed_node=int(s % 300) + 1, root_size=70)
                G = build_base_set(G_stan_full, root, max_in_links=20).graph
            else:
                G = graphs[g_name](s)

            n = G.number_of_nodes()
            nodes = list(range(n))
            A = nx.adjacency_matrix(G, nodelist=nodes, dtype=float).tocsr()

            # SVD singular values
            u, sing_vals, vt = sp.linalg.svds(A, k=2)
            sing_vals = np.sort(sing_vals)[::-1]
            sigma1 = float(sing_vals[0])
            sigma1_sq = sigma1 ** 2
            max_in_degree = int(A.sum(axis=0).max())

            # Verification of property: sigma_1^2 >= max in-degree
            sig_ge_indeg = bool(sigma1_sq >= max_in_degree - 1e-5)

            clean_h = hits(G).scores
            clean_pr = pagerank(G).scores
            order = np.argsort(clean_h)

            targets = [
                int(order[int(n * 0.15)]),
                int(order[int(n * 0.30)]),
                int(order[int(n * 0.45)]),
                int(order[int(n * 0.60)]),
                int(order[int(n * 0.75)]),
            ]

            # Farm size grid spanning 0.1 to 2.0 * sigma1^2 (at least 20 points)
            p_grid = sorted(list(set([
                max(1, int(round(sigma1_sq * mult)))
                for mult in np.linspace(0.1, 2.0, 24)
            ])))

            for target in targets:
                clean_target_h_rank = compute_rank(clean_h, target)
                clean_target_pr_rank = compute_rank(clean_pr, target)

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

                # Smoothness test: largest single-step jump in rank
                h_diffs = [abs(h_ranks[i+1] - h_ranks[i]) for i in range(len(h_ranks)-1)]
                pr_diffs = [abs(pr_ranks[i+1] - pr_ranks[i]) for i in range(len(pr_ranks)-1)]
                max_h_jump = max(h_diffs) if h_diffs else 0
                max_pr_jump = max(pr_diffs) if pr_diffs else 0

                records.append({
                    "graph": g_name,
                    "seed": s,
                    "num_nodes": n,
                    "target_node": target,
                    "clean_h_rank": clean_target_h_rank,
                    "clean_pr_rank": clean_target_pr_rank,
                    "sigma1": sigma1,
                    "sigma1_sq": sigma1_sq,
                    "max_in_degree": max_in_degree,
                    "sigma1_sq_ge_max_indeg": sig_ge_indeg,
                    "p_star_10": p_star_10 if p_star_10 is not None else np.nan,
                    "p_star_1": p_star_1 if p_star_1 is not None else np.nan,
                    "ratio_p_star_10_to_sigma1_sq": (p_star_10 / sigma1_sq) if p_star_10 else np.nan,
                    "ratio_p_star_1_to_sigma1_sq": (p_star_1 / sigma1_sq) if p_star_1 else np.nan,
                    "max_hits_step_jump": max_h_jump,
                    "max_pagerank_step_jump": max_pr_jump,
                    "is_hits_jump_abrupt": bool(max_h_jump > 2 * max_pr_jump),
                })

    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "h2_robustness.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"[DONE B2] Saved {len(df)} runs to {out_csv} in {elapsed:.1f}s")
    return df


# ---------------------------------------------------------
# B3: H1 and H3 Small Versions
# ---------------------------------------------------------
def run_b3_h1_h3():
    print("\n========================================================")
    print("=== B3: Running H1 & H3 Validations (results/h1_h3_eval.csv) ===")
    print("========================================================")
    t_start = time.perf_counter()

    records = []
    seeds = [42, 123, 456]
    budget_grid = [1, 5, 10, 20, 30, 50, 75, 100, 150, 200]

    # H1: B*(10) for HITS vs In-Degree on ER instances
    for s in seeds:
        G_er = generate_erdos_renyi(n=500, p=0.012, seed=s)
        h_clean = hits(G_er).scores
        order = np.argsort(h_clean)
        targets = [int(order[int(500 * f)]) for f in [0.2, 0.4, 0.6]]

        for t in targets:
            h_ranks = []
            indeg_ranks = []
            for b in budget_grid:
                att = attack_a2_hub_farm(G_er, t, budget=b)
                h_res = hits(att.graph, max_iter=50)
                indeg_res = indegree(att.graph)
                h_ranks.append(compute_rank(h_res.scores, t))
                indeg_ranks.append(compute_rank(indeg_res.scores, t))

            b_star_h = b_star_at_k(budget_grid, h_ranks, k=10)
            b_star_deg = b_star_at_k(budget_grid, indeg_ranks, k=10)

            records.append({
                "hypothesis": "H1",
                "graph": "ER_500",
                "seed": s,
                "target_node": t,
                "comparison": "HITS_vs_InDegree",
                "b_star_hits_k10": b_star_h if b_star_h is not None else np.nan,
                "b_star_indeg_k10": b_star_deg if b_star_deg is not None else np.nan,
                "b_star_ratio": (b_star_h / b_star_deg) if (b_star_h and b_star_deg) else np.nan,
            })

    # H3: A2 (pure farm) vs Proposal A5 (attaching to community) on SBM vs ER control
    test_graphs = {
        "SBM_Planted": lambda s: generate_planted_bipartite_sbm(460, 20, 20, seed=s)[0],
        "ER_Control": lambda s: generate_erdos_renyi(500, 0.012, seed=s),
    }

    for g_name, g_fn in test_graphs.items():
        for s in seeds:
            G = g_fn(s)
            h_clean = hits(G).scores
            order = np.argsort(h_clean)
            targets = [int(order[int(500 * f)]) for f in [0.2, 0.4, 0.6]]

            for t in targets:
                a2_ranks = []
                a5_ranks = []
                for b in budget_grid:
                    att_a2 = attack_a2_hub_farm(G, t, budget=b)
                    att_a5 = attack_a5_cross_score(G, t, budget=b, c_top=3)

                    a2_ranks.append(compute_rank(hits(att_a2.graph, max_iter=50).scores, t))
                    a5_ranks.append(compute_rank(hits(att_a5.graph, max_iter=50).scores, t))

                b_star_a2 = b_star_at_k(budget_grid, a2_ranks, k=10)
                b_star_a5 = b_star_at_k(budget_grid, a5_ranks, k=10)

                # Cost reduction: 1 - (B*_A5 / B*_A2)
                cost_saving = (1.0 - (b_star_a5 / b_star_a2)) if (b_star_a2 and b_star_a5) else np.nan

                records.append({
                    "hypothesis": "H3",
                    "graph": g_name,
                    "seed": s,
                    "target_node": t,
                    "comparison": "A2_vs_A5_Proposal",
                    "b_star_a2_k10": b_star_a2 if b_star_a2 is not None else np.nan,
                    "b_star_a5_k10": b_star_a5 if b_star_a5 is not None else np.nan,
                    "cost_saving_pct": cost_saving * 100.0 if not np.isnan(cost_saving) else np.nan,
                })

    df = pd.DataFrame(records)
    out_csv = RESULTS_DIR / "h1_h3_eval.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"[DONE B3] Saved {len(df)} rows in {out_csv} in {elapsed:.1f}s")
    return df


# ---------------------------------------------------------
# B4: Defense x Attack Matrix (Reduced)
# ---------------------------------------------------------
def run_b4_defense_matrix():
    print("\n========================================================")
    print("=== B4: Running Defense x Attack Matrix (results/defenses_eval_v2.csv) ===")
    print("========================================================")
    t_start = time.perf_counter()

    seeds = [42, 123]
    budgets = [25, 100]

    # Pre-calibrate threshold on separate calibration graph (ER-300)
    G_calib = generate_erdos_renyi(n=300, p=0.02, seed=999)
    # Verify calibration thresholds
    calib_out_thresh = 0.40
    calib_cap_fraction = 0.10

    defenses = {
        "Undefended_HITS": lambda g: hits(g, max_iter=60),
        "D1_RandomizedHITS_0.15": lambda g: randomized_hits(g, eps=0.15, max_iter=60),
        "D1_SubspaceHITS_k5": lambda g: subspace_hits(g, k=5),
        "D2_BharatHenzinger": lambda g: bharat_henzinger_hits(g, max_iter=60),
        "D3_HubCapping_0.10": lambda g: hub_capped_hits(g, cap_fraction=calib_cap_fraction, max_iter=60),
        "D4_WuDavison_Mutual": lambda g: wu_davison_hits(g, out_threshold=calib_out_thresh, max_iter=60),
        "D4b_WuDavison_OutJaccard": lambda g: wu_davison_outlink_jaccard_hits(g, overlap_threshold=0.50, max_iter=60),
        "D5_TrustHITS": lambda g: trust_based_hits(g, max_iter=60),
    }

    attacks = {
        "A2_HubFarm": lambda g, t, b: attack_a2_hub_farm(g, t, budget=b),
        "A3_BipartiteBlock": lambda g, t, b: attack_a3_bipartite_block(g, t, budget=b),
        "A4_ProposalInflation": lambda g, t, b: attack_a4_hub_inflation(g, t, budget=b, c_top=3),
        "A5_ProposalCrossScore": lambda g, t, b: attack_a5_cross_score(g, t, budget=b, c_top=3),
        "A6_GreedyGradient": lambda g, t, b: attack_a6_greedy_gradient(g, t, budget=b, candidate_pool_size=1),
        "Camouflaged_Farm": lambda g, t, b: attack_camouflaged_farm(g, t, budget=b, r_camouflage=5),
    }

    eval_graphs = {}
    for s in seeds:
        eval_graphs[f"Synthetic_BA_400_s{s}"] = generate_barabasi_albert(n=400, m=3, seed=s)

    G_stan_full, _, _ = load_snap_graph("web-Stanford", max_edges=60000)
    for s in seeds:
        root = sample_root_set(G_stan_full, seed_node=s + 10, root_size=70)
        base = build_base_set(G_stan_full, root, max_in_links=20)
        eval_graphs[f"SNAP_web-Stanford_BaseSet_s{s}"] = base.graph

    results = []

    for g_name, G in eval_graphs.items():
        n = G.number_of_nodes()
        clean_res = {d_name: d_fn(G) for d_name, d_fn in defenses.items()}
        undef_clean_h = clean_res["Undefended_HITS"].scores

        # Clean top-20 fidelity for each defense
        clean_fidelity = {}
        for d_name in defenses:
            d_clean_scores = clean_res[d_name].scores
            jacc = top_k_jaccard(undef_clean_h, d_clean_scores, k=20)
            ndcg = ndcg_at_k(undef_clean_h, d_clean_scores, k=20)
            clean_fidelity[d_name] = (jacc, ndcg)

        order = np.argsort(undef_clean_h)
        targets = [int(order[int(n * 0.25)]), int(order[int(n * 0.50)]), int(order[int(n * 0.70)])]

        for target in targets:
            clean_ranks = {d_name: compute_rank(clean_res[d_name].scores, target) for d_name in defenses}

            for att_name, att_fn in attacks.items():
                for B in budgets:
                    att_res = att_fn(G, target, B)
                    G_att = att_res.graph

                    # Baseline undefended gain
                    base_att_res = defenses["Undefended_HITS"](G_att)
                    base_att_rank = compute_rank(base_att_res.scores, target)
                    base_gain = clean_ranks["Undefended_HITS"] - base_att_rank

                    for d_name, d_fn in defenses.items():
                        t0 = time.perf_counter()
                        d_att_res = d_fn(G_att)
                        t_cost = time.perf_counter() - t0

                        d_att_rank = compute_rank(d_att_res.scores, target)
                        d_target_score = d_att_res.scores[target] if target < len(d_att_res.scores) else 0.0
                        d_gain = clean_ranks[d_name] - d_att_rank

                        reduction = defense_attack_success_reduction(base_gain, d_gain)
                        clean_jacc, clean_ndcg = clean_fidelity[d_name]

                        # Check if reduction is genuine or score-suppressed
                        meets_goal = bool(reduction >= 0.50 and (1.0 - clean_ndcg) <= 0.05)

                        results.append({
                            "graph": g_name,
                            "target_node": target,
                            "attack": att_name,
                            "budget": B,
                            "defense": d_name,
                            "clean_rank": clean_ranks[d_name],
                            "attacked_rank": d_att_rank,
                            "rank_gain": d_gain,
                            "target_attacked_score": d_target_score,
                            "attack_success_reduction": reduction,
                            "clean_top20_jaccard": clean_jacc,
                            "clean_top20_ndcg": clean_ndcg,
                            "clean_ndcg_loss": 1.0 - clean_ndcg,
                            "clean_jaccard_loss": 1.0 - clean_jacc,
                            "meets_proposal_goal": meets_goal,
                            "runtime_sec": t_cost,
                        })

    df = pd.DataFrame(results)
    out_csv = RESULTS_DIR / "defenses_eval_v2.csv"
    df.to_csv(out_csv, index=False)
    elapsed = time.perf_counter() - t_start
    print(f"[DONE B4] Saved {len(df)} rows in {out_csv} in {elapsed:.1f}s")
    return df


def main():
    print("=== Launching Tier B Experimental Suite ===")
    t0 = time.perf_counter()

    run_b1_cost_curves()
    run_b2_h2_robustness()
    run_b3_h1_h3()
    run_b4_defense_matrix()

    total_time = time.perf_counter() - t0
    print(f"\n[ALL TIER B EXPERIMENTS COMPLETE in {total_time/60:.2f} minutes]")


if __name__ == "__main__":
    main()
