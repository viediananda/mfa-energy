"""Tables and figures of the model (reports/tables/model_*.csv, reports/figures/model_*.png).

`build_all()` writes everything; the notebook calls the same functions, so the notebook and
`analysis/run_model.py` always produce identical files.
"""
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

from . import plotstyle
from .mc import evaluate, run_mc, summary
from .measures import MEASURES, evaporated_water
from .model import BASE, DIST, PROCS, PROPERTY_BASED, TIED, label, ppf

ROOT = Path(__file__).resolve().parents[2]
TAB = ROOT / 'reports' / 'tables'
FIG = plotstyle.FIG_DIR

# ---------------------------------------------------------------- input register
# name: (description, unit, source id (data/sources.csv) or 'assumption', class A-D)
INPUT_META = {
 'E_tot': ('Electricity use 2023', 'GWh/y', 'el_total_2023_t13', 'A'),
 'paper_t': ('Paper production', 't/y', 'prod_paper_2023', 'A'),
 'pulp_t': ('TMP pulp production (ADT)', 't/y', 'prod_tmp_2023', 'A'),
 'DH_export': ('District heat to Norrtalje Energi', 'GWh/y', 'dh_export_2023', 'A'),
 'diesel': ('Diesel, internal transport (energy input, heat ends in air)', 'GWh/y', 'diesel_gwh_2023_t13', 'A'),
 'V_wwtp': ('WWTP effluent volume (18,300 m3/d x 365)', 'm3/y', 'effluent_wwtp_daily_2023', 'A'),
 'V_ff': ('Second outlet FF PM2 = total effluent - WWTP', 'm3/y', 'effluent_total_2023', 'A'),
 'V_cool': ('Release of cooling water and other non-affected process waters', 'm3/y', 'img_wb_cooling', 'B'),
 'dT_cool': ('Temperature rise of cooling water (NOT in any source)', 'K', 'assumption', 'D'),
 'sh_TMP': ('TMP share of electricity', '-', 'el_split_tmp_2025', 'B'),
 'sh_PM': ('Paper machines share (incl. bleaching)', '-', 'el_split_pm_2025', 'B'),
 'sh_EB': ('Electric boilers share', '-', 'el_split_boiler_2025', 'B'),
 'sh_OTH': ('Other users share (remainder; not stated by Holmen)', '-', 'assumption', 'D'),
 'P_wood': ('Wood handling electric power', 'MW', 'wood_handling_el_2025', 'B'),
 'P_bleach': ('Bleaching electric power', 'MW', 'bleaching_el_2025', 'B'),
 'P_wwtp': ('WWTP electric power', 'MW', 'wwtp_el_2025', 'B'),
 'aux_TMP': ('TMP auxiliary drives', 'kWh/t', 'tmp_aux_el_2025', 'B'),
 'm_rec': ('Steam recovered from TMP', 't/h', 'tmp_steam_recycled_2025', 'B'),
 'y_EB': ('Electric boiler steam yield (Holmen); boiler steam = electricity x yield x steam heat', 't/MWh', 'steam_per_MW_2025', 'B'),
 'eff_EB': ('Electric boiler efficiency (used only in sensitivity case S5)', '-', 'assumption', 'C'),
 'dh_override': ('Steam heat counted per tonne: latent heat at 2.4 bar(g), 2.15 GJ/t', 'MWh/t', 'steam_temp_2p4bar_2019', 'C'),
 'm_PM': ('Steam to paper-machine drying (midpoint of 80-110)', 't/h', 'pm_steam_2025', 'B'),
 'm_wood': ('Steam to wood handling', 't/h', 'wood_handling_steam_2025', 'B'),
 'PM11_frac': ('PM11 share of PM+bleaching electricity (Aug 2019 month)', '-', 'el_pm11_aug2019', 'C'),
 'h_prod': ('Production hours (Table 4 weighted 7,174 h, rounded)', 'h/y', 'pm11_days_2023', 'C'),
 'h_wwtp': ('WWTP hours', 'h/y', 'wwtp_days_2023', 'A'),
 'f_dist': ('Internal electricity distribution loss (Holmen: no data)', '-', 'assumption', 'D'),
 'f_steamloss': ('Steam network loss (Holmen: no data)', '-', 'assumption', 'D'),
 'p_steam': ('Steam pressure, 2.4 bar(g) = 3.4 bar abs', 'Pa', 'steam_pressure_pm_2019', 'C'),
 'T_cond': ('Condensate return temperature', 'degC', 'condensate_temp_pm_2019', 'C'),
 'T_TMPwaste': ('Temperature of unrecovered TMP heat', 'degC', 'assumption', 'D'),
 'T_PMwaste': ('PM waste heat temperature (wastewater ~50 C and warmer exhaust air)', 'degC', 'pm_wastewater_T_2019', 'C'),
 'T_HW': ('Hot water temperature', 'degC', 'assumption', 'D'),
 'T_DHs': ('District heat supply temperature', 'degC', 'assumption', 'D'),
 'T_DHr': ('District heat return temperature', 'degC', 'assumption', 'D'),
 'T_eff': ('Effluent temperature (Holmen: roughly 32; about 20 in long shutdowns)', 'degC', 'effluent_dT_sea_2019', 'C'),
 'T_ff': ('Second outlet temperature (same draw as T_eff)', 'degC', 'effluent_dT_sea_2019', 'C'),
 'T0': ('Dead state (annual mean surroundings)', 'degC', 'assumption', 'D'),
 'T_ref': ('Reference temperature for heat in water', 'degC', 'assumption', 'D'),
 'cpv': ('Volumetric heat capacity of water', 'MJ/m3K', 'physical constant', 'A'),
 'dm_rec_M1': ('M1: extra TMP steam recovery', 't/h', 'assumption (group draft)', 'D'),
 'cop_hp': ('M2: COP of high-temperature heat pump', '-', 'Arpagaus et al. 2018 (see docs/assumptions.md)', 'C'),
 'press_dry': ('M3: dryness after press section (baseline)', '-', 'assumption (group draft)', 'D'),
 'd_press_dry': ('M3: dryness gain from the measure', '-', 'assumption (group draft: 48 -> 50 %)', 'D'),
 'fin_moist': ('Final paper moisture', '-', 'paper_water_aq', 'B'),
 'h_evap': ('Evaporation heat in dryer section', 'GJ/t', 'assumption (group draft)', 'D'),
}


