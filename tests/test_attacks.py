"""Unit tests for attacks A1-A6 verifying validity, budget constraints, and edge additions."""
import pytest
import networkx as nx
import numpy as np

from src.attacks import (
    attack_a1_single_fake_hub,
    attack_a2_hub_farm,
    attack_a3_bipartite_block,
    attack_a4_hub_inflation,
    attack_a5_cross_score,
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
    # Check that at least one edge points to target
    target_in = [e for e in res.added_edges if e[1] == target]
    assert len(target_in) > 0


def test_a4_hub_inflation(clean_graph):
    target = 10
    budget = 10
    res = attack_a4_hub_inflation(clean_graph, target_node=target, budget=budget, c_top=2)

    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    assert len(res.added_edges) == res.cost_edges


def test_a5_cross_score(clean_graph):
    target = 10
    budget = 12
    res = attack_a5_cross_score(clean_graph, target_node=target, budget=budget, c_top=2)

    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    assert len(res.added_edges) == res.cost_edges


def test_a6_greedy_gradient(clean_graph):
    target = 10
    budget = 5
    res = attack_a6_greedy_gradient(clean_graph, target_node=target, budget=budget, candidate_pool_size=10)

    assert res.verify_validity(clean_graph)
    assert res.cost_edges <= budget
    assert len(res.added_edges) == res.cost_edges
