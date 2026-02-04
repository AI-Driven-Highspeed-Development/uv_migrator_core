# UV Migrator Core

## Overview

Migration tool that converts ADHD framework modules from `init.yaml` format to `pyproject.toml` format compatible with uv workspaces.

**Layer:** dev (used only during migration)

## Features

- **Single module migration**: `adhd migrate <module_name>`
- **Batch migration**: `adhd migrate --all`
- **Preview mode**: `adhd migrate --dry-run` to see output without writing
- **Safe mode**: `adhd migrate --no-overwrite` to skip existing files
- **Automatic layer inference**: Determines layer based on module type
- **GitHub URL conversion**: Converts GitHub URLs to `[tool.uv.sources]` entries

## Usage

### CLI Commands

```bash
# Migrate a single module
adhd migrate session_manager

# Preview migration without writing
adhd migrate session_manager --dry-run

# Migrate all modules
adhd migrate --all

# Migrate all, skip existing pyproject.toml
adhd migrate --all --no-overwrite
```

### Programmatic Usage

```python
from cores.uv_migrator_core import UVMigratorCore

migrator = UVMigratorCore()

# Migrate single module
result = migrator.migrate_module("session_manager")
print(result.success, result.message)

# Preview migration
content = migrator.preview_migration("session_manager")
print(content)

# Migrate all modules
report = migrator.migrate_all(dry_run=False)
report.print_summary()
```

## Conversion Logic

### Input → Output Mapping

| init.yaml field | pyproject.toml field |
|-----------------|---------------------|
| `version` | `[project].version` |
| folder location | `[tool.adhd].layer` (inferred from path) |
| `requirements` (GitHub URLs) | `[tool.uv.sources]` + `[project].dependencies` |
| `requirements.txt` (PyPI) | `[project].dependencies` |

### Layer Inference Defaults

| Folder | Default Layer |
|--------|---------------|
| cores | foundation (unless dev-specific) |
| utils | foundation |
| managers | runtime |
| plugins | runtime |
| mcps | runtime (+ `mcp = true`) |

### Example Conversion

**Input: init.yaml** (legacy)
```yaml
version: 0.0.1
requirements:
  - https://github.com/AI-Driven-Highspeed-Development/Logger-Util.git
```

**Input: requirements.txt**
```
sqlalchemy>=2.0.0
```

**Output: pyproject.toml**
```toml
[project]
name = "session-manager"
version = "0.0.1"
dependencies = [
    "logger-util",
    "sqlalchemy>=2.0.0",
]

[tool.adhd]
layer = "runtime"

[tool.uv.sources]
logger-util = { git = "https://github.com/AI-Driven-Highspeed-Development/Logger-Util.git" }

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Module Structure

```
cores/uv_migrator_core/
├── __init__.py           # Module exports
├── pyproject.toml        # Module metadata
├── migrator.py           # Conversion logic
├── templates.py          # pyproject.toml template strings
├── uv_migrator_cli.py    # CLI command registration
├── refresh.py            # Framework refresh hook
├── README.md             # This file
├── requirements.txt      # PyPI dependencies
├── tests/                # Unit tests
└── playground/           # Interactive exploration
```

## Dependencies

- `logger_util` - Logging
- `yaml_reading_core` - YAML parsing
- `modules_controller_core` - Module discovery
- `cli_manager` - CLI command registration


## Testing

### Unit Tests (Optional)
```bash
pytest cores/uv_migrator_core/tests/
```

### Adversarial Testing
HyperRed will attack this module based on threat model.
Configure in testing scope: `internal` | `external` | `adversarial`