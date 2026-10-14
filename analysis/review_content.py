"""Text, worked calculations and report edits for the group review page.

The model baseline is aligned with the group draft (12 Oct 2026). Every number shown is computed
here from the model (run(BASE)) or read from reports/tables, so the explanations cannot drift from
the results. build_review_bundle.py turns STEPS into the page and REPORT_EDITS into
docs/review/report_edits.md.
"""
import csv
from pathlib import Path

from hallsta_mfa.measures import evaporated_water, measures
from hallsta_mfa.model import BASE, PROPERTY_BASED, run

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / 'reports' / 'tables'
P = BASE
b = run(BASE)
m = measures(BASE, b)
bp = run({**BASE, **PROPERTY_BASED})


def g(x, nd=1):
    return f'{x:,.{nd}f}'


def table(name):
    with open(TAB / name, newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))


H = {r['metric']: r for r in table('headline.csv')}
EX = {r['exit']: r for r in table('model_exits_draft_format.csv')}


def rng(metric, nd=0):
    r = H[metric]
    return f"{g(float(r['base']), nd)} (P5–P95 {g(float(r['P5']), nd)}–{g(float(r['P95']), nd)})"


def p5p95(metric, nd=0):
    r = H[metric]
    return f"{g(float(r['P5']), nd)}–{g(float(r['P95']), nd)}"


# ---------------------------------------------------------------- derived numbers used in the text
dry_solids = P['paper_t']*(1 - P['fin_moist'])
water_after_press = dry_solids*(1/P['press_dry'] - 1)
water_in_paper = P['paper_t']*P['fin_moist']
W0 = evaporated_water(P['paper_t'], P['press_dry'], P['fin_moist'])
W1 = evaporated_water(P['paper_t'], P['press_dry'] + P['d_press_dry'], P['fin_moist'])
Q_evap = W0*P['h_evap']/3600
dh, dhp = b['dh'], b['dh_prop']           # MWh per tonne: latent (report basis) and full enthalpy drop
ex_t = dh*b['fx_steam']                    # MWh exergy per tonne of steam
pulp_paper = P['pulp_t']/P['paper_t']
slide_tmp = 2.20/pulp_paper*1000
pulp19 = 1451/3.18*1000*pulp_paper
aug19 = 84000*12/pulp19*1000
q_eff = (P['V_wwtp'] + P['V_ff'])*P['cpv']*(P['T_eff'] - P['T_ref'])/3.6e6
SEASON = 0.75
X_air = P['E_tot'] - b['Xdest_total'] - b['X_DH'] - b['X_eff']
acc = float(H['M1 TMP steam recovery +10 t/h']['acceptance_rate'])*100
per_tph = 7200*dh/1000/b['eff_EB']        # GWh electricity per t/h of boiler steam avoided


