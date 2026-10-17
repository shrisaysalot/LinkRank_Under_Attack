"""Data loading utilities for SNAP graphs and WEBSPAM-UK2006."""
import gzip
from pathlib import Path
from typing import Dict, Tuple, Optional, Union
import numpy as np
import networkx as nx
import pandas as pd
import scipy.sparse as sp

from src.config import RAW_DATA_DIR


def load_snap_graph(
    name: str = "wiki-Vote",
    max_edges: Optional[int] = None
) -> Tuple[nx.DiGraph, sp.csr_matrix, Dict[int, int]]:
    """Loads a SNAP directed graph from data/raw/<name>.txt.gz.

    Parameters
    ----------
    name : str
        Dataset name ('wiki-Vote', 'web-Stanford', 'web-NotreDame').
    max_edges : int, optional
        Optional cap on edges to read for fast development/testing.

    Returns
    -------
    G : nx.DiGraph
        Directed graph with nodes re-indexed 0..N-1.
    adj : sp.csr_matrix
        Sparse adjacency matrix.
    orig_to_idx : dict
        Mapping from original node IDs to 0..N-1.
    """
    file_path = RAW_DATA_DIR / f"{name}.txt.gz"
    if not file_path.exists():
        # Check without .gz
        file_path = RAW_DATA_DIR / f"{name}.txt"
        if not file_path.exists():
            raise FileNotFoundError(f"Dataset {name} not found in {RAW_DATA_DIR}. Run scripts/download_data.py first.")

    edges = []
    nodes = set()

    open_fn = gzip.open if str(file_path).endswith(".gz") else open
    with open_fn(file_path, "rt", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                u, v = int(parts[0]), int(parts[1])
                edges.append((u, v))
                nodes.add(u)
                nodes.add(v)
                if max_edges and len(edges) >= max_edges:
                    break

    sorted_nodes = sorted(list(nodes))
    orig_to_idx = {nid: idx for idx, nid in enumerate(sorted_nodes)}

    mapped_edges = [(orig_to_idx[u], orig_to_idx[v]) for u, v in edges]

    G = nx.DiGraph()
    G.add_nodes_from(range(len(sorted_nodes)))
    G.add_edges_from(mapped_edges)

    adj = nx.adjacency_matrix(G, nodelist=range(len(sorted_nodes)), dtype=float).tocsr()
    return G, adj, orig_to_idx


def load_webspam_labels(
    split: str = "set1",
    undecided_mode: str = "exclude"
) -> pd.DataFrame:
    """Loads WEBSPAM-UK2006 host labels and handles undecided labels explicitly.

    Parameters
    ----------
    split : str
        'set1' or 'set2'.
    undecided_mode : str
        Strategy for handling the 'undecided' label (hosts with spamicity == 0.5):
        - 'exclude' (default): discard undecided hosts from evaluation.
        - 'spam': treat undecided as spam (label = 1).
        - 'normal': treat undecided as normal (label = 0).
        - 'keep': preserve as distinct category (label = -1).

    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ['host', 'raw_label', 'spamicity', 'binary_label', 'judgments']
    """
    raw_dir = RAW_DATA_DIR / "webspam-uk2006-2.0"
    file_path = raw_dir / f"webspam-uk2006-{split}-labels.txt"

    if not file_path.exists():
        raise FileNotFoundError(f"WEBSPAM labels file not found at {file_path}. Run scripts/download_data.py first.")

    records = []
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) < 4:
                continue
            host = parts[0]
            raw_label = parts[1].lower()
            try:
                spamicity = float(parts[2])
            except ValueError:
                spamicity = 0.0
            judgments = parts[3]

            if raw_label == "spam":
                binary_label = 1
            elif raw_label == "normal":
                binary_label = 0
            elif raw_label == "undecided":
                if undecided_mode == "exclude":
                    continue
                elif undecided_mode == "spam":
                    binary_label = 1
                elif undecided_mode == "normal":
                    binary_label = 0
                elif undecided_mode == "keep":
                    binary_label = -1
                else:
                    raise ValueError(f"Unknown undecided_mode: {undecided_mode}")
            else:
                continue

            records.append({
                "host": host,
                "raw_label": raw_label,
                "spamicity": spamicity,
                "binary_label": binary_label,
                "judgments": judgments
            })

    return pd.DataFrame(records)
