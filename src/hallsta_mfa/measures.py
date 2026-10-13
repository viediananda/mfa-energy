"""Improvement measures M1-M4 for the electric-boiler load (vectorised over MC arrays).

Every measure returns electricity saved in GWh/y. Boilers are the marginal steam source, so a
steam saving first displaces boiler steam; total displaced steam is capped at the boiler
steam `st_EB`. Savings are annual upper bounds: they assume boilers run all year.
"""
import numpy as np

MEASURES = {
    'M1': 'M1 TMP steam recovery +10 t/h',
    'M1b': 'M1b recovery raised to 90 % of supply',
    'M2': 'M2 heat pump replaces all boiler steam',
    'M3': 'M3 press dryness +2 points (48 -> 50 % at base; dryer steam prop. to water)',
    'M3b': 'M3b press dryness, evaporation heat only (low bound)',
    'M4': 'M4 combined (M3, then M1, then heat pump)',
}


def evaporated_water(paper_t, dryness, fin_moist):
    """Water evaporated in the dryer section (t/y).

    Dry solids S = paper_t (1 - fin_moist). Water entering the dryer = S (1/d - 1).
    Water leaving with the paper = paper_t * fin_moist. Evaporated W(d) = difference.
    """
    S = paper_t*(1 - fin_moist)
    return S*(1/dryness - 1) - paper_t*fin_moist


def measures(p, r):
    """p: input dict (scalars or arrays); r: output of model.run(p). Returns dict of arrays (GWh/y)."""
    st_EB, eff, EB, dh = r['st_EB'], r['eff_EB'], r['el_EB'], r['dh']
    cop = p['cop_hp']
    # M1: +dm_rec t/h more TMP steam
    d1 = np.minimum(p['dm_rec_M1']*p['h_prod']*dh/1000, st_EB)
    # M3: dryness d0 -> d1
    W0 = evaporated_water(p['paper_t'], p['press_dry'], p['fin_moist'])
    W1 = evaporated_water(p['paper_t'], p['press_dry'] + p['d_press_dry'], p['fin_moist'])
    dW = np.maximum(W0 - W1, 0)
    d3a = np.minimum(dW/W0*r['st_PM'], st_EB)                       # (a) dryer steam proportional to water evaporated
    d3b = np.minimum(dW*p['h_evap']/3600, st_EB)                    # (b) only the evaporation heat (GJ/t -> GWh)
    # M1b: raise recovery to 90 % of supply
    d1b = np.minimum(np.maximum(0.90*r['st_supply'] - r['st_rec'], 0), st_EB)
    out = {'M1': d1/eff, 'M1b': d1b/eff, 'M2': EB - st_EB/cop, 'M3': d3a/eff, 'M3b': d3b/eff}
    # M4: sequential, all caps on remaining boiler steam
    s1 = st_EB - d3a
    d1s = np.minimum(p['dm_rec_M1']*p['h_prod']*dh/1000, s1)
    s2 = s1 - d1s
    out['M4'] = EB - s2/cop
    out['M4_steam_left'] = s2
    for k in list(MEASURES):
        out[k + '_MWh_t'] = out[k]*1000/p['paper_t']                # MWh per tonne paper
        out[k + '_SEC'] = p['E_tot']*1000/p['paper_t'] - out[k + '_MWh_t']
    out['dW_frac'] = dW/W0
    return out