# ---------------------------------------------------------------- decision cards
# verdict: Keep = the draft is right as it stands. Keep + support = right, but the report needs the
# justification added. Fix = the draft has an error or inconsistency. Add = something essential is missing.
DECISIONS = {
 'dec:steam-basis': dict(
    title='Steam counted at its latent heat, 2.15 GJ per tonne',
    verdict='Keep + support',
    draft='Section 4.3 and 5.1 convert steam flows with 2.15 GJ/t, "the useful latent thermal energy released when the steam condenses". TMP steam 430 GWh, boiler steam 130, drying 408.',
    check=f'The model uses the same convention and reproduces 430.0, 129.9 and 408.5 GWh. We also ran the alternative convention (full heat from 138 °C steam down to 90 °C condensate, 2.35 GJ/t) as sensitivity case S5.',
    why=[
      'When steam heats something it first condenses and releases its latent heat, 2.15 GJ per tonne at 2.4 bar(g). The condensed water is still at 138 °C and can give off a further ~0.2 GJ/t if it cools to the 90 °C that Holmen reports for condensate. Counting only the latent part is a common convention for steam balances, because the condensate heat mostly returns to the steam system with the condensate. The draft states this convention clearly in section 5.1.',
      'Both conventions are valid as long as the report uses one consistently. The latent convention keeps all the draft\'s steam numbers.',
      f'The convention does not change exergy. One tonne of steam holds {ex_t*1000:.0f} kWh of exergy whichever way its heat is counted, so the exergy results are the same in both. It does not change the improvement measures either: M1–M4 come out identical under both conventions (a test in the code checks this).',
      f'What it does change is the share of steam from TMP (76.8 % in both, because both sources scale equally) and the size of the "electric boiler residual" (next card). Under the 2.35 convention the steam flows are 9.4 % larger: TMP {g(bp["st_rec"],0)}, drying {g(bp["st_PM"],0)} GWh.'],
    report='Section 4.3, after the steam parameters: "Steam flows are expressed as latent heat (2.15 GJ/t at 2.4 bar(g)). Counting the full heat down to 90 °C condensate (2.35 GJ/t) raises all steam flows by 9 % but leaves the exergy results and the measure savings unchanged (sensitivity case S5)."',
    sources=['steam_temp_2p4bar_2019', 'condensate_temp_pm_2019', 'steam_pressure_pm_2019']),
 'dec:boiler-residual': dict(
    title='The 15 GWh "boiler losses" are not a loss',
    verdict='Fix (label only)',
    draft='Section 5.1 says "there is 15 GWh/y as boiler residual", and Table 2 lists "Electric boiler losses 15 GWh (145 − 130)".',
    check='The number is right: 145 GWh × 1.5 t/MWh × 2.15 GJ/t = 130 GWh of latent heat, 15 GWh less than the electricity. The label is what is wrong.',
    why=[
      'Electrode boilers turn about 98–99 % of their electricity into steam heat. Read as a loss, 15 GWh would mean 90 % efficiency, and a marker familiar with boilers will notice.',
      f'At the latent convention the 15 GWh is the heat that raises the feedwater from 90 °C condensate to 138 °C before it boils. It is inside the steam, but the latent convention does not count it as "steam". Check: 1.5 t/MWh × 2.35 GJ/t (full heat) ÷ 3.6 = {1.5*dhp:.2f}, so the boiler is about 98 % efficient on the full-heat basis.',
      'So the number stays and only its name changes.'],
    report='Section 5.1, replace "Based on this there is 15 GWh/y as boiler residual" with: "The remaining 15 GWh/y is not a boiler loss (electric boilers are about 98 % efficient). It is the heat used to raise the feedwater from 90 °C condensate to saturation, which the latent-heat convention does not count as steam." In Table 2, rename the row "Electric boiler residual (condensate heat, see 5.1)".',
    sources=['steam_per_MW_2025', 'condensate_temp_pm_2019']),
 'dec:tmp-share': dict(
    title='TMP uses 70 % of the electricity (2,406 kWh per tonne of pulp)',
    verdict='Keep + support',
    draft='Section 3.2 and 5.1 use Holmen\'s 70 % share without discussion.',
    check='Holmen also says refining "normally" takes 1,500–2,000 kWh/t plus 150 kWh/t for auxiliaries. 70 % of 1,450 GWh over 421,883 t of pulp is 2,406 kWh/t, above that range. A marker may spot the tension, so the report should address it. The full argument is in step 3.',
    why=[f'Two independent plant-level figures from other years give about 2,320 kWh/t: the Holmen energy-flow slide ({g(slide_tmp,0)}) and the August 2019 meter readings ({g(aug19,0)}). 2023 is 4 % above them.',
         'The Miljörapport gives three 2023-specific reasons for higher electricity use per tonne, all pointing the same way.',
         'Holmen\'s "1,500–2,000" was an answer about refiners in normal operation, not the whole TMP plant over a year.',
         'Using 2,150 kWh/t instead would leave 126 GWh of electricity with no consumer, against Holmen\'s split.'],
    report='Add the paragraph in step 3 ("Suggested text") to section 5.2.',
    sources=['el_split_tmp_2025', 'tmp_el_spec_2025', 'tmp_aux_el_2025', 'pptx_tmp_in', 'el_tmp3_aug2019', 'el_tmp12_aug2019', 'narr_l12_quality_2023', 'narr_price_stops_2023', 'narr_full_run_sec_2023']),
 'dec:residual-steam': dict(
    title='130 GWh of steam for "other heat uses"',
    verdict='Keep + support',
    draft='Section 5.1: "408 GWh is used by PM drying, while remaining steam is used for other thermal demands, including warm water production and heating, while excess steam may be released during summer". Section 5.1 (losses) gives it as 560 − 408 − 22 = 130 GWh.',
    check=f'The model gives the same: {g(b["st_HW"],1)} GWh unallocated + {g(b["st_wood"],1)} GWh wood handling = {g(b["st_HW"]+b["st_wood"],0)} GWh. Monte Carlo range for the unallocated part: {p5p95("Steam to hot water, heating and venting (unallocated)")} GWh.',
    why=['The draft\'s description is right and matches Holmen: steam goes first to the dryers, then to warm-water production and domestic heating, and surplus is vented "sometimes during summer months".',
         'What the report should add is how uncertain this number is. Documented uses add up to only about 16 GWh (district heat 11.9 GWh in 2023, domestic heating about 4.4 GWh in 2019). The rest is warm-water production and venting, with no figures in the sources.',
         f'Most of the uncertainty comes from drying steam, which Holmen gives only as 80–110 t/h. At 110 t/h (scenario S3) the remainder falls to {g(float([r for r in table("model_scenarios.csv") if r["scenario"].startswith("S3")][0]["st_HW"]),0)} GWh. The 2019 answer "PM\'s 155,000 GJ", if it is per month, corresponds to about 110 t/h, which points to the upper end.'],
    report='Section 5.1, after "excess steam may be released during summer where no heavy preheat of fresh water is needed": "Only about 16 GWh/y of this 130 GWh/y is documented (district heat and domestic heating). The rest covers warm-water production and summer venting, for which no figures are available. Its size depends mainly on the drying steam, which is known only as 80–110 t/h; at 110 t/h it falls to about 60 GWh/y."',
    sources=['dh_export_2023', 'dh_2019', 'pm_steam_2025', 'steam_pm_2019']),
 'dec:effluent': dict(
    title='Effluent temperature: 32 °C, and one value everywhere',
    verdict='Fix (consistency)',
    draft='Table 2 uses 32 °C (wastewater heat 212 GWh), but the exergy table in 5.3 and Appendix A use 35 °C. Table 2 gives the range as 110–212 GWh, section 6.4 as 125–214.',
    check=f'At 32 °C the model gives {g(b["sink_water"],1)} GWh. The Monte Carlo with the draft\'s own distribution, triangular(20, 32, 32), gives P5–P95 {p5p95("Heat to effluent water")} GWh. That confirms the 125–214 in section 6.4.',
    why=['The source is the 2019 answer: "Roughly 32 degrees most of the time. During longer shut downs temp can drop down to approx 20 degrees." The question asked for the difference to the sea, but the answer reads more naturally as the effluent temperature itself. An effluent "dropping to 20 degrees" during a shutdown makes sense as a temperature. An effluent 32 K above the sea would be near 50 °C in summer, too hot for the biological treatment plant. So 32 °C, as in Table 2, is the right reading.',
         'The draft\'s triangular(20, 32, 32) is well justified: 32 °C most of the time, falling toward 20 °C in long stops, and 2023 had many stops (price-driven stops, the MBBR outage in June–August).',
         'The 35 °C in the exergy table and Appendix A has no source and contradicts Table 2. 110–212 is the 20–32 °C span at one fixed volume, while 125–214 is the Monte Carlo P5–P95. The report should use the Monte Carlo range in both places, since that is what section 6 describes.'],
    report=f'Section 5.3 exergy table: change "Effluent 35 °C, 0.047" to "Effluent 32 °C, {b["f_eff"]:.3f}". Appendix A: change "Effluent temperature 35 °C" to "32 °C (about 20 °C in long shutdowns)". Table 2: change "212 (110–212)" to "212 (123–214, P5–P95)". In 6.4(c), say the range is the Monte Carlo P5–P95.',
    sources=['effluent_dT_sea_2019', 'effluent_dT_sea_shutdown_2019', 'effluent_total_2023']),
 'dec:exits': dict(
    title='Table 2: 684 GWh quantified, 769 GWh by difference',
    verdict='Keep + fix the typos',
    draft='Table 2 gives 684 quantified (47 %) and 769 by difference. Section 5.5 says 766, and the conclusions say 765.',
    check=f'The model reproduces Table 2 exactly: subtotal {g(float(EX["Subtotal, individually quantified"]["base_GWh"]),1)}, by difference {g(float(EX["Not individually quantified (by difference)"]["base_GWh"]),1)} GWh (P5–P95 {g(float(EX["Not individually quantified (by difference)"]["P5"]),0)}–{g(float(EX["Not individually quantified (by difference)"]["P95"]),0)}).',
    why=['766 and 765 are rounding slips of 769. Use 769 everywhere.',
         'One thing to state more carefully: the dryer exhaust rows (278 + 130) are not measured. They are the drying steam estimate (95 t/h) split into evaporation heat and the rest, so "individually quantified" should say "estimated individually" for those rows.',
         f'The draft already says cooling water "with a 10 K rise would carry about 50 GWh/y". Holmen\'s 2024 water balance confirms the volume: 4 Mm³/y of "cooling water and other non affected process waters". At 5–15 K that is 25–70 GWh (base {g(b["sink_cool"],0)}), which can be named as part of the 769.'],
    report='Section 5.5: "766" → "769". Conclusions: "765GWh/y" → "769 GWh/y". Table 2: add a footnote "Dryer rows are estimated from the drying steam flow, not measured." Under "Not individually quantified", add a line "of which cooling water, estimated: about 46 GWh/y (4 Mm³/y at 5–15 K; Holmen water balance 2024)".',
    sources=['img_wb_cooling', 'dh_export_2023', 'effluent_total_2023']),
 'dec:exergy-factor': dict(
    title='One steam exergy factor, and Figure 2 made consistent',
    verdict='Fix (consistency)',
    draft='The steam exergy factor appears as 0.315 (section 5.3 table), 0.318 (Figure 2 caption) and about 0.345 (hotspot table in 5.4). Figure 2 shows 1,324.8 GWh destroyed and 123.2 GWh waste heat, while the text says 1,329 and 119. Nobody could reproduce the Figure 2 values.',
    check=f'With steam counted at latent heat, the consistent factor is exergy per tonne ÷ latent heat per tonne = {ex_t*1000:.0f} ÷ {dh*1000:.0f} kWh = {b["fx_steam"]:.3f}. That is the factor the hotspot table already uses (TMP 430 × 0.344 = 148, boilers 130 × 0.344 = 45). 0.315 is the same exergy divided by the full 2.35 GJ/t heat, and 0.318 is the Carnot factor at 138 °C.',
    why=['Three factors for one quantity looks like an error to a reader, even though each has a reason. With the latent convention, 0.344 is the one that fits the steam numbers.',
         f'The model gives: of 1,450 GWh of exergy, {g(b["Xdest_total"],0)} GWh ({b["Xdest_total"]/P["E_tot"]*100:.0f} %) is destroyed, {g(X_air + b["X_eff"],0)} GWh leaves with waste heat ({g(X_air,0)} to air, {g(b["X_eff"],0)} to water at 32 °C), and {g(b["X_DH"],0)} GWh leaves as district heat. That is within 1–2 GWh of the draft text (1,329 / 119 / 2). The only real change is water, 11 → 9 GWh, because of 32 °C instead of 35 °C.',
         'Figure 2 should be redrawn from these numbers so that the figure and the text agree. The model draws it in reports/figures/model_sankey_exergy.png.'],
    report=f'Section 5.3 table: steam row "0.315" → "{b["fx_steam"]:.3f} (per unit of latent heat)". Figure 2 caption: "factor 0.318" → "factor {b["fx_steam"]:.3f}"; replace the figure with model_sankey_exergy.png. Section 5.3 text: "1,329 GWh (92 %) is destroyed inside the mill. 119 GWh leaves with waste heat (109 GWh to air, 11 GWh to water)" → "{g(b["Xdest_total"],0)} GWh (92 %) is destroyed inside the mill. {g(X_air + b["X_eff"],0)} GWh leaves with waste heat ({g(X_air,0)} GWh to air, {g(b["X_eff"],0)} GWh to water)".',
    sources=['steam_temp_2p4bar_2019']),
 'dec:pm-waste': dict(
    title='Paper-machine waste heat at 55 °C',
    verdict='Keep + support',
    draft='Section 5.3 uses 55 °C for paper-machine waste heat and section 5.4 says it "carries only 50 GWh of exergy".',
    check=f'Holmen gives paper-machine wastewater at "around 50 degrees". The rest of the paper-machine heat leaves with dryer exhaust air, which is warmer. 55 °C as a blend of the two is reasonable. The model gives {g(b["Xwaste|Paper machines"],0)} GWh of exergy at 55 °C. Scenario S9 (50 °C) changes exergy destroyed by 4 GWh.',
    why=['The value is defensible, but the report should say where it comes from, because the only source number is 50 °C.',
         f'The "50 GWh" in 5.4 comes from (218 + 408) × 0.077 = 48 GWh. The model, which excludes bleaching from the paper machines, gives {g(b["Xwaste|Paper machines"],0)} GWh. "About 50 GWh" is fine.'],
    report='Section 5.3, under the exergy table: "Paper-machine waste heat is taken at 55 °C, between the ~50 °C of the PM wastewater (Holmen) and the warmer dryer exhaust air."',
    sources=['pm_wastewater_T_2019']),
 'dec:mc': dict(
    title='Monte Carlo: show the results, not only the method',
    verdict='Add',
    draft='Section 6 describes the distributions (Table 6.2), 10,000 trials and the tornado charts, but gives no output ranges. Section 6.4 says "report how often TMP refining ranks first", but the number is not reported. Section 9.2 calls the macro results robust without a number. Two tornado charts have duplicated labels.',
    check=f'The model implements Table 6.2 exactly as written (CV 2 % electricity, CV 10 % shares renormalised, triangular steam flows, triangular(20, 32, 32) effluent, and so on). It keeps a run only if it is consistent with what is known: TMP supplies 70–90 % of the steam (Holmen), no steam flow is negative, no process destroys negative exergy, and the boilers do not deliver more steam heat than the electricity they use. {acc:.1f} % of runs pass.',
    why=['Without output ranges the reader cannot judge the claim that the results are robust. With them the claim is a measured result.',
         'Key results: TMP > paper machines > electric boilers in exergy destroyed in 100 % of accepted runs. The TMP share of steam stays at 73–81 %, inside Holmen\'s 70–90 %. The boiler share of electricity is the input that moves the savings most.',
         'The draft\'s tornado charts came from a separate script, and two of them have duplicated labels. The model\'s tornado and Spearman figures can replace them (reports/figures/model_tornado.png, model_spearman.png).'],
    report='Section 6: add a results table with base and P5–P95 for the headline results (from reports/tables/headline.csv), one sentence on the acceptance rule and rate, and "TMP refining ranks first in exergy destroyed in 100 % of accepted runs, followed by the paper machines and the electric boilers." Replace the tornado figure. Delete the leftovers "should be agreed and justified by the group" and "(or be sampled with correlation)".',
    sources=['steam_recovery_rate_2025']),
 'dec:m2': dict(
    title='Heat pump saving (Measure 2): 93–108 → 88–104 GWh/y',
    verdict='Fix',
    draft='Measure 2: "Replacing all boiler steam with a COP of 2.5–3.5 would save 93–108 GWh/y", computed as 145 − 130/COP.',
    check=f'130 GWh is the latent heat of the boiler steam. A heat pump has to deliver the full heat, including raising the feedwater from 90 °C, which is the {g(b["loss_EB"],0)} GWh the latent convention leaves out (see the boiler card). Full heat = 130 × 2.35/2.15 = {g(b["st_EB"]*dhp/dh,0)} GWh. Saving = 145 − {g(b["st_EB"]*dhp/dh,0)}/COP = {g(P["el_EB"]-b["st_EB"]*dhp/dh/2.5,0) if "el_EB" in P else g(145-b["st_EB"]*dhp/dh/2.5,0)}–{g(145-b["st_EB"]*dhp/dh/3.5,0)} GWh/y (COP 3.5 to 2.5), {g(m["M2"],0)} at COP 3.',
    why=['The draft\'s combined case already does it this way: it divides the boiler electricity, not the latent steam, by the COP. M2 and the combined case used two different conventions, and this fix makes them agree.',
         'The change is small (4 GWh) and the conclusion does not change: the heat pump still gives the largest single saving.'],
    report='Section 7, Measure 2 and the table: "93–108 GWh/y (0.21–0.24 MWh/t)" → "88–104 GWh/y (0.20–0.23 MWh/t)". Same in 7.1 and 8.3. Add the source of the COP range: Arpagaus et al. (2018).',
    sources=[]),
 'dec:season': dict(
    title='The savings assume the boilers run all year',
    verdict='Add',
    draft='Section 7 notes for Measure 1 that "the saving is smaller in summer, when steam is already in surplus and vented". Section 8.2 says the same. The table and conclusions give single values.',
    check=f'Holmen says recovered steam covers 70–90 % of need "depending on what products are being produced, maintenance shut downs...", and that surplus steam is vented "sometimes during summer months but normally not or very rarely during winter". When steam is vented, the boilers are off and no measure saves anything.',
    why=['Without monthly data we take the worst case consistent with "sometimes during summer months": three months (June–August) with no saving. That gives a lower bound of 75 % of the full-year value. The true value lies between the two.',
         f'This turns each saving into a range: M1 {g(m["M1"]*SEASON,0)}–{g(m["M1"],0)}, M2 {g(m["M2"]*SEASON,0)}–{g(m["M2"],0)}, M3 {g(m["M3"]*SEASON,0)}–{g(m["M3"],0)}, combined {g(m["M4"]*SEASON,0)}–{g(m["M4"],0)} GWh/y. The specific electricity after all measures is {(P["E_tot"]-m["M4"])/P["paper_t"]*1000:.2f}–{(P["E_tot"]-m["M4"]*SEASON)/P["paper_t"]*1000:.2f} MWh/t.',
         'The draft already names the issue for Measure 1. Applying it to all measures and putting it in the table makes the comparison fair and protects the conclusions from an obvious objection.'],
    report=f'Section 7 table: add a column "Seasonal lower bound (75 %)" next to each saving. Text: "Savings assume the electric boilers would otherwise run all year. Holmen reports occasional summer steam surplus, so a lower bound with no saving in June–August is also given." Conclusions: "about 2.98 MWh/t" → "2.98–3.05 MWh/t".',
    sources=['steam_recovery_rate_2025']),
}

