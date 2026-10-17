"""Base class and common data structures for link-analysis rankers."""
from dataclasses import dataclass
from typing import Optional, Dict, Any
import numpy as np
import scipy.sparse as sp


@dataclass
class RankResult:
    """Standardized output container for link-analysis ranking algorithms."""
    scores: np.ndarray                     # Primary ranking score (authorities for HITS/SALSA, PR for PageRank)
    hub_scores: Optional[np.ndarray] = None # Hub scores if computed (HITS, SALSA)
    iterations: int = 0
    converged: bool = True
    eigengap: Optional[float] = None       # sigma_1^2 - sigma_2^2 if available
    elapsed_time: float = 0.0              # Seconds
    peak_memory_mb: float = 0.0            # Megabytes
    metadata: Optional[Dict[str, Any]] = None

    def get_rank(self, target_idx: int) -> int:
        """Return 1-based rank of the target node (rank 1 = highest score)."""
        order = np.argsort(-self.scores)
        ranks = np.empty_like(order)
        ranks[order] = np.arange(1, len(self.scores) + 1)
        return int(ranks[target_idx])

    def top_k_indices(self, k: int = 10) -> np.ndarray:
        """Return indices of top-k ranked nodes."""
        return np.argsort(-self.scores)[:k]
