# Lint and quality check

Read this for a hygiene pass over existing integration code, before a commit or a review.

**Every finding is fixed in the code, or suppressed with its reason; none is left for CI to
find.**

## Contents

1. The check
2. Step 1: Run ruff
3. Step 2: Run mypy
4. Step 3: Run the rest of what CI runs
5. Step 4: Check that `quality_scale.yaml` exists
6. Step 5: Check the manifest's key order
7. Step 6: Report

## The check

### Step 1: Run ruff

`ruff check .` and `ruff format --check .`, under the shipped `pyproject.toml`, with ruff at
the version the mypy and ruff row of `reference/freshness.md` names.

| Rule | Value |
|---|---|
| a finding to act on | fixed in the code |
| a finding left on purpose | `# noqa: <code>` on the line, with the reason beside it |

### Step 2: Run mypy

`mypy --config-file mypy.ini custom_components/`, with mypy at the version the same row names.
Fix every finding to act on.

### Step 3: Run the rest of what CI runs

Each job *The three workflows* in ha-integration-ci's README lists:
https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md.

### Step 4: Check that `quality_scale.yaml` exists

If it does not, offer to create it, as `reference/quality-scale.md` says.

### Step 5: Check the manifest's key order

As the key-order row of *Step 4: Write `manifest.json`* in `reference/scaffold.md` gives it.

### Step 6: Report

Files changed · findings fixed · findings suppressed, each with its reason · manual work left.
