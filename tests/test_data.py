"""Unit tests for synthetic generators, base set construction, and data loaders."""
import pytest
import networkx as nx
import numpy as np

from src.data import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm,
    sample_root_set,
    build_base_set,
    load_snap_graph,
    load_webspam_labels,
    load_webspam_hostgraph
)


def test_synthetic_generators():
    ba = generate_barabasi_albert(n=100, m=3, seed=42)
    assert ba.number_of_nodes() == 100
    assert ba.number_of_edges() > 0
    assert ba.is_directed()

    er = generate_erdos_renyi(n=100, p=0.05, seed=42)
    assert er.number_of_nodes() == 100
    assert er.number_of_edges() > 0
    assert er.is_directed()

    sbm, hubs, auths = generate_planted_bipartite_sbm(
        n_background=80, n_planted_hubs=10, n_planted_authorities=10, seed=42
    )
    assert sbm.number_of_nodes() == 100
    assert len(hubs) == 10
    assert len(auths) == 10
    # Planted community should have high edge count
    comm_edges = sum(1 for h in hubs for a in auths if sbm.has_edge(h, a))
    assert comm_edges >= 50, f"Expected dense community edges, got {comm_edges}"


def test_base_set_builder():
    G = generate_barabasi_albert(n=300, m=3, seed=42)
    root = sample_root_set(G, seed_node=0, root_size=30)
    assert len(root) == 30

    base = build_base_set(G, root, max_in_links=20)
    assert base.num_nodes >= 30
    assert base.adj_matrix.shape == (base.num_nodes, base.num_nodes)
    assert len(base.orig_to_idx) == base.num_nodes


def test_snap_loader_wiki():
    G, adj, orig_to_idx = load_snap_graph("wiki-Vote", max_edges=1000)
    assert G.number_of_nodes() > 0
    assert G.number_of_edges() == 1000
    assert adj.shape[0] == G.number_of_nodes()


def test_webspam_labels_undecided():
    df_ex = load_webspam_labels(split="set1", undecided_mode="exclude")
    assert "undecided" not in df_ex["raw_label"].values
    assert df_ex["binary_label"].isin([0, 1]).all()


def test_webspam_hostgraph_loader():
    G, adj, node_to_host, host_to_node = load_webspam_hostgraph(weighted=False)
    assert G.number_of_nodes() == 11402
    assert G.number_of_edges() == 730774
    assert adj.shape == (11402, 11402)
    assert len(node_to_host) == 11402
    assert len(host_to_node) == 11402
    assert node_to_host[0] == "007cleaningagent.co.uk"


    df_keep = load_webspam_labels(split="set1", undecided_mode="keep")
    assert "undecided" in df_keep["raw_label"].values
    assert (df_keep["binary_label"] == -1).sum() > 0
