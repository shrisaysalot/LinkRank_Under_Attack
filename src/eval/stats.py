"""Statistical testing utilities: Bootstrap confidence intervals and Wilcoxon signed-rank test."""
from typing import Tuple, List, Union
import numpy as np
from scipy import stats


def bootstrap_ci(
    data: Union[List[float], np.ndarray],
    n_boot: int = 1000,
    ci: float = 0.95,
    seed: int = 42
) -> Tuple[float, float, float]:
    """Computes empirical mean and percentile bootstrap confidence interval.

    Returns
    -------
    (mean, ci_lower, ci_upper)
    """
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    if len(arr) == 0:
        return 0.0, 0.0, 0.0
    if len(arr) == 1:
        return float(arr[0]), float(arr[0]), float(arr[0])

    rng = np.random.RandomState(seed)
    boot_means = np.empty(n_boot)
    n = len(arr)

    for i in range(n_boot):
        sample = rng.choice(arr, size=n, replace=True)
        boot_means[i] = np.mean(sample)

    alpha = (1.0 - ci) / 2.0
    ci_lower = float(np.percentile(boot_means, 100.0 * alpha))
    ci_upper = float(np.percentile(boot_means, 100.0 * (1.0 - alpha)))
    mean_val = float(np.mean(arr))

    return mean_val, ci_lower, ci_upper


def wilcoxon_test(
    x: Union[List[float], np.ndarray],
    y: Union[List[float], np.ndarray]
) -> Tuple[float, float]:
    """Performs Wilcoxon signed-rank test between paired samples x and y.

    Returns
    -------
    (statistic, p_value)
    """
    diff = np.asarray(x, dtype=float) - np.asarray(y, dtype=float)
    diff = diff[~np.isnan(diff)]
    diff = diff[diff != 0]

    if len(diff) < 5:
        # Insufficient non-zero pairs for normal approximation
        return 0.0, 1.0

    res = stats.wilcoxon(diff)
    return float(res.statistic), float(res.pvalue)