def _fmt(d):
    name, a, b, c = d
    if name == 'norm': return f'normal(mean {a:g}, sd {b:g})'
    if name == 'tri': return f'triangular({a:g}, {b:g}, {c:g})'
    return f'uniform({a:g}, {b:g})'


def inputs_table():
    rows = []
    for k, v in BASE.items():
        desc, unit, src, cls = INPUT_META[k]
        rows.append(dict(param=k, description=desc, value=v, unit=unit,
                         distribution=_fmt(DIST[k]) if k in DIST else 'fixed', source_id=src, data_class=cls))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- balance, hotspots
def unit_of(k):
    if k in ('dh_prop', 'dh'): return 'MWh/t steam'
    if k in ('fx_steam', 'OTH_negative'): return '-'
    if k in ('rec_pct', 'air_pct', 'water_pct', 'cool_pct', 'Xdest_pct', 'psi_EB_pct'): return '%'
    if k.startswith(('psi|',)) or k in ('rec_ratio', 'TMP_rec_eff', 'eff_EB', 'k_oth', 'dW_frac') or k.startswith('f_'):
        return '-'
    if k.startswith('SEC_'): return 'kWh/t'
    if k == 'y_EB_implied': return 't/MWh'
    if k.endswith('_MWh_t'): return 'MWh/t paper'
    if k.endswith('_SEC'): return 'MWh/t paper'
    return 'GWh/y'


def balance_table(b):
    grp = lambda k: ('electricity' if k.startswith(('el_', 'SEC_')) else 'waste heat' if k in ('TMP_waste', 'PM_waste') else 'steam' if k.startswith(('st_', 'dh', 'fx', 'eff', 'y_EB', 'rec', 'TMP_rec', 'loss_EB'))
                     else 'sinks' if k.startswith('sink_') or k == 'E_in' else 'exergy' if k[0] in 'XPpIf' and k not in ('paper_t',)
                     else 'measures' if k.startswith(('M', 'save', 'gap')) else 'other')
    return pd.DataFrame([dict(flow=k, group=grp(k), value=v, unit=unit_of(k)) for k, v in b.items() if np.ndim(v) == 0])


def energy_loss(b):
    return {'TMP plant': b['TMP_waste'], 'Paper machines': b['PM_waste'], 'Electric boilers': b['loss_EB'],
            'Hot water & heating': b['st_HW'] - b['sink_DH'], 'Steam network': b['st_loss'], 'Bleaching': b['el_bleach'],
            'WWTP': b['el_wwtp'], 'Wood handling': b['el_wood'] + b['st_wood'], 'Utilities & other': b['el_util'],
            'Internal grid losses': b['el_dist']}


def hotspots_table(b):
    el = energy_loss(b)
    HX = pd.DataFrame({'Exergy in': [b[f'Xin|{p}'] for p in PROCS], 'Useful out': [b[f'Xuse|{p}'] for p in PROCS],
                       'Waste out': [b[f'Xwaste|{p}'] for p in PROCS], 'Destroyed': [b[f'Xdest|{p}'] for p in PROCS],
                       'psi': [b[f'psi|{p}'] for p in PROCS], 'Improvement potential': [b[f'IP|{p}'] for p in PROCS],
                       'Energy view: heat lost': [el[p] for p in PROCS]}, index=[label(p) for p in PROCS])
    HX['Energy rank'] = HX['Energy view: heat lost'].rank(ascending=False).astype(int)
    HX['Exergy rank'] = HX['Destroyed'].rank(ascending=False).astype(int)
    HX.index.name = 'process'
    return HX


