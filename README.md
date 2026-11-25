# hallsta-mfa

Electricity energy and exergy flow analysis (MFA) of the Holmen Hallsta paper mill, 2023, with Monte Carlo uncertainty.
Made for a university Material Flow Analysis course (MFA Group 2).

## What it does

- Builds an electricity balance for the mill and follows it through to heat, steam and effluent.
- Computes energy and exergy flows, and exergy destruction per process.
- Propagates input uncertainty with a constrained Monte Carlo and ranks inputs by sensitivity.
- Evaluates four improvement measures (M1-M4) and a set of sensitivity scenarios.
- Writes all result tables and figures, including Sankey diagrams.

The baseline is aligned with the group report draft: steam is counted at its latent heat (2.15 GJ/t), boiler steam comes from Holmen's 1.5 t/MWh (130 GWh), effluent is 32 C, PM waste heat 55 C, and the Monte Carlo ranges follow the draft's Table 6.2. Headline base results: exergy destroyed 1,328 GWh/y (91.6 % of input), TMP 802 / paper machines 290 / electric boilers 100 GWh, effluent heat 212 GWh, unallocated steam 123 GWh, measures M1 48.0, M2 97.6, M3 37.7, M4 125.6 GWh/y. The earlier property-based steam convention (2.35 GJ/t, boiler 98 %) is kept as sensitivity case S5. See `docs/assumptions.md` (section "Alignment with the group draft").

Start with `notebooks/02_model.ipynb`. It explains every step: intuition first, then the formula, then the code, with a glossary at the top. GitHub renders it with all outputs, so you can read it without running anything.

## Quickstart

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh   # once, if you do not have uv
uv sync                                          # installs Python 3.12 and every dependency
uv run python analysis/run_model.py              # Monte Carlo, all tables (reports/tables) and figures (reports/figures)
uv run jupyter lab notebooks/02_model.ipynb      # the explained walkthrough
uv run pytest                                    # tests for the model
```

Re-execute and save the notebook from the command line (it also rewrites the tables and figures):

```bash
cd notebooks && uv run jupyter nbconvert --to notebook --execute --inplace 02_model.ipynb
```

The static Sankey PNGs need Chrome (used by kaleido). Install one with `uv run plotly_get_chrome`. Without Chrome everything still runs, the PNG is skipped and the Sankey HTML is written.

## Change an input / run a scenario

Edit the value in `BASE` in `src/hallsta_mfa/model.py`, or evaluate one case without editing files:

```python
from hallsta_mfa.model import BASE
from hallsta_mfa.mc import evaluate

evaluate({**BASE, 'm_PM': 110.0})
```

The predefined sensitivity cases are in the `SCENARIOS` dict in `src/hallsta_mfa/outputs.py`. See `CONTRIBUTING.md` for the full steps to change an input.

## Outputs

`uv run python analysis/run_model.py` writes tables to `reports/tables/` (`model_*.csv`, `headline.csv`; `model_exits_draft_format.csv` reproduces the draft's Table 2) and figures to `reports/figures/` (`model_*`, PNG, Sankey also HTML).

## Layout

| Path | What |
|---|---|
| `notebooks/02_model.ipynb` | The model, step by step (intuition, formula, code) |
| `notebooks/01_eda.ipynb` | Exploratory data analysis |
| `src/hallsta_mfa/model.py` | The balance: base inputs, uncertainty ranges (`DIST`), exergy maths, `run()` |
| `src/hallsta_mfa/mc.py` | Constrained Monte Carlo (`sample`, `run_mc`) |
| `src/hallsta_mfa/measures.py` | Improvement measures M1-M4 |
| `src/hallsta_mfa/outputs.py` | All tables and figures of the model |
| `src/hallsta_mfa/plotstyle.py` | Shared figure style |
| `analysis/run_model.py` | One script that writes every model output |
| `tests/test_model.py` | Balance, physical-bound, closure, measure and reproducibility tests |
| `data/` | Source register `sources.csv` (every source value with an id) |
| `reports/tables/model_*.csv`, `headline.csv` | Model results (`model_exits_draft_format.csv` reproduces the draft's Table 2) |
| `reports/figures/model_*` | Model figures (PNG, Sankey also HTML) |
| `docs/assumptions.md` | Every class C/D assumption and modelling decision |
| `docs/review/` | Model audit and change log |
| `resources/` | Third-party Holmen source documents and course Q&A (reference only) |
| `LICENSE`, `LICENSE-DATA` | MIT (code), CC-BY-4.0 (data, docs, generated outputs) |
| `CITATION.cff` | Citation metadata |
| `CONTRIBUTING.md`, `CHANGELOG.md` | How to contribute, release notes |
| `.github/workflows/ci.yml` | CI: lint, tests, notebook smoke run |

## Sources and data

Numbers come from Holmen Paper AB, *Miljorapport 2023 Hallsta pappersbruk* (MR2023), and Holmen's answers to student questions (2019, 2025). Only the numbers needed for the calculation are in `data/sources.csv`, each with a reference. The source documents are in `resources/`. They are third-party documents included for reference and are not covered by the licence of this repo.

## Citation

See `CITATION.cff`.

## Licence

Code: MIT (`LICENSE`). Data, docs and generated tables and figures: CC-BY-4.0 (`LICENSE-DATA`). Not covered by either licence: `resources/` (Holmen Paper AB documents and course Q&A) and `reports/*.docx`, `reports/*.pdf`; rights stay with their owners.

## Contributing

See `CONTRIBUTING.md`.