# ---------------------------------------------------------------- steps
STEPS = []

STEPS.append(dict(id='start', n=0, title='Start here', blocks=[
 {'t': 'p', 'text': 'This page checks the group draft (12 October) against all the source data, step by step, in the order the calculation is built: sources, inputs, the three layers of the energy balance (electricity, steam, where the energy leaves), exergy, uncertainty and the improvement measures. The final step lists every edit the report needs, with the exact text.'},
 {'t': 'p', 'text': 'The approach: keep the draft\'s numbers and conventions wherever they can be defended, and change only what is invalid or inconsistent. A computer model of the mill was set up to use exactly the draft\'s conventions. It reproduces the draft\'s main numbers to within rounding (TMP steam 430, boiler steam 130, drying 408, Table 2 684/769, exergy destroyed 1,328 vs 1,329). Most of the draft holds up. The changes are a short list of inconsistencies and missing justifications.'},
 {'t': 'h', 'text': 'What each verdict means'},
 {'t': 'list', 'items': [
    'Keep: the draft is right as it stands.',
    'Keep + support: the draft\'s number is right, but a reader or marker could question it, so the report needs a sentence or paragraph of justification. The card gives the text.',
    'Fix: the draft has an error or an inconsistency (two values for one thing, a wrong label, a typo in a number). The card gives the correction.',
    'Add: something essential is missing, such as uncertainty results.']},
 {'t': 'h', 'text': 'How to review'},
 {'t': 'list', 'items': [
    'Go through the steps in order. Later steps use results from earlier ones.',
    'Each step has a list of checks. Each check says what to look at and how. Mark OK when you have checked and agree, Question when you want it discussed, Wrong when you can say what is wrong. Write the reason in the note.',
    'Decision cards are the places where the draft needs support or a fix. Read the argument and the evidence, then mark the card.',
    'Source quotes open under each item. The original documents are in resources/ in the repository, and every extracted value is in data/sources.csv.',
    'Marks save as you click, and everyone in the group sees them. Claude reads them back.']},
 {'t': 'h', 'text': 'The draft\'s story, confirmed'},
 {'t': 'p', 'text': f'In 2023 Hallsta bought {g(P["E_tot"],0)} GWh of electricity and used {g(P["diesel"],2)} GWh of diesel. TMP takes {g(b["el_TMP"],0)} GWh (70 %) and returns {g(b["st_rec"],0)} GWh as recovered steam ({b["TMP_rec_eff"]*100:.0f} %). The electric boilers add {g(b["st_EB"],0)} GWh of steam. Of the {g(b["st_supply"],0)} GWh supply, {b["rec_ratio"]*100:.0f} % comes from TMP, inside Holmen\'s stated 70–90 %. Drying uses {g(b["st_PM"],0)} GWh. Of the energy leaving the mill, 684 GWh can be estimated individually and 769 GWh is found by difference. In exergy terms {g(b["Xdest_total"],0)} GWh (92 %) is destroyed, most in TMP refining, then the paper machines and the electric boilers, an order that holds in every accepted Monte Carlo run. The measures could save {g(m["M4"]*SEASON,0)}–{g(m["M4"],0)} GWh/y together.'},
 {'t': 'headline'},
 {'t': 'h', 'text': 'Legend'},
 {'t': 'list', 'items': [
    'Data classes: A = official 2023 report (Miljörapport). B = Holmen\'s own recent answer (2025). C = older (2019) or indirect data, or derived. D = our assumption, no source.',
    'P5–P95: the range that contains 90 % of the accepted Monte Carlo runs.',
    'GWh/y: gigawatt-hours per year. MWh/t: megawatt-hours per tonne of paper, unless stated per tonne of pulp (ADT, air-dry tonne).']},
]))

STEPS.append(dict(id='sources', n=1, title='Sources and how conflicts were resolved', blocks=[
 {'t': 'p', 'text': 'The draft draws on six documents. Before checking numbers, it helps to know what each one is, how reliable it is and which year it describes. The draft\'s reference list describes two of them inaccurately, which is fixed in the report edits.'},
 {'t': 'table', 'cols': ['Document', 'What it is', 'Year of data', 'Used for', 'Reliability'], 'rows': [
    ['Miljörapport 2023 Hallsta', 'The mill\'s legally required environmental report to the county board (not a government statistic).', '2023, with five-year tables 2019–2023', 'Total electricity, diesel, paper and pulp production, operating days, effluent volumes, district heat, raw water, narrative on 2023', 'High (class A). Audited.'],
    ['Student questions to Holmen 2025', 'Holmen\'s written answers to this year\'s questions.', 'Recent (2024–2025). Water balance labelled 2024', 'Shares 70/15/10, TMP steam 100 t/h, drying 80–110 t/h, boiler 1.5 t/MWh, MW loads, TMP kWh/t, water balance', 'Medium (class B). Rounded estimates.'],
    ['Answers to questions (undated)', 'Holmen answers on water, TMP lines and steam.', 'Probably 2024–2025', 'Pulp temperatures, steam venting, line capacities', 'Medium. Some steam figures lack a period.'],
    ['Compiled questions to Holmen 2019', 'Answers to students in 2019. The draft cites this as "Hallsta mill steam audit 2019, unpublished technical audit report", which is not what it is.', '2019 (August 2019 meter values)', 'Steam pressure, condensate and effluent temperature, monthly line electricity', 'Medium-low (class C).'],
    ['Questions for the study visit (Answers Hallsta)', 'Answers around the 2019/2020 study visit.', '2019 (three-year average split)', '2019 split 72/22/6, district heat 2019', 'Medium-low (class C).'],
    ['Viktiga energiflöden (slide)', 'One Holmen slide of the main energy flows per tonne of paper.', 'Undated. 565 kt/yr output is above every year 2018–2023, so most likely 2015–2017', 'Cross-checks: TMP kWh/t, steam per tonne, boiler use per tonne', 'Medium. Holmen\'s figures, undated.']]},
 {'t': 'checks', 'items': [
    {'id': 'chk:src-classes', 'text': 'The reliability classes are reasonable.', 'how': 'Open two or three documents in resources/ and compare.'},
    {'id': 'chk:src-refs', 'text': 'The draft\'s reference list needs the corrections in step 9.', 'how': 'Compare "Holmen (2019) Hallsta mill steam audit" with the 2019 Q&A document in resources/.'}]},
 {'t': 'h', 'text': 'Where the sources disagree, and what the draft uses'},
 {'t': 'table', 'cols': ['Quantity', 'Values in the sources', 'Draft uses', 'Verdict and reason'], 'rows': [
    ['Electricity split', '2019 (three-year average): TMP 72, PM 22, boilers 6 %. 2025: 70, 15, 10 (+5 other). Slide: 73, 23, 4.', '2025 split', 'Keep. Closest to 2023 and the only split given with the current total. The rise in boiler share matches the Miljörapport, which says weak steam recovery raised boiler use. The 2019 split is scenario S1.'],
    ['TMP recovered steam', '100 t/h (2025). "145,000 GJ", no period (2019). "~10,000 GJ/month" (undated).', '100 t/h', f'Keep. The only value with a clear unit. 145,000 GJ per month = {g(145000*12/3600,0)} GWh/y, which is 12 % above 430 and consistent. Per year (40 GWh) or 10,000 GJ/month (33 GWh/y) is impossible for refiners using 1,000 GWh, so those must describe smaller streams.'],
    ['Drying steam', '80–110 t/h (2025). "PM\'s 155,000 GJ", no period (2019).', '95 t/h', 'Keep. Midpoint of the stated range. 155,000 GJ per month ≈ 120 t/h at 2.15 GJ/t, which points to the upper half of the range (scenario S3).'],
    ['Effluent temperature', '"Roughly 32 degrees", "approx 20 degrees" in long shutdowns (2019).', '32 °C in Table 2, 35 °C elsewhere', 'Fix: use 32 °C everywhere (step 5).'],
    ['Effluent volume', '7,288,861 m³ (2023). 7 Mm³ (2024). 13.5 m³/min = 7.1 Mm³ (2025).', '7.29 Mm³', 'Keep. Audited figure; the others agree within 4 %.'],
    ['Paper production', '444,494 t (Tabell 3). About 439,000 t implied by 1,450 GWh ÷ 3.3 MWh/t (Tabell 13).', '444,494 t', 'Keep. Tabell 13 rounds the specific consumption.'],
    ['Operating hours', 'PM11 285.3 days, PM12 314 days (Tabell 4).', '7,200 h', 'Keep + support. Weighting the two machines by their production gives 298.9 days = 7,174 h; 7,200 is that rounded. The draft says "7,200 h" without showing this.'],
    ['Steam pressure', '"Approx 2.5 bar", "2.4 bar = 138 °C" (2019).', '2.4 bar(g), 138 °C', 'Keep. Saturated steam at 138 °C is 3.4 bar absolute, so 2.4 bar is gauge pressure.'],
    ['Cooling water', '4 Mm³/y "cooling water and other non affected process waters" (2024 balance). Intake 11.05 − effluent 7.29 Mm³ (2023).', '"About 4 Mm³", 10 K gives 50 GWh (text only)', 'Keep + support: cite the 2024 balance (step 5).']]},
 {'t': 'checks', 'items': [
    {'id': 'chk:conf-split', 'text': 'Using the 2025 split for 2023 is justified.', 'how': 'Compare the three splits.'},
    {'id': 'chk:conf-steam', 'text': 'The "GJ with no period" values are rightly treated as cross-checks only.', 'how': 'Recompute 145,000 × 12 ÷ 3,600 = 483 GWh.'},
    {'id': 'chk:conf-rest', 'text': 'The other resolutions are correct.', 'how': 'Spot-check one or two against the documents.'}]},
 {'t': 'conflicts'},
]))

