import numpy as np
import pytest

from hallsta_mfa.mc import evaluate, run_mc, sample
from hallsta_mfa.measures import evaporated_water
from hallsta_mfa.model import BASE, DIST, PROCS, f_sens, ppf, run, steam_v

ELEC = ["el_TMP", "el_PM", "el_bleach", "el_EB", "el_wood", "el_wwtp", "el_util", "el_dist"]


@pytest.fixture(scope="module")
def b():
    return evaluate(dict(BASE))


@pytest.fixture(scope="module")
def mc():
    return run_mc(10_000, 2023)


def test_exergy_factor_is_zero_at_dead_state_and_grows_with_temperature():
    assert f_sens(7.0, 7.0) == 0.0
    assert 0 < f_sens(35, 7) < f_sens(60, 7) < f_sens(90, 7) < 1


def test_steam_properties():
    dh, fx = steam_v(3.4e5, 90.0, 7.0)
    assert dh == pytest.approx(0.6537, abs=1e-3)      # 2.35 GJ/t
    assert fx == pytest.approx(0.3147, abs=1e-3)
    import CoolProp.CoolProp as CP
    assert CP.PropsSI("T", "P", 3.4e5, "Q", 1, "Water") - 273.15 == pytest.approx(138, abs=1)  # Holmen: 138 C


# ---- balances
def test_electricity_balance_closes(b):
    assert sum(b[k] for k in ELEC) == pytest.approx(BASE["E_tot"])


def test_steam_balance_closes(b):
    assert b["st_supply"] == pytest.approx(b["st_PM"] + b["st_wood"] + b["st_loss"] + b["st_HW"])


def test_energy_closure_includes_cooling_water_and_diesel(b):
    assert b["E_in"] == pytest.approx(BASE["E_tot"] + BASE["diesel"])
    assert b["E_in"] == pytest.approx(b["sink_water"] + b["sink_cool"] + b["sink_DH"] + b["sink_air"])
    assert b["sink_cool"] == pytest.approx(4.0e6*4.17*10/3.6e6)


def test_exergy_balance_per_process(b):
    for p in PROCS:
        assert b[f"Xin|{p}"] == pytest.approx(b[f"Xuse|{p}"] + b[f"Xwaste|{p}"] + b[f"Xdest|{p}"])


def test_plant_exergy_closure(b):
    # destroyed + waste + useful hot water = exergy input (electricity; diesel excluded)
    assert b["Xdest_total"] + b["Xwaste_total"] + b["Xuse|Hot water & heating"] == pytest.approx(BASE["E_tot"])


# ---- physical bounds
def test_base_physical_bounds(b):
    assert b["st_HW"] >= 0 and b["el_util"] >= 0
    assert b["eff_EB"] <= 1
    for p in PROCS:
        assert b[f"Xdest|{p}"] >= -1e-9
        assert 0 <= b[f"psi|{p}"] <= 1


def test_mc_physical_bounds(mc):
    Y = mc.Y
    assert (Y.eff_EB <= 1).all()
    assert (Y.el_util >= -1e-9).all()
    for p in PROCS:
        assert ((Y[f"psi|{p}"] >= 0) & (Y[f"psi|{p}"] <= 1 + 1e-12)).all()
    acc = Y[mc.ok]
    assert (acc.st_HW >= 0).all()
    assert (acc[[f"Xdest|{p}" for p in PROCS]] >= -1e-9).all().all()


def test_base_inside_every_dist_range():
    for k, (d, a, bb, c) in DIST.items():
        lo, hi = ppf(k, 0.0001), ppf(k, 0.9999)
        assert lo <= BASE[k] <= hi, k
        if d == "tri":
            assert a <= BASE[k] <= c, k
        if d == "uni":
            assert a <= BASE[k] <= bb, k


def test_k_guard_rarely_binds(mc):
    # sh_OTH lower bound 4.5 % sits just above the named items (about 3.75 % at base)
    assert mc.k_binding_rate < 0.02


def test_acceptance_rate_is_high(mc):
    assert 0.95 < mc.acceptance <= 1.0


def test_mc_reproducible():
    a, c = sample(200, 7), sample(200, 7)
    assert all(np.array_equal(a[k], c[k]) for k in a)
    r1, r2 = run_mc(300, 5), run_mc(300, 5)
    assert np.array_equal(r1.Y.Xdest_total.values, r2.Y.Xdest_total.values)


def test_run_accepts_arrays_for_steam_inputs():
    rng = np.random.default_rng(0)
    P = dict(BASE, p_steam=rng.uniform(3.3e5, 3.6e5, 50), T_cond=rng.uniform(80, 100, 50), sh_TMP=rng.uniform(0.6, 0.75, 50))
    r = run(P)
    assert np.allclose(sum(r[k] for k in ELEC), BASE["E_tot"])
    assert (r["eff_EB"] <= 1).all()


# ---- measures
def test_measures_never_exceed_boiler_electricity(b, mc):
    for src in (b, mc.Y):
        for m in ("M1", "M1b", "M2", "M3", "M3b", "M4"):
            assert (np.asarray(src[m]) <= np.asarray(src["el_EB"]) + 1e-9).all(), m
            assert (np.asarray(src[m]) >= -1e-9).all(), m
    assert (mc.Y.M4_steam_left >= -1e-9).all()


def test_m3_matches_water_balance():
    W = evaporated_water(444494, 0.48, 0.07)
    assert W == pytest.approx(416_700, rel=1e-3)   # group draft figure


def test_m4_is_below_sum_of_parts_plus_cap(b):
    assert b["M4"] <= b["el_EB"]
    assert b["M4"] >= max(b["M1"], b["M3"])


# ---- pinned headline values (update deliberately)
def test_headline_values_pinned(b):
    assert b["el_TMP"] == pytest.approx(1015.0)
    assert b["el_EB"] == pytest.approx(145.0)
    assert b["dh"] == pytest.approx(0.6537, abs=1e-4)
    assert b["st_rec"] == pytest.approx(470.7, abs=0.1)
    assert b["st_PM"] == pytest.approx(447.1, abs=0.1)
    assert b["st_HW"] == pytest.approx(134.1, abs=0.2)
    assert b["sink_water"] == pytest.approx(232.9, abs=0.1)
    assert b["sink_cool"] == pytest.approx(46.3, abs=0.1)
    assert b["sink_air"] == pytest.approx(1161.7, abs=0.2)
    assert b["SEC_TMP"] == pytest.approx(2405.9, abs=0.1)
    assert b["save_rec90"] == pytest.approx(82.5, abs=0.1)
    assert b["Xdest_total"] == pytest.approx(1333.3, abs=0.2)
    assert b["y_EB_implied"] == pytest.approx(1.5, abs=0.01)
    assert b["M2"] == pytest.approx(97.6, abs=0.1)
    assert b["M3"] == pytest.approx(37.7, abs=0.1)
    assert b["M4"] == pytest.approx(125.6, abs=0.2)


def test_scenario_switches(b):
    s5 = evaluate({**BASE, "dh_override": 2.15/3.6})
    assert s5["dh"] == pytest.approx(0.5972, abs=1e-3)
    assert s5["st_rec"] < b["st_rec"]
    s6 = evaluate({**BASE, "sec_TMP_override": 2150.0})
    assert s6["SEC_TMP"] == pytest.approx(2150.0)
    assert sum(s6[k] for k in ELEC) == pytest.approx(BASE["E_tot"])
    assert s6["el_util"] > b["el_util"] + 50
