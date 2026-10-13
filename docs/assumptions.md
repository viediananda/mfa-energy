# Assumptions register and modelling decisions

Source ids refer to `data/sources.csv`. Data classes: A measured 2023, B recent Holmen estimate (2025), C older (2019) or indirect, D our own assumption. The full input list with distributions is `reports/tables/model_inputs.csv` (written by `analysis/run_model.py`).

## 1. Class C/D assumptions and uncertainty ranges

Baseline aligned with the group report draft (see "Alignment with the group draft" below). Where the draft's Table 6.2 states a distribution, it is used exactly; other inputs keep their earlier ranges.

| Parameter | Base | Range (distribution) | Class | Justification | Source id |
|---|---|---|---|---|---|
| `sh_TMP`, `sh_PM`, `sh_EB`, `sh_OTH` electricity shares | 70 / 15 / 10 / 5 % | normal, CV 10 % each, renormalised to 100 % | B / D | Holmen's 2025 split; "other" is only the remainder. Draft Table 6.2. Named items (wood 2.5 MW x h_prod, WWTP 2.5 MW x 8,760 h, grid loss 1 %) are about 54 GWh = 3.75 %; with CV 10 % the other bucket is sometimes smaller, and the k-guard scales the named items down (binds in 8.7 % of runs). | el_split_*_2025 |
| `E_tot`, `diesel`, `paper_t` | 1,450 GWh, 2.82 GWh, 444,494 t | normal, CV 2 %, 5 %, 1 % | A | Draft Table 6.2. | MR2023 |
| `V_wwtp`, `V_ff` effluent volumes | MR2023 | normal, CV 2 % | A | Draft Table 6.2. | effluent_total_2023 |
| `f_dist` grid loss | 1 % | uni(0.5, 2) % | D | Holmen: "Electricity transmission losses ?" (no data). | assumption |
| `f_steamloss` steam network loss | 4 % | uni(2, 6) % | D | Holmen: "Steam distribution losses ?" (no data). | assumption |
| `dh_override` steam heat per tonne | 2.15 GJ/t (latent) | normal, CV 3 % | C | Draft convention: heat released when steam condenses at 2.4 bar(g). Property-based 2.35 GJ/t is sensitivity case S5. | steam_temp_2p4bar_2019 |
| `y_EB` boiler steam yield | 1.5 t/MWh | normal, CV 5 % | B | Holmen's yield; boiler steam = electricity x y_EB x steam heat. Draft Table 6.2. | steam_per_MW_2025 |
| `eff_EB` boiler efficiency | 0.98 | not sampled in the base | C | Used only in sensitivity case S5 (property-based). | steam_per_MW_2025 |
| `m_rec` TMP steam | 100 t/h | tri(85, 100, 115) | B | Draft Table 6.2. | tmp_steam_recycled_2025 |
| `m_PM` PM steam | 95 t/h | tri(80, 95, 110) | B | Midpoint of Holmen's 80-110 t/h; draft Table 6.2. | pm_steam_2025 |
| `h_prod` production hours | 7,200 h | tri(6800, 7200, 7800) | C | Tabell 4: production-weighted 298.9 d = 7,174 h; draft Table 6.2. One shared draw for TMP and PM steam. | pm11_days_2023, pm12_days_2023 |
| `T_eff` effluent temperature | 32 C, whole effluent | tri(20, 32, 32) | C | Source "roughly 32 degrees"; 20 C is the long-shutdown value (S10). `T_ff` is tied to `T_eff` (one draw). Draft Table 6.2. | effluent_dT_sea_2019 |
| `cpv` water heat capacity | 4.18 MJ/m3K | fixed | A | Draft value. | physical constant |
| `T_PMwaste` PM waste heat | 55 C | uni(50, 60) | C | Blend of ~50 C PM wastewater and warmer dryer exhaust air. Wastewater value alone (50 C) is S9. | pm_wastewater_T_2019 |
| `T_TMPwaste` unrecovered TMP heat | 80 C | uni(70, 100) | D | Pulp temperature before bleaching (80 C) used as heat-rejection temperature; pulp leaves refiners at 170-200 C. | pulp_T_prebleach_aq |
| `T_HW` hot water | 60 C | uni(50, 70) | D | Typical heating hot water. | assumption |
| `T_DHs`, `T_DHr` district heat | 85 / 45 C | fixed | D | Typical Swedish district heating; only affects X_DH. | assumption |
| `V_cool` cooling water | 4.0 Mm3/y | normal, sd 10 % | B | "Release of cooling water and other non affected process waters", water-balance image, 2024 data. | img_wb_cooling |
| `dT_cool` cooling-water temperature rise | 10 K | uni(5, 15) | D | **Not in any source.** Chosen as typical for once-through cooling. Drives 25-70 GWh. | assumption |
| `PM11_frac` | 14/22 | uni(0.525, 0.66) | C | August 2019 month only; the production share is 0.525. Affects only the PM line split. | el_pm11_aug2019, el_pm12_aug2019 |
| `dm_rec_M1` | 10 t/h | fixed | D | Measure definition taken from the group draft. | assumption |
| `cop_hp` | 3.0 | uni(2.5, 3.5) | C | See section 3. | Arpagaus et al. 2018 |
| `press_dry` baseline dryness | 48 % | tri(45, 48, 51) % | D | Draft Table 6.2. | assumption (group draft) |
| `d_press_dry` dryness gain | +2 points | fixed | D | Group draft (48 -> 50 %). Applied to the sampled baseline, so the range reflects only how the saving depends on the starting dryness. | assumption (group draft) |
| `h_evap` | 2.4 GJ/t water | normal, CV 2 % | D | Group draft value (evaporation plus heating); draft Table 6.2. | assumption (group draft) |
| `T0` | 7 C | uni(5, 10) | D | Annual mean surroundings; draft Table 6.2. `T_ref` (wastewater reference) is tied to the same draw. A fixed T0 = 25 C is S2. | assumption |
| 'Other' scenario factor 0.9625 | - | - | D | Scenario S1 rescales the 2019 split to leave room for the named other items. | - |

