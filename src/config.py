"""Central configuration module with fixed random seeds and global constants."""
from pathlib import Path

# Base Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = REPO_ROOT / "src"
DATA_DIR = REPO_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
RESULTS_DIR = REPO_ROOT / "results"
FIGURES_DIR = REPO_ROOT / "figures"
DOCS_DIR = REPO_ROOT / "docs"

for d in [RAW_DATA_DIR, RESULTS_DIR, FIGURES_DIR, DOCS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# Random Seeds
DEFAULT_SEED = 42
EXPERIMENT_SEEDS = [42, 123, 456, 789, 999]

# Ranker Hyperparameters
HITS_TOL = 1e-8
HITS_MAX_ITER = 200

PAGERANK_ALPHA = 0.85
PAGERANK_TOL = 1e-8
PAGERANK_MAX_ITER = 200

SALSA_TOL = 1e-8
SALSA_MAX_ITER = 200

RANDOMIZED_HITS_EPS = 0.15
SUBSPACE_HITS_K = 5

# Base Set Parameters (Kleinberg 1999)
BASE_SET_ROOT_SIZE = 200
BASE_SET_MAX_IN_LINKS = 50

# Attack Budgets (Node and Edge limits)
DEFAULT_BUDGET_GRID = [1, 5, 10, 25, 50, 100, 200, 500]
FAST_BUDGET_GRID = [1, 5, 10, 25, 50, 100]
