# Audit: Hallsta electricity energy/exergy MFA (2023)

Read-only audit. No repo files were edited. Scratch scripts are in `.../scratchpad/audit/` (a1-a4.py, run/).
Baseline run: `uv run pytest` gives 9 passed. Every number below was computed by running `run()` or taken from the quoted source.

## Verdict in brief
- The arithmetic is internally correct. No formula is wrong: `f_sens`, the steam properties, the district-heat log-mean factor, the IP formula, the `gap_SEC_net` logic and `save_rec90` all check out.
- The notebook DIST is identical to `model.DIST`. The committed CSVs equal a fresh run (max diff 6e-12). The notebook's headline text numbers (77 %, 83 %/16 %/0.8 %, 99.96 %, S4 negative residual, "top 3 same in every scenario") all reproduce.
- The weakness is not arithmetic. It is that the three "gap" residuals absorb everything (steam to hot water 134 GWh, heat to air 1,205 GWh, util 18 GWh). Several inputs are undocumented assumptions. The exergy convention gives ψ = 0 to many processes. The MC treats some assumptions as data.
- The notebook does NOT run headless on this machine as shipped (Chrome/kaleido, cell 31). With that single line stubbed, all 54 cells execute.

---
## BUG (wrong or misleading result)

### B1 [med] The model can create exergy and steam below zero in the MC, and these runs stay in the reported percentiles
- `notebooks` cell 40 computes `ok = rec_ratio in [0.70,0.90] & st_HW>=0`, prints it, and never applies it. Cell 39 says runs are "flagged".
- 0.79 % of runs (79 of 10,000) have `st_HW < 0`. In those runs `Xdest|Hot water & heating` goes negative (min -11.7 GWh), which is physically impossible.
- Effect on reported numbers is small. Steam residual P5 moves from 33.3 to 36.6 GWh if the filter is applied. Other outputs move by 0.3 GWh or less.
- Fix: apply `ok`, or clip `st_HW`.

