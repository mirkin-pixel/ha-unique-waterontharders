## What and why

<!-- What changes, and what it is for. Link the issue or discussion if there is one. -->

## Checklist

- [ ] `ruff check .`, `ruff format --check .`, `mypy` and `pytest --cov` pass, coverage floor included.
- [ ] A new behaviour comes with the test that pins it down.
- [ ] Text a user sees is in English in `strings.json` and `translations/en.json`, and in Dutch in `translations/nl.json`.
- [ ] A change to `README.md` has its counterpart in `docs/nl/README.md`. No Dutch? Put the English text in the Dutch page and say so here; it gets translated before the merge.
- [ ] Nothing in [what a version number promises](https://github.com/mirkin-pixel/ha-unique-waterontharders/blob/main/CONTRIBUTING.md#what-a-version-number-promises) breaks: no unique ID renamed, no entity removed or changed in what it measures.
