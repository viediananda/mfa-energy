"""Reproduce every number in reports/MFA Group2 Report Draft.pdf from the draft's own inputs.

Run: uv run python analysis/draft_reproduction.py
Writes analysis/outputs/draft_reproduction.csv
status: match = within 1 % or within half a unit of the draft's last printed digit
        (766/765 residuals forced to mismatch: same formula as 769, so they are typos not rounding);
        mismatch = formula found but value differs; could_not_reproduce = no formula found.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from CoolProp.CoolProp import PropsSI

OUT = Path(__file__).parent / "outputs" / "draft_reproduction.csv"
rows = []


def add(section, item, draft, repro, formula, unit=None, force=None):
    """Append one comparison row. unit = size of the draft's last printed digit."""
    if repro is None:
        rows.append(dict(section=section, item=item, draft_value=draft, reproduced_value=np.nan,
                         abs_diff=np.nan, formula=formula, status="could_not_reproduce"))
        return
    if unit is None:
        s = repr(float(draft))
        unit = 10 ** -len(s.split(".")[1]) if s.split(".")[1] != "0" else 1
    d = abs(repro - draft)
    ok = d <= 0.5 * unit + 1e-9 or d <= 0.01 * abs(draft)
    rows.append(dict(section=section, item=item, draft_value=draft, reproduced_value=round(float(repro), 4),
                     abs_diff=round(float(d), 4), formula=formula, status=force or ("match" if ok else "mismatch")))


# ---- inputs stated in the draft ----
E_EL, E_DI = 1450.0, 2.82
SH = dict(TMP=.70, PM=.15, EB=.10, OTH=.05)
H, STEAM_GJ, TMP_TPH, BOIL_T_MWH, PM_TPH = 7200, 2.15, 100, 1.5, 95
PAPER, PRESS_DRY, FIN_MOIST, EVAP_GJ = 444494, .48, .07, 2.4
WW_M3, CP, T_WW, T_WW_LOW, T0C = 7.29e6, 4.18, 32, 20, 7
T0 = 280.0
GWH = 3600.0  # GJ per GWh


def gwh_steam(tph):  # t/h of steam -> GWh/y of latent heat
    return tph * H * STEAM_GJ / GWH


# ---- 5.1 energy ----
E_IN = E_EL + E_DI
add("5.1", "E_in total (GWh/y)", 1452.82, E_IN, "1450 + 2.82")
e = {k: v * E_EL for k, v in SH.items()}
add("5.1", "E_TMP electricity", 1015, e["TMP"], "70% x 1450")
add("5.1", "E_PM electricity", 218, e["PM"], "15% x 1450 = 217.5")
add("5.1", "E_EP electricity", 145, e["EB"], "10% x 1450")
add("5.1", "E_other electricity", 73, e["OTH"], "5% x 1450 = 72.5")
add("5.1", "Sum of rounded shares 1015+218+145+73 (stated = 1450)", 1450, 1015 + 218 + 145 + 73,
    "arithmetic sum of the printed terms (=1451)")
E_TMP_STEAM = gwh_steam(TMP_TPH)
add("5.1", "E_TMP,steam", 430, E_TMP_STEAM, "100 t/h x 7200 h x 2.15 GJ/t / 3600")
add("5.1", "E_TMP,residual", 585, e["TMP"] - E_TMP_STEAM, "1015 - 430")
add("5.1", "TMP electricity returned as steam (%)", 42, 100 * E_TMP_STEAM / e["TMP"], "430 / 1015")
BOIL_T = e["EB"] * 1000 * BOIL_T_MWH  # t steam /y
E_EP_STEAM = BOIL_T * STEAM_GJ / GWH
add("5.1", "E_EP,steam", 130, E_EP_STEAM, "145,000 MWh x 1.5 t/MWh x 2.15 / 3600")
add("5.1", "E_EP,residual (boiler loss)", 15, e["EB"] - E_EP_STEAM, "145 - 130")
STEAM_SUP = E_TMP_STEAM + E_EP_STEAM
add("5.1", "Steam supply", 560, STEAM_SUP, "430 + 130")
add("5.1", "TMP share of steam supply (%)", 77, 100 * E_TMP_STEAM / STEAM_SUP, "430 / 560 (Sec 5.5)")
E_PM = gwh_steam(PM_TPH)
add("5.1", "E_PM,drying", 408, E_PM, "95 t/h x 7200 x 2.15 / 3600")
dry_solids = PAPER * (1 - FIN_MOIST)
water_in = dry_solids * (1 / PRESS_DRY - 1)
evap_t = water_in - PAPER * FIN_MOIST
add("5.1", "Water evaporated (t/y)", 416700, evap_t, "paper x 0.93 x (1/0.48 - 1) - paper x 0.07")
Q_EVAP = 416700 * EVAP_GJ / GWH
add("5.1", "Q_evap", 278, Q_EVAP, "416,700 t x 2.4 GJ/t / 3600")
add("5.1", "PM drying residual steam", 130, E_PM - Q_EVAP, "408 - 278 (unrounded 408.5 - 277.8)")

