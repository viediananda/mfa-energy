"""Run the model end to end: Monte Carlo, tables (reports/tables/model_*.csv, headline.csv)
and figures (reports/figures/model_*). The notebook notebooks/02_model.ipynb calls the same
`build_all()` after walking through the steps.

    uv run python analysis/run_model.py
"""
from hallsta_mfa.outputs import build_all

if __name__ == '__main__':
    out = build_all()
    print(out['head'][['unit', 'base', 'P5', 'P50', 'P95']].round(2).to_string())
