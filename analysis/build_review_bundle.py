"""Collect model outputs, source quotes and reviewer judgements into one JSON bundle
for the group review page (reports/review/review_data.json)."""
import base64
import csv
import json
from pathlib import Path

from hallsta_mfa.model import BASE, run

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / 'reports' / 'tables'
FIG = ROOT / 'reports' / 'figures'
OUT = ROOT / 'reports' / 'review'


def rows(name):
    with open(TAB / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


def num(x, nd=1):
    try:
        return round(float(x), nd)
    except (TypeError, ValueError):
        return x


src = {r['id']: r for r in csv.DictReader(open(ROOT / 'data' / 'sources.csv', newline='', encoding='utf-8'))}


def cite(ids):
    out = []
    for i in str(ids).replace(' vs ', '+').split('+'):
        i = i.strip()
        if i in src:
            s = src[i]
            out.append({'id': i, 'file': s['source_file'], 'loc': s['location'], 'year': s['data_year'],
                        'quote': s['quote'], 'value': s['value'] or f"{s['value_low']}–{s['value_high']}", 'unit': s['unit']})
    return out


b = run(BASE)

inputs = [{'id': 'in:' + r['param'], 'param': r['param'], 'desc': r['description'], 'value': num(r['value'], 4),
           'unit': r['unit'], 'dist': r['distribution'], 'cls': r['data_class'], 'source': r['source_id'],
           'cites': cite(r['source_id'])} for r in rows('model_inputs.csv')]

E_in = b['E_in']
layers = [
    {'id': 'bal:electricity', 'title': 'Layer 1 · Electricity end uses', 'total_label': 'Purchased electricity', 'total': BASE['E_tot'],
     'note': 'Shares 70/15/10/5 % (Holmen 2025) split 1,450 GWh. Named "other" items are sized from Holmen\'s MW figures; utilities is what remains.',
     'rows': [('TMP refiners', b['el_TMP_ref'], 'electricity'), ('TMP auxiliaries (150 kWh/t)', b['el_TMP_aux'], 'electricity'),
              ('Paper machines', b['el_PM'], 'electricity'), ('Bleaching (3 MW)', b['el_bleach'], 'electricity'),
              ('Electric boilers', b['el_EB'], 'electricity'), ('WWTP (2.5 MW, 8,760 h)', b['el_wwtp'], 'electricity'),
              ('Wood handling (2.5 MW)', b['el_wood'], 'electricity'), ('Internal grid losses (1 %)', b['el_dist'], 'electricity'),
              ('Utilities & other (residual)', b['el_util'], 'residual')]},
    {'id': 'bal:steam', 'title': 'Layer 2 · Steam loop', 'total_label': 'Steam supply (TMP recovery + boilers)', 'total': b['st_supply'],
     'note': f"TMP recovery {b['st_rec']:.0f} GWh (100 t/h) + boilers {b['st_EB']:.0f} GWh (145 GWh × 0.98). Steam heat {b['dh']*3.6:.2f} GJ/t.",
     'rows': [('Paper machine drying (95 t/h)', b['st_PM'], 'steam'), ('Wood handling (1.5 t/h)', b['st_wood'], 'steam'),
              ('Distribution losses (4 %)', b['st_loss'], 'steam'), ('Hot water, heating, venting (unallocated)', b['st_HW'], 'residual')]},
    {'id': 'bal:exits', 'title': 'Layer 3 · Where the energy leaves', 'total_label': 'Electricity + diesel', 'total': E_in,
     'note': 'Everything ends as heat. Water, cooling water and district heat are sized from volumes and temperatures; air is what remains.',
     'rows': [('Heat to effluent water (35 °C)', b['sink_water'], 'water'), ('Heat to cooling water (ΔT 10 K)', b['sink_cool'], 'water'),
              ('District heat to Norrtälje Energi', b['sink_DH'], 'useful'), ('Heat to air (residual)', b['sink_air'], 'residual')]},
]
for L in layers:
    L['rows'] = [{'label': a, 'value': round(v, 1), 'kind': k} for a, v, k in L['rows']]
    L['closure'] = round(L['total'] - sum(r['value'] for r in L['rows']), 2)
    L['total'] = round(L['total'], 1)

hot = rows('model_exergy_hotspots.csv')
exergy = [{'process': r['process'].replace('Hot water & heating', 'Hot water & venting (unallocated)'),
           'xin': num(r['Exergy in']), 'useful': num(r['Useful out']), 'waste': num(r['Waste out']),
           'destroyed': num(r['Destroyed']), 'psi': num(float(r['psi'])*100), 'heat': num(r['Energy view: heat lost'])} for r in hot]

head = [{'metric': r['metric'], 'unit': r['unit'], 'base': num(r['base'], 2), 'p5': num(r['P5'], 2), 'p95': num(r['P95'], 2)}
        for r in rows('headline.csv')]
checks = [{'id': f'chk:{i}', 'quantity': r['quantity'], 'model': num(r['model']), 'indep': num(r['independent']), 'unit': r['unit'],
           'diff': num(r['diff_pct']), 'note': r['note'], 'cites': cite(r['source_id'])} for i, r in enumerate(rows('model_crosschecks.csv'))]
meas = [{'id': 'mea:' + r['measure'], 'desc': r['description'], 'base': num(r['base_GWh']), 'p5': num(r['P5_GWh']), 'p95': num(r['P95_GWh']),
         'mwh_t': num(r['base_MWh_t'], 3), 'sec': num(r['base_newSEC_MWh_t'], 2)} for r in rows('model_measures.csv')]
recon = [r for r in rows('eda_reconciliation.csv') if r['flag'].strip()]
recon = [{'id': f"rec:{r['source_id']}", 'input': r['model_input'], 'source': r['source'], 'year': r['year'], 'value': r['source_value'],
          'flag': r['flag'], 'used': r['value_used_in_model'], 'cites': cite(r['source_id'])} for r in recon]

judgements = json.loads((ROOT / 'docs' / 'review' / 'judgements.json').read_text(encoding='utf-8'))
for j in judgements['changes']:
    j['cites'] = cite('+'.join(j.get('source_ids', [])))

figs = {name: 'data:image/png;base64,' + base64.b64encode((FIG / f'{name}.png').read_bytes()).decode()
        for name in ['model_sankey_energy', 'model_measures']}

OUT.mkdir(parents=True, exist_ok=True)
bundle = dict(inputs=inputs, layers=layers, exergy=exergy, headline=head, checks=checks, measures=meas, recon=recon,
              changes=judgements['changes'], tmp=judgements['tmp'], questions=judgements['questions'], figs=figs)
(OUT / 'review_data.json').write_text(json.dumps(bundle, ensure_ascii=False), encoding='utf-8')
print(f"inputs {len(inputs)}, checks {len(checks)}, recon flags {len(recon)}, changes {len(judgements['changes'])} -> {OUT / 'review_data.json'}")

# Render the review page: inject the bundle into the template (escape "</" so the JSON cannot close the script tag)
tpl = (OUT / 'template.html').read_text(encoding='utf-8')
page = tpl.replace('/*__DATA__*/', json.dumps(bundle, ensure_ascii=False).replace('</', '<\\/'))
(OUT / 'hallsta_review.html').write_text(page, encoding='utf-8')
print(f"page -> {OUT / 'hallsta_review.html'} ({len(page)/1e6:.2f} MB)")