# ---- Table 2 ----
ww_gwh = lambda dT: WW_M3 * 1000 * CP * dT / 3.6e9  # m3 -> kg, kJ -> GWh
WW = ww_gwh(T_WW - T0C)
add("5.1/T2", "District heat", 11.9, 11877 / 1000, "11,877 MWh / 1000")
add("5.1/T2", "Dryer exhaust latent", 278, Q_EVAP, "see Q_evap")
add("5.1/T2", "Dryer exhaust residual", 130, 408 - 278, "408 - 278")
add("5.1/T2", "Wastewater (32 C)", 212, WW, "7.29 Mm3 x 4.18 x (32-7) K")
add("5.1/T2", "Wastewater lower bound (20 C)", 110, ww_gwh(T_WW_LOW - T0C), "7.29 Mm3 x 4.18 x (20-7) K")
LOSS_EB = e["EB"] - E_EP_STEAM
add("5.1/T2", "Electric boiler losses", 15, 145 - 130, "145 - 130")
STEAM_DIST = .04 * 560
add("5.1/T2", "Steam distribution losses", 22, STEAM_DIST, "4% x 560")
GRID = .01 * E_EL
add("5.1/T2", "Internal grid losses", 15, GRID, "1% x 1450 = 14.5")
SUB = 11.877 + 278 + 130 + WW + 15 + STEAM_DIST + GRID
add("5.1/T2", "Subtotal quantified", 684, 11.9 + 278 + 130 + 212 + 15 + 22 + 15, "sum of printed exits (683.9)")
RESID = E_IN - (11.9 + 278 + 130 + 212 + 15 + 22 + 15)
add("5.1/T2", "Residual by difference (Table 2, text)", 769, RESID, "1452.82 - 683.9")
add("5.5", "Residual in Sec 5.5 text", 766, RESID, "1452.82 - 683.9 (same formula as Table 2)", force="mismatch")
add("10", "Residual in Conclusions", 765, RESID, "1452.82 - 683.9 (same formula as Table 2)", force="mismatch")
add("5.5/Fig1", "Residual in Fig 1", 768.92, RESID, "1452.82 - 683.9")
add("5.1", "Share traceable (%)", 47, 100 * 683.9 / E_IN, "683.9 / 1452.82")
add("5.1", "Residual share (%)", 53, 100 * RESID / E_IN, "768.9 / 1452.82")
add("5.1", "Residual if wastewater at 20 C", 870, RESID + (212 - 110), "769 + (212 - 110)")
add("5.1", "Remaining steam 560-408-22", 130, 560 - 408 - 22, "arithmetic")
add("5.1", "Cooling-water heat per K, 4 Mm3 (GWh/y)", 5, 4e6 * 1000 * CP / 3.6e9, "4 Mm3 x 4.18 / 3.6", unit=1)
add("5.1", "Cooling-water heat for 10 K (GWh/y)", 50, 10 * 4e6 * 1000 * CP / 3.6e9, "10 x above", unit=10)
add("5.1", "Raw water minus effluent (Mm3), 'about 4'", 4, 11.05 - 7.29, "11.05 - 7.29", unit=1)
add("5.5/Fig1", "Fig 1 low-grade waste heat", 980.92, RESID + 212, "residual + wastewater")
add("5.5/Fig1", "Fig 1 paper machines", 625.5, 217.5 + 408, "217.5 + 408")

# ---- 5.2 SEC ----
add("5.2", "SEC electricity (MWh/t)", 3.26, 1450000 / PAPER, "1,450,000 / 444,494")
add("5.2", "SEC TMP", 2.28, e["TMP"] * 1000 / PAPER, "1,015,000 / 444,494")
add("5.2", "SEC PM", 0.49, e["PM"] * 1000 / PAPER, "217,500 / 444,494")
add("5.2", "SEC electric boilers", 0.33, e["EB"] * 1000 / PAPER, "145,000 / 444,494")

