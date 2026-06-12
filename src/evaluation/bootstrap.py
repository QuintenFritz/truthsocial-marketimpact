"""Bootstrap confidence intervals voor groepsverschillen.

In-cursus alternatief voor de Welch t-toets en Mann-Whitney (zie cursusmodule
04 "Resampling, model selection, shrinkage methods"). In plaats van een
parametrische toets schatten we de samplingverdeling van het verschil
stat(behandeling) − stat(controle) via resampling met teruglegging, en lezen
we een percentiel-confidence-interval af.

Voordelen:
- Maakt geen aanname van normaliteit of gelijke varianties.
- Door `stat=np.median` te kiezen is het van nature robuust tegen uitschieters
  (vervangt daarmee de rol van Mann-Whitney).
- Een CI dat 0 uitsluit is het bootstrap-equivalent van "significant"; doordat
  we CI's rapporteren i.p.v. p-waarden vervalt de noodzaak van een
  Bonferroni-correctie voor meervoudig toetsen.
"""

from __future__ import annotations

from typing import Callable

import numpy as np
import pandas as pd


def bootstrap_diff_ci(
    treatment,
    control,
    stat: Callable[[np.ndarray], float] = np.mean,
    n_boot: int = 10000,
    ci: float = 95.0,
    random_state: int = 42,
) -> dict:
    """Bootstrap-CI voor het verschil stat(treatment) − stat(control).

    Parameters
    ----------
    treatment, control : array-like
        De twee groepen (bv. AR op mention-dagen vs. controle-dagen).
    stat : callable
        Statistiek per groep. ``np.mean`` (default) of ``np.median``.
    n_boot : int
        Aantal bootstrap-resamples.
    ci : float
        Breedte van het confidence interval in procent (95 → 2,5–97,5 percentiel).
    random_state : int
        Seed voor reproduceerbaarheid.

    Returns
    -------
    dict met sleutels:
        obs_diff       — geobserveerd verschil
        ci_low, ci_high — grenzen van het bootstrap-CI
        excludes_zero  — True als het CI 0 niet bevat (≈ significant)
        p_boot         — tweezijdige bootstrap-p (aandeel resamples aan andere kant van 0)
        n_treat, n_ctrl
    """
    rng = np.random.default_rng(random_state)
    t = np.asarray(pd.Series(treatment).dropna(), dtype=float)
    c = np.asarray(pd.Series(control).dropna(), dtype=float)
    if len(t) == 0 or len(c) == 0:
        raise ValueError("Beide groepen moeten minstens één observatie hebben.")

    obs = stat(t) - stat(c)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        bt = rng.choice(t, size=len(t), replace=True)
        bc = rng.choice(c, size=len(c), replace=True)
        diffs[i] = stat(bt) - stat(bc)

    alpha = (100.0 - ci) / 2.0
    lo, hi = np.percentile(diffs, [alpha, 100.0 - alpha])
    p_boot = 2.0 * min((diffs <= 0).mean(), (diffs >= 0).mean())
    return {
        "obs_diff": float(obs),
        "ci_low": float(lo),
        "ci_high": float(hi),
        "excludes_zero": bool(lo > 0 or hi < 0),
        "p_boot": float(min(p_boot, 1.0)),
        "n_treat": int(len(t)),
        "n_ctrl": int(len(c)),
    }


def bootstrap_diff_bp(treatment, control, **kwargs) -> dict:
    """Zelfde als bootstrap_diff_ci maar verschil-velden in basispunten (×1e4).

    Handig voor returns: de event-study rapporteert effecten in bp.
    """
    res = bootstrap_diff_ci(treatment, control, **kwargs)
    for k in ("obs_diff", "ci_low", "ci_high"):
        res[k + "_bp"] = res[k] * 1e4
    return res
