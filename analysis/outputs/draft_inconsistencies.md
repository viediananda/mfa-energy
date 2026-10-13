# Internal inconsistencies in "MFA Group2 Report Draft" (12 Oct 2026)

Section numbers are the draft's. Values checked by `analysis/draft_reproduction.py`.

## Energy balance
1. **Residual by difference: 769 / 766 / 765 GWh/y.** Table 2 and 5.1 text say 769 (= 1,453 - 684; unrounded 768.9, also Fig 1 "768.92"). Sec 5.5 text says 766; Sec 10 (Conclusions) says 765. Same formula gives 768.9 every time.
2. **Rounded electricity terms do not sum.** Sec 5.1: 1,015 + 218 + 145 + 73 = 1,451, not 1,450 (unrounded 1015 + 217.5 + 145 + 72.5). Appendix B printed rows also sum to 1,451 (952+63+196+145+22+22+18+18+15).
3. **Wastewater range: 110-212 vs 125-214.** Sec 5.1 text/Table 2 use 20-32 C at T0 = 7 C, giving 110-212. Sec 6.4(c) says 125-214. Only the Monte Carlo P5-P95 (T triangular 20/32/32, T0 uniform 5-10 C, volume N 2 %) gives 125-214; that is a percentile range, not the min-max range, and is not labelled as such.
4. **Effluent temperature 32 vs 35 C.** Table 2, Sec 5.1, Table 6.2 and Fig 1 use 32 C (T - T0 = 25 K, 212 GWh). Sec 5.3 factor table and Appendix A say 35 C ("32 K above sea"). Waste exergy to water "11 GWh" only reproduces at 35 C (237 GWh x 0.047); Fig 2 shows 8.9 (32 C, factor 0.0424). Appendix A's "32 K above sea" would be ~39 C, not 35 C.
5. **Residual if wastewater at 20 C: "about 870".** Reproduces (871), but this uses the 110 lower bound, so the 20 C case is only valid for the Table 2 basis, not for the 125 lower bound of Sec 6.4.
6. **Cooling-water rule of thumb.** "1 K of about 4 Mm3 = roughly 5 GWh/y" is 4.64 (so 10 K = 46, not 50). The raw-minus-effluent difference is 11.05 - 7.29 = 3.76 Mm3, i.e. 4.4 GWh/K.
7. **Electric boilers described as residual loss only.** Table 2 treats the 15 GWh boiler loss as a separate exit, but Fig 1 draws it as coming out of "Other processes 72.5", not from the "Electric boilers 145" node.
8. **Sec 4.3 "post-dryer paper moisture of 48 %"** contradicts Sec 5.1 (48 % is post-press dryness; final moisture is 7 %).
9. **Sec 5.1 "boilers provide steam when recovered TMP steam is sufficient"** is the wrong way round (should be insufficient). Sec 5.1 also says 408 GWh "dryer exhaust air" while Table 2 splits it 278 + 130; the "largest exit" is therefore 408 only after summing two rows.
10. **Rounding chain in steam/PM.** 408 - 278 = 130 uses rounded values (unrounded 408.5 - 277.8 = 130.7); "Other heat uses 130" is the same number as the PM residual 130 and the boiler steam 130 by coincidence of rounding; three different flows share the value 130 in Fig 1.

## Exergy
11. **Steam exergy factor: 0.315 vs 0.318 vs ~0.345.**
    - 0.315 (Sec 5.3 table) = exergy of saturated vapour 3.41 bar(a) to 90 C condensate divided by the full enthalpy drop to 90 C (2.35 GJ/t).
    - 0.318 (Fig 2 caption, steam supply 178.3, PM 347.4, other heat uses 41.4) = Carnot factor 1 - 280/411 at 138 C.
    - ~0.345 (hotspot table: 148 = 430 x 0.345, 45 = 130 x 0.345, 193 = 560 x 0.345) = the same 0.315-type exergy divided by the latent heat 2.15 GJ/t only.
    The three are applied to the same 2.15 GJ/t latent-heat energy flows. The table, the Sankey and the hotspot table therefore disagree: steam supply exergy is 193 (hotspot) vs 178.3 (Fig 2) vs 176 (0.315).
