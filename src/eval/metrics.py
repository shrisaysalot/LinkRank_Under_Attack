"""Evaluation metrics for measuring adversarial vulnerability and ranking fidelity."""
from typing import List, Set, Union, Optional
import numpy as np
from scipy import stats


def compute_rank(scores: np.ndarray, target_idx: int) -> int:
    """Computes 1-based rank (rank 1 = highest score)."""
    if target_idx >= len(scores):
        return len(scores) + 1
    # Nodes with strictly greater score + 1
    return int(np.sum(scores > scores[target_idx]) + 1)


def rank_gain(clean_scores: np.ndarray, attacked_scores: np.ndarray, target_idx: int) -> int:
    """Computes rank gain of target node: rank_clean - rank_attacked.

    Positive value indicates promotion towards top rank.
    """
    r_clean = compute_rank(clean_scores, target_idx)
    r_attacked = compute_rank(attacked_scores, target_idx)
    return r_clean - r_attacked


def score_amplification(clean_scores: np.ndarray, attacked_scores: np.ndarray, target_idx: int) -> float:
    """Ratio of attacked score to clean score for the target."""
    c_score = clean_scores[target_idx] if target_idx < len(clean_scores) else 0.0
    a_score = attacked_scores[target_idx] if target_idx < len(attacked_scores) else 0.0
    return float(a_score / max(c_score, 1e-12))


def top_k_jaccard(scores1: np.ndarray, scores2: np.ndarray, k: int = 20) -> float:
    """Computes Jaccard similarity of top-k ranked items between two score vectors."""
    n1 = min(k, len(scores1))
    n2 = min(k, len(scores2))
    top1 = set(np.argsort(-scores1)[:n1])
    top2 = set(np.argsort(-scores2)[:n2])
    intersection = len(top1 & top2)
    union = len(top1 | top2)
    return float(intersection / union) if union > 0 else 1.0


def ndcg_at_k(ground_truth_scores: np.ndarray, test_scores: np.ndarray, k: int = 20) -> float:
    """Computes NDCG@k of test_scores using ground_truth_scores as relevance values.

    Newly added fake nodes not present in ground_truth_scores receive relevance 0.
    """
    n = min(k, len(test_scores))
    if n <= 1:
        return 1.0

    # Predicted order
    pred_order = np.argsort(-test_scores)[:n]
    
    # Safe relevance mapping (0 for fake nodes)
    relevance = np.array([
        ground_truth_scores[idx] if idx < len(ground_truth_scores) else 0.0
        for idx in pred_order
    ])

    # DCG
    discounts = np.log2(np.arange(2, n + 2))
    dcg = np.sum(relevance / discounts)

    # Ideal DCG from clean ground truth
    ideal_rel = np.sort(ground_truth_scores)[::-1][:n]
    idcg = np.sum(ideal_rel / discounts[:len(ideal_rel)])

    return float(dcg / idcg) if idcg > 0 else 1.0


def kendall_tau(scores1: np.ndarray, scores2: np.ndarray) -> float:
    """Computes Kendall's tau rank correlation between two score vectors on common nodes."""
    min_len = min(len(scores1), len(scores2))
    if min_len < 2:
        return 1.0
    tau, _ = stats.kendalltau(scores1[:min_len], scores2[:min_len])
    return float(tau) if not np.isnan(tau) else 0.0


def fake_share_at_k(scores: np.ndarray, fake_nodes: Union[List[int], Set[int]], k: int = 20) -> float:
    """Fraction of top-k items that are attacker-injected fake nodes."""
    top_indices = np.argsort(-scores)[:k]
    fake_set = set(fake_nodes)
    fake_count = sum(1 for idx in top_indices if idx in fake_set)
    return float(fake_count / min(k, len(scores)))


def defense_attack_success_reduction(gain_nodef: float, gain_def: float) -> float:
    """Computes 1 - (gain_def / gain_nodef). 1.0 = perfect defense, 0.0 = no reduction."""
    if gain_nodef <= 0:
        return 1.0 if gain_def <= 0 else 0.0
    return float(1.0 - (gain_def / gain_nodef))


def spearman_rho(scores1: np.ndarray, scores2: np.ndarray) -> float:
    """Computes Spearman's rank correlation coefficient between two score vectors on common nodes."""
    min_len = min(len(scores1), len(scores2))
    if min_len < 2:
        return 1.0
    rho, _ = stats.spearmanr(scores1[:min_len], scores2[:min_len])
    return float(rho) if not np.isnan(rho) else 0.0


def normalized_rank_gain(clean_scores: np.ndarray, attacked_scores: np.ndarray, target_idx: int) -> float:
    """Computes normalized rank gain: (rank_clean - rank_attacked) / (rank_clean - 1).

    Returns 1.0 if target reached rank 1, 0.0 if no change, negative if demoted.
    If target was already rank 1 in clean graph, returns 0.0.
    """
    r_clean = compute_rank(clean_scores, target_idx)
    r_attacked = compute_rank(attacked_scores, target_idx)
    if r_clean <= 1:
        return 0.0
    return float((r_clean - r_attacked) / (r_clean - 1.0))


def b_star_at_k(budgets: List[int], ranks: List[int], k: int = 10) -> Optional[int]:
    """Computes B*(k): the minimum budget B at which target rank <= k.

    Returns None if target never achieves rank <= k across evaluated budgets.
    """
    pairs = sorted(zip(budgets, ranks), key=lambda x: x[0])
    for b, r in pairs:
        if r <= k:
            return int(b)
    return None

