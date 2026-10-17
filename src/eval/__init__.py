"""Evaluation module exporting metrics and statistical validation."""
from src.eval.metrics import (
    compute_rank,
    rank_gain,
    score_amplification,
    top_k_jaccard,
    ndcg_at_k,
    kendall_tau,
    fake_share_at_k,
    defense_attack_success_reduction,
)
from src.eval.stats import bootstrap_ci, wilcoxon_test

__all__ = [
    "compute_rank",
    "rank_gain",
    "score_amplification",
    "top_k_jaccard",
    "ndcg_at_k",
    "kendall_tau",
    "fake_share_at_k",
    "defense_attack_success_reduction",
    "bootstrap_ci",
    "wilcoxon_test",
]