## 2. Decisions (current baseline)

1. **Steam heat basis: latent heat, 2.15 GJ/t** (0.5972 MWh/t), as in the group draft. Boiler steam = electricity x 1.5 t/MWh x 2.15 GJ/t = 129.9 GWh from 145 GWh. The 15.1 GWh difference is labelled "electric boiler residual: condensate heat not counted at latent basis"; it is not a boiler loss. Exergy per tonne of steam is kept (0.741 GJ/t), so the exergy factor is 0.344 per unit of latent heat (0.315 per unit of the full 2.35 GJ/t drop; the draft printed 0.315, 0.318 and 0.345 in different places).
2. **Effluent**: T_eff = 32 C absolute for the whole effluent (T_ff tied to T_eff), cpv 4.18 MJ/m3K, tri(20, 32, 32) C. Pre-2020 source, ambiguous between a temperature difference and an absolute value; an absolute value is more plausible for a biological WWTP.
3. **T_PMwaste** = 55 C, uni(50, 60) C: blend of ~50 C PM wastewater and warmer dryer exhaust air.
4. **Cooling water sink** V_cool = 4.0 Mm3/y, dT_cool 10 K (5-15 K, class D, flagged). `sink_air` is the residual after effluent water, cooling water and district heat. Possible double count: the second outlet FF PM2 (0.61 Mm3) may be part of the cooling stream; the sum effluent + cooling = 11.29 Mm3 versus 11.05 Mm3 raw intake (+2 %).
5. **Diesel** 2.82 GWh/y (Tabell 13) is an energy input whose heat ends in air; total input = E_tot + diesel. The exergy analysis excludes diesel: vehicles, outside the electricity-steam system, below 0.2 % of the input.
6. **Electric boiler**: steam = electricity x y_EB x steam heat (y_EB from Holmen, normal CV 5 %). The ratio steam heat / electricity (0.896 at base) is an output and must not exceed 1 (Monte Carlo acceptance condition 4).
7. **Other electricity** (audit B3): shares normal CV 10 % renormalised (draft Table 6.2). The k-guard (`min(1, OTH/named)`) is kept and counted; it binds in 8.7 % of runs because the 'other' bucket is sometimes smaller than the named small users.
8. **Monte Carlo** lives in `src/hallsta_mfa/mc.py` (`sample`, `run_mc`, seed 2023, N = 10,000). Constrained MC: accept runs with (1) TMP share of steam in 70-90 % (steam_recovery_rate_2025), (2) steam residual >= 0, (3) every Xdest >= 0 (tolerance 1e-9), (4) boiler steam heat <= boiler electricity. Acceptance 96.98 %. Headline ranges are the constrained P5/P50/P95; unconstrained columns are kept for the appendix.
9. **Tornado**: every input moved to its own P5 and P95 (scipy ppf, one convention); tied inputs move together.
10. **DIST** has one copy (`hallsta_mfa.model.DIST`, tied draws in `TIED`); the notebook imports it.
11. **Plotly static export** is wrapped in try/except (no Chrome needed to execute); the Sankey is always also written as HTML.
12. **TMP specific energy** (audit S1): SEC_TMP 2,406 kWh/t is in the cross-check table against Holmen's 1,500-2,000 + 150 aux. Scenario S6 sets TMP electricity to 2,150 kWh/t x pulp and moves the difference to "unexplained/other". The `gap_SEC` lever is conditional on the 70 % share being right.
13. **Steam residual** (audit S5) stays a residual, labelled "Steam to hot water, heating and venting (unallocated)": 122.6 GWh at base (+ 6.5 GWh wood-handling steam = the draft's 130). The cross-check table compares it to documented uses (DH 11.9 GWh + about 4.4 GWh domestic heating, 2019). It is not plugged.
14. **Exergy convention** (Q1): units with no useful output (PM, bleaching, WWTP, wood, utilities, grid) get psi = 0 by convention; the useful exergy of "hot water" counts the whole residual steam at T_HW. psi and improvement-potential columns are convention-dependent; the top-3 ranking is not.

### Sensitivity cases (scenarios; moved out of the baseline)

| Case | What | Former status |
|---|---|---|
| S5 | Property-based steam: 2.35 GJ/t to 90 C condensate, boiler efficiency 0.98 (`PROPERTY_BASED`). Boiler steam 142.1 GWh, unallocated steam 134.1 GWh, exergy destroyed 1,328.6 GWh. M1-M4 unchanged (within 0.03 GWh). | Previous baseline (decision 1) |
| S7 | Effluent 39 C (32 K above 7 C), whole effluent. | Alternative reading of the 2019 source |
| S9 | PM waste heat 50 C (PM wastewater value). | Previous baseline (T_PMwaste) |
| S10 | Effluent 20 C (long-shutdown value). | New |
| S1-S4, S6, S8 | 2019 split, T0 = 25 C, PM steam 110 t/h, stress case, TMP at normal SEC, 8,760 h. | Unchanged |

## Alignment with the group draft

Kept from the draft (12 Oct 2026) and why:

- **Latent-heat steam basis (2.15 GJ/t).** Counts the heat released on condensation. The sensible heat of the condensate (138 -> 90 C, about 0.20 GJ/t) is then a residual at the source. Both conventions give the same exergy per tonne and the same measure savings, so the choice is bookkeeping; the draft's basis keeps the report and the model on the same numbers.
- **Boiler steam from Holmen's 1.5 t/MWh** (130 GWh), rather than a derived efficiency; it is Holmen's own figure.
- **Effluent 32 C for the whole effluent, cpv 4.18.** One source value, one temperature; T_ff tied to T_eff.
- **PM waste heat 55 C.** Blend of PM wastewater (~50 C) and warmer dryer exhaust air.
- **Table 6.2 distributions** wherever the draft states one (see section 1).
- **Table 2 exit structure** (684 GWh quantified, 769 by difference, P5-P95) in `reports/tables/model_exits_draft_format.csv`.

Deliberate deviations:

- **M2 heat-pump convention.** The heat pump must supply the full steam enthalpy (2.35 GJ/t, `dh_prop`), because it also has to heat the feedwater from 90 C. M2 = 97.6 GWh (88-104 for COP 3.5-2.5) instead of the draft's 101.7 (93-108), which divided only the latent boiler steam (130) by the COP, whereas the draft's combined case divides boiler electricity. M1 (48.0), M3 (37.7) and M4 (125.6) match the draft.
- **Monte Carlo acceptance conditions.** A fourth condition (boiler steam heat <= boiler electricity) is added; with the draft's yield and latent heat distributions a boiler could otherwise create energy.
- **Cooling water inside the 769.** The 46 GWh cooling-water estimate is shown as an "of which" line inside the by-difference exit, not added to the quantified subtotal, because its temperature rise is a class-D assumption.
- **Steam exergy factor.** One value (0.344 relative to latent heat) is used throughout; the draft printed 0.315, 0.318 and 0.345.

## 3. Heat-pump COP (measure M2)

Source: Arpagaus, C., Bless, F., Uhlmann, M., Schiffmann, J., Bertsch, S. S. (2018). *High temperature heat pumps: Market overview, state of the art, research status, refrigerants, and application potentials.* Energy 152, 985-1010. DOI 10.1016/j.energy.2018.03.166. https://ideas.repec.org/a/eee/energy/v152y2018icp985-1010.html

The review covers heat sink temperatures of 90-160 C. For sinks near 120 C it reports COP of about 5.7-6.5 at a temperature lift of 30 K and 2.2-2.8 at 70 K; commercial units reach COP 2.4-5.8 over lifts of 40-95 K. Lifting ~80 C waste heat to 138 C steam is a lift of about 58 K, and generating steam from 90 C condensate needs extra work, and the 138 C sink is hotter than the 120 C quoted. Interpolating the quoted pairs gives about 3.3-3.9 at 58 K and 120 C, reduced here for the hotter sink and steam generation. **Range used: uniform 2.5-3.5, base 3.0.** This is a judgement inside a sourced bracket (class C), not a quoted value. The group draft used the same 2.5-3.5. Not checked: that enough 80 C waste heat is available at the right times.

## 4. Measures: conventions and caveats

- Boilers are the marginal steam source, so every steam saving first displaces boiler steam; total displaced steam is capped at the boiler steam `st_EB`. Electricity saved = steam displaced / (steam heat per MWh of boiler electricity, 0.896 at base).
- Heat pumps (M2, M4) supply the full steam enthalpy (`dh_prop`/`dh` = 1.095 times the latent boiler steam), see "Alignment with the group draft". M1-M4 are the same under both steam conventions.
- M3 variant (a) (dryer steam proportional to evaporated water) is the base; variant (b) (evaporation heat only, 2.4 GJ/t) is the low bound. Dry solids = paper_t x 0.93 (final moisture 7 %, paper_water_aq).
- M4 is sequential: M3 first (demand cut), then M1, then a heat pump on the remaining boiler steam; the saving is EB - steam_left x (dh_prop/dh)/COP.
- Savings are **annual upper bounds**: they assume the boilers run all year. Holmen's recovery of 70-90 % of need means boilers run less in some periods. The constrained MC (rec_ratio 70-90 %) bounds the effect, and the ranges in `model_measures.csv` come from it.