# ---------------------------------------------------------------- cross-checks
def crosschecks(b):
    E = BASE['E_tot']
    rows = [
     ('TMP electricity', b['el_TMP'], (46000 + 38000)*12/1000, 'GWh/y', 'el_tmp3_aug2019+el_tmp12_aug2019', 'one month (Aug 2019) x 12'),
     ('PM + bleaching electricity', b['el_PM'] + b['el_bleach'], (14000 + 8000)*12/1000, 'GWh/y', 'el_pm11_aug2019+el_pm12_aug2019', 'one month (Aug 2019) x 12'),
     ('Recovered TMP steam', b['st_rec'], 145000*12/3600, 'GWh/y', 'steam_tmp_net_2019', '145,000 GJ read as per month (period not stated in source; conflicts with steam_tmp3_use_aq)'),
     ('PM drying steam', b['st_PM'], 155000*12/3600, 'GWh/y', 'steam_pm_2019', '155,000 GJ read as per month (period not stated)'),
     ('WWTP share of electricity', b['el_wwtp']/E*100, 1.25, '%', 'el_wwtp_share_2019', 'midpoint of 1-1.5 %'),
     ('Share of steam from TMP', b['rec_ratio']*100, 80.0, '%', 'steam_recovery_rate_2025', 'midpoint of 70-90 %'),
     ('Mill specific electricity', b['SEC_mill']/1000, 3.3, 'MWh/t paper', 'spec_energy_2023_t13', 'NOT independent: same electricity and tonnage'),
     ('Total energy input (electricity + diesel)', b['E_in'], 1453.0, 'GWh/y', 'energy_sum_2023_t13', 'NOT independent: built from the same table'),
     ('TMP specific energy vs upper normal range', b['SEC_TMP'], 2150.0, 'kWh/t', 'tmp_el_spec_2025+tmp_aux_el_2025', 'Holmen normal 1,500-2,000 + 150 aux; model above the range (audit S1)'),
     ('TMP specific energy vs range midpoint', b['SEC_TMP'], 1900.0, 'kWh/t', 'tmp_el_spec_2025+tmp_aux_el_2025', 'midpoint 1,750 + 150'),
     ('Electric boiler yield (implied)', b['y_EB_implied'], 1.5, 't/MWh', 'steam_per_MW_2025', 'implied = eff_EB / dh'),
     ('Production hours', BASE['h_prod'], 7174.0, 'h/y', 'pm11_days_2023+pm12_days_2023', 'production-weighted 298.9 d x 24 h'),
     ('Steam residual vs documented heat use', b['st_HW'], 11.877 + 16000/3600, 'GWh/y', 'dh_export_2023+dh_2019', 'DH export 11.9 GWh + ~4.4 GWh domestic heating (2019); rest is unallocated'),
     ('Effluent + cooling water volume vs raw water intake', (BASE['V_wwtp'] + BASE['V_ff'] + BASE['V_cool'])/1e6, 11.047, 'Mm3/y', 'effluent_total_2023+img_wb_cooling vs water_raw_total_2023', 'FF PM2 may be part of the cooling-water stream (possible double count)'),
    ]
    df = pd.DataFrame(rows, columns=['quantity', 'model', 'independent', 'unit', 'source_id', 'note'])
    df['diff_pct'] = (df.model/df.independent - 1)*100
    return df


# ---------------------------------------------------------------- scenarios
SCENARIOS = {
 'S0 Base (draft-aligned)': {},
 'S1 2019 electricity split': dict(sh_TMP=0.72*0.9625, sh_PM=0.22*0.9625, sh_EB=0.06*0.9625, sh_OTH=0.0375),
 'S2 T0 = 25 C': dict(T0=25.0),
 'S3 PM steam 110 t/h': dict(m_PM=110.0),
 'S4 stress: 85 t/h recovery + 110 t/h PM': dict(m_rec=85.0, m_PM=110.0),
 'S5 steam to 90 C condensate (2.35 GJ/t, boiler 98 %)': dict(PROPERTY_BASED),
 "S6 TMP at Holmen's normal SEC (2,150 kWh/t)": dict(sec_TMP_override=2150.0),
 'S7 effluent 39 C (read as 32 K above 7 C)': dict(T_eff=39.0, T_ff=39.0),
 'S8 hours 8,760 h': dict(h_prod=8760.0),
 'S9 PM waste heat 50 C (PM wastewater value)': dict(T_PMwaste=50.0),
 'S10 effluent 20 C (long-shutdown value)': dict(T_eff=20.0, T_ff=20.0),
}


EXITS = [  # key, label (group draft Table 2 structure)
 ('DH', 'District heat to Norrtälje Energi'), ('evap', 'Dryer exhaust air: latent heat in evaporated water'),
 ('dryer_rest', 'Dryer exhaust air and hood losses: residual drying heat'), ('water', 'Wastewater to Edeboviken'),
 ('EB_rest', 'Electric boiler residual (condensate heat not counted at latent basis)'),
 ('st_loss', 'Steam distribution losses'), ('grid', 'Internal electrical grid losses'),
 ('subtotal', 'Subtotal, individually quantified'), ('by_diff', 'Not individually quantified (by difference)'),
 ('cool', '  of which: cooling water, estimated (4 Mm3/y, 5-15 K)'), ('total', 'Total = energy input')]


def exits_draft(p, r):
    """Exit table in the group draft's Table 2 structure (works on scalars and MC arrays)."""
    evap = evaporated_water(p['paper_t'], p['press_dry'], p['fin_moist'])*p['h_evap']/3600
    d = {'DH': p['DH_export'] + 0*r['E_in'], 'evap': evap, 'dryer_rest': r['st_PM'] - evap, 'water': r['sink_water'],
         'EB_rest': r['loss_EB'], 'st_loss': r['st_loss'], 'grid': r['el_dist']}
    d['subtotal'] = sum(d[k] for k in ['DH', 'evap', 'dryer_rest', 'water', 'EB_rest', 'st_loss', 'grid'])
    d['by_diff'] = r['E_in'] - d['subtotal']; d['cool'] = r['sink_cool']; d['total'] = r['E_in']
    return d


