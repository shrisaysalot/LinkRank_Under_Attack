"""Unit tests for evaluation metrics and statistical testing."""
import numpy as np
import pytest

from src.eval import (
    compute_rank,
    rank_gain,
    normalized_rank_gain,
    b_star_at_k,
    top_k_jaccard,
    ndcg_at_k,
    kendall_tau,
    spearman_rho,
    fake_share_at_k,
    defense_attack_success_reduction,
    bootstrap_ci,
    wilcoxon_test,
    holm_bonferroni,
)


def test_ranking_metrics():
    clean = np.array([0.5, 0.3, 0.1, 0.05, 0.05])
    # Node 2 is rank 3 (0.5, 0.3 are higher)
    assert compute_rank(clean, 2) == 3

    # Attacked: node 2 boosted to rank 1
    attacked = np.array([0.2, 0.1, 0.6, 0.05, 0.05])
    assert compute_rank(attacked, 2) == 1
    assert rank_gain(clean, attacked, 2) == 2  # 3 - 1 = 2

    # Normalized rank gain: (3 - 1) / (3 - 1) = 1.0 (reached top rank)
    assert normalized_rank_gain(clean, attacked, 2) == 1.0

    # Intermediate boost: node 2 boosted to rank 2
    attacked_mid = np.array([0.5, 0.2, 0.3, 0.0, 0.0])
    # rank of node 2 in attacked_mid: 0.5 > 0.3 -> rank 2
    assert compute_rank(attacked_mid, 2) == 2
    assert normalized_rank_gain(clean, attacked_mid, 2) == 0.5  # (3 - 2)/(3 - 1) = 0.5


def test_b_star_at_k():
    budgets = [1, 5, 10, 25, 50]
    ranks = [100, 50, 15, 8, 1]

    # Target enters top 10 at budget 25
    b_star_10 = b_star_at_k(budgets, ranks, k=10)
    assert b_star_10 == 25

    # Target enters top 20 at budget 10
    b_star_20 = b_star_at_k(budgets, ranks, k=20)
    assert b_star_20 == 10

    # Never enters top 0
    assert b_star_at_k(budgets, ranks, k=0) is None


def test_correlations():
    x = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    y = np.array([2.0, 4.0, 6.0, 8.0, 10.0])
    assert np.isclose(spearman_rho(x, y), 1.0)
    assert np.isclose(kendall_tau(x, y), 1.0)

    y_inv = np.array([5.0, 4.0, 3.0, 2.0, 1.0])
    assert np.isclose(spearman_rho(x, y_inv), -1.0)
    assert np.isclose(kendall_tau(x, y_inv), -1.0)


def test_bootstrap_ci():
    data = [10.0, 12.0, 11.0, 10.5, 11.5, 9.8, 12.2]
    mean, lower, upper = bootstrap_ci(data, n_boot=500, ci=0.95, seed=42)
    assert lower <= mean <= upper
    assert 9.5 < mean < 12.5


def test_wilcoxon_test():
    x = [10, 12, 14, 16, 18, 20, 22, 24]
    y = [9, 11, 13, 15, 17, 19, 21, 23]
    stat, p = wilcoxon_test(x, y)
    assert p < 0.05  # x is strictly greater than y


def test_holm_bonferroni():
    # 3 p-values: one highly significant, one borderline, one non-significant
    p_vals = [0.005, 0.02, 0.10]
    rejected, adj_p = holm_bonferroni(p_vals, alpha=0.05)
    # Sorted: 0.005 (x3 = 0.015), 0.02 (x2 = 0.04), 0.10 (x1 = 0.10)
    assert rejected[0] == True
    assert rejected[1] == True
    assert rejected[2] == False
    assert np.isclose(adj_p[0], 0.015)
    assert np.isclose(adj_p[1], 0.040)
    assert np.isclose(adj_p[2], 0.100)


def test_independent_per_attack_eval():
    """Tests aggregating paired differences per unit before Wilcoxon testing."""
    df_dummy = [
        {"graph": "G1", "target": 1, "ranker": "HITS", "gain": 0.9},
        {"graph": "G1", "target": 1, "ranker": "PR", "gain": 0.2},
        {"graph": "G1", "target": 2, "ranker": "HITS", "gain": 0.8},
        {"graph": "G1", "target": 2, "ranker": "PR", "gain": 0.3},
        {"graph": "G2", "target": 1, "ranker": "HITS", "gain": 0.95},
        {"graph": "G2", "target": 1, "ranker": "PR", "gain": 0.1},
        {"graph": "G2", "target": 2, "ranker": "HITS", "gain": 0.85},
        {"graph": "G2", "target": 2, "ranker": "PR", "gain": 0.4},
        {"graph": "G3", "target": 1, "ranker": "HITS", "gain": 0.7},
        {"graph": "G3", "target": 1, "ranker": "PR", "gain": 0.2},
        {"graph": "G3", "target": 2, "ranker": "HITS", "gain": 0.75},
        {"graph": "G3", "target": 2, "ranker": "PR", "gain": 0.25},
    ]
    import pandas as pd
    df = pd.DataFrame(df_dummy)
    piv = df.pivot(index=["graph", "target"], columns="ranker", values="gain")
    stat, p = wilcoxon_test(piv["HITS"].values, piv["PR"].values)
    assert p < 0.05
    rej, adj_p = holm_bonferroni([p], alpha=0.05)
    assert rej[0] == True