### B2 [low-med] `eff_EB` cap at 0.995 is hit by 11 % of MC runs (6 % would exceed 100 % without it)
- `model.py:52`: `eff_EB = min(y_EB*dh, 0.995)`.
- `eff_EB` is the product of two independently drawn quantities, `y_EB` tri(1.45, 1.50, 1.53) and `dh` (from `T_cond` 80-100 °C). With T_cond = 80 °C, dh = 0.6654 and 1.53*dh > 1.0.
- Base value is 0.9806 (1.5 t/MWh is Holmen's own figure, so base is fine).
- In the MC, 11.15 % of runs are clipped at 0.995 and 5.96 % would have been above 1.0, which is impossible.
- The cap makes the `y_EB` upper tail and the `T_cond` effect partly inert. It biases `eff_EB`, `st_EB` and `save_rec90` slightly.
- Correct treatment is to draw efficiency directly or to cap `y_EB` at 1/dh.

### B3 [med] Named "other" electricity items are silently scaled down in 23 % of MC runs
- `model.py:42-43`: `k = min(1, OTH/(wood+wwtp+dist))`.
- Wood (18 GWh), WWTP (21.9 GWh) and grid loss (14.5 GWh) sum to 54.4 GWh. The base OTH bucket is 72.5 GWh, so k = 1 at base.
- `sh_OTH` is tri(0.02, 0.05, 0.08). In 22.96 % of runs OTH is below 54.4 GWh, so k < 1. `util` is then exactly 0 (22.9 % of runs).
- These items are power*hours figures given directly by Holmen. In those runs the MC overrides them to fit a share range that is itself an assumption.
- Consequence: `el_wwtp` and `el_wood` are not independent of `sh_OTH`. The range for `sh_OTH` (2-8 %) is inconsistent with the named items. Its lower end, 2 % = 29 GWh, cannot contain 54 GWh.
- The README and notebook never mention this behaviour.

### B4 [low] Cell 27 "waste-heat pool" balance check is an identity, not a check
- `Waste-heat pool − (water+air)`: `sink_air` is defined as `E − water − DH` (`model.py:63`).
- The pool algebraically equals `E − DH` for any inputs: TMP_waste + loss_EB + st_loss + PM_waste + the other terms + st_HW − DH = E − DH.
- So the check can never fail, and the same is true of the layer-1, -2 and -3 checks and `test_sinks_add_up_to_input`, `test_steam_balance_closes`, `test_exergy_balance_per_process`. All of these test residuals that were defined to close.
- The only non-tautological check is the final exergy identity (the sum of the exergy terms equals 1450.000), which does pass.

### B5 [low] Cross-check "Mill specific use 3.3 MWh/t" in cell 28 is circular
- The model value is `E_tot/paper_t` (3.262), compared with MR2023 Table 13's 3.3, which is the same 1450 GWh divided by the same paper tonnage, rounded. The deviation of -1.1 % is not independent evidence.
- A genuinely informative cross-check is missing. `SEC_TMP` = 2,406 kWh/t is 12 % above Holmen's own "normal 1,500-2,000 + 150 aux" (see S1 below).

---
## SOURCE MISMATCH

### S1 [high] TMP specific energy 2,406 kWh/ADT contradicts Holmen's 1,500-2,000 (+150 aux) range
- Source: "Student questions to Holmen 2025": "somewhere between 1500 and 2000 kWh/tonne is a normal energy span" and "150 kWh/ton in relation to about 2000 kWh/tonne for refining".
- Model: 70 % of 1450 GWh = 1,015 GWh, divided by 421,883 t = 2,406 kWh/t. The upper normal range is 2,150, so the model is 12 % above it. The cell-36 "Lever 1" is a 108 GWh gross gap, which comes from this contradiction.
- Possible causes the notebook does not discuss: the 70 % share applies to the whole TMP area including pumps, screens and cleaning; pulp tonnage basis; 2023 had many stops (MR2023 p.~6 "flertalet stopp"), which raise specific use.
- This is shown as an "energy saving lever" but the more likely reading is that the share or tonnage basis is off.
- Impact: the result `gap_SEC` has P5-P95 of 51-159 GWh and its P95 is entirely driven by this mismatch. It is not tested against the 2000 kWh/t bound in 5b.

### S2 [med] The "145,000 GJ" / "155,000 GJ" steam figures have no period in the source; "per month" is an inference
- Source (Compiled questions 2019): "Net production steam TMP approx 145 000 GJ, PM's 155 000 GJ." No unit of time.
- Notebook raw table (cell 5): `GJ/month`, and conversion `× 12/3600` (cell 10).
- The inference is plausible (145,000 GJ/month x 12 = 483 GWh against model 471 GWh, -2.6 %). Annual would be 40 GWh and implausible against 100 t/h.
- But in "Answers to questions-1.docx" Holmen says "TMP3 uses between 500-5000 GJ/month of steam" and "recently the steam production has been around 10 000 GJ/month". This is 14 times lower than 145,000 GJ/month and is never mentioned in the notebook. One of these statements has a different basis. It should be recorded as a conflict (§3).
- The PM figure also gets multiplied by 12 from one 2019 month (August; Holmen says "values for Aug. 2019" for the electricity items).
- Cell 28 ("TMP electricity vs MWh/month x12 = 1008 GWh") annualises a single August 2019 month. Cell 28 also never checks the PM electricity (22,000 MWh/month x 12 = 264 GWh against model 217.5 GWh, +21 % over the model).

### S3 [low-med] `T_PMwaste` BASE = 55 °C, source says 50 °C
- Source (2019 Q&A): "average temperature of the waste water from PM11 and PM12? Around 50 degrees". Notebook raw `T_PMww = 50`. BASE `T_PMwaste = 55` (DIST range 45-65 symmetric about 55). Cell 33 labels "PM waste heat, 55 °C".
- Impact of using 50: f = 0.0697 instead of 0.0770; Xdest PM becomes 291.8 (+4.7 GWh), Xdest_total 1333.3 (+4.7). It does not change the ranking.
- A 50 °C wastewater temperature is not the same as the dryer exhaust/vapour that carries most PM heat (see Q2).

### S4 [low] Steam pressure
- BASE `p_steam = 3.4e5` Pa abs = 2.4 bar(g) + 1. Holmen wrote only "Temp at 2,4 bar = 138 c". CoolProp: Tsat(3.4 bar abs) = 137.8 °C, Tsat(2.4 bar abs) = 126.1 °C. So gauge is the correct reading and 3.4e5 is correct.
- Holmen's other quote "Steam pressure mostly approx 2,5 bar" is consistent with 2.5 bar(g) = 3.5e5, inside DIST uni(3.3e5, 3.6e5) (but 3.4e5 is not the midpoint, 3.45e5; irrelevant).
- Sensitivity is negligible: dh changes from 0.6537 (3.4 bar) to 0.6541 (3.5 bar), 0.06 %. Taking 2.5 bar as absolute instead: dh = 0.6498 (-0.6 %), fx = 0.298 (-5 %). Immaterial, all results change < 1 GWh.
- Raw table class for `p_steam_g` is 'B' but the year is 2019 (the legend defines class C as older Holmen data). Cosmetic.

### S5 [med] District heat is sourced from the steam residual, but Holmen says it mainly is not
- Source (2025 Q&A): "District heating is produced by internally produced warm water produced mainly by recovered heat from waste water and cooling of compressors. Additionally heated by steam... not necessarily TMP steam is the main source."
- Model: `Hot water & heating` (134 GWh steam residual) → DH 11.877 GWh. Cell 31 sends 122 GWh from this node to "low-grade waste heat".
- The residual of 134 GWh (22 % of steam supply) is larger than any documented use. Documented heat uses: DH export 11.9 GWh (MR2023) and ~4.4 GWh domestic heating in 2019 (16,000 GJ). The remaining ~118 GWh of "hot water/venting" has no source and is the plug that makes steam close.
- Holmen (Answers-1) says steam is vented "sometimes during summer, normally not or very rarely during winter". A systematic 134 GWh of vented/unused steam, produced partly by electric boilers, is hard to believe. More plausible: `m_PM` is closer to 110 t/h (S3 makes the residual 63.5 GWh) or h_prod differs. See Q3.

### S6 [low] Items that are in BASE but not documented in the raw table (cell 5), no source and no class
`f_dist` (1 %), `f_steamloss` (4 %), `T_TMPwaste` (80, whereas raw `T_pulp` 80 is the pulp temperature before bleaching, not waste-heat temperature), `T_HW` (60), `T_DHs/T_DHr` (85/45), `T_ff` (30), `cpv`, and `V_ff` (derived). Holmen explicitly says "Steam Distribution Losses ?" and "Electricity Transmission Losses ?" (no data). These are class D and should be labelled so. The text in cell 8 and the Conclusions imply they are traced to data.

### Values that check out against the source
| BASE | Source | OK |
|---|---|---|
| E_tot 1450 GWh | MR2023 Table 13, "El, totalt 2023 = 1450" | yes |
| paper_t 444,494, pulp_t 421,883 | Table 3 | yes |
| DH_export 11.877 GWh | MR2023 §8.3.3, 11 877 MWh | yes |
| V_wwtp 18,300 m³/d x 365 | §5.2 "ca 18 300 m³/dygn"; Table 4: sewage plant ran 365 d | yes |
| V_ff = 7,288,861 − 6,679,500 = 609,361 | §5.2, total of the 2 outlets | yes (derived) |
| sh 70/15/10 % | 2025 Q&A "TMP ~70 %, PMs ~15 %, EB ~10 %" | yes; sh_OTH 5 % is just the remainder, not stated by Holmen |
| P_wood 2.5 MW, P_bleach 3 MW, P_wwtp 2.5 MW | 2025 Q&A | yes |
| aux_TMP 150 kWh/t | 2025 Q&A | yes |
| m_rec 100 t/h, y_EB 1.5 t/MWh, m_wood 1.5 t/h | 2025 Q&A | yes |
| m_PM 95 (range 80-110) | 2025 Q&A "80-110 tonnes/h" | midpoint, yes |
| T_cond 90, T_eff 35/32 K | 2019 Q&A | see Q4 |
| PM11_frac 14/22 | 2019 Q&A Aug 2019, PM11 incl. bleaching 14,000, PM12 8,000 | yes, but single month of 2019; production share is 0.525 |
| h_prod 7,200 | Table 4: PM11 285.3 d (6,847 h), PM12 314 d (7,536 h); production-weighted 298.9 d = 7,174 h | yes, within 0.4 % |

---
## QUESTIONABLE ASSUMPTION

### Q1 [med] Exergy convention: "useful output" of PM, bleaching, WWTP, wood, utilities, grid is zero; hot water counts as useful
- `model.py:70-76`. All of these get Xuse = 0, so ψ = 0 and IP = Xin. The ranking "PM second" (287 GWh) rests on this: electricity to presses, vacuum pumps and refiner-like motors does mechanical work, and the paper itself has no exergy credit. Bleaching, WWTP, wood, utilities and grid (96 GWh) are 100 % "destroyed".
- At the other end, `Hot water & heating` has Xuse = st_HW·fHW = 11.3 GWh, as if all 134 GWh of residual steam became useful 60 °C hot water, while the energy view (cell 34, Sankey) treats 122 of those 134 GWh as lost. Exergy of actual DH delivered (`X_DH`) is 2.03 GWh. Counting only X_DH as useful raises Xdest_total from 1,328.6 to about 1,338 (+0.7 %). The ψ = 27 % reported for this node is therefore not meaningful.
- The notebook's check (cell 27, last row) subtracts `Xuse|Hot water` explicitly, so the closure hides this.
- The ranking of the top 3 is not affected. The ψ and IP columns of the table are convention-dependent and should say so.

### Q2 [med] PM waste heat evaluated at a single 55 °C
- `Xwaste|Paper machines = (PM + st_PM)·f_sens(55 °C)` = 49.5 GWh. This applies the exergy factor of 55 °C water to 643 GWh, much of which leaves as humid dryer exhaust and wet-end heat, partly reused to preheat incoming water (Holmen 2019: "recovering heat from the drying section ... to warm incoming process water during the cold season"). The reuse is not modelled.
- Likewise 80 °C for all unrecovered TMP heat (`T_TMPwaste`) is pulp temperature before bleaching, not a heat-rejection temperature.
- Exergy results are therefore insensitive to the actual physics. Impact is limited: Xwaste total is 110 GWh against 1,329 GWh destroyed.

### Q3 [med] Operating hours: h_prod = 7,200 h applied to all steam flows, and TMP uses PM hours
- `st_rec = m_rec·h_prod·dh` and `st_PM = m_PM·h_prod·dh`. Table 4 gives 365 operating days for the WWTP, "which corresponds to the paper mill's operating time" ("vilket motsvarar pappersbrukets drifttid"). PM11 and PM12 run 285.3 and 314 d, and the TMP lines are not the same as PM hours.
- The 2019 monthly steam (155,000 GJ/month) at 7,200 h implies 110 t/h, the very top of Holmen's 80-110 range, and at 8,760 h gives 90 t/h. The 13.5 % "PM steam" deviation in cell 28 therefore comes from the choice of hours, not from a data conflict.
- Sensitivity (all else base): h = 8,760 gives st_rec 572.7, st_PM 544.0, rec_ratio 0.801, st_HW 133.6, save_rec90 72.1 GWh. h = 6,847 gives rec_ratio 0.759, save_rec90 84.9.
- Note `st_HW` hardly moves, because rec and PM scale together. `h_prod` is a single shared variable, which is correct for the MC (hours are correlated by construction). But the same variable multiplies wood steam, bleach and PM steam, and TMP uptime is not PM uptime. TMP at 421,883 t and 85 ADT/h capacity needs at least 4,963 h.

### Q4 [low-med] Effluent heat: T_eff = 35 °C
- Source: "32 degrees above sea most of the time" (2019, before the WWTP rebuilt in 2020 with new cooling towers: MR2023 permit list "2019-05-20 ... nya kyltorn och MBBR-teknik"). The model value 35 corresponds to 28 K above T_ref = 7 °C, not 32 K.
- The notebook raw table itself records `dT_eff = 32 K, pre-2020 WWTP`. Using 32 K over 7 °C gives 39 °C: `sink_water` would be 263.8 GWh instead of 232.9 (+31), and `sink_air` 1,174 instead of 1,205. DIST uni(28, 40) spans both.
- `sink_air` is the plug for everything, so every error moves "heat to air" 1:1. The 83 % in Conclusions is 1450 minus two estimates.
- `V_ff` (609,361 m³/y) is the second outlet "FF PM2". Its temperature (30 °C) is an assumption. What the stream is (cooling water?) is not documented in the sources reviewed; the 2019 Q&A says cooling water is released without WWTP.

### Q5 [low] `sink_air = E − water − DH` ignores diesel and the energy that leaves in the product
- Diesel 2.82 GWh (Table 13) is excluded; including it would add 2.8 GWh (+0.2 %) to heat to air. Stated scope is electricity only, so it is a NOTE-level item.
- Product enthalpy leaving the site (paper at about 40 °C, hot pulp) is also not deducted.

### Q6 [low-med] MC distribution shape pulls the central value away from BASE
- `sh_EB` tri(0.05, 0.10, 0.12) has mean 9.0 %, so MC P50 for boiler electricity is 132.6 GWh against base 145 GWh (base sits at the 74.5th percentile). `sh_PM` tri(0.12, 0.15, 0.22) gives PM P50 212 against base 196 (+8 %).
- `save_rec90` P50 71.0 against base 82.5; `st_HW` P50 120 against base 134.
- Reading "base" next to P5-P95 in the MC table is misleading: the base is not the median.
- Whether skewed ranges are intended should be stated. 2019 values pulled the range, but the 2025 values are the baseline.
- Correlated inputs: shares are renormalised inside `run()` (OK: the sum has P5/P95 0.946/1.062, effective `sh_TMP` P5-P95 0.664-0.732 against nominal 0.665-0.734, so the renormalisation hardly changes them). But `m_rec`/`m_PM`/`sh_EB`/`h_prod` are drawn independently, although steam supply and demand are linked (that is what the 99.2 % `ok` check is for). `V_wwtp` and `V_ff` are independent normals (5 %/10 %), although their sum is a measured total (7,288,861) known to better than 1 %.

### Q7 [low] DIST: items missing from the MC
- Not sampled: `T0`, `T_ref`, `cpv`, `T_DHs/T_DHr` (these affect only X_DH), and the hard-coded 2,150 kWh/t in `gap_SEC` (`model.py:90`). The 2,150 is neither in BASE nor in DIST nor in the raw table. It is Holmen's upper normal range, so the "saving" is a best-case.
- Comment in cell 37, "Where 2019 and 2025 disagree, the 2019 value marks the far end of the triangle", is true only for `sh_PM` (0.22). For sh_TMP (0.72 inside 0.65-0.75) and sh_EB (0.06 inside 0.05-0.12) it is not the end.

### Q8 [low] `ends()` in the tornado cell (cell 49): inconsistent quantiles
- Reading `DIST` tuples: normals use `a ± 1.645·b` (P5/P95). Triangulars use `(a, c)` = (low, high) = P0/P100. Uniforms use `(a, bb)` = P0/P100. The tuple unpacking `(d, a, bb, c)` is correct for all three types (no indexing bug), but the bars are not comparable.
- Using P5/P95 for all, the swing of `sh_EB` is 58.3 GWh against 84.8 GWh in the notebook. Top 8 membership is unchanged (same 8 inputs), order is similar. Top is still `sh_EB`, so the headline sentence holds, but the magnitude of the bars is inflated 1.45x for the tri/uni inputs compared with normal ones (E_tot swing 4.29 both ways).

### Q9 [low] The IP formula and the 90 % lever
- `IP = (1−ψ)(Xin−Xuse)`. This is the standard van Gool form, so it is correct. With ψ = 0 for 7 of 10 processes it reduces to IP = Xin, which adds nothing.
- `save_rec90 = max(0, 0.9·supply − st_rec)/eff_EB` (82.5 GWh). Logic is right: it holds total supply fixed, replaces Δ boiler steam by TMP steam and divides by boiler efficiency. It cannot exceed `el_EB` because 0.9·supply − st_rec < supply − st_rec = st_EB, so no extra cap is needed (verified: it is never 0 or above the boiler flow in 10,000 runs). The unstated assumptions are that 90 % is defined against steam supply (including losses and the residual) while Holmen defined recovery rate against "needed consumption", and that the TMP can supply the extra 81 GWh with no change in electricity.
- `gap_SEC_net = gap·(1 − TMP_rec_eff/eff_EB)` is right if the steam lost is replaced by boilers, but uses the average recovery efficiency (46 %) not the marginal.

---
## NOTE (verified correct, no action)
- N1. `steam_v` rounding: `p` is rounded to 100 Pa and `T_cond` to 0.1 K. `dh` unrounded = rounded = 0.6537174 for the base. Over the MC range the error is < 1e-5 relative. No impact.
- N2. `f_sens` is correct: f(60 °C) = 0.0841, f(80) = 0.1113, f(35) = 0.0469. Returns 0 at Th <= T0.
- N3. District heat factor: Tlm = 40/ln(358.15/318.15) = 338.0 K; fDH = 1 − 280.15/338.0 = 0.1706. Correct. The 85/45 °C are assumptions.
- N4. Steam exergy factor 0.3147 (relative to 90 °C condensate). Steam is not double counted. 'Paper machines' Xin = PM electricity + st_PM·fx and 'Steam network' Xuse = (st_PM + st_wood + st_HW)·fx is the same exergy passed on, with the steam network destroying only the 4 % loss (7.7 GWh). Sum check: Xdest_total (1,328.6) + Xwaste_total (110.1) + Xuse|HW (11.3) = 1,450.000. The total is consistent with 1,450 GWh. Do not sum the "Exergy in" column over processes (it contains intermediate steam exergy several times).
- N5. 'Wood handling' Xin = 18 GWh electricity + 7.06 GWh x 0.3147 steam = 20.2 GWh. Correct.
- N6. eff_EB at base 0.9806 = 1.5 × 0.6537 (consistent with a boiler fed 90 °C condensate).
- N7. Conversion factors in cell 10 and `model.py:62` are right: GJ/month x 12/3,600 (1 GWh = 3,600 GJ), MWh/month x 12/1,000, and water heat V*cpv*dT/3.6e6 (MJ to GWh; 6.68e6 m3 x 4.17 x 28 / 3.6e6 = 216.7 GWh).
- N8. District-heat log-mean, `sink_DH`, `X_eff = 10.8 GWh` and `X_DH = 2.0 GWh` are computed but `X_eff` is not used in any process balance.
- N9. Seed 2023 with `default_rng`, N = 10,000: reproducible, and the committed CSVs equal a fresh run. P5-P95 via `quantile(.05/.95)` on all 10,000 runs, correct. Draw order depends on dict order of `DIST`; changing that order changes numbers.
- N10. In cell 40 the comment says DIST is "imported from src/hallsta_mfa/model.py", but cell 38 redefines `DIST` as a literal copy that shadows the import. The two are identical today (diffed programmatically: identical for all 27 keys). It is a drift risk: editing one will not change the other.
- N11. Cell 29 text "WWTP comes out at 1.51 %" ✓ (21.9/1450). Cell 52 conclusions all reproduce: 70/13.5/10/6.5 %, 76.8 % TMP steam, 83.1/16.1/0.8 % sinks, 99.96 % ranking (0.9996), electric boiler ψ 31 %. S4 residual = −4.2 GWh. Top-3 order unchanged in S0-S4. Energy view: PM loses more heat than TMP in 94.7 % of runs.
- N12. Scenario S1 hard-codes `sh_OTH = 0.0375` and scales the 2019 shares by 0.9625 so that the named items (54.4 GWh = 3.75 %) fit exactly, giving `util` = 0. This is an assumption not stated in the text. Bleaching is deemed inside the PM share in both splits (2019 explicit: "PM11 incl. bleaching"). 2025 does not say, and if Holmen's "PMs about 15 %" excludes bleaching, the PM electricity in the model is 21.6 GWh too low.
- N13. The MC filter results: `rec_ratio` in 0.70-0.90 for 100 % of runs, so only `st_HW >= 0` ever bites.
- N14. A directory `data/` (README.md, sources.csv) appears as untracked in git. I did not create it (timestamp matches a concurrent process). Left untouched.

---
## Execution of the notebook (item 6)
- Command as given fails at cell 31: `fig_E.write_image(...)` → plotly/kaleido: "Kaleido requires Google Chrome ... run `plotly_get_chrome`". Not fixed, as requested. Cells 0-30 ran; cells 31-53 did not.
- With only the `write_image` and `display(Image(...))` lines stubbed out, in a copy at `.../audit/run/nb.ipynb` (cwd in the scratch dir so repo outputs were not overwritten), all 54 cells execute without error.
- CSV comparison, repo `notebooks/outputs/*.csv` vs a fresh execution: `nb_mc_summary`, `nb_exergy_hotspots`, `nb_sankey_energy_links` max diff 6e-12, 9e-12, 2e-12. Also `Destroyed` column vs fresh `run(BASE)`: 5e-12. So the committed outputs are current.
- `pyproject.toml` lists `kaleido>=1.4.0` as a dependency, but it needs a Chrome binary. This is an environment prerequisite that the README should state.

## Tests (item 5): what is not tested
1. The tests mostly check identities that hold by construction (see B4). They would pass even if `st_HW`, `sink_air` or `Xdest` contained an error in an input.
2. `test_headline_numbers` pins only `el_TMP`, `el_EB` and `rec_ratio` ±0.01. Nothing pins `dh` (0.6537), `fx_steam` (0.3147), `st_rec`, `st_PM`, `st_HW`, `sink_water`, `Xdest_total` (1328.6), `save_rec90` (82.5), `gap_SEC`.
3. Physical bounds are not tested: `st_HW >= 0`, `util >= 0`, `Xdest >= 0` for every process, `0 <= ψ <= 1`, `eff_EB <= 1`, `save_rec90 <= el_EB`. A MC-based test would catch B1 (79 runs with `st_HW<0`, negative Xdest) and B2/B3.
4. The `k` scaling (B3) and the 0.995 cap (B2) are not exercised at all.
5. `DIST` is imported in the test file but never used: no test that BASE lies inside every DIST range, that tri `low<=mode<=high`, that no draw gives a negative or nonphysical value, or that notebook DIST equals model DIST (N10).
6. No independent exergy check, e.g. total exergy in (electricity 1450) = sum of destroyed + waste + useful (it holds, but it is only exercised through `Xdest` defined as residual).
7. `steam_v` is only tested with loose bounds (0.6 < dh < 0.7, 0.2 < fx < 0.4). Neither p (3.4e5 vs g/abs confusion) nor the 138 °C Tsat from Holmen is tested.
8. `test_run_accepts_arrays` varies only `sh_TMP`; it does not test array draws for `p_steam`, `T_cond` or `y_EB`, where `np.round` and the cap matter.
9. The MC step (seed, N, percentile extraction, tornado `ends`) lives only in the notebook and has no test.

## Impact table
| Item | Quantity | Base | Alternative | Change |
|---|---|---|---|---|
| S1 | SEC_TMP vs 2,150 | 2,406 kWh/t | 2,150 | gap_SEC 108 GWh |
| S3 | T_PMwaste 50 °C | Xdest_total 1,328.6 | 1,333.3 | +4.7 |
| Q1 | count only X_DH as useful | Xdest_total 1,328.6 | about 1,338 | +0.7 % |
| Q3 | h_prod 8,760 | rec_ratio 0.768, save_rec90 82.5 | 0.801, 72.1 | -10.4 GWh |
| Q4 | effluent 39 °C | sink_water 232.9 / air 1,205.3 | 263.8 / 1,174.3 | ±31 GWh |
| B1 | apply `ok` filter | st_HW P5 33.3 | 36.6 | +3.3 |
| Q6 | MC median vs base | el_EB 145 | P50 132.6 (base = P74.5) | -8.6 % |
| Q5 | add diesel | sink_air 1,205.3 | 1,208.1 | +2.8 |
