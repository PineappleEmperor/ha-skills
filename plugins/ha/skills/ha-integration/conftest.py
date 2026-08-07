"""Keep pytest out of templates/ when it runs in the skill repo.

`templates/conftest.py` is an artefact shipped to consuming integrations, where
its first statement — `import custom_components` — is correct and load-bearing.
In *this* repo there is no such package, so letting pytest descend into
templates/ loads that file as a real conftest and aborts collection with
`ModuleNotFoundError: No module named 'custom_components'`.

Ignoring the directory keeps `pytest` usable at the repo root. To actually run
`templates/tests/test_manifest_gate.py`, build a fixture that has a
custom_components package — `evals/make_fixture.sh 02` copies both the gate and
its test into one.
"""

collect_ignore = ["templates"]
