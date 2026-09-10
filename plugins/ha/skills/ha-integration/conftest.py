"""Keep pytest out of templates/ when it runs in the skill repo.

`templates/conftest.py` is an artefact shipped to consuming integrations, where
its first statement — `import custom_components` — is correct and load-bearing.
In *this* repo there is no such package, so letting pytest descend into
templates/ loads that file as a real conftest and aborts collection with
`ModuleNotFoundError: No module named 'custom_components'`.

Ignoring the directory keeps `pytest` usable at the repo root. `templates/` ships
no test of its own any more: the scripts a scaffold used to copy now live in the
CI repositories, and their suites run there.
"""

collect_ignore = ["templates"]