def exits_table(mc, b):
    base = exits_draft(BASE, b)
    P = dict(BASE); P.update({k: mc.X[k].values for k in mc.X.columns})
    for k, src in TIED.items():
        P[k] = P[src]
    ok = mc.ok.values
    dm = exits_draft(P, mc.Y)
    rows = []
    for k, lab in EXITS:
        v = np.asarray(dm[k])[ok]
        rows.append({'exit': lab, 'base_GWh': base[k], 'share_pct': base[k]/b['E_in']*100,
                     'P5': np.percentile(v, 5), 'P95': np.percentile(v, 95)})
    return pd.DataFrame(rows)


def scenarios_table():
    rows = {}
    for n, ch in SCENARIOS.items():
        r = evaluate({**BASE, **ch})
        top = sorted(PROCS, key=lambda p: r[f'Xdest|{p}'], reverse=True)[:3]
        rows[n] = {'el_TMP': r['el_TMP'], 'el_EB': r['el_EB'], 'el_util_unexplained': r['el_util'],
                   'rec_ratio_pct': r['rec_ratio']*100, 'st_HW': r['st_HW'], 'eff_EB': r['eff_EB'], 'y_EB_implied': r['y_EB_implied'],
                   'sink_air': r['sink_air'], 'Xdest_TMP': r['Xdest|TMP plant'], 'Xdest_PM': r['Xdest|Paper machines'],
                   'Xdest_EB': r['Xdest|Electric boilers'], 'Xdest_total': r['Xdest_total'],
                   'M1b_save_rec90': r['save_rec90'], 'M4_combined': r['M4'], 'gap_SEC': r['gap_SEC'],
                   'top3_exergy': ' > '.join(top)}
    df = pd.DataFrame(rows).T
    df.index.name = 'scenario'
    return df


# ---------------------------------------------------------------- MC summaries
KEYS = {'el_TMP': 'Electricity TMP', 'el_PM': 'Electricity paper machines', 'el_EB': 'Electricity electric boilers',
        'el_util': 'Utilities & other (residual)', 'st_rec': 'Recovered TMP steam', 'st_EB': 'Electric-boiler steam',
        'rec_ratio': 'Share of steam from TMP', 'st_HW': 'Steam to hot water, heating and venting (unallocated)',
        'sink_water': 'Heat to effluent water', 'sink_cool': 'Heat to cooling water', 'sink_air': 'Heat to air',
        'SEC_TMP': 'TMP kWh/t', 'y_EB_implied': 'Implied boiler yield t/MWh',
        'Xdest|TMP plant': 'Exergy destroyed TMP', 'Xdest|Paper machines': 'Exergy destroyed PM',
        'Xdest|Electric boilers': 'Exergy destroyed boilers', 'Xdest_total': 'Exergy destroyed total',
        'save_rec90': 'Saving, 90% steam from TMP (M1b)', 'gap_SEC': 'Saving, TMP at 2,150 kWh/t (gross, conditional)'}


HEADLINE = [  # key, label, unit
 ('el_TMP', 'Electricity to TMP plant', 'GWh/y'), ('el_PM', 'Electricity to paper machines (excl. bleaching)', 'GWh/y'),
 ('el_EB', 'Electricity to electric boilers', 'GWh/y'), ('el_util', 'Utilities & other (residual / unexplained)', 'GWh/y'),
 ('SEC_TMP', 'TMP specific electricity', 'kWh/t'),
 ('st_rec', 'Recovered TMP steam', 'GWh/y'), ('st_EB', 'Electric-boiler steam', 'GWh/y'), ('rec_pct', 'Share of steam from TMP', '%'),
 ('st_HW', 'Steam to hot water, heating and venting (unallocated)', 'GWh/y'),
 ('sink_air', 'Heat to air', 'GWh/y'), ('air_pct', 'Heat to air, share of input', '%'),
 ('sink_water', 'Heat to effluent water', 'GWh/y'), ('sink_cool', 'Heat to cooling water', 'GWh/y'),
 ('Xdest_total', 'Exergy destroyed, total', 'GWh/y'), ('Xdest_pct', 'Exergy destroyed, share of input', '%'),
 ('Xdest|TMP plant', 'Exergy destroyed, TMP plant', 'GWh/y'), ('Xdest|Paper machines', 'Exergy destroyed, paper machines', 'GWh/y'),
 ('Xdest|Electric boilers', 'Exergy destroyed, electric boilers', 'GWh/y'), ('psi_EB_pct', 'Exergy efficiency of electric boilers', '%'),
 ('M1', 'M1 TMP steam recovery +10 t/h', 'GWh/y'), ('M1b', 'M1b recovery to 90 % of supply', 'GWh/y'),
 ('M2', 'M2 heat pump replaces all boiler steam', 'GWh/y'), ('M3', 'M3 press dryness +2 points (48 to 50 %)', 'GWh/y'),
 ('M4', 'M4 combined', 'GWh/y'), ('M4_MWh_t', 'M4 combined, per tonne paper', 'MWh/t'),
]


def headline_table(mc, b):
    bd = b
    keys = {k: l for k, l, u in HEADLINE}
    df = summary(mc, keys, bd)
    df['unit'] = [u for k, l, u in HEADLINE]
    df.index.name = 'metric'
    return df[['key', 'unit', 'base', 'P5', 'P50', 'P95', 'uncon_P5', 'uncon_P50', 'uncon_P95', 'acceptance_rate']]