STEPS.append(dict(id='inputs', n=2, title='Model inputs', blocks=[
 {'t': 'p', 'text': 'Every number the model uses, with its value, the range used in the uncertainty analysis, data class and source quote. Class A and B come straight from a document. Class C are older or derived. Class D are assumptions and deserve the closest look.'},
 {'t': 'p', 'text': 'Ranges follow the draft\'s Table 6.2 wherever it states one: official figures get a normal distribution with a CV of 1–5 %, Holmen\'s shares a normal distribution with CV 10 % (renormalised to 100 %), steam flows triangular ranges, the effluent temperature triangular(20, 32, 32), and so on. Inputs Table 6.2 does not cover keep a range based on typical values.'},
 {'t': 'checks', 'items': [
    {'id': 'chk:inp-A', 'text': 'Class A values match the Miljörapport.', 'how': 'Filter to class A, open each source and compare with the PDF (Tabell 3, 4, 13, sections 5.2 and 8.3.3).'},
    {'id': 'chk:inp-B', 'text': 'Class B values match Holmen\'s answers, read with the right unit.', 'how': 'Watch MW vs MWh: wood handling, bleaching and WWTP figures are loads in MW and are multiplied by hours.'},
    {'id': 'chk:inp-D', 'text': 'Class D assumptions are reasonable, with wide enough ranges.', 'how': 'For each: is the base plausible, and would a value outside the range be believable?'}]},
 {'t': 'inputs'},
]))

el_rows = [
 ('TMP plant total', f'0.70 × {g(P["E_tot"],0)}', b['el_TMP']),
 ('  of which auxiliaries', f'150 kWh/t × {g(P["pulp_t"],0)} t ÷ 10⁶', b['el_TMP_aux']),
 ('  of which refiners', f'{g(b["el_TMP"],1)} − {g(b["el_TMP_aux"],1)}', b['el_TMP_ref']),
 ('Paper machines incl. bleaching', f'0.15 × {g(P["E_tot"],0)}', b['el_PM'] + b['el_bleach']),
 ('  of which bleaching', '3 MW × 7,200 h ÷ 1,000', b['el_bleach']),
 ('  of which paper machines', f'{g(b["el_PM"]+b["el_bleach"],1)} − {g(b["el_bleach"],1)}', b['el_PM']),
 ('Electric boilers', f'0.10 × {g(P["E_tot"],0)}', b['el_EB']),
 ('Other users', f'0.05 × {g(P["E_tot"],0)}', b['el_util'] + b['el_wood'] + b['el_wwtp'] + b['el_dist']),
 ('  of which WWTP', '2.5 MW × 8,760 h ÷ 1,000', b['el_wwtp']),
 ('  of which wood handling', '2.5 MW × 7,200 h ÷ 1,000', b['el_wood']),
 ('  of which internal grid losses', f'1 % × {g(P["E_tot"],0)}', b['el_dist']),
 ('  of which utilities (remainder)', f'{g(72.5,1)} − {g(b["el_wwtp"],1)} − {g(b["el_wood"],1)} − {g(b["el_dist"],1)}', b['el_util']),
]
s6 = [r for r in table('model_scenarios.csv') if r['scenario'].startswith('S6')][0]
STEPS.append(dict(id='electricity', n=3, title='Layer 1: where the electricity goes', blocks=[
 {'t': 'p', 'text': 'The first layer splits the 1,450 GWh of purchased electricity between its users. Holmen gives the split as rounded shares: TMP about 70 %, paper machines about 15 % (including bleaching), electric boilers about 10 %. The remaining 5 % covers everything else. For a few users Holmen gives electric loads in MW (WWTP 2.5, wood handling 2.5, bleaching 3), which are converted to energy by multiplying by running hours. What is left of the 5 % is "utilities" (pumps, compressors, lighting). This is the draft\'s Appendix B, and the model reproduces it.'},
 {'t': 'calc', 'title': 'Worked calculation (GWh/y), same as draft Appendix B', 'rows': el_rows},
 {'t': 'layer', 'id': 'bal:electricity'},
 {'t': 'checks', 'items': [
    {'id': 'chk:el-app-b', 'text': 'The calculation matches the draft\'s Appendix B.', 'how': 'Compare row by row (TMP refiners 952, auxiliaries 63, PM 196, boilers 145, WWTP 22, bleaching 22, utilities 18, wood 18, grid 15).'},
    {'id': 'chk:el-hours', 'text': 'MW loads use sensible hours.', 'how': 'WWTP runs all year (Tabell 4: 365 days), so 8,760 h. Wood handling and bleaching follow production, so 7,200 h.'},
    {'id': 'chk:el-wwtp', 'text': 'The WWTP share is plausible.', 'how': '21.9 GWh = 1.5 %. Holmen said in 2019 "about 1–1.5 %", and the plant was rebuilt with more aeration in 2020.'}]},
 {'t': 'h', 'text': 'Is 70 % for TMP right? (2,406 kWh per tonne of pulp)'},
 {'t': 'p', 'text': 'This is the most important point to support in layer 1, because TMP is 70 % of everything and the largest exergy hotspot. Holmen gave two statements in 2025 that do not fit together:'},
 {'t': 'list', 'items': [
    f'"TMP-plant uses about 70 %" of about 1.5 TWh. For 2023: 0.70 × 1,450 = {g(b["el_TMP"],0)} GWh, or {g(b["SEC_TMP"],0)} kWh per tonne of pulp (421,883 t).',
    '"Somewhere between 1,500 and 2,000 kWh/tonne is a normal energy span" for refining, plus 150 kWh/t for auxiliaries: 1,650–2,150 kWh/t, or 696–907 GWh for 2023 (48–63 % of the electricity).']},
 {'t': 'p', 'text': 'Both statements cannot describe the 2023 plant total. The draft uses 70 %, which is the right choice, but it does not say why. A marker who reads Holmen\'s answers may ask. Four pieces of evidence support 70 %:'},
 {'t': 'tmpfig'},
 {'t': 'h', 'text': 'Evidence 1: two independent plant-level figures from other years'},
 {'t': 'p', 'text': f'The Holmen slide gives 2.20 MWh of electricity into TMP per tonne of paper. Per tonne of pulp: in 2023 the mill made {pulp_paper:.3f} t of pulp per tonne of paper (421,883 ÷ 444,494), because paper also contains fillers. 2.20 ÷ {pulp_paper:.3f} = {g(slide_tmp,0)} kWh/t.'},
 {'t': 'p', 'text': f'The 2019 answer gives metered electricity for August 2019: TMP3 46,000 MWh and TMP12 38,000 MWh, together 84,000 MWh. 2019 production was 1,451 GWh ÷ 3.18 MWh/t ≈ 456,000 t of paper, or about {g(pulp19,0)} t of pulp, {g(pulp19/12,0)} t per month. 84,000 MWh ÷ {g(pulp19/12,0)} t = {g(aug19,0)} kWh/t.'},
 {'t': 'p', 'text': f'Both are plant-level figures, the same basis as the 70 % share, and both give about 2,320 kWh/t. 2023 is {(b["SEC_TMP"]/((slide_tmp+aug19)/2)-1)*100:.0f} % higher. Neither is near Holmen\'s "normal" 1,650–2,150. Limits: the slide is undated (probably 2015–2017), and August 2019 is one full-production month scaled to a year.'},
 {'t': 'h', 'text': 'Evidence 2: 2023 had specific reasons for higher use per tonne'},
 {'t': 'p', 'text': 'The Miljörapport 2023 (section 1.2.1) describes three things that all raise electricity per tonne:'},
 {'t': 'list', 'items': [
    '"...man har jobbat med åtgärder för att öka elförbrukningen i syfte att klara kvaliten" (L12). Refining on line L12 was deliberately increased to hold pulp quality.',
    '"Planerade stopp på grund av elpris bidrar till en ökad förbrukning av el per ton papper." Stops at high electricity prices raised use per tonne.',
    '"Den specifika elförbrukningen under perioder då produktionen har gått fullt har tyvärr ökat i förhållande till historiska värden." Even at full production, use per tonne was above historical levels.']},
 {'t': 'h', 'text': 'Evidence 3: what Holmen\'s "normal" range describes'},
 {'t': 'p', 'text': 'The question was the "average electricity consumption for the TMP refining stage". The answer began "Depends on the refiner, wood chip characteristics, required pulp quality". That is about a refiner line in steady operation for a typical grade. The plant\'s annual average also includes reject refining, idling, restarts after stops and harder grades, so it should sit above that range. All three plant-level figures do.'},
 {'t': 'h', 'text': 'Evidence 4: what breaks if 2,150 kWh/t is used'},
 {'t': 'p', 'text': f'Scenario S6 sets TMP to 2,150 kWh/t and keeps the other shares. The 108 GWh taken from TMP then has no consumer: "utilities and other" grows from 18 to {g(float(s6["el_util_unexplained"]),0)} GWh, 9 % of the electricity, against Holmen\'s 5 % for everything outside TMP, PM and boilers. So the 2,150 reading conflicts with Holmen\'s own split.'},
 {'t': 'decision', 'id': 'dec:tmp-share'},
 {'t': 'h', 'text': 'Suggested text for section 5.2'},
 {'t': 'copy', 'id': 'tmp:report-text', 'text': f'TMP specific electricity is {g(b["SEC_TMP"],0)} kWh per tonne of pulp (70 % of 1,450 GWh over 421,883 t). This is above the 1,500–2,000 kWh/t that Holmen describes as a normal span for refining, plus 150 kWh/t for auxiliary drives. Two independent plant-level figures, an undated Holmen energy-flow overview (about {g(round(slide_tmp,-1),0)} kWh/t) and metered line data for August 2019 (about {g(round(aug19,-1),0)} kWh/t), both give about 2,320 kWh/t. This suggests that the normal span describes refiner operation rather than the plant\'s annual average. The 2023 value is about 4 % higher, consistent with the environmental report\'s account of increased refining on line L12 to maintain pulp quality, price-driven production stops, and higher specific consumption even at full production. The 70 % share is therefore retained. Using the top of Holmen\'s normal span instead (2,150 kWh/t) would leave about 108 GWh/y with no identified consumer (sensitivity case S6).'},
]))

