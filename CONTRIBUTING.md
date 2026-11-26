# Contributing

This file is for people working on the integration. If you are looking for how to install or configure it, that is the [README](README.md), which is the page HACS shows. The README has an English and a Dutch section side by side: a change to one belongs in the other. If you do not write Dutch, put your English text in the Dutch section as well and say so in the pull request; it is translated before the merge.

Contributions are welcome. For anything larger than a fix, an [idea in Discussions](https://github.com/mirkin-pixel/ha-unique-waterontharders/discussions/new?category=ideas) first is appreciated, so nobody writes the same thing twice.

## Getting set up

Python 3.14 or newer, and nothing else:

```bash
python -m venv .venv
. .venv/bin/activate          # .venv\Scripts\Activate.ps1 on Windows
pip install -r requirements_test.txt
```

There is no Home Assistant installation to keep alongside this. The tests bring their own through [pytest-homeassistant-custom-component](https://github.com/MatthewFlamm/pytest-homeassistant-custom-component), which pins the Home Assistant version they run against.

## Checks

```bash
ruff check .        # style and imports
ruff format .       # layout; CI runs it with --check
mypy                # types, over custom_components/unique_waterontharder
pytest --cov        # tests, and the coverage floor
```

The tests run on Windows too, even though Home Assistant itself only ever runs on Linux and imports two modules CPython ships on POSIX alone. `pytest_windows.py` stands in for `fcntl` and `resource`, and lets the event loop have the loopback socket pair it wakes itself over, which `pytest-socket` would otherwise refuse. It is loaded through `addopts` in `pyproject.toml` and does nothing at all on Linux, so the same `pytest` runs in both places.

Coverage has a floor of 95% over `custom_components/unique_waterontharder`, set in `pyproject.toml`. It is a floor rather than a target: a new branch of behaviour is expected to arrive with the test that pins it down.

Every test also fails when Home Assistant reports that this integration uses something on its way out, the warning it logs with the version that will stop it working. So a deprecation is found in CI, not in a user's log.

### The oldest supported Home Assistant

`hacs.json` says which Home Assistant this needs at least: 2026.3. CI runs the tests against that release too, from `tests/oldest/requirements.txt`. That file sits outside the root on purpose: Dependabot updates every requirements file in the root, and a pin it raised would quietly stop testing the oldest release at all. Raising the minimum is allowed in a minor version: change `hacs.json`, the README and `tests/oldest/requirements.txt` together.

### The upcoming Home Assistant

Every Thursday, the day after a beta comes out, the **Upcoming Home Assistant** workflow installs the newest Home Assistant there is, beta included, loads every module against it, type-checks against it and runs the tests. It opens or updates an issue when any of that fails, and can be started by hand as well. The test harness is made for one Home Assistant version and can lag behind; when it cannot even start on the newest one, the run says so in its summary instead of opening an issue, and loading and type-checking still count.

### In CI only

Two more workflow jobs run in CI only, hassfest and HACS validation. They check the manifest and the repository layout rather than the code, so nothing they check changes on a normal code change.

## Translations

**English is the source**, as it is for the rest of Home Assistant. User-facing text lives in `custom_components/unique_waterontharder/strings.json`, and is mirrored into `translations/en.json`; the two are identical, so a change to one belongs in the other. Dutch lives in `translations/nl.json`. Entity names come from `translation_key`, never from a hard-coded `name`.

## What a version number promises

From 1.0 on, the version says whether an upgrade can break something you built. Automations, dashboards and templates lean on the integration in a few places, and those stay as they are until the next major version:

- **Entities keep their identity.** A unique ID is never changed, so the entity ID, its history and anything that refers to it survive every upgrade. An entity is not removed and does not change what it measures or its unit.
- **A configured entry keeps working.** An older entry is migrated in place and never has to be removed and set up again.

What a minor version may do, because none of it breaks what is already there: add entities and options; change a display name or a translation, since the entity ID is not taken from it after setup; and ask for a newer Home Assistant, which HACS checks before it offers the update.

Anything else is a major version, with the change and what to do about it at the top of the release notes. A patch version only fixes what did not work as documented.

## Releases

The standard HACS flow: bump `version` in `manifest.json`, merge to the default branch, then publish a GitHub release with a matching tag, `v1.0.0` for version `1.0.0`. The release workflow checks that the tag matches the manifest version, runs every check a pull request runs on the tagged code, and only then attaches a zip of the integration to the release, with its SHA-256 beside it. HACS installs that zip, so a release whose checks fail gets no zip and cannot be installed: fix the cause, then publish a new release.

Before each release, read what the next Home Assistant changes for custom integrations: the developer blog at developers.home-assistant.io lists it a week ahead, with the beta. Anything that applies is fixed in the release, or noted in its release notes.