def mc_summary_table(mc, b):
    return summary(mc, KEYS, b).rename_axis('quantity')


def measures_table(mc, b):
    Y, ok = mc.Y, mc.ok
    rows = []
    for m, name in MEASURES.items():
        r = dict(measure=m, description=name)
        for src, suf in ((f'{m}', 'GWh'), (f'{m}_MWh_t', 'MWh_t'), (f'{m}_SEC', 'newSEC_MWh_t')):
            r[f'base_{suf}'] = b[src]
            r[f'P5_{suf}'], r[f'P50_{suf}'], r[f'P95_{suf}'] = (Y.loc[ok, src].quantile(q) for q in (.05, .5, .95))
        r['uncon_P5_GWh'], r['uncon_P95_GWh'] = Y[m].quantile(.05), Y[m].quantile(.95)
        r['P50_pct_of_boiler_el'] = (Y.loc[ok, m]/Y.loc[ok, 'el_EB']).median()*100
        rows.append(r)
    return pd.DataFrame(rows)


def rank_stability(mc):
    D = mc.Y.loc[mc.ok, [f'Xdest|{p}' for p in PROCS]]; D.columns = [label(p) for p in PROCS]
    rk = D.rank(axis=1, ascending=False)
    st = pd.DataFrame({f'rank_{r}': (rk == r).mean() for r in range(1, len(PROCS) + 1)})
    st.index.name = 'process'
    top3 = float(((rk[label('TMP plant')] == 1) & (rk[label('Paper machines')] == 2) & (rk[label('Electric boilers')] == 3)).mean())
    return st, top3


SP_OUT = ['Xdest|TMP plant', 'Xdest|Electric boilers', 'Xdest|Paper machines', 'rec_ratio', 'st_HW', 'sink_air', 'save_rec90', 'M4']


def spearman_table(mc):
    Y, X = mc.Y[mc.ok], mc.X[mc.ok]
    return pd.DataFrame({o: [spearmanr(X[k], Y[o])[0] for k in DIST] for o in SP_OUT}, index=list(DIST)).rename_axis('input')


TORNADO_METRICS = {'save_rec90': 'M1b saving (GWh/y)', 'M4': 'M4 combined saving (GWh/y)',
                   'sink_air': 'Heat to air (GWh/y)', 'Xdest_total': 'Exergy destroyed total (GWh/y)'}


def tornado_table():
    base = evaluate(dict(BASE)); rows = []
    for k in DIST:
        lo, hi = ppf(k, .05), ppf(k, .95)
        tie = lambda v, k=k: {k: v, **{t: v for t, src in TIED.items() if src == k}}
        rl, rh = evaluate({**BASE, **tie(lo)}), evaluate({**BASE, **tie(hi)})
        for m in TORNADO_METRICS:
            rows.append(dict(metric=m, input=k, P5_value=lo, P95_value=hi, at_P5=rl[m], at_P95=rh[m], base=base[m],
                             swing=abs(rh[m] - rl[m])))
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- figures
def _sankey(links, title, color_of, name, node_color):
    import plotly.graph_objects as go
    from kaleido.errors import ChromeNotFoundError
    nodes = list(dict.fromkeys(list(links.source) + list(links.target))); ix = {n: i for i, n in enumerate(nodes)}
    tot = {n: max(links[links.source == n]['GWh/y'].sum(), links[links.target == n]['GWh/y'].sum()) for n in nodes}
    fig = go.Figure(go.Sankey(valueformat=',.0f', valuesuffix=' GWh/y', arrangement='snap',
        node=dict(label=[f'{n}  {tot[n]:,.0f}' for n in nodes], pad=16, thickness=14, color=[node_color(n) for n in nodes],
                  line=dict(width=0)),
        link=dict(source=links.source.map(ix), target=links.target.map(ix), value=links['GWh/y'],
                  color=[color_of(s, t) for s, t in zip(links.source, links.target)])))
    fig.update_layout(title=dict(text=title, x=0.01, font_size=15), height=640, width=1150, font=dict(size=12, family='DejaVu Sans'),
                      margin=dict(l=10, r=10, t=60, b=10), paper_bgcolor='white')
    FIG.mkdir(parents=True, exist_ok=True)
    fig.write_html(FIG / f'{name}.html', include_plotlyjs='cdn')
    try:
        fig.write_image(FIG / f'{name}.png', scale=2)
        ok = True
    except ChromeNotFoundError as e:   # no Chrome for kaleido: HTML is still written
        print(f'[warn] static PNG for {name} skipped ({type(e).__name__}); HTML written. Run `uv run plotly_get_chrome` to enable PNG.')
        ok = False
    return fig, ok


def _rgba(hexc, a):
    h = hexc.lstrip('#'); return f'rgba({int(h[0:2],16)},{int(h[2:4],16)},{int(h[4:6],16)},{a})'


C = plotstyle.CARRIER
HWL = label('Hot water & heating')