# ---- 5.3 exergy factors ----
P_BAR = (2.4 + 1.01325) * 1e5
hg, sg = PropsSI("H", "P", P_BAR, "Q", 1, "Water"), PropsSI("S", "P", P_BAR, "Q", 1, "Water")
hf = PropsSI("H", "P", P_BAR, "Q", 0, "Water")
hc, sc = PropsSI("H", "T", 363.15, "P", P_BAR, "Water"), PropsSI("S", "T", 363.15, "P", P_BAR, "Water")
ex_cond = (hg - hc) - T0 * (sg - sc)  # J/kg, sat. vapour 2.4 bar(g) -> 90 C condensate
F_STEAM = ex_cond / (hg - hc)
F_STEAM_LAT = ex_cond / (hg - hf)
F_CARNOT = 1 - T0 / (138 + 273.15)
add("5.3", "Steam exergy factor (table)", 0.315, F_STEAM, "CoolProp: [dh - T0 ds](sat vap 3.41 bar -> liq 90 C) / dh(to 90 C)")
add("Fig2", "Steam exergy factor (Fig 2 caption)", 0.318, F_CARNOT, "Carnot 1 - 280/411.15 at 138 C")
add("5.4", "Steam factor implied by hotspot table (148/430)", 0.345, F_STEAM_LAT,
    "same exergy but divided by latent heat only (hfg=2.15 GJ/t): 148.4/430")
tm_dh = 40 / np.log((85 + 273.15) / (45 + 273.15))
add("5.3", "District heat 85/45 C", 0.171, 1 - T0 / tm_dh, "Carnot at log-mean temperature of 85/45 C")
wf = lambda tc: 1 - T0 * np.log((tc + 273.15) / T0) / (tc + 273.15 - T0)
for name, tc, v in [("Unrecovered TMP heat 80 C", 80, .111), ("Hot process water 60 C", 60, .084),
                    ("PM waste heat 55 C", 55, .077), ("Effluent 35 C", 35, .047)]:
    add("5.3", name, v, wf(tc), "1 - T0 ln(T/T0)/(T - T0), warm-water equation of Table 1")
add("5.3", "Exergy destroyed (%)", 92, 100 * 1329 / 1450, "1329 / 1450")
add("5.3", "Exergy destroyed 1329", 1329, 1450 - 119 - 2, "1450 - 119 - 2 (uses draft's own 119; identity only)")
# candidate for 109 (non-unique; many 3-4 term combinations land within +-1)
AIR = 585 * wf(80) + 408 * wf(55) + 15 * F_STEAM_LAT + 22 * F_STEAM_LAT
add("5.3", "Waste exergy to air 109", 109, AIR,
    "CANDIDATE only: 585*.111 + 408*.077 + 15*.345 + 22*.345; not unique, not confirmed", force="could_not_reproduce")
WW_EX = ww_gwh(35 - T0C) * wf(35)
add("5.3", "Waste exergy to water 11", 11, WW_EX, "7.29 Mm3 x 4.18 x (35-7) K x 0.047 (35 C, not the 32 C of Table 2)")
add("5.3", "Waste exergy total 119", 119, None, "109 + 11 = 120 in the draft itself; 119 not derivable")
add("5.3", "District-heat exergy 2", 2, 11.9 * (1 - T0 / tm_dh), "11.9 x 0.171")
add("Fig2", "Fig 2 exergy destroyed", 1324.8, None, "no consistent route (1450 - 123.2 - 2.0 is only an identity)")
add("Fig2", "Fig 2 waste-heat exergy", 123.2, None, "composition not stated")
add("Fig2", "Fig 2 steam supply", 178.3, 560 * F_CARNOT, "560 x 0.3189 (Carnot factor)")
add("Fig2", "Fig 2 paper machines", 347.4, 217.5 + 408 * F_CARNOT, "217.5 + 408 x 0.318")
add("Fig2", "Fig 2 other heat uses", 41.4, 130 * F_CARNOT, "130 x 0.318")
add("Fig2", "Fig 2 wastewater exergy", 8.9, WW * wf(32), "212 x 0.0424 (32 C)")

