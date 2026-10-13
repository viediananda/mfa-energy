# Model changes after the audit (base case, old to new)

Old base: st_rec 470.7, st_PM 447.1, st_HW 134.1, sink_water 232.9, sink_air 1,205.3, SEC_TMP 2,405.9, save_rec90 82.5, Xdest_total 1,328.6. New base (`reports/tables/headline.csv`): st_rec 470.7, st_PM 447.1, st_HW 134.1, sink_water 232.9, sink_air 1,161.7, SEC_TMP 2,405.9, save_rec90 82.5, Xdest_total 1,333.3. Step-by-step effects were computed by toggling one change at a time.

| # | Change | Outputs that moved (base case) |
|---|---|---|
| 1 | eff_EB sampled directly, base 0.98 (was min(1.5 x dh, 0.995) = 0.9806) | st_EB 142.18 to 142.10 (-0.08); st_HW 134.14 to 134.06; save_rec90 82.50 to 82.47. Implied yield 1.499 t/MWh. In the MC the clip and the >1 efficiencies (6 % of runs) are gone. |
| 2 | T_PMwaste 55 to 50 C (audit S3) | Xwaste_total 110.10 to 105.41 (-4.69); Xdest_total 1,328.62 to 1,333.31 (+4.69). Energy flows unchanged. |
| 3 | Cooling-water sink 4.0 Mm3 x 10 K | New sink_cool 46.3 GWh; sink_air 1,205.25 to 1,158.92 (-46.3). |
| 4 | Diesel 2.82 GWh as input | sink_air +2.82 to 1,161.74; total input 1,452.82. Exergy untouched. |
| 5 | Steam residual relabelled "unallocated" | Label only. Documented-use cross-check added (134 vs 16 GWh). |
| 6 | sh_OTH tri(0.02, 0.05, 0.08) to tri(0.04, 0.05, 0.07); T_PMwaste 45-60; T_eff uni 30-40 (was 28-40); new DIST entries (diesel, V_cool, dT_cool, cop_hp, press_dry, eff_EB replaces y_EB) | MC only. k-guard binds in 3.76 % of runs (was 23 %). |
| 7 | Constrained MC (rec_ratio 70-90 %, st_HW >= 0, Xdest >= 0), acceptance 99.2 % | Removes the 0.8 % of runs with negative steam residual and negative Xdest (audit B1). Headline P5 of the steam residual 35.6 GWh (unconstrained 31.7). |
| 8 | Tornado at P5/P95 for all distributions (audit Q8) | Bars comparable; M1b swing smaller than the former min-max bars. |
| 9 | Notebook DIST copy removed (N10); Sankey PNG wrapped in try/except, HTML always written | No numeric effect. |
| 10 | New cross-checks (SEC_TMP, boiler yield, steam residual, water volumes, PM electricity) and scenarios S5-S9 | S5 latent-only steam: st_rec 470.7 to 430.0, st_HW 134.3. S6 TMP at 2,150 kWh/t: el_util 18 to 126 GWh, Xdest_TMP 806 to 710, Xdest_total 1,345. S7 effluent 39 C: sink_water +31. |
| 11 | New `measures.py` (M1, M1b, M2, M3, M3b, M4) | Base: 48.0, 82.5, 97.6, 37.7 (23.4 low bound), 125.6 GWh/y. M3 and M4 reproduce the group draft (37.7 and 125.6). M2 is 97.6 at COP 3.0, 4.1 below the draft's 145 - 130/COP (101.7) because it uses boiler steam (142.1) not 130. |

## Deviation from the brief

- The k-guard binding rate with sh_OTH tri(0.04, 0.05, 0.07) is **3.76 %**, not below 1 %. The named items vary with P_wood, P_wwtp, f_dist and h_prod, so a 4 % lower bound still sometimes sits below them. A lower bound near 4.6 % would give < 1 %. The test asserts < 5 %; the reviewer should decide whether to raise the lower bound.

## 2026-10-14: baseline aligned with the group draft

The base case now follows the group report draft (12 Oct 2026). The previous property-based baseline is kept as sensitivity case S5. Nothing in the audit-driven changes above is reverted; the changes below sit on top of them.

What changed in the model:

