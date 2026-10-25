"""Unit tests for attacks A1-A6 verifying validity, budget constraints, and edge additions."""
import pytest
import networkx as nx
import numpy as np

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
from src.data.synthetic import generate_barabasi_albert


@pytest.fixture
def clean_graph():
    return generate_barabasi_albert(n=50, m=3, seed=42)


def test_a1_single_fake_hub(clean_graph):
    target = 10
    res = attack_a1_single_fake_hub(clean_graph, target_node=target, budget=1)

    assert res.verify_validity(clean_graph)
    assert res.cost_edges == 1
    assert res.cost_nodes == 1
    assert (res.added_nodes[0], target) in res.added_edges
    assert clean_graph.number_of_edges() + 1 == res.graph.number_of_edges()


def test_a2_hub_farm(clean_graph):
    target = 10
    budget = 8
    res = attack_a2_hub_farm(clean_graph, target_node=target, budget=budget)

    assert res.verify_validity(clean_graph)
    assert res.cost_edges == budget
    assert res.cost_nodes == budget
    for edge in res.added_edges:
        assert edge[1] == target
    assert clean_graph.number_of_edges() + budget == res.graph.number_of_edges()


def test_a3_bipartite_block(clean_graph):
    target = 10
    budget = 12
    res = attack_a3_bipartite_block(clean_graph, target_node=target, budget=budget)

    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    assert len(res.added_edges) == res.cost_edges
    target_in = [e for e in res.added_edges if e[1] == target]
    assert len(target_in) > 0


def test_a4_proposal_hub_inflation(clean_graph):
    target = 10
    budget = 3
    # Case 1: Target itself out-links (0 fake nodes added)
    res0 = attack_a4_hub_inflation(clean_graph, target_node=target, budget=budget, c_top=3, use_one_fake_page=False)
    assert res0.verify_validity(clean_graph)
    assert res0.cost_nodes == 0
    assert res0.cost_edges <= budget
    assert all(e[0] == target for e in res0.added_edges)

    # Case 2: Exactly ONE fake page links to target and top authorities (1 fake node added)
    res1 = attack_a4_hub_inflation(clean_graph, target_node=target, budget=budget, c_top=3, use_one_fake_page=True)
    assert res1.verify_validity(clean_graph)
    assert res1.cost_nodes == 1
    assert res1.cost_edges <= budget
    assert any(e[1] == target for e in res1.added_edges)


def test_a4b_multi_hub_inflation(clean_graph):
    target = 10
    budget = 10
    res = attack_a4b_multi_hub_inflation(clean_graph, target_node=target, budget=budget, c_top=2)
    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    assert res.cost_nodes > 1


def test_a5_proposal_cross_score(clean_graph):
    target = 10
    budget = 12
    # p fake hubs each link to c top authorities and target (no cross-links)
    res = attack_a5_cross_score(clean_graph, target_node=target, budget=budget, c_top=2)
    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    # Verify no cross links among added fake nodes
    fake_set = set(res.added_nodes)
    inter_fake_edges = [e for e in res.added_edges if e[0] in fake_set and e[1] in fake_set]
    assert len(inter_fake_edges) == 0


def test_a5b_cross_score(clean_graph):
    target = 10
    budget = 12
    res = attack_a5b_cross_score(clean_graph, target_node=target, budget=budget, c_top=2)
    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget


def test_a6_greedy_gradient(clean_graph):
    target = 10
    budget = 5
    res = attack_a6_greedy_gradient(clean_graph, target_node=target, budget=budget, candidate_pool_size=10)
    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    assert len(res.added_edges) == res.cost_edges