steam_rows = [
 ('Latent heat per tonne', '2.15 GJ/t ÷ 3.6', dh*1000, 'kWh/t'),
 ('TMP recovered steam', f'100 t/h × 7,200 h × 2.15 GJ/t ÷ 3,600', b['st_rec'], 'GWh/y'),
 ('Boiler steam', f'{g(b["el_EB"],0)} GWh × 1.5 t/MWh × 2.15 GJ/t ÷ 3.6', b['st_EB'], 'GWh/y'),
 ('Electric boiler residual (condensate heat)', f'{g(b["el_EB"],0)} − {g(b["st_EB"],1)}', b['loss_EB'], 'GWh/y'),
 ('Steam supply', f'{g(b["st_rec"],1)} + {g(b["st_EB"],1)}', b['st_supply'], 'GWh/y'),
 ('Paper-machine drying', '95 t/h × 7,200 h × 2.15 ÷ 3,600', b['st_PM'], 'GWh/y'),
 ('Distribution losses', f'4 % × {g(b["st_supply"],1)}', b['st_loss'], 'GWh/y'),
 ('Other heat uses (remainder)', f'{g(b["st_supply"],1)} − {g(b["st_PM"],1)} − {g(b["st_loss"],1)}', b['st_HW'] + b['st_wood'], 'GWh/y'),
 ('  of which wood handling', '1.5 t/h × 7,200 h × 2.15 ÷ 3,600', b['st_wood'], 'GWh/y'),
 ('Share of steam from TMP', f'{g(b["st_rec"],1)} ÷ {g(b["st_supply"],1)}', b['rec_ratio']*100, '%'),
 ('TMP electricity returned as steam', f'{g(b["st_rec"],1)} ÷ {g(b["el_TMP"],0)}', b['TMP_rec_eff']*100, '%'),
]
evap_rows = [
 ('Dry solids in paper', '444,494 t × (1 − 0.07)', dry_solids, 't/y'),
 ('Water entering the dryers', f'{g(dry_solids,0)} × (1/0.48 − 1)', water_after_press, 't/y'),
 ('Water leaving in the paper', '444,494 × 0.07', water_in_paper, 't/y'),
 ('Water evaporated', f'{g(water_after_press,0)} − {g(water_in_paper,0)}', W0, 't/y'),
 ('Heat to evaporate it', f'{g(W0,0)} t × 2.4 GJ/t ÷ 3,600', Q_evap, 'GWh/y'),
 ('Share of drying steam used for evaporation', f'{g(Q_evap,1)} ÷ {g(b["st_PM"],1)}', Q_evap/b['st_PM']*100, '%'),
]
STEPS.append(dict(id='steam', n=4, title='Layer 2: the steam loop', blocks=[
 {'t': 'p', 'text': 'Steam is made in two places. The TMP refiners turn most of their electricity into heat, and part of it is recovered as clean steam in heat-recovery units. When that is not enough, the electric boilers make the rest. All steam goes into one network. The paper-machine dryers are the main user. Smaller users are wood handling and warm-water production, and the network loses some heat. Holmen gives these flows in tonnes per hour. They are converted to energy as t/h × hours × heat per tonne.'},
 {'t': 'decision', 'id': 'dec:steam-basis'},
 {'t': 'calc', 'title': 'Worked calculation, same as draft section 5.1', 'rows4': steam_rows},
 {'t': 'decision', 'id': 'dec:boiler-residual'},
 {'t': 'layer', 'id': 'bal:steam'},
 {'t': 'h', 'text': 'Independent check of the drying steam (draft section 5.1)'},
 {'t': 'p', 'text': 'The draft checks the drying steam against the water the dryers must evaporate. The paper enters the dryers at about 48 % dry solids and leaves at 93 % (7 % moisture, Holmen). Evaporating the difference takes about 2.4 GJ per tonne of water. This is the minimum heat the dryers need, independent of the 95 t/h estimate.'},
 {'t': 'calc', 'title': 'Evaporation check (reproduces the draft: 416,700 t, 278 GWh)', 'rows4': evap_rows},
 {'t': 'p', 'text': f'{Q_evap/b["st_PM"]*100:.0f} % of the drying steam (latent heat) goes into evaporating water. The rest heats the paper web and air, leaves with hood exhaust or is lost from cylinders. Paper dryers commonly use about 1.2–1.5 tonnes of steam per tonne of water evaporated, which corresponds to 65–80 % here. The check shows 95 t/h is the right size. It cannot tell 80 from 110 t/h apart, but it rules out much less than 80.'},
 {'t': 'decision', 'id': 'dec:residual-steam'},
 {'t': 'checks', 'items': [
    {'id': 'chk:st-conv', 'text': 'The t/h to GWh conversions are correct.', 'how': 'Recompute TMP steam: 100 × 7,200 × 2.15 ÷ 3,600 = 430.'},
    {'id': 'chk:st-share', 'text': 'The 77 % share of steam from TMP agrees with Holmen.', 'how': 'Holmen 2025: "Roughly the recovery rate is about 70–90 % of the needed consumption." The draft does not mention this check; it supports the steam numbers and could be added to section 5.1.'},
    {'id': 'chk:st-evap', 'text': 'The evaporation check is correct.', 'how': 'Recompute the evaporated water from the table above.'},
    {'id': 'chk:st-loss', 'text': 'The 4 % network loss is reasonable.', 'how': 'No source. The draft cites Spirax Sarco ("below about 5 %"). Range 2–6 % in the uncertainty analysis.'}]},
]))

exits_rows = [[r['exit'], g(float(r['base_GWh']), 1), f"{float(r['share_pct']):.1f} %", f"{g(float(r['P5']),0)}–{g(float(r['P95']),0)}"] for r in table('model_exits_draft_format.csv')]
STEPS.append(dict(id='exits', n=5, title='Layer 3: where the energy leaves (draft Table 2)', blocks=[
 {'t': 'p', 'text': 'In a steady year all the energy that enters must leave, almost all of it as low-temperature heat. The draft\'s Table 2 lists the exits that can be estimated one by one and finds the rest by difference. The model reproduces Table 2 exactly and adds an uncertainty range to each row.'},
 {'t': 'table', 'cols': ['Exit route (draft Table 2)', 'GWh/y', 'Share', 'P5–P95'], 'rows': exits_rows},
 {'t': 'calc', 'title': 'Wastewater row', 'rows': [
    ('Wastewater heat', f'7,288,861 m³ × {P["cpv"]} MJ/m³K × (32 − 7) K ÷ 3,600', q_eff),
    ('Cooling water (part of the 769)', f'4,000,000 m³ × {P["cpv"]} × 10 K ÷ 3,600', b['sink_cool'])]},
 {'t': 'p', 'text': 'Why 7 °C is the reference: heat in water is counted relative to its surroundings. 7 °C is a typical annual mean for air and sea near Norrtälje and lies in Holmen\'s 2–25 °C range for incoming water. It is also the exergy dead state (step 6). The draft varies it from 5 to 10 °C in the uncertainty analysis.'},
 {'t': 'decision', 'id': 'dec:exits'},
 {'t': 'decision', 'id': 'dec:effluent'},
 {'t': 'fig', 'src': 'model_sankey_energy', 'caption': 'Energy flows at Hallsta 2023 (GWh/y), drawn by the model. It can replace Figure 1 if the group wants a figure that is generated from the same numbers as the tables.', 'id': 'bal:sankey'},
 {'t': 'checks', 'items': [
    {'id': 'chk:ex-table2', 'text': 'The table matches draft Table 2.', 'how': 'Compare row by row: 11.9, 278, 130, 212, 15, 22, 15; subtotal 684; by difference 769.'},
    {'id': 'chk:ex-water', 'text': 'The wastewater calculation is correct.', 'how': 'Recompute 7,288,861 × 4.18 × 25 ÷ 3,600.'},
    {'id': 'chk:ex-ref', 'text': '7 °C is a reasonable reference temperature.', 'how': 'Holmen gives incoming water at 2–25 °C over the year.'}]},
]))

