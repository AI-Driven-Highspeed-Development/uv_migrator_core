"""Templates for pyproject.toml generation.

Contains the template structure and formatting functions for
generating uv-compatible pyproject.toml files from init.yaml.
"""

from __future__ import annotations

from typing import Any

# Template parts for pyproject.toml
PROJECT_HEADER = '''[project]
name = "{name}"
version = "{version}"
description = "{description}"
requires-python = ">=3.11"
'''

DEPENDENCIES_SECTION = '''dependencies = [
{deps}]
'''

TOOL_ADHD_SECTION = '''
[tool.adhd]
layer = "{layer}"
'''

UV_SOURCES_SECTION = '''
[tool.uv.sources]
{sources}'''

BUILD_SYSTEM = '''
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
only-include = ["."]

[tool.hatch.build.targets.wheel.sources]
"" = "{module_name}"
'''


def format_dependencies(deps: list[str]) -> str:
    """Format dependency list for pyproject.toml."""
    if not deps:
        return ""
    lines = [f'    "{dep}",' for dep in deps]
    return "\n".join(lines) + "\n"


def format_uv_sources(sources: dict[str, dict[str, str]]) -> str:
    """Format uv sources section for pyproject.toml.
    
    For workspace development, uses { workspace = true }.
    The git URLs from init.yaml are preserved in comments for reference.
    """
    if not sources:
        return ""
    lines = []
    for package_name, source_info in sources.items():
        # Use workspace = true for local development
        lines.append(f'{package_name} = {{ workspace = true }}')
    return "\n".join(lines)


def generate_pyproject_content(
    name: str,
    version: str,
    description: str,
    layer: str,
    dependencies: list[str],
    uv_sources: dict[str, dict[str, str]],
    module_name: str,
    is_mcp: bool = False,
) -> str:
    """
    Generate complete pyproject.toml content.
    
    Args:
        name: Package name (hyphenated)
        version: Version string
        description: Package description
        layer: Layer classification (foundation, runtime, dev)
        dependencies: List of all dependencies (ADHD + PyPI)
        uv_sources: Dict of ADHD packages to their git sources
        module_name: Module name (underscored) for wheel sources mapping
        is_mcp: Whether this is an MCP server module
        
    Returns:
        Complete pyproject.toml content as string
    """
    content_parts = []
    
    # Project header
    content_parts.append(
        PROJECT_HEADER.format(
            name=name,
            version=version,
            description=description,
        )
    )
    
    # Dependencies section
    if dependencies:
        content_parts.append(
            DEPENDENCIES_SECTION.format(deps=format_dependencies(dependencies))
        )
    else:
        content_parts.append('dependencies = []\n')
    
    # Tool.adhd section
    tool_adhd = TOOL_ADHD_SECTION.format(layer=layer)
    if is_mcp:
        # Add mcp = true before the closing newline
        tool_adhd = tool_adhd.rstrip('\n') + 'mcp = true\n'
    content_parts.append(tool_adhd)
    
    # UV sources section (only if there are ADHD dependencies)
    if uv_sources:
        content_parts.append(
            UV_SOURCES_SECTION.format(sources=format_uv_sources(uv_sources))
        )
    
    # Build system with sources mapping
    content_parts.append(
        BUILD_SYSTEM.format(module_name=module_name)
    )
    
    return "".join(content_parts)
