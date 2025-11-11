# Repository Guidelines

## Project Structure & Module Organization
- Entrypoints: `run_pipeline.py`, `run_vision_analysis.py`, `validate_images.py`, `setup_pipeline.py`.
- Utilities: `scripts/` (e.g., `build_manifest_strict.py`, `validate_pack.py`, `make_previews_and_augment_json.py`).
- Packs & config: `ArBot-Vision-Pack_v0.7.1/` (`modules/*.json`, `prompts/`, `schemas/`, `controlpanel.json`) and root `manifest.json`.
- Outputs: `pipeline_output/`, `reports/`. Source materials in `docs/`.

## Build, Test, and Development Commands
- Create venv (Win): `python -m venv .venv && .\.venv\Scripts\activate`
- Create venv (Unix): `python3 -m venv .venv && source .venv/bin/activate`
- Install: `pip install -r requirements.txt` (if present) + `pip install -U openai requests pytest`.
- Run pipeline: `python run_pipeline.py --manifest manifest.json` → writes to `pipeline_output/`.
- Vision analysis: `python run_vision_analysis.py --pack ArBot-Vision-Pack_v0.7.1`.
- OAuth batch (GPT‑4o): `python gpt4o_batch_analysis_oauth.py --images-dir images --limit 10`.
- Validate pack: `python scripts/validate_pack.py --pack ArBot-Vision-Pack_v0.7.1`.

## Coding Style & Naming Conventions
- Python: PEP8, 4 spaces, type hints where helpful.
- Names: `snake_case` (files/functions), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants).
- Use `pathlib` for paths, no side effects at import. Keep modules focused and small.
- JSON: preserve key order/indent; avoid trailing commas.

## Testing Guidelines
- Smoke checks: `python -m compileall .`, `python validate_images.py`, `python scripts/validate_pack.py`.
- Add `tests/` with `pytest` when adding logic. Test files: `test_*.py`. Run: `pytest -q`.
- Prefer fixture data under `docs/` or a `tests/data/` subfolder.

## Commit & Pull Request Guidelines
- Commits: imperative mood + scope (e.g., `feat: add pack validator`). Reference issues (`#123`).
- PRs: summary, motivation, affected paths, example commands, and links to outputs (e.g., `pipeline_output/pipeline_summary.json`).
- Do not commit large binaries/secrets; redact sensitive data in reports.

## Security & Configuration Tips
- Config surfaces: `manifest.json`, `ArBot-Vision-Pack_v0.7.1/controlpanel.json`.
- OAuth: set `OPENAI_CLIENT_ID`, `OPENAI_CLIENT_SECRET`, `OPENAI_REDIRECT_URI` in `.env.local`; tokens stored in `.oauth/`.
- Prefer repo‑relative paths and small sample runs before full analysis.