STEPS.append(dict(id='exergy', n=6, title='Exergy: where the ability to do work is lost', blocks=[
 {'t': 'p', 'text': 'An energy balance cannot say where electricity is wasted, because energy is never lost. It only says where the heat ends up. Exergy is the part of energy that could still do useful work. Electricity is 100 % exergy, steam at 138 °C about one third, water at 32 °C almost none. The exergy analysis shows where electricity\'s work potential is destroyed, which is where efficiency gains are worth most.'},
 {'t': 'h', 'text': 'Exergy factors, consistent with the latent-heat steam numbers'},
 {'t': 'list', 'items': [
    'Electricity: 1.',
    f'Steam: one tonne of steam at 2.4 bar(g) condensing to 90 °C holds {ex_t*1000:.0f} kWh of exergy (from steam tables, relative to 7 °C). Its latent heat is {dh*1000:.0f} kWh. Factor per unit of latent heat: {b["fx_steam"]:.3f}. This is the factor to use with the draft\'s steam numbers (see the decision card below).',
    f'Warm water or waste heat cooled from T to T₀ = 280.15 K: factor = 1 − T₀ ln(T/T₀) ÷ (T − T₀). Unrecovered TMP heat at 80 °C: {b["f_TMPw"]:.3f}. Hot water 60 °C: {b["f_HW"]:.3f}. Paper-machine waste heat 55 °C: {b["f_PMw"]:.3f}. Effluent 32 °C: {b["f_eff"]:.3f}.',
    f'District heat 85/45 °C: factor at the log-mean temperature, {b["f_DH"]:.3f}.']},
 {'t': 'decision', 'id': 'dec:exergy-factor'},
 {'t': 'h', 'text': 'Worked example: the electric boilers'},
 {'t': 'calc', 'title': 'Electric boilers (GWh/y), same as draft hotspot table', 'rows': [
    ('Exergy in', 'electricity, factor 1', b['el_EB']),
    ('Useful exergy out', f'{g(b["st_EB"],1)} GWh steam × {b["fx_steam"]:.3f}', b['Xuse|Electric boilers']),
    ('Exergy destroyed', f'{g(b["el_EB"],1)} − {g(b["Xuse|Electric boilers"],1)}', b['Xdest|Electric boilers']),
    ('Exergy efficiency ψ', f'{g(b["Xuse|Electric boilers"],1)} ÷ {g(b["el_EB"],1)}', b['psi|Electric boilers']*100)]},
 {'t': 'p', 'text': 'In energy terms the boilers turn about 98 % of their electricity into steam heat. In exergy terms they destroy 69 % of what they receive, because they turn electricity, which could drive any machine, into steam that can only heat. A heat pump makes the same steam with about a third of the electricity, which is why the measures target the boilers.'},
 {'t': 'h', 'text': 'All processes (draft section 5.4)'},
 {'t': 'exergy'},
 {'t': 'p', 'text': 'The draft\'s hotspot table is consistent with these numbers: TMP 1,015 in, 148 useful, ψ 15 %; paper machines 337 in; boilers 145 in, 45 useful, ψ 31 %; hot water 42 in, 11 useful; the small users together 96; the steam network 193 in, 185 out. The improvement potential column uses IP = (1 − ψ) × (exergy in − useful out). The draft does not state this formula, and it should, with the note that IP is a ranking figure, not an achievable saving.'},
 {'t': 'p', 'text': 'Why energy and exergy rank differently. In energy terms the paper machines release the most heat (all drying steam ends as warm exhaust), ahead of TMP. In exergy terms TMP destroys far more (802 vs 290 GWh), because it takes in pure electricity and hands on only a third of it as steam, while the paper machines receive steam that is already two-thirds "spent". So the paper machines are where low-temperature heat could be recovered (preheating, district heat), while TMP and the boilers are where electricity is degraded. The draft\'s section 5.4 says this well.'},
 {'t': 'p', 'text': 'A convention to state: units that hand on no useful product in exergy terms (paper machines, bleaching, WWTP, wood handling, utilities) get ψ = 0. Turning chips into fibre and drying paper are real work, but they have no standard exergy value, so they count as destroyed. This affects ψ and IP, not the ranking by exergy destroyed. Diesel is left out of the exergy analysis: it is 0.2 % of input and powers vehicles outside the electricity–steam system. The draft should say this in one sentence.'},
 {'t': 'decision', 'id': 'dec:pm-waste'},
 {'t': 'checks', 'items': [
    {'id': 'chk:x-factor', 'text': 'One steam factor (0.344) should replace 0.315 and 0.318.', 'how': 'Check that 430 × 0.344 = 148 and 130 × 0.344 = 45, as in the draft hotspot table.'},
    {'id': 'chk:x-ip', 'text': 'The improvement-potential formula should be stated.', 'how': 'TMP: (1 − 0.146) × (1,015 − 148) = 740, as in the draft.'},
    {'id': 'chk:x-fig2', 'text': 'Figure 2 must be redrawn so it agrees with the text.', 'how': 'Draft figure: 1,324.8 destroyed, 123.2 waste. Text: 1,329 and 119.'}]},
 {'t': 'fig', 'src': 'model_sankey_exergy', 'caption': f'Exergy flows at Hallsta 2023 (GWh/y), drawn by the model with the {b["fx_steam"]:.3f} steam factor. Replacement for draft Figure 2. "Useful hot water" ({g(b["Xuse|Hot water & heating"],0)} GWh) is used in the mill and for district heat ({g(b["X_DH"],0)} GWh); apart from the district heat it ends as waste heat, which is why the text gives {g(X_air + b["X_eff"],0)} GWh of waste heat in total.', 'id': 'fig:exergy'},
]))

scen = table('model_scenarios.csv')
scen_expl = {
 'S0': 'The draft-aligned baseline.',
 'S1': 'Holmen\'s 2019 split (72/22/6). Less boiler electricity, so TMP supplies 85 % of the steam and every boiler saving shrinks.',
 'S2': 'Reference temperature 25 °C. Exergy factors shrink, more exergy counts as destroyed. Ranking unchanged.',
 'S3': 'Drying steam at the top of Holmen\'s range (110 t/h). Unallocated steam falls to about 58 GWh.',
 'S4': 'Stress test: low TMP recovery (85 t/h) and high drying steam (110 t/h). Demand exceeds supply, so these extremes cannot both be true. Such runs are filtered out.',
 'S5': 'Steam counted as full heat to 90 °C condensate (2.35 GJ/t). Steam flows +9 %. Exergy and measures unchanged.',
 'S6': 'TMP at Holmen\'s "normal" 2,150 kWh/t. 126 GWh of electricity left without a consumer (step 3).',
 'S7': 'Effluent at 39 °C (32 K above 7 °C). Moves about 60 GWh from "by difference" to wastewater.',
 'S8': 'Steam flows over 8,760 h instead of 7,200. Steam flows +22 %, TMP share 80 %.',
 'S9': 'Paper-machine waste heat at 50 °C (wastewater value). Exergy destroyed +4 GWh.',
 'S10': 'Effluent at 20 °C (long-shutdown value). Wastewater heat falls to about 110 GWh.'}
STEPS.append(dict(id='uncertainty', n=7, title='Uncertainty (draft section 6)', blocks=[
 {'t': 'p', 'text': 'The draft\'s method is sound: draw every input from its distribution (Table 6.2), recompute the balance 10,000 times, rescale the shares to 1,450 GWh in each run, and use one value of operating hours per run for all steam flows. The model implements exactly that. What the draft is missing is the results.'},
 {'t': 'p', 'text': f'One step is added: a run is kept only if it is consistent with what is known. TMP must supply 70–90 % of the steam (Holmen\'s statement), no steam flow may be negative, no process may destroy negative exergy, and the boilers may not deliver more steam heat than the electricity they use (with CV 5 % on the yield and CV 3 % on the latent heat, a few raw draws exceed 100 %). {acc:.1f} % of runs pass.'},
 {'t': 'decision', 'id': 'dec:mc'},
 {'t': 'h', 'text': 'Which inputs drive which results'},
 {'t': 'p', 'text': 'Spearman rank correlation (ρ from −1 to +1) between each random input and each result. The largest:'},
 {'t': 'list', 'items': [
    'Exergy destroyed in TMP: the TMP share (ρ +0.68) and total electricity (+0.47).',
    'Exergy destroyed in the boilers and all measure savings: the boiler share (ρ about +0.73 to +0.75), then the TMP share (about −0.56, because shares are renormalised). The boiler share is the input that matters most for the savings, and Holmen\'s 2019 and 2025 answers differ on it (6 % vs 10 %).',
    'Share of steam from TMP: boiler share (−0.61), TMP share (+0.47), TMP steam flow (+0.41).',
    'Unallocated steam: drying steam (−0.65) and TMP steam (+0.62).',
    'Heat by difference: total electricity (+0.66) and effluent temperature (−0.55).']},
 {'t': 'p', 'text': 'This supports the draft\'s plain-language reading in 6.4 (a)–(f).'},
 {'t': 'h', 'text': 'Scenarios'},
 {'t': 'scenarios', 'rows': [{'name': r['scenario'], 'el_TMP': float(r['el_TMP']), 'el_EB': float(r['el_EB']), 'rec': float(r['rec_ratio_pct']), 'stHW': float(r['st_HW']), 'air': float(r['sink_air']), 'xd': float(r['Xdest_total']), 'm4': float(r['M4_combined']), 'expl': scen_expl.get(r['scenario'].split()[0], '')} for r in scen]},
 {'t': 'checks', 'items': [
    {'id': 'chk:mc-impl', 'text': 'The model implements Table 6.2 as written.', 'how': 'Compare Table 6.2 with the ranges in step 2.'},
    {'id': 'chk:mc-filter', 'text': 'The acceptance rule is sensible.', 'how': 'Is dropping runs that contradict Holmen\'s 70–90 % statement, or produce negative flows, justified?'},
    {'id': 'chk:mc-results', 'text': 'The results table should go into section 6.', 'how': 'See the headline numbers on the "Start here" step.'}]},
]))

