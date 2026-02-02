"""UV Migrator Core - Migration tool for init.yaml to pyproject.toml conversion.

This module provides tools to migrate ADHD framework modules from the legacy
init.yaml format to pyproject.toml format compatible with uv workspaces.
"""

from __future__ import annotations

from .uv_migrator_core import (
    UVMigratorCore,
    MigrationResult,
    MigrationReport,
)
from .migrator import (
    parse_init_yaml,
    parse_requirements_txt,
    github_url_to_package_name,
    convert_requirements,
    infer_layer,
    generate_pyproject_toml,
)

__all__ = [
    "UVMigratorCore",
    "MigrationResult",
    "MigrationReport",
    "parse_init_yaml",
    "parse_requirements_txt",
    "github_url_to_package_name",
    "convert_requirements",
    "infer_layer",
    "generate_pyproject_toml",
]