def energy_links(b):
    other_el = b['el_bleach'] + b['el_wwtp'] + b['el_wood'] + b['el_util'] + b['el_dist']
    return pd.DataFrame([
     ('Grid electricity', 'TMP plant', b['el_TMP']), ('Grid electricity', 'Electric boilers', b['el_EB']),
     ('Grid electricity', 'Paper machines', b['el_PM']), ('Grid electricity', 'Other users*', other_el),
     ('Diesel', 'Low-grade waste heat', BASE['diesel']),
     ('TMP plant', 'Steam network', b['st_rec']), ('Electric boilers', 'Steam network', b['st_EB']),
     ('TMP plant', 'Low-grade waste heat', b['TMP_waste']), ('Electric boilers', 'Low-grade waste heat', b['loss_EB']),
     ('Steam network', 'Paper machines', b['st_PM']), ('Steam network', 'Hot water & venting (unallocated)', b['st_HW']),
     ('Steam network', 'Other users*', b['st_wood']), ('Steam network', 'Low-grade waste heat', b['st_loss']),
     ('Paper machines', 'Low-grade waste heat', b['PM_waste']), ('Other users*', 'Low-grade waste heat', other_el + b['st_wood']),
     ('Hot water & venting (unallocated)', 'District heating', b['sink_DH']),
     ('Hot water & venting (unallocated)', 'Low-grade waste heat', b['st_HW'] - b['sink_DH']),
     ('Low-grade waste heat', 'Heat to air', b['sink_air']), ('Low-grade waste heat', 'Heat to effluent water', b['sink_water']),
     ('Low-grade waste heat', 'Heat to cooling water', b['sink_cool'])], columns=['source', 'target', 'GWh/y'])


def fig_sankey_energy(b):
    links = energy_links(b)
    def col(s, t):
        if s in ('Grid electricity',): return _rgba(C['electricity'], .45)
        if s == 'Diesel': return _rgba(C['diesel'], .5)
        if t == 'Steam network' or (s == 'Steam network' and t != 'Low-grade waste heat'): return _rgba(C['steam'], .5)
        if t in ('Heat to effluent water', 'Heat to cooling water'): return _rgba(C['water'], .5)
        if t == 'District heating': return _rgba('#008300', .6)
        return _rgba(C['waste heat'], .35)
    nc = lambda n: (C['electricity'] if n == 'Grid electricity' else C['diesel'] if n == 'Diesel' else C['steam'] if n == 'Steam network'
                    else C['water'] if 'water' in n else C['waste heat'] if n in ('Low-grade waste heat', 'Heat to air') else '#52514e')
    fig, ok = _sankey(links, 'Energy flows of electricity and diesel, Hallsta 2023 (GWh/y)    *Other = bleaching, WWTP, wood, utilities, grid losses',
                      col, 'model_sankey_energy', nc)
    return links, fig, ok


def exergy_links(b):
    other_x = sum(b[f'Xin|{p}'] for p in ['Bleaching', 'WWTP', 'Wood handling', 'Utilities & other', 'Internal grid losses'])
    el_other = b['el_bleach'] + b['el_wwtp'] + b['el_wood'] + b['el_util'] + b['el_dist']
    D = lambda p: b[f'Xdest|{p}']
    return pd.DataFrame([
     ('Grid electricity', 'TMP plant', b['el_TMP']), ('Grid electricity', 'Electric boilers', b['el_EB']),
     ('Grid electricity', 'Paper machines', b['el_PM']), ('Grid electricity', 'Other users*', el_other),
     ('TMP plant', 'Steam network', b['Xuse|TMP plant']), ('Electric boilers', 'Steam network', b['Xuse|Electric boilers']),
     ('TMP plant', 'Exergy in waste heat', b['Xwaste|TMP plant']), ('TMP plant', 'Exergy destroyed', D('TMP plant')),
     ('Electric boilers', 'Exergy destroyed', D('Electric boilers')),
     ('Steam network', 'Paper machines', b['st_PM']*b['fx_steam']), ('Steam network', 'Other users*', b['st_wood']*b['fx_steam']),
     ('Steam network', 'Hot water & venting (unallocated)', b['st_HW']*b['fx_steam']),
     ('Steam network', 'Exergy destroyed', D('Steam network')),
     ('Paper machines', 'Exergy in waste heat', b['Xwaste|Paper machines']), ('Paper machines', 'Exergy destroyed', D('Paper machines')),
     ('Hot water & venting (unallocated)', 'Useful hot water', b['Xuse|Hot water & heating']),
     ('Hot water & venting (unallocated)', 'Exergy destroyed', D('Hot water & heating')),
     ('Other users*', 'Exergy destroyed', other_x)], columns=['source', 'target', 'GWh/y'])


def fig_sankey_exergy(b):
    links = exergy_links(b)
    col = lambda s, t: (_rgba(C['exergy destroyed'], .4) if t == 'Exergy destroyed' else _rgba(C['waste heat'], .4) if t == 'Exergy in waste heat'
                        else _rgba('#008300', .6) if t == 'Useful hot water' else _rgba(C['electricity'], .45) if s == 'Grid electricity'
                        else _rgba(C['steam'], .5))
    nc = lambda n: (C['electricity'] if n == 'Grid electricity' else C['exergy destroyed'] if n == 'Exergy destroyed' else C['steam'] if n == 'Steam network'
                    else C['waste heat'] if n == 'Exergy in waste heat' else '#008300' if n == 'Useful hot water' else '#52514e')
    fig, ok = _sankey(links, 'Exergy flows, Hallsta 2023 (GWh/y of exergy; diesel excluded)    *Other = bleaching, WWTP, wood, utilities, grid losses',
                      col, 'model_sankey_exergy', nc)
    return links, fig, ok