ms = 7200*dh/1000
meas_rows = [
 ('1 t/h of boiler steam avoided', f'7,200 h × 1 t/h ÷ 1.5 t/MWh ÷ 1,000', per_tph),
 ('M1: TMP steam +10 t/h', f'10 × {per_tph:.2f}', m['M1']),
 ('M1b: TMP to 90 % of steam', f'(0.90 × {g(b["st_supply"],1)} − {g(b["st_rec"],1)}) GWh steam ÷ {g(b["st_EB"]/b["el_EB"],3)}', m['M1b']),
 ('M2: heat pump, COP 3', f'145 − 130 × (2.35/2.15) ÷ 3 = 145 − {g(b["st_EB"]*dhp/dh,1)} ÷ 3', m['M2']),
 ('M3: press dryness 48 → 50 %', f'evaporated water {g(W0,0)} → {g(W1,0)} t (−{(1-W1/W0)*100:.2f} %); {(1-W1/W0)*100:.2f} % × 95 t/h = {(1-W1/W0)*95:.2f} t/h × {per_tph:.2f}', m['M3']),
 ('M4: M3, then M1, then heat pump', f'boiler steam left {g(m["M4_steam_left"],1)} GWh; 145 − {g(m["M4_steam_left"],1)} × (2.35/2.15) ÷ 3', m['M4']),
]
mt = {r['measure']: r for r in table('model_measures.csv')}
STEPS.append(dict(id='measures', n=8, title='Improvement measures (draft section 7)', blocks=[
 {'t': 'p', 'text': f'All measures target the electric boilers, which turn electricity into steam at 31 % exergy efficiency. One tonne per hour of boiler steam avoided saves 7,200 h ÷ 1.5 t/MWh = {per_tph:.1f} GWh of electricity a year. The boilers make about 30 t/h, so the measures together can never save more than 145 GWh/y. The draft states all of this correctly.'},
 {'t': 'calc', 'title': 'Worked calculation (GWh/y), full-year values', 'rows': meas_rows},
 {'t': 'p', 'text': 'M1, M3 and the combined case reproduce the draft exactly (48, 37.7, 125.6 ≈ 126). M2 differs by 4 GWh (decision card below). M1b, raising TMP\'s share of steam to 90 %, the top of Holmen\'s range, is shown for reference.'},
 {'t': 'measures', 'rows': [{'id': 'mea:' + k, 'desc': mt[k]['description'], 'base': float(mt[k]['base_GWh']), 'p5': float(mt[k]['P5_GWh']), 'p95': float(mt[k]['P95_GWh']), 'season': float(mt[k]['base_GWh'])*SEASON, 'mwh_t': float(mt[k]['base_MWh_t']), 'sec': float(mt[k]['base_newSEC_MWh_t'])} for k in ['M1', 'M1b', 'M2', 'M3', 'M3b', 'M4']]},
 {'t': 'decision', 'id': 'dec:m2'},
 {'t': 'decision', 'id': 'dec:season'},
 {'t': 'fig', 'src': 'model_measures', 'caption': 'Electricity saved per measure, full-year values, base case with P5–P95 whiskers.'},
 {'t': 'p', 'text': 'Two more points the draft gets right and should keep: higher press dryness can reduce paper bulk, which matters for book paper, and a heat pump reduces the mill\'s ability to switch load quickly. The Miljörapport confirms the second: Hallsta earns money by offering demand flexibility to the grid, and electric boilers can start and stop fast.'},
 {'t': 'checks', 'items': [
    {'id': 'chk:m-calc', 'text': 'The worked calculations are correct.', 'how': 'Recompute M1 and M2.'},
    {'id': 'chk:m-m2', 'text': 'The M2 correction is right.', 'how': 'Does a heat pump have to supply the condensate heat as well as the latent heat?'},
    {'id': 'chk:m-season', 'text': 'The 75 % seasonal lower bound is fair.', 'how': 'Holmen: venting "sometimes during summer months but normally not or very rarely during winter".'}]},
]))

STEPS.append(dict(id='limits', n=9, title='Limitations the report must state', blocks=[
 {'t': 'p', 'text': 'No more data will come from Holmen, so every open point is decided with the existing sources. Section 9.3 of the draft ends mid-sentence ("Insufficient monitoring data for the secondary metering points in the factory"). These are the points to state there, each with how the analysis handles it and whether it could change a conclusion.'},
 {'t': 'limits', 'items': [
    {'id': 'lim:tmp', 'title': 'The 2023 TMP share is an estimate', 'text': 'Holmen\'s 70 % share and its "normal" refining range disagree. 70 % is kept, supported by two independent plant-level figures (step 3). Could it change a conclusion? Not the ranking: TMP is first in every case.'},
    {'id': 'lim:steam', 'title': 'Steam flows are rounded estimates', 'text': 'TMP recovery (100 t/h) and drying (80–110 t/h) are Holmen estimates, not meter readings. The remainder of the steam balance (about 130 GWh) has only about 16 GWh of documented uses. This changes the size of the remainder but not the hotspots or the measures.'},
    {'id': 'lim:boiler', 'title': 'The boiler share drives every saving', 'text': 'Holmen gives 6 % (2019) and 10 % (2025). The savings scale roughly with it. The order of the measures does not change.'},
    {'id': 'lim:season', 'title': 'The model is annual and steady-state', 'text': 'Summer venting, winter peaks, stops and price-driven load shifting are not modelled. Savings are therefore given between a seasonal lower bound (75 %) and a full-year upper bound.'},
    {'id': 'lim:diff', 'title': '53 % of the outflow is found by difference', 'text': 'There are no exhaust-air or cooling-water temperature measurements. Cooling water probably carries 25–70 GWh of the 769.'},
    {'id': 'lim:temps', 'title': 'Some temperatures come from 2019', 'text': 'The effluent temperature (32 °C) and condensate temperature (90 °C) date from before the 2020 treatment-plant rebuild.'},
    {'id': 'lim:cop', 'title': 'The heat pump COP comes from a literature review', 'text': 'COP 2.5–3.5 for an 80 → 138 °C lift is based on Arpagaus et al. (2018). M2 is indicative.'},
    {'id': 'lim:vintage', 'title': 'Data come from different years', 'text': 'Core 2023 data come from the Miljörapport. The electricity split and steam flows are Holmen answers from 2025, and some temperatures from 2019. 2023 was an unusual year (stops, the MBBR failure, the L12 quality problem).'}]},
]))

