from __future__ import annotations

from pathlib import Path

import pytest

from commitizen.changelog import Metadata
from commitizen.changelog_formats.markdown import Markdown
from commitizen.config.base_config import BaseConfig

CHANGELOG_A = """
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
- Start using "changelog" over "change log" since it's the common usage.

## [1.0.0] - 2017-06-20
### Added
- New visual identity by [@tylerfortune8](https://github.com/tylerfortune8).
- Version navigation.
""".strip()

EXPECTED_A = Metadata(
    latest_version="1.0.0",
    latest_version_position=10,
    unreleased_end=10,
    unreleased_start=7,
)


CHANGELOG_B = """
## [Unreleased]
- Start using "changelog" over "change log" since it's the common usage.

## 1.2.0
""".strip()

EXPECTED_B = Metadata(
    latest_version="1.2.0",
    latest_version_position=3,
    unreleased_end=3,
    unreleased_start=0,
)


CHANGELOG_C = """
# Unreleased

## v1.0.0
"""
EXPECTED_C = Metadata(
    latest_version="1.0.0",
    latest_version_position=3,
    unreleased_end=3,
    unreleased_start=1,
)

CHANGELOG_D = """
## Unreleased
- Start using "changelog" over "change log" since it's the common usage.
"""

EXPECTED_D = Metadata(
    latest_version=None,
    latest_version_position=None,
    unreleased_end=2,
    unreleased_start=1,
)


@pytest.fixture
def format(config: BaseConfig) -> Markdown:
    return Markdown(config)


VERSIONS_EXAMPLES = [
    ("## [1.0.0] - 2017-06-20", "1.0.0"),
    (
        "# [10.0.0-next.3](https://github.com/angular/angular/compare/10.0.0-next.2...10.0.0-next.3) (2020-04-22)",
        "10.0.0-next.3",
    ),
    ("### 0.19.1 (Jan 7, 2020)", "0.19.1"),
    ("## 1.0.0", "1.0.0"),
    ("## v1.0.0", "1.0.0"),
    ("## v1.0.0 - (2012-24-32)", "1.0.0"),
    ("# version 2020.03.24", "2020.03.24"),
    ("## [Unreleased]", None),
    ("All notable changes to this project will be documented in this file.", None),
    ("# Changelog", None),
    ("### Bug Fixes", None),
]


@pytest.mark.parametrize("line_from_changelog,output_version", VERSIONS_EXAMPLES)
def test_changelog_detect_version(
    line_from_changelog: str, output_version: str, format: Markdown
):
    version = format.parse_version_from_title(line_from_changelog)
    assert version == output_version


TITLES_EXAMPLES = [
    ("## [1.0.0] - 2017-06-20", 2),
    ("## [Unreleased]", 2),
    ("# Unreleased", 1),
]


@pytest.mark.parametrize("line_from_changelog,output_title", TITLES_EXAMPLES)
def test_parse_title_type_of_line(
    line_from_changelog: str, output_title: str, format: Markdown
):
    title = format.parse_title_level(line_from_changelog)
    assert title == output_title


@pytest.mark.parametrize(
    "content, expected",
    (
        pytest.param(CHANGELOG_A, EXPECTED_A, id="A"),
        pytest.param(CHANGELOG_B, EXPECTED_B, id="B"),
        pytest.param(CHANGELOG_C, EXPECTED_C, id="C"),
        pytest.param(CHANGELOG_D, EXPECTED_D, id="D"),
    ),
)
def test_get_matadata(
    tmp_path: Path, format: Markdown, content: str, expected: Metadata
):
    changelog = tmp_path / format.default_changelog_file
    changelog.write_text(content)

    assert format.get_metadata(str(changelog)) == expected