# ---- 5.4 hotspots ----
PM_ELEC_EX = e["PM"] - 3 * 7200 / 1000  # 15% minus 3 MW bleaching
add("5.4", "PM exergy 'about 50 GWh' at 55 C", 50, (217.5 + 408) * wf(55), "(217.5 + 408) x 0.077", unit=1)


def hot(name, ex_in, ex_out, d_in, d_out, d_psi, d_ip, note="see formula"):
    psi = ex_out / ex_in
    ip = (1 - psi) * (ex_in - ex_out)
    f = "IP = (1-psi)(Ex_in - Ex_useful)"
    add("5.4", f"{name}: exergy in", d_in, ex_in, note)
    if d_out is not None:
        add("5.4", f"{name}: useful out", d_out, ex_out, "steam/heat x exergy factor")
    add("5.4", f"{name}: psi (%)", d_psi, 100 * psi, "Ex_useful / Ex_in", unit=1)
    add("5.4", f"{name}: improvement potential", d_ip, ip, f)


hot("TMP", e["TMP"], E_TMP_STEAM * F_STEAM_LAT, 1015, 148, 15, 740, "70% x 1450; useful = 430 x 0.345")
hot("Paper machines", PM_ELEC_EX + E_PM * F_STEAM_LAT, 0.0, 337, None, 0, 337, "195.9 (15% elec - 21.6 bleaching) + 408.5 x 0.345")
hot("Electric boilers", e["EB"], E_EP_STEAM * F_STEAM_LAT, 145, 45, 31, 69, "10% x 1450; useful = 129.9 x 0.345")
HW_IN = 130 * F_CARNOT
hot("Hot water and heating", HW_IN, 130 * wf(60), 42, 11, 27, 23, "130 x 0.318 (Carnot steam factor as in Fig 2); 0.345 would give 44.9; useful = 130 x 0.084")
hot("Bleaching/WWTP/wood/utilities/grid", e["OTH"] + 3 * 7200 / 1000, 0.0, 96, None, 0, 96, "72.5 (5% other) + 21.6 bleaching = 94.1; Appendix B items sum to 95")
SN_IN = STEAM_SUP * F_STEAM_LAT
hot("Steam network", SN_IN, SN_IN * .96, 193, 185, 96, 0.3, "560 x 0.345; useful = 96% (4% distribution loss)")

# ---- 6 uncertainty: wastewater range 125-214 ----
rng = np.random.default_rng(1)
n = 200000
V = rng.normal(7.288861, .02 * 7.288861, n)
T = rng.triangular(20, 32, 32, n)
T0s = rng.uniform(5, 10, n)
Q = V * 1e9 * CP * (T - T0s) / 3.6e9
p5, p95 = np.percentile(Q, [5, 95])
add("6/6.4c", "Wastewater loss range low (GWh/y)", 125, p5, "MC P5: V~N(7.289,2%), T~Tri(20,32,32), T0~U(5,10)")
add("6/6.4c", "Wastewater loss range high (GWh/y)", 214, p95, "MC P95, same setup")

# ---- 7 measures ----
STEP = H / BOIL_T_MWH / 1000  # GWh elec per t/h boiler steam
add("7", "1 t/h boiler steam avoided (GWh/y)", 4.8, STEP, "7200 h / 1.5 t/MWh")
BOIL_TPH = BOIL_T / H
add("7", "Boiler steam flow (t/h)", 30, BOIL_TPH, "145,000 x 1.5 / 7200")
add("7", "Cap on total saving (GWh/y)", 145, e["EB"], "all boiler electricity")
M1 = 10 * STEP
add("7", "M1 saving (GWh/y)", 48, M1, "10 t/h x 4.8")
add("7", "M1 MWh/t", 0.11, M1 * 1000 / PAPER, "48 GWh / 444,494 t")
cop_lo, cop_hi = 2.5, 3.5
M2_lo = e["EB"] - 130 / cop_lo
M2_hi = e["EB"] - 130 / cop_hi
add("7", "M2 saving COP 2.5 (GWh/y)", 93, M2_lo, "145 - 130/COP (heat pump electricity replaces 145 boiler GWh)")
add("7", "M2 saving COP 3.5 (GWh/y)", 108, M2_hi, "145 - 130/COP")
add("7", "M2 MWh/t low", 0.21, M2_lo * 1000 / PAPER, "93 / 444,494")
add("7", "M2 MWh/t high", 0.24, M2_hi * 1000 / PAPER, "108 / 444,494")
evap50 = dry_solids * (1 / .50 - 1) - PAPER * FIN_MOIST
red = 1 - evap50 / evap_t
add("7", "M3 evaporation reduction (%)", 8, 100 * red, "1 - evap(50%)/evap(48%)", unit=1)
M3_tph = red * PM_TPH
add("7", "M3 steam saved (t/h)", 7.9, M3_tph, "8.27% x 95 t/h")
M3 = M3_tph * STEP
add("7", "M3 saving (GWh/y)", 38, M3, "7.86 t/h x 4.8")
add("7", "M3 MWh/t", 0.09, M3 * 1000 / PAPER, "37.7 / 444,494 = 0.085 (draft rounds 38/444,494 = 0.0855 up to 0.09)")
# combined: M1 + M3 + heat pump on the boiler steam that is left, COP mid-range 3.0
left_tph = BOIL_TPH - 10 - M3_tph
COP_MID = 3.0
comb = M1 + M3 + left_tph * STEP * (1 - 1 / COP_MID)
add("7", "Combined saving (GWh/y)", 126, comb,
    "M1 + M3 + (30.2-10-7.86) t/h x 4.8 x (1 - 1/3.0); equals 145 - 59.3/3.0. COP 3.1 gives 125.9")