# ---------------------------------------------------------------- report edits (also written to docs/review/report_edits.md)
REPORT_EDITS = [
 # (section, type, current, new, why)
 ('1 Introduction', 'Fix', '"The pulp and building industry is one of Sweden\'s biggest industrial electricity users"', '"The pulp and paper industry is one of Sweden\'s biggest industrial electricity users"', 'Typo.'),
 ('1 Introduction', 'Fix', '"...supports Sweden\'s national electrification goals (Holmen Q&A, 2025)"', '"...supports Sweden\'s national electrification goals (Swedish Government, 2022)"', 'A policy claim needs the policy source, not the mill Q&A.'),
 ('3.3 System boundary', 'Add', '(end of section)', '"Energy in the wood raw material and in the bark sold as fuel (about 204 GWh in 2023) is outside the scope; the analysis follows purchased electricity and diesel."', 'A reader will ask where the wood energy is. One sentence closes it.'),
 ('3.4 Reference year', 'Fix', '"The most recent year with comprehensive government statistics is 2023 (Holmen, 2023)."', '"2023 is the most recent year covered by the mill\'s environmental report (Holmen Paper, 2024)."', 'The Miljörapport is a company report to the authority, not a government statistic.'),
 ('3.4 Reference year', 'Add', '(after the first paragraph)', '"2023 was not a typical year: production (444 kt) was the second lowest of 2019–2023 and specific electricity use (3.26 MWh/t) the highest, because of price-driven and market-related stops, a three-month outage of the biological treatment stage and increased refining for pulp quality on line L12 (Miljörapport 2023, section 1.2.1). Specific figures are therefore somewhat above a typical year."', 'Supported by the EDA; protects the per-tonne results.'),
 ('3.4 Reference year', 'Add', '"The model is annualised using 7,200 operational hours"', '"...7,200 operational hours (the production-weighted running time of PM11 and PM12 in 2023, 7,174 h, rounded; Miljörapport Table 4)"', 'Shows where 7,200 comes from.'),
 ('3.4 Limitations', 'Fix', '"...taken into qualitative consideration by the screening LCA [check with Miao]."', 'Delete "[check with Miao]".', 'Draft leftover.'),
 ('4.1 Data sources', 'Add', '(end of section)', '"Electricity shares and steam flows are Holmen\'s estimates given in 2025 and applied to 2023; some temperatures date from 2019. Where sources disagree, the value used and the reason are listed in Appendix A."', 'States the data vintage.'),
 ('4.3 Steam', 'Fix', '"post-dryer paper moisture of 48%"', '"post-press dryness of 48% (final moisture 7%)"', '48 % is the dryness after the press, not the moisture after the dryer.'),
 ('4.3 Steam', 'Add', '(end of section)', DECISIONS['dec:steam-basis']['report'].split(': ', 1)[1], 'Makes the steam convention explicit.'),
 ('4.4 Exergy', 'Fix', 'Table 1: "Ex - mCp[...]", "law value heat", "nex"', '"Ex = mcp[(T − T0) − T0 ln(T/T0)]", "low-value heat", "ηex"', 'Typos.'),
 ('4.4 Exergy', 'Add', '(end of section)', '"Diesel (0.2 % of the energy input, used by vehicles) is included in the energy balance but not in the exergy analysis."', 'Explains why diesel is missing from Figure 2.'),
 ('4.5 / 6.3', 'Fix', '"each trail", "fulling independent", "There are around 10,000 trials", "should all share one sampled value each trial (or be sampled with correlation)", Table 6.2 footnote "should be agreed and justified by the group"', '"each trial", "fully independent", "10,000 trials are performed", "share one sampled value in each trial", delete the footnote sentence', 'Typos and draft leftovers.'),
 ('5.1 Energy', 'Fix', '"Ein = Eout + Ecirculating"', '"Ein = Eout (steady state; steam circulating inside the mill is an internal flow)"', 'Internal flows do not appear in the external balance.'),
 ('5.1 Electric boilers', 'Fix', '"The electric boilers provide steam when recovered TMP steam is sufficient."', '"...when recovered TMP steam is insufficient."', 'Reverses the meaning.'),
 ('5.1 Electric boilers', 'Fix', '"Based on this there is 15 GWh/y as boiler residual." / Table 2 "Electric boiler losses"', DECISIONS['dec:boiler-residual']['report'].split(': ', 1)[1], 'Electric boilers are about 98 % efficient; 15 GWh is condensate heat, not a loss.'),
 ('5.1 PM drying', 'Fix', '"Homen using Valmet", "At 100C normal boiling point, hevap = 2.4 Gj/t water"', '"Holmen uses Valmet", "With hevap ≈ 2.4 GJ/t water (evaporation at about 100 °C including heating)"', 'Typos and units.'),
 ('5.1 Steam supply', 'Add', '(after "excess steam may be released during summer...")', DECISIONS['dec:residual-steam']['report'].split(': ', 1)[1], 'Says how uncertain the 130 GWh is.'),
 ('5.1 Steam supply', 'Add', '(after "estimated steam supply is approximately 560 GWh/y")', '"TMP thus supplies 77 % of the steam, within the 70–90 % recovery rate Holmen reports, which supports the estimated flows."', 'Independent check the draft does not use.'),
 ('Table 2', 'Fix', '"212 (110–212)"', '"212 (123–214)" with a footnote "P5–P95 from the Monte Carlo analysis (section 6)"', 'Same range as 6.4.'),
 ('Table 2', 'Add', '(footnote and under "Not individually quantified")', DECISIONS['dec:exits']['report'].split('Table 2: ', 1)[1], 'The dryer rows are estimates; cooling water is now sized.'),
 ('5.2 SEC', 'Add', '(new paragraph)', 'The "Suggested text for section 5.2" in step 3.', 'Answers the obvious question about Holmen\'s 1,500–2,000 kWh/t.'),
 ('5.3 Exergy', 'Fix', 'Steam row "0.315"; effluent row "35 °C, 0.047"', f'"{b["fx_steam"]:.3f} (per unit of latent heat)"; "32 °C, {b["f_eff"]:.3f}"', 'One steam factor, consistent with the latent-heat steam numbers; one effluent temperature.'),
 ('5.3 Exergy', 'Fix', '"1,329 GWh (92%) is destroyed inside the mill. 119 GWh leaves with waste heat (109GWh to air, 11GWh to water)"', f'"{g(b["Xdest_total"],0)} GWh (92 %) is destroyed inside the mill. {g(X_air + b["X_eff"],0)} GWh leaves with waste heat ({g(X_air,0)} GWh to air, {g(b["X_eff"],0)} GWh to water)"', 'Consistent with 32 °C effluent.'),
 ('5.3 Exergy', 'Add', '(under the exergy table)', DECISIONS['dec:pm-waste']['report'].split(': ', 1)[1], 'The only source value is 50 °C.'),
 ('5.4 Hotspots', 'Add', '(under the hotspot table)', '"Improvement potential IP = (1 − ψ)(Exin − Exuseful); it ranks where exergy is lost, it is not an achievable saving. Units without a useful exergy output (paper machines, bleaching, WWTP, wood handling) have ψ = 0 by convention."', 'States the formula and the convention.'),
 ('5.5 Figure 1', 'Fix', '"The remaining 766 GWh/y (53%)"', '"The remaining 769 GWh/y (53 %)"', 'Same number as Table 2.'),
 ('5.5 Figure 2', 'Fix', 'Figure 2 (1,324.8 destroyed, 123.2 waste) and caption "factor 0.318"', f'Replace with reports/figures/model_sankey_exergy.png; caption: factor "{b["fx_steam"]:.3f}", and add "Useful hot water ({g(b["Xuse|Hot water & heating"],0)} GWh) is used in the mill and for district heat ({g(b["X_DH"],0)} GWh); apart from the district heat it also ends as waste heat."', 'Figure and text must agree.'),
 ('6 Uncertainty', 'Add', '(new subsection 6.5 Results)', DECISIONS['dec:mc']['report'], 'The draft gives no output ranges.'),
 ('6.4 (c)', 'Fix', '"the loss could be anywhere from about 125 to 214 GWh/y"', '"the loss lies between about 123 and 214 GWh/y (P5–P95)"', 'Matches Table 2.'),
 ('7 Measures', 'Fix', 'Measure 2 "93–108 GWh/y (0.21–0.24 MWh/t)" (text, table, 7.1, 8.3)', '"88–104 GWh/y (0.20–0.23 MWh/t)"', DECISIONS['dec:m2']['why'][0]),
 ('7 Measures', 'Add', '(text and table)', DECISIONS['dec:season']['report'], 'Every saving assumes the boilers run all year.'),
 ('7 Measures', 'Add', 'Measure 2: "A high-temperature heat pump could upgrade waste heat..."', 'Add the source of the COP range: "(Arpagaus et al., 2018)".', 'COP range needs a citation.'),
 ('7 Measures', 'Add', 'Measure 3: "This saves about 7.9 t/h of steam"', '"This saves about 7.9 t/h of steam, assuming drying steam scales with the water evaporated (counting only the evaporation heat gives about 5 t/h)"', 'States the assumption behind 7.9 t/h.'),
 ('9.3 Limitations', 'Fix', '"Insufficient monitoring data for the secondary metering points in the factory" (sentence ends)', 'Replace with the limitation list in step 9.', 'Incomplete sentence; limitations are a marking point.'),
 ('10 Conclusions', 'Fix', '"more than half of the energy outflow (765GWh/y)"', '"more than half of the energy outflow (769 GWh/y)"', 'Same number as Table 2.'),
 ('10 Conclusions', 'Fix', '"Improvement scenarios and preliminary screening-level LCA were also assessed"', 'Keep, but in the LCA sentence say "a qualitative screening LCA"', 'Section 8.1 says no quantitative LCA was done.'),
 ('10 Conclusions', 'Fix', '"could reduce electricity consumption to approximately 2.98 MWh/t paper"', f'"could reduce specific electricity use from 3.26 to {(P["E_tot"]-m["M4"])/P["paper_t"]*1000:.2f}–{(P["E_tot"]-m["M4"]*SEASON)/P["paper_t"]*1000:.2f} MWh/t"', 'Seasonal range.'),
 ('12 References', 'Fix', '"Holmen. (2019). Hallsta mill steam audit 2019. Unpublished technical audit report."', '"Holmen Paper AB (2019). Answers to compiled student questions, Hallsta paper mill. Personal communication."', 'The source is a Q&A, not an audit report.'),
 ('12 References', 'Fix', '"Holmen. (2023). Sustainability and environmental report 2023. Holmen Group."', '"Holmen Paper AB (2024). Miljörapport 2023, Hallsta pappersbruk. Annual environmental report."', 'All 2023 data come from the mill\'s Miljörapport.'),
 ('12 References', 'Add', '(new entries)', '"Arpagaus, C., Bless, F., Uhlmann, M., Schiffmann, J. and Bertsch, S.S. (2018). High temperature heat pumps: Market overview, state of the art, research status, refrigerants, and application potentials. Energy, 152, 985–1010." Also the 2025 Q&A, the study-visit answers and the Viktiga energiflöden slide as personal communication.', 'Cited sources must be listed.'),
 ('12 References', 'Fix', 'Morris et al. "(Accessed: 4 October 2026)"; Spirax Sarco URL "?utm_source"', 'Remove "Accessed" for the printed book; remove "?utm_source" from the URL.', 'Citation format.'),
 ('Appendix A', 'Fix', '"Effluent temperature 35 °C, Holmen 2019 (32 K above sea)"', '"Effluent temperature 32 °C (about 20 °C in long shutdowns), Holmen 2019"', 'Same as Table 2.'),
 ('Appendix A', 'Add', '(new rows)', '"Cooling water 4 Mm³/y, Holmen water balance 2024"; "Steam recovery rate 70–90 % of need, Holmen 2025"', 'Sources used in the text.'),
 ('New 4.2 Data screening', 'Add', '(new short section, about one page)', 'The EDA figures (eda_context, eda_electricity_split, eda_tmp_steam, eda_water_heat) with captions from reports/tables/eda_report_map.csv.', 'Shows the data were screened; supports 3.4, 5.1 and 5.2.'),
]