def fig_hotspots(HX):
    plotstyle.use()
    d = HX.sort_values('Destroyed')
    fig, ax = plt.subplots(figsize=(8, 5)); y = np.arange(len(d))
    ax.barh(y - 0.2, d['Energy view: heat lost'], 0.38, color=C['waste heat'], label='Energy view: heat leaving')
    ax.barh(y + 0.2, d['Destroyed'], 0.38, color=C['exergy destroyed'], label='Exergy view: exergy destroyed')
    for i, (e, x) in enumerate(zip(d['Energy view: heat lost'], d['Destroyed'])):
        ax.text(e + 8, i - 0.2, f'{e:,.0f}', va='center', fontsize=7, color=plotstyle.INK_2)
        ax.text(x + 8, i + 0.2, f'{x:,.0f}', va='center', fontsize=7, fontweight='bold')
    ax.set_yticks(y, [textwrap_label(n) for n in d.index]); ax.set_xlabel('GWh/y'); ax.legend(loc='lower right')
    ax.set_title('Energy versus exergy: where heat leaves and where useful work is lost'); ax.grid(axis='y', visible=False)
    plotstyle.save(fig, 'model_hotspots'); return fig


def textwrap_label(s, w=34):
    import textwrap
    return '\n'.join(textwrap.wrap(s, w))


def fig_mc_hist(mc, b):
    plotstyle.use()
    ks = [('Xdest|TMP plant', 'Exergy destroyed, TMP'), ('Xdest|Electric boilers', 'Exergy destroyed, boilers'), ('st_HW', 'Steam unallocated'),
          ('sink_air', 'Heat to air'), ('save_rec90', 'M1b saving'), ('M4', 'M4 combined saving')]
    fig, axes = plt.subplots(2, 3, figsize=(10, 5.2)); Y = mc.Y[mc.ok]
    for ax, (k, t) in zip(axes.ravel(), ks):
        ax.hist(Y[k], bins=50, color=plotstyle.SEQ[2]); ax.axvline(b[k], color=plotstyle.SERIES[1], lw=2, label='base')
        for q in (.05, .95): ax.axvline(Y[k].quantile(q), color=plotstyle.INK_2, ls='--', lw=1)
        ax.set_title(t); ax.set_xlabel('GWh/y'); ax.set_yticks([]); ax.grid(False)
    axes[0, 0].legend()
    fig.suptitle(f'Constrained Monte Carlo ({int(mc.ok.sum()):,} accepted runs); dashed = P5 and P95', x=0.01, ha='left', fontweight='bold')
    fig.tight_layout(); plotstyle.save(fig, 'model_mc_hist'); return fig


NICE = {'sh_EB': 'Boiler share of electricity', 'sh_TMP': 'TMP share of electricity', 'sh_PM': 'PM share of electricity',
        'sh_OTH': 'Other users share', 'm_rec': 'TMP steam recovered (t/h)', 'm_PM': 'Drying steam (t/h)', 'y_EB': 'Boiler steam yield (t/MWh)',
        'E_tot': 'Total electricity', 'h_prod': 'Operating hours', 'cop_hp': 'Heat pump COP', 'dh_override': 'Steam latent heat',
        'T_eff': 'Effluent temperature', 'dT_cool': 'Cooling-water temperature rise', 'V_cool': 'Cooling-water volume', 'T0': 'Reference temperature',
        'press_dry': 'Press dryness', 'h_evap': 'Evaporation heat', 'f_steamloss': 'Steam network loss', 'f_dist': 'Grid loss',
        'T_PMwaste': 'PM waste-heat temperature', 'T_TMPwaste': 'TMP waste-heat temperature', 'T_HW': 'Hot-water temperature',
        'aux_TMP': 'TMP auxiliaries (kWh/t)', 'pulp_t': 'Pulp production', 'paper_t': 'Paper production', 'm_wood': 'Wood-handling steam',
        'V_wwtp': 'Effluent volume', 'p_steam': 'Steam pressure', 'T_cond': 'Condensate temperature', 'diesel': 'Diesel', 'DH_export': 'District heat'}
nice = lambda k: NICE.get(k, k)


def fig_tornado(T):
    plotstyle.use()
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2))
    for ax, m in zip(axes, ['save_rec90', 'M4']):
        t = T[T.metric == m].nlargest(8, 'swing')[::-1]; base = t.base.iloc[0]
        ax.barh([nice(k) for k in t.input], t.at_P5 - base, left=base, color=plotstyle.INK_3, label='input at P5')
        ax.barh([nice(k) for k in t.input], t.at_P95 - base, left=base, color=plotstyle.SERIES[0], label='input at P95')
        ax.axvline(base, color='k', ls='--', lw=1); ax.set_xlabel('GWh/y'); ax.set_title(f'{TORNADO_METRICS[m]}, base {base:.1f}'); ax.grid(axis='y', visible=False)
    axes[0].legend(loc='lower right'); fig.suptitle('One-at-a-time sensitivity: every input moved to its own P5 and P95', x=0.01, ha='left', fontweight='bold')
    fig.tight_layout(); plotstyle.save(fig, 'model_tornado'); return fig


