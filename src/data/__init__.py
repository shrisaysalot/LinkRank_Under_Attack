"""Data module exporting dataset loaders, synthetic generators, and base-set construction."""
from src.data.loader import load_snap_graph, load_webspam_labels
from src.data.synthetic import (
    generate_barabasi_albert,
    generate_erdos_renyi,
    generate_planted_bipartite_sbm,
)
from src.data.base_set import BaseSet, sample_root_set, build_base_set

__all__ = [
    "load_snap_graph",
    "load_webspam_labels",
    "generate_barabasi_albert",
    "generate_erdos_renyi",
    "generate_planted_bipartite_sbm",
    "BaseSet",
    "sample_root_set",
    "build_base_set",
]
