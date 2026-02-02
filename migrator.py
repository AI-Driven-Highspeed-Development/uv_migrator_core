"""
Migration logic for converting init.yaml to pyproject.toml.

This module contains the core conversion functions for:
- Parsing init.yaml and requirements.txt
- Converting GitHub URLs to package names
- Splitting requirements into dependencies and uv.sources
- Inferring layer from module type
- Generating pyproject.toml content
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional
from urllib.parse import urlparse

from logger_util import Logger
from yaml_reading_core.yaml_reading import YamlReadingCore as YamlReader

from .templates import generate_pyproject_content


# Layer inference defaults by module type
LAYER_DEFAULTS: dict[str, str] = {
    "core": "foundation",
    "util": "foundation",
    "manager": "runtime",
    "plugin": "runtime",
    "mcp": "dev",
}

# Known dev-only cores that should override the foundation default
DEV_CORES: set[str] = {
    "module_creator_core",
    "project_creator_core",
    "questionary_core",
    "uv_migrator_core",  # This module itself is dev-only
}


def parse_init_yaml(module_path: Path) -> dict[str, Any]:
    """
    Parse init.yaml from a module directory.
    
    Args:
        module_path: Path to the module directory
        
    Returns:
        Parsed init.yaml content as dict
        
    Raises:
        FileNotFoundError: If init.yaml doesn't exist
        ValueError: If init.yaml is malformed
    """
    init_yaml_path = module_path / "init.yaml"
    
    if not init_yaml_path.exists():
        raise FileNotFoundError(f"No init.yaml found at {init_yaml_path}")
    
    yaml_reader = YamlReader()
    data = yaml_reader.read_yaml(init_yaml_path)
    
    if not isinstance(data, dict):
        raise ValueError(f"init.yaml at {init_yaml_path} is not a valid YAML dict")
    
    return data


def parse_requirements_txt(module_path: Path) -> list[str]:
    """
    Parse requirements.txt from a module directory.
    
    Args:
        module_path: Path to the module directory
        
    Returns:
        List of PyPI requirements (empty if file doesn't exist)
    """
    req_path = module_path / "requirements.txt"
    
    if not req_path.exists():
        return []
    
    requirements = []
    with open(req_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if line and not line.startswith("#"):
                requirements.append(line)
    
    return requirements


def github_url_to_package_name(url: str) -> str:
    """
    Convert a GitHub URL to a package name.
    
    Examples:
        https://github.com/AI-Driven-Highspeed-Development/Logger-Util.git → logger-util
        https://github.com/org/Config-Manager.git → config-manager
        https://github.com/org/session_manager.git → session-manager
        
    Args:
        url: GitHub repository URL
        
    Returns:
        Package name (lowercase, hyphenated)
        
    Raises:
        ValueError: If URL is not a valid GitHub URL
    """
    parsed = urlparse(url)
    
    if "github.com" not in parsed.netloc:
        raise ValueError(f"Not a GitHub URL: {url}")
    
    # Extract path and get repo name
    path_parts = parsed.path.strip("/").split("/")
    if len(path_parts) < 2:
        raise ValueError(f"Invalid GitHub URL format: {url}")
    
    repo_name = path_parts[-1]
    
    # Remove .git suffix if present
    if repo_name.endswith(".git"):
        repo_name = repo_name[:-4]
    
    # Convert to package name: lowercase, underscores to hyphens
    package_name = repo_name.lower().replace("_", "-")
    
    return package_name


def is_github_url(requirement: str) -> bool:
    """Check if a requirement string is a GitHub URL."""
    return "github.com" in requirement.lower()


def convert_requirements(
    requirements: list[str],
) -> tuple[list[str], dict[str, dict[str, str]]]:
    """
    Split requirements into dependencies and uv.sources.
    
    - GitHub URLs → add to both dependencies AND uv_sources
    - PyPI packages → add to dependencies only
    
    Args:
        requirements: List of requirements (mix of GitHub URLs and PyPI specs)
        
    Returns:
        Tuple of (dependencies list, uv_sources dict)
    """
    logger = Logger(name="UVMigrator")
    dependencies: list[str] = []
    uv_sources: dict[str, dict[str, str]] = {}
    
    for req in requirements:
        req = req.strip()
        if not req:
            continue
            
        if is_github_url(req):
            try:
                package_name = github_url_to_package_name(req)
                dependencies.append(package_name)
                uv_sources[package_name] = {"git": req}
            except ValueError as e:
                logger.warning(f"Skipping malformed GitHub URL: {req} - {e}")
        else:
            # PyPI package - add as-is to dependencies
            dependencies.append(req)
    
    return dependencies, uv_sources


def infer_layer(module_type: str, module_name: str, init_yaml: dict[str, Any]) -> str:
    """
    Infer layer from module type and name.
    
    Priority:
    1. Explicit layer in init_yaml (if present)
    2. Known dev-only cores override
    3. Default based on module type
    
    Args:
        module_type: Type of module (core, manager, util, plugin, mcp)
        module_name: Name of the module
        init_yaml: Parsed init.yaml content
        
    Returns:
        Layer string: "foundation", "runtime", or "dev"
    """
    # Check for explicit layer in init.yaml
    if "layer" in init_yaml:
        return init_yaml["layer"]
    
    # Check for known dev-only cores
    if module_name in DEV_CORES:
        return "dev"
    
    # Default based on module type
    return LAYER_DEFAULTS.get(module_type, "runtime")


def module_name_to_package_name(module_name: str) -> str:
    """
    Convert module name (snake_case) to package name (hyphenated).
    
    Examples:
        session_manager → session-manager
        logger_util → logger-util
    """
    return module_name.replace("_", "-")


def generate_pyproject_toml(
    module_path: Path,
    dry_run: bool = False,
) -> str:
    """
    Generate pyproject.toml for a module from its init.yaml.
    
    Args:
        module_path: Path to the module directory
        dry_run: If True, don't write file, just return content
        
    Returns:
        Generated pyproject.toml content
        
    Raises:
        FileNotFoundError: If init.yaml doesn't exist
    """
    logger = Logger(name="UVMigrator")
    
    # Parse init.yaml
    init_yaml = parse_init_yaml(module_path)
    
    # Parse requirements.txt (PyPI deps)
    pypi_requirements = parse_requirements_txt(module_path)
    
    # Extract fields from init.yaml
    version = init_yaml.get("version", "0.0.1")
    module_type = init_yaml.get("type", "unknown")
    module_name = module_path.name
    
    # Generate description from module name
    description = f"ADHD Framework {module_type}: {module_name}"
    
    # Convert init.yaml requirements (GitHub URLs)
    adhd_requirements = init_yaml.get("requirements", []) or []
    adhd_deps, uv_sources = convert_requirements(adhd_requirements)
    
    # Merge ADHD deps and PyPI deps
    all_dependencies = adhd_deps + pypi_requirements
    
    # Infer layer
    layer = infer_layer(module_type, module_name, init_yaml)
    
    # Generate package name
    package_name = module_name_to_package_name(module_name)
    
    # Generate content
    content = generate_pyproject_content(
        name=package_name,
        version=version,
        description=description,
        module_type=module_type,
        layer=layer,
        dependencies=all_dependencies,
        uv_sources=uv_sources,
        module_name=module_name,  # Underscored name for wheel sources mapping
    )
    
    if not dry_run:
        pyproject_path = module_path / "pyproject.toml"
        with open(pyproject_path, "w", encoding="utf-8") as f:
            f.write(content)
        logger.info(f"Generated {pyproject_path}")
    
    return content
