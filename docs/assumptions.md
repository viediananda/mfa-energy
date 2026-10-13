# Assumptions register and modelling decisions

Source ids refer to `data/sources.csv`. Data classes: A measured 2023, B recent Holmen estimate (2025), C older (2019) or indirect, D our own assumption. The full input list with distributions is `reports/tables/model_inputs.csv` (written by `analysis/run_model.py`).

## 1. Class C/D assumptions

| Parameter | Base | Range (distribution) | Class | Justification | Source id |
|---|---|---|---|---|---|
| `sh_OTH` other users share | 5 % | tri(4, 5, 7) % | D | Remainder of Holmen's 70/15/10 split; not stated by Holmen. Named items (wood 2.5 MW x h_prod, WWTP 2.5 MW x 8,760 h, grid loss 1 %) are about 54 GWh = 3.75 %, so the lower end is set just above that. | assumption |
| `f_dist` grid loss | 1 % | uni(0.5, 2) % | D | Holmen: "Electricity transmission losses ?" (no data). | assumption |
| `f_steamloss` steam network loss | 4 % | uni(2, 6) % | D | Holmen: "Steam distribution losses ?" (no data). | assumption |
| `T_TMPwaste` unrecovered TMP heat | 80 C | uni(70, 100) | D | Pulp temperature before bleaching (80 C) used as heat-rejection temperature; pulp leaves refiners at 170-200 C. | pulp_T_prebleach_aq |
| `T_PMwaste` PM waste heat | 50 C | uni(45, 60) | C | Source: PM wastewater "around 50 C". Applied to all PM waste heat, which is a simplification (dryer exhaust is warmer and partly reused). | pm_wastewater_T_2019 |
| `T_HW` hot water | 60 C | uni(50, 70) | D | Typical heating hot water. | assumption |
| `T_DHs`, `T_DHr` district heat | 85 / 45 C | fixed | D | Typical Swedish district heating; only affects X_DH. | assumption |
| `T_eff` effluent | 35 C absolute | uni(30, 40) | D | See decision 2. | effluent_dT_sea_2019 |
| `T_ff` second outlet FF PM2 | 30 C | uni(20, 40) | D | No data. | assumption |
| `V_cool` cooling water | 4.0 Mm3/y | normal, sd 10 % | B | "Release of cooling water and other non affected process waters", water-balance image, 2024 data. | img_wb_cooling |
| `dT_cool` cooling-water temperature rise | 10 K | uni(5, 15) | D | **Not in any source.** Chosen as typical for once-through cooling. Drives 25-70 GWh. | assumption |
| `eff_EB` electric boiler efficiency | 0.98 | tri(0.95, 0.98, 0.995) | C | Holmen: 1.5 t steam/MWh; implied yield eff/dh = 1.50 at base. Upper end below 1 for physical reasons. | steam_per_MW_2025 |
| `m_PM` PM steam | 95 t/h | uni(80, 110) | B | Midpoint of Holmen's 80-110 t/h. | pm_steam_2025 |
| `h_prod` production hours | 7,200 h | tri(6800, 7200, 7600) | C | Tabell 4: PM11 285.3 d, PM12 314 d; production-weighted (233,453 t, 211,041 t) 298.9 d = 7,174 h. One shared draw per run for TMP and PM steam (TMP lines follow PM demand per Holmen). | pm11_days_2023, pm12_days_2023 |
| `PM11_frac` | 14/22 | uni(0.525, 0.66) | C | August 2019 month only; the production share is 0.525. Affects only the PM line split. | el_pm11_aug2019, el_pm12_aug2019 |
| `dm_rec_M1` | 10 t/h | fixed | D | Measure definition taken from the group draft. | assumption |
| `cop_hp` | 3.0 | uni(2.5, 3.5) | C | See section 3. | Arpagaus et al. 2018 |
| `press_dry` baseline dryness | 48 % | tri(45, 48, 51) % | D | Group draft; Sec 4.3/5.1. | assumption (group draft) |
| `d_press_dry` dryness gain | +2 points | fixed | D | Group draft (48 -> 50 %). Applied to the sampled baseline, so the range reflects only how the saving depends on the starting dryness, not a varying target. | assumption (group draft) |
| `h_evap` | 2.4 GJ/t water | fixed | D | Group draft value (evaporation plus heating). | assumption (group draft) |
| `T0`, `T_ref` | 7 C | fixed (not sampled) | D | Annual mean surroundings; the T0 effect is shown as scenario S2. | assumption |
| 'Other' scenario factor 0.9625 | - | - | D | Scenario S1 rescales the 2019 split to leave room for the named other items. | - |

## 2. Decisions made by the reviewer (implemented as given)

