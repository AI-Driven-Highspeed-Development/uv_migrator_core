"""
UV Migrator Core - Migration tool for init.yaml to pyproject.toml conversion.

This module provides tools to migrate ADHD framework modules from the legacy
init.yaml format to pyproject.toml format compatible with uv workspaces.
"""

from __future__ import annotations

import os
import sys

# Path setup for module imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.getcwd()
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from cores.uv_migrator_core.uv_migrator_core import (
    UVMigratorCore,
    MigrationResult,
    MigrationReport,
)
from cores.uv_migrator_core.migrator import (
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