def fig_spearman(SP):
    plotstyle.use()
    S = SP[(SP.abs() >= 0.15).any(axis=1)]
    fig, ax = plt.subplots(figsize=(8, 0.35*len(S) + 1.8))
    im = ax.imshow(S.values, cmap='RdBu_r', vmin=-1, vmax=1, aspect='auto'); ax.grid(False)
    ax.set_xticks(range(len(S.columns)), [o.replace('Xdest|', 'Ex dest. ') for o in S.columns], rotation=30, ha='right'); ax.set_yticks(range(len(S)), [nice(k) for k in S.index])
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            v = S.values[i, j]
            if abs(v) >= 0.15: ax.text(j, i, f'{v:.2f}', ha='center', va='center', fontsize=7, color='white' if abs(v) > 0.6 else 'black')
    plt.colorbar(im, ax=ax, label='Spearman rho'); ax.set_title('Which inputs drive which results (constrained MC)')
    fig.tight_layout(); plotstyle.save(fig, 'model_spearman'); return fig


def fig_measures(MT):
    plotstyle.use()
    d = MT[::-1]
    fig, ax = plt.subplots(figsize=(8, 3.8)); y = np.arange(len(d))
    ax.barh(y, d.base_GWh, color=[plotstyle.SERIES[0] if m != 'M3b' else plotstyle.INK_3 for m in d.measure], height=0.55)
    ax.errorbar(d.base_GWh, y, xerr=[(d.base_GWh - d.P5_GWh).clip(lower=0), (d.P95_GWh - d.base_GWh).clip(lower=0)],
                fmt='none', ecolor=plotstyle.INK, capsize=3, lw=1.2)
    for i, (b, lo, hi) in enumerate(zip(d.base_GWh, d.P5_GWh, d.P95_GWh)):
        ax.text(max(hi, b) + 3, i, f'{b:.0f}  ({lo:.0f}-{hi:.0f})', va='center', fontsize=8)
    ax.set_yticks(y, [textwrap_label(s, 38) for s in d.description]); ax.set_xlabel('Electricity saved, GWh/y (bar = base case, whiskers = P5-P95)')
    ax.set_xlim(0, d.P95_GWh.max()*1.3); ax.grid(axis='y', visible=False)
    ax.set_title('Improvement measures (annual upper bounds; boilers assumed to run all year)')
    plotstyle.save(fig, 'model_measures'); return fig


def fig_rank(st):
    plotstyle.use()
    d = st.copy(); d['rank 4+'] = d.iloc[:, 3:].sum(axis=1); d = d[['rank_1', 'rank_2', 'rank_3', 'rank 4+']]
    d = d.sort_values(['rank_1', 'rank_2', 'rank_3'], ascending=True)
    d = d[(d.rank_1 + d.rank_2 + d.rank_3) > 0.001]
    fig, ax = plt.subplots(figsize=(8, 3.2)); left = np.zeros(len(d))
    for c, col, l in zip(d.columns, [plotstyle.SEQ[5], plotstyle.SEQ[3], plotstyle.SEQ[1], plotstyle.GRID], ['rank 1', 'rank 2', 'rank 3', 'rank 4 or lower']):
        ax.barh([textwrap_label(i, 34) for i in d.index], d[c], left=left, color=col, label=l); left += d[c].values
    ax.set_xlim(0, 1); ax.set_xlabel('Share of accepted runs'); ax.legend(ncol=4, loc='upper center', bbox_to_anchor=(0.5, -0.25)); ax.grid(axis='y', visible=False)
    ax.set_title('Rank of each process by exergy destroyed')
    plotstyle.save(fig, 'model_rank_stability'); return fig


# ---------------------------------------------------------------- build everything
def write(df, name, index=True):
    TAB.mkdir(parents=True, exist_ok=True); df.to_csv(TAB / name, index=index)


def build_all(N=10_000, seed=2023, mc=None, verbose=True):
    plotstyle.use()
    b = evaluate(dict(BASE))
    mc = mc or run_mc(N, seed)
    out = dict(b=b, mc=mc)
    write(inputs_table(), 'model_inputs.csv', False)
    write(balance_table(b), 'model_balance.csv', False)
    HX = hotspots_table(b); write(HX, 'model_exergy_hotspots.csv'); out['HX'] = HX
    out['mcsum'] = mc_summary_table(mc, b); write(out['mcsum'], 'model_mc_summary.csv')
    st, top3 = rank_stability(mc); write(st, 'model_rank_stability.csv'); out['rank'], out['top3'] = st, top3
    SP = spearman_table(mc); write(SP, 'model_spearman.csv'); out['SP'] = SP
    T = tornado_table(); write(T, 'model_tornado.csv', False); out['T'] = T
    MT = measures_table(mc, b); write(MT, 'model_measures.csv', False); out['MT'] = MT
    out['xc'] = crosschecks(b); write(out['xc'], 'model_crosschecks.csv', False)
    out['sc'] = scenarios_table(); write(out['sc'], 'model_scenarios.csv')
    out['exits'] = exits_table(mc, b); write(out['exits'], 'model_exits_draft_format.csv', False)
    out['head'] = headline_table(mc, b); write(out['head'], 'headline.csv')
    out['links_E'], _, ok1 = fig_sankey_energy(b); out['links_X'], _, ok2 = fig_sankey_exergy(b)
    out['sankey_png'] = ok1 and ok2
    fig_hotspots(HX); fig_mc_hist(mc, b); fig_tornado(T); fig_spearman(SP); fig_measures(MT); fig_rank(st)
    plt.close('all')
    if verbose:
        print(f'MC: N={mc.N}, accepted {mc.acceptance:.2%}, k-guard binds in {mc.k_binding_rate:.2%}; tables -> {TAB.relative_to(ROOT)}, figures -> {FIG.relative_to(ROOT)}')
    return out