12. **Exergy destroyed 1,329 (Sec 5.3) vs 1,324.8 (Fig 2).** Waste exergy 119 (text) vs 123.2 (Fig 2); air 109 vs 114.3; water 11 vs 8.9; district heat 2 vs 2.0. Text also says 119 = 109 + 11, which is 120.
13. **Hotspot "Exergy in" values mix factor bases.** PM 337 = 196 + 408 x 0.345 (0.345 basis) but Fig 2 shows PM 347.4 (0.318 basis). Hot water 42 matches 130 x 0.318 (Fig 2: 41.4), not 130 x 0.345 (44.9), so one table mixes both factors. Hot-water psi 27 % vs 26.5 % from 11/41.5.
14. **Paper-machine waste heat "only 50 GWh of exergy" (Sec 5.4).** (218 + 408) x 0.077 = 48; not derivable exactly.
15. **"Bleaching, WWTP, wood, utilities, grid losses" = 96.** Appendix B items give 95 and 5 % other + bleaching gives 94.1. Bleaching (22) is excluded from the PM row (196) and counted here; the improvement-potential column repeats 96, whose per-item remark "no single item above 22" is correct (max 21.9).
16. **TMP "useful exergy out" counts only steam** (148) but PM/EB rows have the same basis; steam-network exergy-in (193) counts the same steam flow already counted as outputs of TMP (148) and boilers (45), so rows are not additive (1015 + 337 + 145 + 42 + 96 + 193 is not a balance).
17. **Reference temperature "7 C (280 K)"** is 280.15 K. Effect <0.01 on factors, but Sec 4.4 and Table 6.2 present it as exact.
18. **Table 1** uses "Ex - mCp[...]" (typo for "="); Table 1 steam equation gives no temperature basis.

## Measures (Sec 7)
19. **Heat pump saving 93-108.** Reproduces as 145 - 130/COP (COP 2.5-3.5), i.e. assumes heat-pump electricity replaces all 145 GWh boiler input. The text says "replacing all boiler steam", consistent, but then Sec 7.1 calls the saving "net electricity saving" without noting TMP waste heat availability (no check that ~80 C TMP heat is sufficient).
20. **Combined 126 GWh / 0.28 MWh/t / 2.98 MWh/t.** Table row says "1 + 3 + heat pump for the rest". Reproduces (125.2) only with COP 3.0 applied to the remaining 12.3 t/h; the draft does not state COP. Sec 7.1 says "all three measures" combined; that wording (and Sec 7 line "measures not fully additive") conflicts with the table's "1 + 3 + heat pump for the rest". Also 126 is stated as reachable although the heat pump alone supposedly saves up to 108 and the cap is 145.
21. **M3 MWh/t:** 37.7/444,494 = 0.085 (rounds to 0.08 or 0.09 depending on whether 37.7 or 38 is used).
22. **"10 % refining cut saves about 95 GWh"** uses 952 GWh (TMP refiners, Appendix B), not the 1,015 GWh TMP total used elsewhere (10 % = 101.5).
23. **Sec 9.1** calls the measure 1 "reboiler" system; no such unit is defined (EP1/EP2 are electric boilers).

## Figures
24. **Fig 1 vs text.** Fig 1 shows residual 768.92 and low-grade waste heat 980.92; text says 766. Fig 1 diesel (2.82) joins low-grade heat directly, so exits are drawn against 1,452.82, while Fig 2 excludes diesel (1,450).
25. **Fig 2 steam supply (178.3), PM (347.4), other heat uses (41.4)** all use 0.318; hotspot table uses 0.345 and Sec 5.3 table 0.315 (item 11).
26. **Tornado charts (Sec 6.4)** show Spearman coefficients with no printed values; qualitative statements (a)-(e) were not re-run (no MC model in the draft).
27. **Sec 6.3 / 4.5** say "around 10,000" trials / "10000 independent" trials; wastewater percentile 125-214 needs ~10^5 draws for +-1 GWh stability.
