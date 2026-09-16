# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A prototype LLM-based simulated patient system for training medical students in clinical
communication. A "patient" LLM role-plays a clinical case (symptoms, history, ideas/concerns/
expectations) against a student's questions, while a separate "examiner" role marks the
resulting transcript against a rubric. Content (cases, personas, prompts, locale rules) is
strictly separated from code and lives under `content/`.

Many modules under `src/simpatia/` are currently **empty placeholder files** left over from the
initial scaffold (e.g. `examiner/grader.py`, `examiner/feedback.py`, `content/registry.py`,
`models/rubric.py`, `models/persona.py`, `models/transcript.py`, `storage/*`, `api/*`, all
`patient/guardrails/*`, `scripts/repl.py`'s siblings). Don't assume behaviour from a filename —
check whether the file actually has content before relying on it existing. The `simpatia.cli:app`
entry point declared in `pyproject.toml` also does not exist yet.

## Commands

Dependency management and running commands is via `uv`.

```bash
uv sync --extra api                 # install deps (matches CI)
uv run ruff check .                 # lint
uv run ruff format --check .        # format check (--check omitted to auto-format)
uv run python scripts/validate_content.py   # validate all case/locale YAML against schemas
uv run pytest -q --cov=simpatia --cov-report=xml   # full test suite with coverage
uv run pytest tests/test_loader.py::test_case_loads   # single test
uv run pytest -m llm                # run tests that hit a real LLM (excluded by default, costs money)
uv run mypy                         # strict type check of src/simpatia
uv run python scripts/repl.py cholecystitis-01 en-GB   # interactive terminal chat with a case
```

A `.pre-commit-config.yaml` runs `ruff-check --fix` and `ruff-format` on commit (`pre-commit` is
not itself a project dependency — install it separately, e.g. `pipx install pre-commit`, then
`pre-commit install`). CI (`.github/workflows/workflow.yml`) runs lint, format check, content
validation, pytest with coverage, and SonarCloud on every push/PR to `main`.

By default `pytest` excludes anything marked `llm` (see `addopts = "-m 'not llm'"` in
`pyproject.toml`) — those tests call a real model endpoint and cost money/require a running
backend.

## Architecture

**Content/code separation.** `src/simpatia/` has no hardcoded clinical content, prompt wording,
or UI strings — those all live in `content/` (see below) and are loaded via
`simpatia.content.loader` / `simpatia.config.get_settings().content_dir`. This is deliberate so
non-engineers can author/edit cases without touching Python, and so content changes don't need a
release.

**The diagnosis-leak boundary.** `models/case.py` (`PatientCase`) is the patient-visible half of
a case: HPI, ICE, background, and disclosure lists (`volunteered_freely`, `if_asked_only`,
`denies`, `does_not_know`) — but deliberately **no diagnosis or mark-scheme field**, and
`ConfigDict(extra="forbid")` on every model so a stray `diagnosis:` key in a case YAML fails
validation instead of silently reaching the patient's prompt. The answer key/rubric is meant to
live under `content/cases/<id>/rubric/<locale>.yaml` and load through a separate path (intended
for `models/rubric.py`, not yet implemented) that the patient-prompt code never touches. When
touching `content/loader.py` or `models/case.py`, preserve this separation —
`tests/test_no_diagnosis_leak.py` encodes it as an invariant.

**Content layout** (`content/`):
- `cases/<case-id>/meta.yaml` — language-neutral facts (age, sex, difficulty, `available_locales`), validated as `CaseMeta`.
- `cases/<case-id>/<locale>.yaml` — patient-visible content per locale, validated as `PatientCase`.
- `cases/<case-id>/rubric/<locale>.yaml` — examiner-only mark scheme (kept out of the patient path).
- `personas/<name>/` — reusable patient personality traits (meta + per-locale), not yet wired into loading.
- `locales/<locale>.yaml` — per-language generation constraints (`max_sentences`, `max_words`, `banned_jargon`, `lid_threshold` for language-detection), validated as `LocaleConfig`.
- `prompts/behaviour_rules.jinja` — shared patient behaviour rules included across locale prompt templates.
- `prompts/<locale>/patient_system.jinja` — locale-specific system prompt template, rendered by `prompting/builder.py`.
- `prompts/<locale>/examiner_system.jinja`, `patient_examples.yaml` — for the examiner role (not yet consumed by code).
- `ui/<locale>.json` — plain UI string lookups for `i18n.t()`, unrelated to case content.

`scripts/validate_content.py` is the authoritative check that every case/locale file parses
against its Pydantic model — run it after adding or editing content, and it must pass in CI.

**Prompt rendering.** `prompting/builder.py` uses its own cached Jinja `Environment` with
`autoescape=False` on purpose: output is plain text fed to an LLM, not HTML, so escaping would
corrupt apostrophes/accents. Any future HTML-rendering environment (e.g. in `api/`) must enable
autoescape — don't share the Jinja environment between the two.

**LLM client abstraction** (`llm/client.py`). `OpenAICompatClient` targets any OpenAI-compatible
endpoint (Ollama, vLLM, LM Studio, OpenRouter, OpenAI) purely by changing `base_url`/`api_key` in
config — there's deliberately no provider-specific branching for that path.
`get_client(role: "patient" | "examiner")` returns a cached per-role singleton built from
`Settings.patient` / `Settings.examiner`. `build_client()` is the non-cached entry point used by
eval harnesses that need to sweep across models/configs.

**Patient vs. examiner LLM configs** (`config.py`) are intentionally different and validated as
such: `PatientLLMConfig` wants variability (temperature 0.7) so students don't get identical
phrasing twice; `ExaminerLLMConfig` forces `temperature=0.0` — a `model_validator` on `Settings`
*raises* if examiner temperature is ever non-zero, because marking must be reproducible for the
same transcript/rubric. Don't loosen this without understanding why it's there. Settings are read
from env vars prefixed `SIMPATIA_` with `__` as the nested delimiter (e.g.
`SIMPATIA_EXAMINER__MODEL`), see `.env.example`.

**`Session` is framework-free** (`patient/session.py`): no FastAPI/HTTP dependency, by design, so
the same class is driven by both the web layer and eval runners/the REPL
(`scripts/repl.py`). Prefer extending `Session` itself over duplicating conversation-turn logic in
a route handler or eval script.

## Locales

Currently `en-GB` and `es-ES`. Every case must declare its supported locales in `meta.yaml`
(`available_locales`), and a matching `<locale>.yaml` file must exist —
`tests/test_no_diagnosis_leak.py::test_declared_locales_exist` and
`scripts/check_locale_coverage.py` check this. When adding a new case or locale, keep
`meta.yaml`, the per-locale content file, the per-locale rubric, and the prompt templates in sync.
