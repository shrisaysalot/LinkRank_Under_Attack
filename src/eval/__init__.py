"""Evaluation module exporting metrics and statistical validation."""
from src.eval.metrics import (
    compute_rank,
    rank_gain,
    normalized_rank_gain,
    score_amplification,
    top_k_jaccard,
    ndcg_at_k,
    kendall_tau,
    spearman_rho,
    fake_share_at_k,
    defense_attack_success_reduction,
    b_star_at_k,
)
from src.eval.stats import bootstrap_ci, wilcoxon_test, holm_bonferroni

__all__ = [
    "compute_rank",
    "rank_gain",
    "normalized_rank_gain",
    "score_amplification",
    "top_k_jaccard",
    "ndcg_at_k",
    "kendall_tau",
    "spearman_rho",
    "fake_share_at_k",
    "defense_attack_success_reduction",
    "b_star_at_k",
    "bootstrap_ci",
    "wilcoxon_test",
    "holm_bonferroni",
]
