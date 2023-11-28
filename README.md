# Python: TechnoVE API Client

[![GitHub Release][releases-shield]][releases]
[![License][license-shield]](LICENSE)

[![Build Status][build-shield]][build]
[![Code Coverage][codecov-shield]][codecov]
[![Open in Dev Containers][devcontainer-shield]][devcontainer]

Asynchronous Python client for TechnoVE charging station.

## About

`python-technove` (aka `pytechnove`) is a Python 3.11, `asyncio`-driven interface
to the unofficial TechnoVE charger API from TechnoVE.\
This is originally meant to be integrated into Home Assistant, but can be used anywhere.

## Usage

```python
import asyncio

from technove import TecnnoVE


async def main() -> None:
    """Show example on controlling your TecnnoVE station."""
    async with WLED("192.168.1.10") as technove:
        station = await technove.update()
        print(station.info.version)


if __name__ == "__main__":
    asyncio.run(main())
```

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality.

Releases are based on [Semantic Versioning][semver], and use the format
of `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented
based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

Thank you for being involved!

## Setting up development environment

The easiest way to start, is by opening a CodeSpace here on GitHub, or by using
the [Dev Container][devcontainer] feature of Visual Studio Code.

[![Open in Dev Containers][devcontainer-shield]][devcontainer]

This Python project is fully managed using the [Poetry][poetry] dependency
manager. But also relies on the use of NodeJS for certain checks during
development.

You need at least:

- Python 3.11+
- [Poetry][poetry-install]
- NodeJS 20+ (including NPM)

To install all packages, including all development requirements:

```bash
npm install
poetry install
```

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## Authors & contributors

The original setup of this repository is by [Christophe Gagnier][moustachauve].

Credits to [@frenck][frenck] for the base structure and classes of this library
based on [python-wled][python-wled].\
The license of python-wled can be found in
[third_party/python-wled/LICENSE](third_party/python-wled/LICENSE).

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## Disclaimer

This project is not an official Google project. It is not supported by
Google and Google specifically disclaims all warranties as to its quality,
merchantability, or fitness for a particular purpose.

Google Play and the Google Play logo are trademarks of Google LLC.

[build-shield]: https://github.com/Moustachauve/pytechnove/actions/workflows/tests.yaml/badge.svg
[build]: https://github.com/Moustachauve/pytechnove/actions/workflows/tests.yaml
[codecov-shield]: https://codecov.io/gh/Moustachauve/pytechnove/branch/main/graph/badge.svg
[codecov]: https://codecov.io/gh/Moustachauve/pytechnove
[contributors]: https://github.com/Moustachauve/pytechnove/graphs/contributors
[devcontainer-shield]: https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode
[devcontainer]: https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Moustachauve/pytechnove
[moustachauve]: https://github.com/Moustachauve
[frenck]: https://github.com/frenck
[python-wled]: https://github.com/frenck/python-wled/
[license-shield]: https://img.shields.io/github/license/Moustachauve/pytechnove.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2023.svg
[poetry-install]: https://python-poetry.org/docs/#installation
[poetry]: https://python-poetry.org
[pre-commit]: https://pre-commit.com/
[releases-shield]: https://img.shields.io/github/release/Moustachauve/pytechnove.svg
[releases]: https://github.com/Moustachauve/pytechnove/releases
[semver]: http://semver.org/spec/v2.0.0.html
