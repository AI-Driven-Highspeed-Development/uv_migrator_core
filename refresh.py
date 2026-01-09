"""
Refresh script for uv_migrator_core module.

This script is called during framework refresh to perform any
necessary setup or synchronization for the UV Migrator Core module.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root is in sys.path
if str(Path.cwd()) not in sys.path:
    sys.path.append(str(Path.cwd()))

from utils.logger_util import Logger
from cores.uv_migrator_core.uv_migrator_cli import register_cli


def main() -> None:
    """
    Refresh script for uv_migrator_core.
    
    Registers CLI commands with the centralized CLIManager.
    """
    logger = Logger(name="UVMigratorCoreRefresh")
    
    try:
        register_cli()
        logger.info("UV Migrator core refresh: CLI commands registered.")
    except Exception as e:
        logger.warning(f"UV Migrator core refresh: Could not register CLI commands: {e}")


if __name__ == "__main__":
    main()
