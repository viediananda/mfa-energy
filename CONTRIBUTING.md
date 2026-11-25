# Contributing

## Setup

```bash
uv sync
```

## Test and lint

```bash
uv run pytest
uv run ruff check src tests analysis
```

Do not run `ruff format`; the code uses compact one-liners on purpose.

## Regenerate outputs

```bash
uv run python analysis/run_model.py
```

This rewrites the tables in `reports/tables` and the figures in `reports/figures`.

## Change an input

1. Edit the value in `BASE` in `src/hallsta_mfa/model.py`. If it is uncertain, edit its distribution in `DIST` too.
2. Add or update its row in `INPUT_META` in `src/hallsta_mfa/outputs.py`.
3. Cite a source id from `data/sources.csv` (add a row there if the value is new).
4. If the value is a class C or D assumption, record it in `docs/assumptions.md`.
5. Regenerate the outputs and run the tests.

## Pinned values

`tests/test_model.py::test_headline_values_pinned` pins the headline results. Change those numbers only on purpose, when a model or input change is meant to move them, and say so in the PR.

## Pull requests

Fork the repo, create a branch, make the change, and open a pull request against `main`. Describe what changed and why, and note any change to the headline numbers. CI runs lint, tests and a notebook smoke run.
