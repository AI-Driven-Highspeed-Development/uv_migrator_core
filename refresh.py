"""Refresh script for uv_migrator_core module.

This script is called during framework refresh to perform any
necessary setup or synchronization for the UV Migrator Core module.
"""

from __future__ import annotations

from logger_util import Logger


def main() -> None:
    """
    Refresh script for uv_migrator_core.
    
    Currently no special refresh actions needed.
    The module can be used via:
        python -m uv_migrator_core.uv_migrator_cli migrate <module_name>
    """
    logger = Logger(name="UVMigratorCoreRefresh")
    logger.info("UV Migrator core refresh: Ready.")


if __name__ == "__main__":
    main()
