# Lint and quality check

Read this for a hygiene pass over existing integration code, before a commit or a review.

**Every finding is fixed in the code; only a ruff finding left on purpose carries `# noqa` and
its reason, only an aligned table a `# fmt: off` fence, and none is left for CI to find.**

## Contents

1. The check
2. Step 1: Run ruff
3. Step 2: Run mypy
4. Step 3: Run the rest of what CI runs
5. Step 4: Check that `quality_scale.yaml` exists
6. Step 5: Check the manifest's key order
7. Step 6: Report
8. Cases
9. Alignment a human chose meets `ruff format` — Step 1

## The check

### Step 1: Run ruff

`ruff check .` and `ruff format --check .`, under the shipped `pyproject.toml`, with ruff at
the version the mypy and ruff row of `reference/freshness.md` names.

| Rule | Value |
|---|---|
| a finding to act on | fixed in the code |
| a finding left on purpose | `# noqa: <code>` on the line, with the reason beside it |
| a table someone aligned, which `ruff format` would flatten | fenced — *Alignment a human chose meets `ruff format` — Step 1* |

### Step 2: Run mypy

`mypy --config-file mypy.ini custom_components/`, with mypy at the version the same row names.
Fix every finding in the code, as *Step 4: Type it, and suppress nothing* in
`reference/patterns.md` requires.

### Step 3: Run the rest of what CI runs

Each job *The three workflows* in ha-integration-ci's README lists:
https://raw.githubusercontent.com/PineappleEmperor/ha-integration-ci/main/README.md.

| Rule | Value |
|---|---|
| the local hooks | `PREK_SKIP=no-commit-to-branch prek run --all-files`, with the tool and wrapper *Step 6: Copy the config and CI files* in `reference/scaffold.md` gives; the skip drops the guard on `main`, which fails every run on that branch, as CI drops it |

### Step 4: Check that `quality_scale.yaml` exists

If it does not, write it before anything else, as *Step 1: Scaffold `quality_scale.yaml` from
the start* in `reference/quality-scale.md` says.

### Step 5: Check the manifest's key order

As the key-order row of *Step 4: Write `manifest.json`* in `reference/scaffold.md` gives it.

### Step 6: Report

Files changed · findings fixed · findings suppressed, each with its reason · manual work left.

## Cases

### Alignment a human chose meets `ruff format` — Step 1

`ruff format` reduces every run of spaces to one, which destroys a table someone aligned so
it could be read as a table. Fence it rather than surrendering it or turning the formatter
off:

```python
# fmt: off
CONF_EMAIL         = "email"
CONF_API_KEY       = "api_key"
CONF_REFRESH_TOKEN = "refresh_token"
# fmt: on
```

| Rule | Value |
|---|---|
| what the fence stops | the formatter only — `ruff check` still runs inside it, so line length, import order and unused names are all still caught |
| what you give up | whitespace normalisation, which is what you are overriding |
| scope | statement-level: one inside a dict or call literal does nothing, so it wraps the whole enclosing statement at that statement's indent |
| `# fmt: on` | never at a different indent from its `# fmt: off` |
| which statement | the smallest one containing the table, never a class body and never a file |
| the column | one per block, set one space past the longest key, spaces only and never tabs; a new block restarts it |
| an entry too long for the column | re-pad the whole block, in the same commit |
| a generator that emits a fenced table | emits the fence too, or the next regeneration drops it |

**What earns a fence:**

- Padding before `=` or `:`.
- Padding after them, where the values form the column.
- Padding after `,`.
- One row or record per source line, even where nothing is padded — glyph rasters, icon bitmaps, colour palettes, layout tables, field-descriptor lists.
- Not a flat wrapped list of strings, which is not a table; leave that to the formatter.

**Symptom:** an unfenced raster or bitmap table comes back one element per line, and the
shape a reader could see in the source is gone.
