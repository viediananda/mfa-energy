"""Build the group review page (reports/review/hallsta_review.html) and docs/review/report_edits.md.

Text and worked calculations come from analysis/review_content.py; tables and figures come from
reports/tables and reports/figures (run analysis/run_model.py first).
"""
import base64
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import review_content as R  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / 'reports' / 'tables'
FIG = ROOT / 'reports' / 'figures'
OUT = ROOT / 'reports' / 'review'
b = R.b


def rows(name):
    with open(TAB / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def num(x, nd=2):
    try:
        return round(float(x), nd)
    except (TypeError, ValueError):
        return x


src = {r['id']: r for r in csv.DictReader(open(ROOT / 'data' / 'sources.csv', newline='', encoding='utf-8'))}


def cite(ids):
    out = []
    for i in ids:
        for j in str(i).replace(' vs ', '+').split('+'):
            j = j.strip()
            if j in src:
                s = src[j]
                out.append({'id': j, 'file': s['source_file'], 'loc': s['location'], 'year': s['data_year'], 'quote': s['quote'],
                            'value': s['value'] or (f"{s['value_low']}–{s['value_high']}" if s['value_low'] else ''), 'unit': '' if s['unit'] == 'text' else s['unit']})
    return out


# rationale for each input, shown in the inputs table
WHY = {
 'E_tot': 'Miljörapport Tabell 13. Normal CV 2 % (draft Table 6.2).', 'paper_t': 'Tabell 3. CV 1 % (Table 6.2).',
 'pulp_t': 'Tabell 3, integrated TMP production. CV 1 %.', 'DH_export': 'Section 8.3.3, 11,877 MWh. CV 5 %.',
 'diesel': 'Tabell 13. CV 5 % (Table 6.2).', 'V_wwtp': 'Section 5.2: 18,300 m³/d from the treatment plant. CV 2 % (Table 6.2).',
 'V_ff': 'Section 5.2: total 7,288,861 m³ minus the treatment-plant outlet. CV 2 %.',
 'V_cool': 'Holmen 2024 water balance: 4 Mm³/y cooling and unaffected water. Used only to size part of the 769 GWh.',
 'dT_cool': 'No source. 5–15 K is typical for once-through cooling. Used only to size part of the 769 GWh.',
 'sh_TMP': 'Holmen 2025 "about 70 %". Normal CV 10 %, shares rescaled to 100 % (Table 6.2).',
 'sh_PM': 'Holmen 2025 "about 15 %", including bleaching. CV 10 %.', 'sh_EB': 'Holmen 2025 "around 10 %". CV 10 %.',
 'sh_OTH': 'Remainder of Holmen\'s split. CV 10 %.', 'P_wood': 'Holmen 2025, 2.5 MW, × 7,200 h.', 'P_bleach': 'Holmen 2025, 3 MW, × 7,200 h.',
 'P_wwtp': 'Holmen 2025, 2.5 MW, × 8,760 h (runs all year).', 'aux_TMP': 'Holmen 2025: "150 kWh/ton in relation to about 2000 kWh/tonne for refining".',
 'm_rec': 'Holmen 2025 "about 100 tonnes of steam/hour". Triangular 85–115 (Table 6.2).',
 'y_EB': 'Holmen 2025 "1.5 tonnes of steam/MW". Normal CV 5 % (Table 6.2).',
 'eff_EB': 'Only in sensitivity case S5 (full-heat convention).', 'm_PM': 'Holmen 2025 "80–110 tonnes/h". Triangular, mode 95 (Table 6.2).',
 'm_wood': 'Holmen 2025 "1,5 tonnes/h".', 'PM11_frac': 'August 2019 line meters; only splits PM electricity between the two lines.',
 'h_prod': 'Tabell 4 production-weighted 7,174 h, rounded. Triangular 6,800–7,800 (Table 6.2).', 'h_wwtp': 'Tabell 4: treatment plant 365 days.',
 'f_dist': 'No source ("?" in Holmen\'s answer). Draft cites DOE: <1 % to >4 %.', 'f_steamloss': 'No source. Draft cites Spirax Sarco: below about 5 %.',
 'dh_override': 'Latent heat at 2.4 bar(g), 2.15 GJ/t. Normal CV 3 % (Table 6.2).', 'p_steam': '2.4 bar(g) = 3.4 bar absolute (138 °C). Only used for steam exergy.',
 'T_cond': 'Holmen 2019: condensate "approx 90 degrees". Used for steam exergy and the S5 case.',
 'T_TMPwaste': 'Pulp before bleaching is 80 °C (Holmen). Unrecovered TMP heat is taken at that temperature.',
 'T_PMwaste': 'PM wastewater ~50 °C (Holmen), exhaust air warmer: 55 °C as a blend.', 'T_HW': 'Typical heating hot water.',
 'T_DHs': 'Typical Swedish district heating supply.', 'T_DHr': 'Typical district heating return.',
 'T_eff': 'Holmen 2019: "roughly 32 degrees", "approx 20" in long shutdowns. Triangular(20, 32, 32) (Table 6.2).',
 'T_ff': 'Same draw as the main effluent.', 'T0': 'Annual mean surroundings. Uniform 5–10 °C (Table 6.2).', 'T_ref': 'Same as T0.',
 'cpv': 'Water, 4.18 MJ/m³K (draft value).', 'dm_rec_M1': 'Measure 1 as defined in the draft.', 'cop_hp': 'Arpagaus et al. (2018); uniform 2.5–3.5.',
 'press_dry': 'Draft: about 48 % for a Valmet press section. Triangular 45–51 (Table 6.2).', 'd_press_dry': 'Measure 3 as defined in the draft (48 → 50 %).',
 'fin_moist': 'Holmen: water in paper about 7 %.', 'h_evap': 'Draft value, evaporation plus heating. CV 2 % (Table 6.2).'}

inputs = [{'id': 'in:' + r['param'], 'param': r['param'], 'desc': r['description'], 'value': num(r['value'], 4), 'unit': r['unit'],
           'dist': r['distribution'], 'cls': r['data_class'], 'why': WHY.get(r['param'], ''), 'cites': cite([r['source_id']])}
          for r in rows('model_inputs.csv')]

layers = {
 'bal:electricity': dict(title='Electricity end uses', total_label='Purchased electricity', total=1450.0, rows=[
    ('TMP refiners', b['el_TMP_ref'], 'electricity'), ('TMP auxiliaries', b['el_TMP_aux'], 'electricity'), ('Paper machines', b['el_PM'], 'electricity'),
    ('Bleaching', b['el_bleach'], 'electricity'), ('Electric boilers', b['el_EB'], 'electricity'), ('WWTP', b['el_wwtp'], 'electricity'),
    ('Wood handling', b['el_wood'], 'electricity'), ('Internal grid losses', b['el_dist'], 'electricity'), ('Utilities (remainder)', b['el_util'], 'residual')]),
 'bal:steam': dict(title='Steam use', total_label='Steam supply (TMP + boilers)', total=b['st_supply'], rows=[
    ('Paper-machine drying', b['st_PM'], 'steam'), ('Wood handling', b['st_wood'], 'steam'), ('Distribution losses', b['st_loss'], 'steam'),
    ('Other heat uses (remainder)', b['st_HW'], 'residual')]),
}
for L in layers.values():
    L['rows'] = [{'label': a, 'value': round(v, 1), 'kind': k} for a, v, k in L['rows']]
    L['closure'] = round(L['total'] - sum(r['value'] for r in L['rows']), 2)

exergy = [{'process': r['process'].replace('Hot water & heating', 'Hot water & venting (unallocated)'), 'xin': num(r['Exergy in'], 1),
           'useful': num(r['Useful out'], 1), 'waste': num(r['Waste out'], 1), 'destroyed': num(r['Destroyed'], 1),
           'psi': num(float(r['psi'])*100, 1), 'ip': num(r['Improvement potential'], 1)} for r in rows('model_exergy_hotspots.csv')]
head = [{'metric': r['metric'], 'unit': r['unit'], 'base': num(r['base']), 'p5': num(r['P5']), 'p95': num(r['P95'])} for r in rows('headline.csv')]
recon = [{'id': f"rec:{r['source_id']}", 'input': r['model_input'], 'source': r['source'], 'year': r['year'], 'value': r['source_value'],
          'flag': r['flag'], 'used': r['value_used_in_model'], 'cites': cite([r['source_id']])} for r in rows('eda_reconciliation.csv') if r['flag'].strip()]

decisions = {k: {**d, 'id': k, 'cites': cite(d.get('sources', []))} for k, d in R.DECISIONS.items()}
edits = [{'id': f'edit:{i}', 'section': s, 'type': t, 'current': c, 'new': n, 'why': w} for i, (s, t, c, n, w) in enumerate(R.REPORT_EDITS, 1)]
steps = R.STEPS + [dict(id='edits', n=10, title='Edits to make in the report', blocks=[
    {'t': 'p', 'text': f'Every change the report needs, section by section, with the exact text. {sum(e["type"] == "Fix" for e in edits)} are fixes (errors, inconsistencies, typos) and {sum(e["type"] == "Add" for e in edits)} are additions (missing justification or results). Nothing here changes the draft\'s conclusions. Mark each edit OK if it should go in, Question if it needs discussion, Wrong if it should not.'},
    {'t': 'edits'}])]

figs = {n: 'data:image/png;base64,' + base64.b64encode((FIG / f'{n}.png').read_bytes()).decode()
        for n in ['model_sankey_energy', 'model_sankey_exergy', 'model_measures']}

bundle = dict(steps=steps, decisions=decisions, inputs=inputs, layers=layers, exergy=exergy, headline=head, recon=recon, edits=edits, figs=figs,
              tmp=[{'label': 'Model 2023 (70 % of 1,450 GWh ÷ 421,883 t)', 'value': round(b['SEC_TMP']), 'kind': 'model'},
                   {'label': 'Holmen slide, undated (2.20 MWh/t paper ÷ 0.949 t pulp/t paper)', 'value': round(R.slide_tmp), 'kind': 'independent'},
                   {'label': 'August 2019 meters, TMP3 + TMP12 (84 GWh ÷ est. monthly pulp)', 'value': round(R.aug19), 'kind': 'independent'},
                   {'label': 'Holmen "normal", top of range (2,000 + 150 auxiliaries)', 'value': 2150, 'kind': 'claim'},
                   {'label': 'Holmen "normal", midpoint (1,750 + 150)', 'value': 1900, 'kind': 'claim'}])

OUT.mkdir(parents=True, exist_ok=True)
data = json.dumps(bundle, ensure_ascii=False)
(OUT / 'review_data.json').write_text(data, encoding='utf-8')
page = (OUT / 'template.html').read_text(encoding='utf-8').replace('/*__DATA__*/', data.replace('</', '<\\/'))
(OUT / 'hallsta_review.html').write_text(page, encoding='utf-8')

# report edits as markdown, for the group's working copy
md = ['# Report edits for the group draft (12 Oct 2026)', '',
      'Generated by analysis/build_review_bundle.py from analysis/review_content.py. The model baseline is aligned with the draft: '
      'only invalid or inconsistent items are fixed, and missing support is added.', '',
      '| # | Section | Type | Current | Change to | Why |', '|---|---|---|---|---|---|']
md += ['| ' + ' | '.join([str(i), e['section'], e['type'], e['current'], e['new'], e['why']]).replace('\n', ' ') + ' |' for i, e in enumerate(edits, 1)]
md += ['', '## Decision cards', '']
for d in R.DECISIONS.values():
    md += [f"### {d['title']} ({d['verdict']})", '', f"**Draft:** {d['draft']}", '', f"**What we checked:** {d['check']}", '', '**Why:**']
    md += [f'- {x}' for x in d['why']] + ['', f"**Report text:** {d['report']}", '']
(ROOT / 'docs' / 'review' / 'report_edits.md').write_text('\n'.join(md), encoding='utf-8')
print(f'{len(steps)} steps, {len(decisions)} decisions, {len(edits)} edits, {len(inputs)} inputs -> {OUT / "hallsta_review.html"} ({len(page)/1e6:.2f} MB)')
