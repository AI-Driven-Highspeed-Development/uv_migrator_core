"""
UV Migrator Core - Main controller for init.yaml to pyproject.toml migration.

This module provides the high-level orchestration for migrating ADHD modules
from init.yaml format to pyproject.toml format compatible with uv workspaces.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field

# Ensure project root is in sys.path
if str(Path.cwd()) not in sys.path:
    sys.path.append(str(Path.cwd()))

from utils.logger_util import Logger
from cores.modules_controller_core.modules_controller import ModulesController, ModuleInfo
from cores.uv_migrator_core.migrator import generate_pyproject_toml


@dataclass
class MigrationResult:
    """Result of a single module migration."""
    module_name: str
    success: bool
    message: str
    output_path: Optional[Path] = None
    content: Optional[str] = None


@dataclass 
class MigrationReport:
    """Summary report of migration operation."""
    results: list[MigrationResult] = field(default_factory=list)
    
    @property
    def successful(self) -> list[MigrationResult]:
        return [r for r in self.results if r.success]
    
    @property
    def failed(self) -> list[MigrationResult]:
        return [r for r in self.results if not r.success]
    
    def print_summary(self, logger: Logger) -> None:
        """Print migration summary."""
        total = len(self.results)
        success_count = len(self.successful)
        fail_count = len(self.failed)
        
        logger.info(f"Migration complete: {success_count}/{total} successful")
        
        if self.failed:
            logger.warning(f"{fail_count} modules had issues:")
            for result in self.failed:
                logger.warning(f"  - {result.module_name}: {result.message}")


class UVMigratorCore:
    """
    Controller for migrating ADHD modules to pyproject.toml format.
    
    Provides high-level methods for:
    - Migrating a single module
    - Migrating all discovered modules
    - Dry-run preview mode
    """
    
    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize the migrator.
        
        Args:
            root_path: Project root path. Defaults to cwd.
        """
        self.root_path = (root_path or Path.cwd()).resolve()
        self.logger = Logger(name="UVMigratorCore")
        self._modules_controller = ModulesController(self.root_path)
    
    def migrate_module(
        self,
        module_name: str,
        dry_run: bool = False,
        no_overwrite: bool = False,
    ) -> MigrationResult:
        """
        Migrate a single module to pyproject.toml format.
        
        Args:
            module_name: Name of the module to migrate
            dry_run: If True, preview without writing
            no_overwrite: If True, skip if pyproject.toml exists
            
        Returns:
            MigrationResult with success status and details
        """
        # Find the module
        module_info = self._find_module(module_name)
        if module_info is None:
            return MigrationResult(
                module_name=module_name,
                success=False,
                message=f"Module '{module_name}' not found",
            )
        
        module_path = self.root_path / module_info.path
        pyproject_path = module_path / "pyproject.toml"
        
        # Check for existing pyproject.toml
        if no_overwrite and pyproject_path.exists():
            return MigrationResult(
                module_name=module_name,
                success=True,
                message="Skipped (pyproject.toml exists)",
                output_path=pyproject_path,
            )
        
        try:
            content = generate_pyproject_toml(module_path, dry_run=dry_run)
            
            if dry_run:
                self.logger.info(f"[DRY RUN] Would generate {pyproject_path}")
                return MigrationResult(
                    module_name=module_name,
                    success=True,
                    message="Dry run - preview only",
                    output_path=pyproject_path,
                    content=content,
                )
            else:
                return MigrationResult(
                    module_name=module_name,
                    success=True,
                    message="Generated pyproject.toml",
                    output_path=pyproject_path,
                    content=content,
                )
                
        except FileNotFoundError as e:
            return MigrationResult(
                module_name=module_name,
                success=False,
                message=f"Missing init.yaml: {e}",
            )
        except Exception as e:
            return MigrationResult(
                module_name=module_name,
                success=False,
                message=f"Migration failed: {e}",
            )
    
    def migrate_all(
        self,
        dry_run: bool = False,
        no_overwrite: bool = False,
        include_cores: bool = True,
    ) -> MigrationReport:
        """
        Migrate all discovered modules.
        
        Args:
            dry_run: If True, preview without writing
            no_overwrite: If True, skip modules with existing pyproject.toml
            include_cores: If True, include core modules
            
        Returns:
            MigrationReport with results for all modules
        """
        report = MigrationReport()
        
        # Get all modules
        modules = self._modules_controller.discover_modules()
        
        for module in modules:
            # Optionally skip cores
            if not include_cores and module.module_type.name == "core":
                continue
            
            result = self.migrate_module(
                module_name=module.name,
                dry_run=dry_run,
                no_overwrite=no_overwrite,
            )
            report.results.append(result)
        
        return report
    
    def _find_module(self, module_name: str) -> Optional[ModuleInfo]:
        """Find a module by name."""
        modules = self._modules_controller.discover_modules()
        for module in modules:
            if module.name == module_name:
                return module
        return None
    
    def preview_migration(self, module_name: str) -> Optional[str]:
        """
        Preview what pyproject.toml would be generated.
        
        Args:
            module_name: Name of the module
            
        Returns:
            Generated content or None if module not found
        """
        result = self.migrate_module(module_name, dry_run=True)
        return result.content if result.success else None
