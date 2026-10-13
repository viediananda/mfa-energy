"""Monte Carlo (constrained) for the Hallsta model.

`run_mc()` draws every DIST input once per run, evaluates the model and the measures, and
flags runs that are consistent with Holmen's data (constrained MC):
  TMP share of steam in 70-90 %  AND  steam residual >= 0  AND  every Xdest >= 0
  AND  boiler steam heat <= boiler electricity.
Headline ranges use the accepted runs; unconstrained results are kept for the appendix.
"""
from dataclasses import dataclass

import numpy as np
import pandas as pd

from .model import BASE, DIST, PROCS, TIED, run
from .measures import measures

REC_LO, REC_HI = 0.70, 0.90   # steam_recovery_rate_2025


def sample(N=10_000, seed=2023):
    """Draw N values for every DIST input (dict of arrays). Order of DIST fixes the stream."""
    rng = np.random.default_rng(seed)
    S = {}
    for k, (d, a, b, c) in DIST.items():
        S[k] = (rng.normal(a, b, N) if d == 'norm' else
                rng.triangular(a, b, c, N) if d == 'tri' else rng.uniform(a, b, N))
    for k, src in TIED.items():
        S[k] = S[src]
    return S


def derive(d):
    """Percent columns used in tables (works on scalars and arrays)."""
    d['rec_pct'] = d['rec_ratio']*100
    d['air_pct'] = d['sink_air']/d['E_in']*100
    d['water_pct'] = d['sink_water']/d['E_in']*100
    d['cool_pct'] = d['sink_cool']/d['E_in']*100
    d['Xdest_pct'] = d['Xdest_total']/d['E_tot']*100
    d['psi_EB_pct'] = d['psi|Electric boilers']*100
    return d


def evaluate(P):
    """Model + measures for an input dict (scalars or arrays). Returns a flat dict."""
    r = run(P)
    r.update(measures(P, r))
    return derive(r)


@dataclass
class MCResult:
    X: pd.DataFrame          # sampled inputs
    Y: pd.DataFrame          # outputs (model + measures)
    ok: pd.Series            # accepted by the consistency filter
    flags: pd.DataFrame      # which condition failed
    N: int
    seed: int

    @property
    def acceptance(self):
        return float(self.ok.mean())

    @property
    def k_binding_rate(self):
        return float((self.Y['k_oth'] < 1).mean())


def run_mc(N=10_000, seed=2023):
    S = sample(N, seed)
    P = dict(BASE); P.update(S)
    r = evaluate(P)
    Y = pd.DataFrame({k: v for k, v in r.items() if np.ndim(v) == 1})
    X = pd.DataFrame(S)
    flags = pd.DataFrame({
        'rec_ratio_in_range': Y.rec_ratio.between(REC_LO, REC_HI),
        'st_HW_nonneg': Y.st_HW >= 0,
        'Xdest_nonneg': (Y[[f'Xdest|{p}' for p in PROCS]] >= -1e-9).all(axis=1),
        'boiler_heat_le_electricity': Y.eff_EB <= 1.0})  # tolerance: float noise
    return MCResult(X, Y, flags.all(axis=1), flags, N, seed)


def summary(mc, keys, base):
    """Table: base, constrained P5/P50/P95, unconstrained P5/P50/P95, acceptance rate."""
    Y, ok = mc.Y, mc.ok
    rows = {}
    for k, name in keys.items():
        rows[name] = dict(key=k, base=base[k],
                          P5=Y.loc[ok, k].quantile(.05), P50=Y.loc[ok, k].median(), P95=Y.loc[ok, k].quantile(.95),
                          uncon_P5=Y[k].quantile(.05), uncon_P50=Y[k].median(), uncon_P95=Y[k].quantile(.95),
                          acceptance_rate=mc.acceptance)
    return pd.DataFrame(rows).T