add("7", "Combined MWh/t", 0.28, comb * 1000 / PAPER, "125.2 / 444,494")
add("7", "SEC after combined (MWh/t)", 2.98, 1450000 / PAPER - comb * 1000 / PAPER, "3.262 - 0.282")
add("7.1", "Combined in Sec 7.1 (GWh/y)", 126, comb, "same as above")
# 10 % refining cut
REF = 952
cut = .1 * REF
add("7", "10% refining cut saving (GWh/y)", 95, cut, "10% x 952 GWh TMP refiners (Appendix B); 10% of 1015 would be 101.5")
lost = .1 * E_TMP_STEAM / (E_EP_STEAM / e["EB"])
add("7", "Extra boiler electricity to replace lost steam (GWh/y)", 47.5, lost,
    "10% x 430 GWh steam / (130/145 steam per boiler GWh); draft says 'about half of 95'", unit=1)
add("7", "Fraction of saving lost (%)", 50, 100 * lost / cut, "48 / 95", unit=1)

# ---- appendix ----
aux = .150 * 421883 / 1000
add("App B", "TMP auxiliary drives", 63, aux, "150 kWh/t x 421,883 t")
add("App B", "TMP refiners", 952, e["TMP"] - aux, "1015 - 63.3")
add("App B", "Paper machines", 196, e["PM"] - 21.6, "217.5 - bleaching 21.6")
add("App B", "WWTP", 22, 2.5 * 8760 / 1000, "2.5 MW x 8760 h")
add("App B", "Bleaching", 22, 3 * 7200 / 1000, "3 MW x 7200 h")
add("App B", "Wood handling", 18, 2.5 * 7200 / 1000, "2.5 MW x 7200 h")
add("App B", "Internal grid losses", 15, 14.5, "1% x 1450")
util = e["OTH"] - 2.5 * 8760 / 1000 - 18 - 14.5
add("App B", "Utilities and other", 18, util, "72.5 - WWTP 21.9 - wood 18 - grid 14.5")
add("App B", "Total of printed rows", 1450, 952 + 63 + 196 + 145 + 22 + 22 + 18 + 18 + 15, "sum of printed rows (=1451)")
add("App B", "TMP refiners share (%)", 65.6, 100 * (e["TMP"] - aux) / 1450, "951.7/1450")
add("App B", "TMP aux share (%)", 4.4, 100 * aux / 1450, "63.3/1450")
add("App B", "PM share (%)", 13.5, 100 * (e["PM"] - 21.6) / 1450, "195.9/1450")
add("App B", "Utilities share (%)", 1.2, 100 * util / 1450, "18.1/1450")
add("App A", "Effluent volume Mm3", 7.29, 6.68 + 0.61, "6.68 + 0.61")
add("App A", "Production hours", 7200, (285 * 24 + 314 * 24) / 2, "mean of PM11 285 d and PM12 314 d x 24 h (=7188)")

df = pd.DataFrame(rows, columns=["section", "item", "draft_value", "reproduced_value", "abs_diff", "formula", "status"])
OUT.parent.mkdir(exist_ok=True)
df.to_csv(OUT, index=False)
print(df.status.value_counts().to_string())
print(df[df.status != "match"][["section", "item", "draft_value", "reproduced_value", "status"]].to_string())
