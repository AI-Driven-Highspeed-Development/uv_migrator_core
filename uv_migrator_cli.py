"""CLI commands for uv_migrator_core.

Provides the `adhd migrate` command for migrating modules
from init.yaml to pyproject.toml format.

Usage:
    python -m uv_migrator_core.uv_migrator_cli migrate <module_name> [--dry-run] [--no-overwrite]
    python -m uv_migrator_core.uv_migrator_cli migrate --all [--dry-run] [--no-overwrite]
"""

from __future__ import annotations

import sys
from typing import Optional

from logger_util import Logger
from .uv_migrator_core import UVMigratorCore


def migrate_command(
    module_name: Optional[str] = None,
    all_modules: bool = False,
    dry_run: bool = False,
    no_overwrite: bool = False,
) -> None:
    """
    Migrate module(s) from init.yaml to pyproject.toml format.
    
    Args:
        module_name: Name of specific module to migrate (mutually exclusive with all_modules)
        all_modules: If True, migrate all discovered modules
        dry_run: If True, preview without writing files
        no_overwrite: If True, skip modules that already have pyproject.toml
    """
    logger = Logger(name="UVMigrator")
    migrator = UVMigratorCore()
    
    if not module_name and not all_modules:
        logger.error("Please specify a module name or use --all")
        logger.info("Usage: adhd migrate <module_name> [--dry-run] [--no-overwrite]")
        logger.info("       adhd migrate --all [--dry-run] [--no-overwrite]")
        return
    
    if module_name and all_modules:
        logger.error("Cannot specify both module name and --all")
        return
    
    if all_modules:
        logger.info("Migrating all modules...")
        report = migrator.migrate_all(
            dry_run=dry_run,
            no_overwrite=no_overwrite,
        )
        report.print_summary(logger)
        
        # Print details for successful migrations
        if not dry_run and report.successful:
            logger.info("Successfully migrated:")
            for result in report.successful:
                if result.output_path:
                    logger.info(f"  ✓ {result.module_name} → {result.output_path}")
    else:
        logger.info(f"Migrating module: {module_name}")
        result = migrator.migrate_module(
            module_name=module_name,
            dry_run=dry_run,
            no_overwrite=no_overwrite,
        )
        
        if result.success:
            if dry_run and result.content:
                logger.info(f"[DRY RUN] Would generate:\n")
                print(result.content)
            else:
                logger.info(f"✓ {result.message}")
                if result.output_path:
                    logger.info(f"  Output: {result.output_path}")
        else:
            logger.error(f"✗ {result.message}")


def main(args: Optional[list[str]] = None) -> None:
    """Main CLI entry point."""
    if args is None:
        args = sys.argv[1:]
    
    # Parse command (first positional arg should be 'migrate')
    if not args or args[0] not in ("migrate", "--help", "-h"):
        print("Usage: python -m uv_migrator_core.uv_migrator_cli migrate <module_name> [OPTIONS]")
        print("       python -m uv_migrator_core.uv_migrator_cli migrate --all [OPTIONS]")
        print("\nOptions:")
        print("  --dry-run      Preview without writing files")
        print("  --no-overwrite Skip modules that already have pyproject.toml")
        return
    
    if args[0] in ("--help", "-h"):
        print("UV Migrator - Convert init.yaml to pyproject.toml")
        print("\nCommands:")
        print("  migrate    Migrate module(s) to pyproject.toml format")
        return
    
    # Skip 'migrate' command and process remaining args
    _cli_migrate_handler(args[1:])


def _cli_migrate_handler(args: list[str]) -> None:
    """CLI handler that parses args and calls migrate_command."""
    module_name: Optional[str] = None
    all_modules = False
    dry_run = False
    no_overwrite = False
    
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--all":
            all_modules = True
        elif arg == "--dry-run":
            dry_run = True
        elif arg == "--no-overwrite":
            no_overwrite = True
        elif not arg.startswith("--"):
            module_name = arg
        i += 1
    
    migrate_command(
        module_name=module_name,
        all_modules=all_modules,
        dry_run=dry_run,
        no_overwrite=no_overwrite,
    )


if __name__ == "__main__":
    main()