- **Steam counted at latent heat, 2.15 GJ/t** (`dh_override`). Boiler steam = electricity x Holmen's 1.5 t/MWh (`y_EB`) x 2.15 GJ/t = 129.9 GWh. The 15.1 GWh difference to the electricity is the "electric boiler residual: condensate heat not counted at latent basis", not a boiler loss. Exergy per tonne is unchanged, so the steam exergy factor is 0.344 (per unit of latent heat).
- **Effluent 32 C for the whole effluent** (`T_ff` tied to `T_eff`), cpv 4.18; **PM waste heat 55 C** (blend of ~50 C wastewater and warmer dryer exhaust air).
- **Scenarios**: S5 is now the property-based case (2.35 GJ/t, boiler 0.98); S7 effluent 39 C; S9 PM waste heat 50 C; new S10 effluent 20 C.
- **`DIST` implements the draft's Table 6.2** where it states a distribution (electricity CV 2 %, diesel CV 5 %, paper CV 1 %, volumes CV 2 %, T_eff tri(20, 32, 32), shares normal CV 10 % renormalised, m_rec tri(85, 100, 115), m_PM tri(80, 95, 110), yield CV 5 %, hours tri(6800, 7200, 7800), steam heat CV 3 %, evaporation heat CV 2 %, press dryness tri(45, 48, 51), T0 uni(5, 10), `T_ref` tied to T0).
- **Monte Carlo acceptance** gains a fourth condition (boiler steam heat <= boiler electricity). Acceptance 96.98 % (was 99.18 %); the k-guard binds in 8.7 % of runs (was 3.76 %) because shares with CV 10 % sometimes leave the 'other' bucket smaller than the named small users.
- **Heat pump (M2, M4)** supplies the full steam enthalpy (`dh_prop`, 2.35 GJ/t) because it also heats feedwater from 90 C. M2 = 97.6 GWh (88-104 for COP 2.5-3.5), against the draft's 101.7 (93-108), which divided only latent boiler steam (130) by the COP. M1 48.0, M3 37.7 and M4 125.6 match the draft. M1-M4 are the same under both steam conventions (a test checks it).
- **New table** `reports/tables/model_exits_draft_format.csv` reproduces the draft's Table 2 (684 GWh quantified, 769 by difference, with P5-P95). The cooling-water estimate (46 GWh) is shown as an "of which" line inside the 769.

Key outputs, old (property-based, `headline.csv` at commit f80c42e) to new (draft-aligned). Value is base (P5-P95 of accepted runs).

| Output | Old (property-based) | New (draft-aligned) |
|---|---|---|
| Recovered TMP steam (GWh) | 470.7 (421-523) | 430.0 (383-487) |
| Boiler steam (GWh) | 142.1 (92-155) | 129.9 (103-159) |
| Boiler electricity (GWh) | 145.0 (94-158) | 145.0 (118-174) |
| PM drying steam (GWh) | 447.1 | 408.5 |
| Steam supply (GWh) | 612.8 | 559.9 |
| TMP share of steam (%) | 76.8 (75-84) | 76.8 (73-81) |
| Unallocated steam (GWh) | 134.1 (35-206) | 122.6 (55-190) |
| Heat to effluent (GWh) | 232.9 (193-274) | 211.6 (123-214) |
| Heat to air (GWh) | 1,161.7 (1,109-1,215) | 1,182.9 (1,154-1,291) |
| Exergy destroyed, total (GWh) | 1,333.3 (1,304-1,354) | 1,328.0 (1,281-1,371) |
| Exergy destroyed, TMP plant (GWh) | 806.3 (750-838) | 801.8 (734-857) |
| Exergy destroyed, paper machines (GWh) | 291.8 (264-351) | 290.1 (254-333) |
| Exergy destroyed, electric boilers (GWh) | 100.3 (65-110) | 100.3 (82-121) |
| Boiler exergy efficiency (%) | 30.8 (30-31) | 30.9 (28-33) |
| M1 TMP steam recovery +10 t/h (GWh) | 48.0 (46-50) | 48.0 (44-53) |
| M1b recovery to 90 % (GWh) | 82.5 (36-95) | 82.5 (57-109) |
| M2 heat pump (GWh) | 97.6 (63-109) | 97.6 (78-119) |
| M3 press dryness (GWh) | 37.7 (32-44) | 37.7 (33-44) |
| M4 combined (GWh) | 125.6 (91-135) | 125.6 (107-146) |
| MC acceptance | 99.18 % | 96.98 % |

Reading the table: the energy flows move because steam is counted on a different basis (about 9 % less steam heat), not because the mill changed. Exergy destroyed and the measures barely move, which is the point of the convention change: the exergy per tonne of steam and the savings in electricity are the same under both conventions. Base M2 is unchanged at 97.6 only because the old model happened to use the same full-enthalpy convention; the new P5-P95 ranges are wider because of the draft's wider distributions. Exergy destroyed 1,328 (draft 1,329); effluent heat P5-P95 123-214 (draft section 6 said 125-214); TMP useful exergy 148; boiler psi 30.9 %.
