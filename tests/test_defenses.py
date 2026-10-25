"""Unit tests for defenses D1-D5."""
import networkx as nx
import numpy as np
import pytest

from src.rankers.hits import hits
from src.defenses import (
    randomized_hits,
    subspace_hits,
    bharat_henzinger_hits,
    hub_capped_hits,
    wu_davison_hits,
    wu_davison_outlink_jaccard_hits,
    trust_based_hits,
)
from src.data.synthetic import generate_barabasi_albert


@pytest.fixture
def sample_graph():
    return generate_barabasi_albert(n=40, m=3, seed=42)


def test_d1_randomized_hits(sample_graph):
    res = randomized_hits(sample_graph, eps=0.15)
    assert res.converged
    assert np.isclose(res.scores.sum(), 1.0, atol=1e-5)
    assert np.all(res.scores >= 0)


def test_d1_subspace_hits(sample_graph):
    res = subspace_hits(sample_graph, k=3)
    assert np.isclose(res.scores.sum(), 1.0, atol=1e-5)
    assert np.all(res.scores >= 0)


def test_d2_bharat_henzinger_changes_scores():
    """Proves Bharat-Henzinger modifies edge weights and changes scores when multiple
    edges originate from the same domain pointing to the same page.
    """
    # Create graph where nodes 0, 1, 2 are in domain "farm" and both link to target node 3
    # Node 4 is in domain "independent" and also links to node 3
    G = nx.DiGraph()
    G.add_nodes_from(range(5))
    # Domain farm: nodes 0, 1, 2 point to target authority 3
    G.add_edge(0, 3)
    G.add_edge(1, 3)
    G.add_edge(2, 3)
    # Node 4 (independent) points to authority 3 and authority 5
    G.add_node(5)
    G.add_edge(4, 3)
    G.add_edge(4, 5)
    # Add back edges so HITS is mutually reinforcing
    G.add_edge(3, 0)
    G.add_edge(5, 4)

    domain_map = {0: "farm", 1: "farm", 2: "farm", 3: "target", 4: "indep", 5: "auth2"}

    # Undefended HITS
    res_hits = hits(G)

    # Bharat-Henzinger defended HITS
    res_bh = bharat_henzinger_hits(G, domain_map=domain_map)

    # Both authority scores and hub scores must differ significantly
    assert not np.allclose(res_hits.scores, res_bh.scores, atol=1e-3), (
        "Bharat-Henzinger authority scores should differ from plain HITS under multi-link domain"
    )
    assert not np.allclose(res_hits.hub_scores, res_bh.hub_scores, atol=1e-3), (
        "Bharat-Henzinger hub scores should differ from plain HITS under multi-link domain"
    )
    assert res_bh.converged


def test_d3_hub_capping(sample_graph):
    res = hub_capped_hits(sample_graph, cap_fraction=0.10)
    assert res.converged
    assert np.isclose(res.scores.sum(), 1.0, atol=1e-5)
    assert np.all(res.scores >= 0)


def test_d4_wu_davison(sample_graph):
    res_d4 = wu_davison_hits(sample_graph)
    assert res_d4.converged
    assert np.isclose(res_d4.scores.sum(), 1.0, atol=1e-5)

    res_d4b = wu_davison_outlink_jaccard_hits(sample_graph)
    assert res_d4b.converged
    assert np.isclose(res_d4b.scores.sum(), 1.0, atol=1e-5)


def test_d5_trust_hits(sample_graph):
    trusted = [0, 1]
    res = trust_based_hits(sample_graph, trusted_seeds=trusted, eps=0.20)
    assert res.converged
    assert np.isclose(res.scores.sum(), 1.0, atol=1e-5)
    assert np.all(res.scores >= 0)