1. **Steam heat basis** stays property-based: saturated steam at 3.4 bar abs (2.4 bar(g), 138 C) condensed to 90 C condensate, 0.6537 MWh/t (2.35 GJ/t). Scenario S5 uses latent heat only, 2.15 GJ/t (`dh_override`; the exergy per tonne is kept, so the exergy factor scales).
2. **Effluent** T_eff = 35 C absolute, uniform 30-40 C. The 2019 source ("roughly 32 degrees") is ambiguous between a temperature difference to the sea and an absolute value, pre-dates the 2020 WWTP rebuild, and an absolute 32-35 C is physically more plausible for a biological WWTP. Scenario S7 reads it as 32 K above 7 C = 39 C.
3. **T_PMwaste** = 50 C (source), range 45-60 C (audit S3).
4. **Cooling water sink** V_cool = 4.0 Mm3/y, dT_cool 10 K (5-15 K, class D, flagged). `sink_air` is the residual after effluent water, cooling water and district heat. Possible double count: the second outlet FF PM2 (0.61 Mm3) may be part of the cooling stream; the sum effluent + cooling = 11.29 Mm3 versus 11.05 Mm3 raw intake (+2 %).
5. **Diesel** 2.82 GWh/y (Tabell 13) is an energy input whose heat ends in air; total input = E_tot + diesel. The exergy analysis excludes diesel: vehicles, outside the electricity-steam system, below 0.2 % of the input.
6. **Electric boiler**: efficiency is sampled directly (no 0.995 clip); the implied yield eff/dh is an output, cross-checked against 1.5 t/MWh (audit B2).
7. **Other electricity** (audit B3): sh_OTH tri(4.5, 5, 7) %. The named items (wood, WWTP, grid loss) are about 3.75 % at base, so the lower bound sits just above them. The k-guard (`min(1, OTH/named)`) is kept and counted; see model_changes.md for the binding rate.
8. **Monte Carlo** lives in `src/hallsta_mfa/mc.py` (`sample`, `run_mc`, seed 2023, N = 10,000). Constrained MC: accept runs with TMP share of steam in 70-90 % (steam_recovery_rate_2025), steam residual >= 0, every Xdest >= 0 (tolerance 1e-9). Headline ranges are the constrained P5/P50/P95; unconstrained columns are kept for the appendix.
9. **Tornado**: every input moved to its own P5 and P95 (scipy ppf, one convention).
10. **DIST** has one copy (`hallsta_mfa.model.DIST`); the notebook imports it.
11. **Plotly static export** is wrapped in try/except (no Chrome needed to execute); the Sankey is always also written as HTML.
12. **TMP specific energy** (audit S1): SEC_TMP 2,406 kWh/t is in the cross-check table against Holmen's 1,500-2,000 + 150 aux. Scenario S6 sets TMP electricity to 2,150 kWh/t x pulp and moves the difference to "unexplained/other". The `gap_SEC` lever is conditional on the 70 % share being right.
13. **Steam residual** (audit S5) stays a residual, labelled "Steam to hot water, heating and venting (unallocated)". The cross-check table compares it to documented uses (DH 11.9 GWh + about 4.4 GWh domestic heating, 2019). It is not plugged.
14. **Exergy convention** (Q1): units with no useful output (PM, bleaching, WWTP, wood, utilities, grid) get psi = 0 by convention; the useful exergy of "hot water" counts the whole residual steam at T_HW. psi and improvement-potential columns are convention-dependent; the top-3 ranking is not.

## 3. Heat-pump COP (measure M2)

Source: Arpagaus, C., Bless, F., Uhlmann, M., Schiffmann, J., Bertsch, S. S. (2018). *High temperature heat pumps: Market overview, state of the art, research status, refrigerants, and application potentials.* Energy 152, 985-1010. DOI 10.1016/j.energy.2018.03.166. https://ideas.repec.org/a/eee/energy/v152y2018icp985-1010.html

The review covers heat sink temperatures of 90-160 C. For sinks near 120 C it reports COP of about 5.7-6.5 at a temperature lift of 30 K and 2.2-2.8 at 70 K; commercial units reach COP 2.4-5.8 over lifts of 40-95 K. Lifting ~80 C waste heat to 138 C steam is a lift of about 58 K, and generating steam from 90 C condensate needs extra work, and the 138 C sink is hotter than the 120 C quoted. Interpolating the quoted pairs gives about 3.3-3.9 at 58 K and 120 C, reduced here for the hotter sink and steam generation. **Range used: uniform 2.5-3.5, base 3.0.** This is a judgement inside a sourced bracket (class C), not a quoted value. The group draft used the same 2.5-3.5. Not checked: that enough 80 C waste heat is available at the right times.

## 4. Measures: conventions and caveats

- Boilers are the marginal steam source, so every steam saving first displaces boiler steam; total displaced steam is capped at the boiler steam `st_EB`.
- M3 variant (a) (dryer steam proportional to evaporated water) is the base; variant (b) (evaporation heat only, 2.4 GJ/t) is the low bound. Dry solids = paper_t x 0.93 (final moisture 7 %, paper_water_aq).
- M4 is sequential: M3 first (demand cut), then M1, then a heat pump on the remaining boiler steam; the saving is EB - steam_left/COP.
- Savings are **annual upper bounds**: they assume the boilers run all year. Holmen's recovery of 70-90 % of need means boilers run less in some periods. The constrained MC (rec_ratio 70-90 %) bounds the effect, and the ranges in `model_measures.csv` come from it.
