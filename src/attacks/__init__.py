"""Attacks module exporting A1-A6 link injection attacks."""
from src.attacks.base import AttackResult
from src.attacks.a1_single_fake_hub import attack_a1_single_fake_hub
from src.attacks.a2_hub_farm import attack_a2_hub_farm
from src.attacks.a3_bipartite_block import attack_a3_bipartite_block
from src.attacks.a4_hub_inflation import attack_a4_hub_inflation, attack_a4b_multi_hub_inflation
from src.attacks.a5_cross_score import attack_a5_cross_score, attack_a5b_cross_score
from src.attacks.a6_greedy_gradient import attack_a6_greedy_gradient

__all__ = [
    "AttackResult",
    "attack_a1_single_fake_hub",
    "attack_a2_hub_farm",
    "attack_a3_bipartite_block",
    "attack_a4_hub_inflation",
    "attack_a4b_multi_hub_inflation",
    "attack_a5_cross_score",
    "attack_a5b_cross_score",
    "attack_a6_greedy_gradient",
]
