# Epic 7: Data Persistence & File Management - Implementation Tasks

**Phase:** 3 (Foundation)
**Priority:** High
**Dependencies:** Epic 1 (Core Data Models), Epic 9 (Error Handling)
**Estimated Tasks:** 30+

---

## Story 7.1: DataManager Class

**Prerequisites:** Epic 1, Epic 9 (exceptions and validators)

### Task 7.1.1: Create persistence package
- [ ] Create `persistence/__init__.py`:
```python
"""
Data persistence module for Beauty Salon Expense Manager.
Handles CSV file I/O, settings management, and backup operations.
"""

from .data_manager import DataManager

__all__ = ['DataManager']
```

### Task 7.1.2: Create DataManager with constants
- [ ] Create `persistence/data_manager.py` with imports and constants:
```python
"""
DataManager - Centralized file operations for all data persistence.
"""

import os
import csv
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

import pandas as pd

from config import DATA_DIR, LOGS_DIR
from utils.exceptions import (
    DataFileNotFoundError,
    DataFilePermissionError,
    DataIntegrityError,
    BackupError,
    DataImportError
)
from utils.error_handler import get_error_handler

# CSV Column Definitions
EXPENSE_COLUMNS = [
    'expense_id', 'amount', 'date', 'category', 'subcategory',
    'vendor', 'payment_method', 'description', 'tags',
    'is_recurring', 'recurring_type', 'recurring_action',
    'next_due_date', 'last_recurring_date', 'recurring_parent_id',
    'is_deleted', 'deleted_at', 'created_at', 'updated_at'
]

BUDGET_COLUMNS = [
    'budget_id', 'name', 'budget_type', 'category', 'amount',
    'month', 'year', 'warning_threshold', 'enable_rollover',
    'rollover_amount', 'rollover_cap_percent', 'is_active',
    'created_at', 'updated_at'
]

TEMPLATE_COLUMNS = [
    'template_id', 'name', 'category', 'subcategory', 'vendor',
    'typical_amount', 'payment_method', 'description', 'tags',
    'use_count', 'last_used', 'created_at'
]

# File paths
EXPENSES_FILE = 'expenses.csv'
BUDGETS_FILE = 'budgets.csv'
TEMPLATES_FILE = 'templates.csv'
SETTINGS_FILE = 'settings.json'
BACKUPS_DIR = 'backups'
```

### Task 7.1.3: Implement DataManager initialization
- [ ] Add DataManager class with initialization:
```python
class DataManager:
    """
    Centralized file operations for all data persistence.

    Handles loading/saving expenses, budgets, templates, and settings.
    Provides backup/restore functionality and CSV import.
    """

    def __init__(self, data_dir: str = DATA_DIR):
        """
        Initialize DataManager with data directory.

        Args:
            data_dir: Path to data directory
        """
        self.data_dir = Path(data_dir)
        self.backups_dir = self.data_dir / BACKUPS_DIR
        self.error_handler = get_error_handler()

        # File paths
        self.expenses_path = self.data_dir / EXPENSES_FILE
        self.budgets_path = self.data_dir / BUDGETS_FILE
        self.templates_path = self.data_dir / TEMPLATES_FILE
        self.settings_path = self.data_dir / SETTINGS_FILE

        # Ensure directories exist
        self.ensure_data_dir()

    def ensure_data_dir(self) -> None:
        """Create data directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
```

### Task 7.1.4: Implement expense file operations
- [ ] Add expense load/save methods:
```python
    def load_expenses(self) -> pd.DataFrame:
        """
        Load expenses CSV into DataFrame.

        Returns:
            DataFrame with expense data

        Raises:
            DataFileNotFoundError: If file not found and cannot create
        """
        if not self.expenses_path.exists():
            self.error_handler.log_warning(
                f"Expenses file not found, creating: {self.expenses_path}"
            )
            self._create_csv_with_headers(self.expenses_path, EXPENSE_COLUMNS)
            return pd.DataFrame(columns=EXPENSE_COLUMNS)

        try:
            df = pd.read_csv(
                self.expenses_path,
                encoding='utf-8',
                dtype={'expense_id': str, 'tags': str}
            )

            # Ensure all required columns exist
            for col in EXPENSE_COLUMNS:
                if col not in df.columns:
                    df[col] = None

            return df[EXPENSE_COLUMNS]

        except Exception as e:
            self.error_handler.log_error(e, "Loading expenses")
            raise DataFileNotFoundError(str(self.expenses_path))

    def save_expenses(self, df: pd.DataFrame) -> None:
        """
        Save DataFrame to expenses CSV using atomic write.

        Args:
            df: DataFrame with expense data
        """
        self._safe_write_csv(self.expenses_path, df, EXPENSE_COLUMNS)

    def _create_csv_with_headers(self, filepath: Path, columns: List[str]) -> None:
        """Create empty CSV file with headers."""
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(columns)
```

### Task 7.1.5: Implement budget file operations
- [ ] Add budget load/save methods:
```python
    def load_budgets(self) -> pd.DataFrame:
        """
        Load budgets CSV into DataFrame.

        Returns:
            DataFrame with budget data
        """
        if not self.budgets_path.exists():
            self.error_handler.log_warning(
                f"Budgets file not found, creating: {self.budgets_path}"
            )
            self._create_csv_with_headers(self.budgets_path, BUDGET_COLUMNS)
            return pd.DataFrame(columns=BUDGET_COLUMNS)

        try:
            df = pd.read_csv(
                self.budgets_path,
                encoding='utf-8',
                dtype={'budget_id': str}
            )

            # Ensure all required columns exist
            for col in BUDGET_COLUMNS:
                if col not in df.columns:
                    df[col] = None

            return df[BUDGET_COLUMNS]

        except Exception as e:
            self.error_handler.log_error(e, "Loading budgets")
            raise DataFileNotFoundError(str(self.budgets_path))

    def save_budgets(self, df: pd.DataFrame) -> None:
        """
        Save DataFrame to budgets CSV.

        Args:
            df: DataFrame with budget data
        """
        self._safe_write_csv(self.budgets_path, df, BUDGET_COLUMNS)
```

### Task 7.1.6: Implement template file operations
- [ ] Add template load/save methods:
```python
    def load_templates(self) -> pd.DataFrame:
        """
        Load templates CSV into DataFrame.

        Returns:
            DataFrame with template data
        """
        if not self.templates_path.exists():
            self.error_handler.log_warning(
                f"Templates file not found, creating: {self.templates_path}"
            )
            self._create_csv_with_headers(self.templates_path, TEMPLATE_COLUMNS)
            return pd.DataFrame(columns=TEMPLATE_COLUMNS)

        try:
            df = pd.read_csv(
                self.templates_path,
                encoding='utf-8',
                dtype={'template_id': str, 'tags': str}
            )

            # Ensure all required columns exist
            for col in TEMPLATE_COLUMNS:
                if col not in df.columns:
                    df[col] = None

            return df[TEMPLATE_COLUMNS]

        except Exception as e:
            self.error_handler.log_error(e, "Loading templates")
            raise DataFileNotFoundError(str(self.templates_path))

    def save_templates(self, df: pd.DataFrame) -> None:
        """
        Save DataFrame to templates CSV.

        Args:
            df: DataFrame with template data
        """
        self._safe_write_csv(self.templates_path, df, TEMPLATE_COLUMNS)
```

### Task 7.1.7: Implement settings operations
- [ ] Add settings load/save methods with default structure:
```python
    # Default settings structure
    DEFAULT_SETTINGS = {
        "general": {
            "salon_name": "Beauty Salon",
            "salon_address": "",
            "salon_contact": "",
            "language": "en",
            "date_format": "DD/MM/YYYY"
        },
        "backup": {
            "auto_backup": True,
            "backup_location": "data/backups/",
            "retention_days": 30,
            "max_backups": 7
        },
        "alerts": {
            "warning_threshold": 80,
            "show_notifications": True,
            "show_on_startup": True
        },
        "display": {
            "theme": "default",
            "default_view": "dashboard",
            "page_size": 50
        },
        "data": {
            "auto_save": True,
            "duplicate_detection": True,
            "duplicate_days_threshold": 3
        }
    }

    def load_settings(self) -> Dict:
        """
        Load settings from JSON, create defaults if missing.

        Returns:
            Settings dictionary
        """
        if not self.settings_path.exists():
            self.error_handler.log_warning(
                f"Settings file not found, creating defaults: {self.settings_path}"
            )
            self.save_settings(self.DEFAULT_SETTINGS.copy())
            return self.DEFAULT_SETTINGS.copy()

        try:
            with open(self.settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Merge with defaults to add any new settings
            merged = self._merge_settings(self.DEFAULT_SETTINGS, settings)
            return merged

        except json.JSONDecodeError as e:
            self.error_handler.log_error(e, "Parsing settings")
            return self.DEFAULT_SETTINGS.copy()

    def save_settings(self, settings: Dict) -> None:
        """
        Save settings to JSON.

        Args:
            settings: Settings dictionary
        """
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.error_handler.log_error(e, "Saving settings")
            raise

    def _merge_settings(self, defaults: Dict, current: Dict) -> Dict:
        """Merge current settings with defaults, adding missing keys."""
        result = defaults.copy()
        for key, value in current.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    def get_settings(self) -> Dict:
        """
        Get currently loaded settings.

        Returns:
            Copy of current settings dictionary
        """
        if not hasattr(self, '_settings') or self._settings is None:
            self._settings = self.load_settings()
        return self._settings.copy()

    def update_settings(self, new_settings: Dict) -> None:
        """
        Update and save settings.

        Args:
            new_settings: New settings dictionary to save
        """
        self._settings = new_settings.copy()
        self.save_settings(self._settings)
```

### Task 7.1.8: Implement safe write (atomic)
- [ ] Add atomic write functionality:
```python
    def _safe_write_csv(
        self,
        filepath: Path,
        df: pd.DataFrame,
        columns: List[str]
    ) -> None:
        """
        Safely write CSV file with temp file and atomic rename.

        Args:
            filepath: Target file path
            df: DataFrame to write
            columns: Column order
        """
        temp_path = filepath.with_suffix('.tmp')

        try:
            # Write to temp file
            df[columns].to_csv(
                temp_path,
                index=False,
                encoding='utf-8'
            )

            # Verify temp file is valid
            pd.read_csv(temp_path, nrows=1)

            # Atomic rename
            if os.name == 'nt':  # Windows
                if filepath.exists():
                    filepath.unlink()
            temp_path.rename(filepath)

        except Exception as e:
            # Clean up temp file on error
            if temp_path.exists():
                temp_path.unlink()
            self.error_handler.log_error(e, f"Safe write to {filepath}")
            raise
```

### Task 7.1.9: Implement backup operations
- [ ] Add backup/restore methods:
```python
    def create_backup(self, name: str = None) -> str:
        """
        Create timestamped backup of all data files.

        Args:
            name: Optional backup name suffix

        Returns:
            Path to created backup file
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"backup_{timestamp}"
        if name:
            backup_name += f"_{name}"
        backup_name += ".zip"

        backup_path = self.backups_dir / backup_name

        try:
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add data files
                for filepath in [self.expenses_path, self.budgets_path,
                               self.templates_path, self.settings_path]:
                    if filepath.exists():
                        zf.write(filepath, filepath.name)

            self.error_handler.log_info(f"Backup created: {backup_path}")
            return str(backup_path)

        except Exception as e:
            self.error_handler.log_error(e, "Creating backup")
            raise BackupError(str(e), backup_path=str(backup_path), operation="backup")

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore from backup file. Creates safety backup first.

        Args:
            backup_path: Path to backup zip file

        Returns:
            True if successful
        """
        backup_path = Path(backup_path)

        if not backup_path.exists():
            raise BackupError("Backup file not found", backup_path=str(backup_path))

        try:
            # Create safety backup first
            self.create_backup(name="pre_restore")

            # Extract backup
            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extractall(self.data_dir)

            self.error_handler.log_info(f"Restored from backup: {backup_path}")
            return True

        except Exception as e:
            self.error_handler.log_error(e, "Restoring backup")
            raise BackupError(str(e), backup_path=str(backup_path), operation="restore")

    def list_backups(self) -> List[Dict]:
        """
        List available backups with metadata.

        Returns:
            List of backup info dictionaries
        """
        backups = []

        for backup_file in self.backups_dir.glob("backup_*.zip"):
            try:
                stat = backup_file.stat()
                with zipfile.ZipFile(backup_file, 'r') as zf:
                    expense_count = 0
                    if EXPENSES_FILE in zf.namelist():
                        with zf.open(EXPENSES_FILE) as f:
                            expense_count = sum(1 for _ in f) - 1  # Subtract header

                backups.append({
                    'path': str(backup_file),
                    'name': backup_file.name,
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'size_kb': stat.st_size // 1024,
                    'expense_count': expense_count,
                    'type': 'Auto' if 'pre_restore' not in backup_file.name else 'Manual'
                })
            except Exception as e:
                self.error_handler.log_warning(f"Error reading backup: {backup_file}")

        return sorted(backups, key=lambda x: x['created'], reverse=True)
```

### Task 7.1.10: Implement CSV import
- [ ] Add import_csv method:
```python
    def import_csv(
        self,
        file_path: str,
        mapping: Dict[str, str]
    ) -> Tuple[int, int, List[Dict]]:
        """
        Import external CSV with column mapping.

        Args:
            file_path: Path to CSV file to import
            mapping: Dict mapping our columns to CSV columns

        Returns:
            Tuple of (imported_count, skipped_count, skipped_rows)
            skipped_rows format: [{'row': int, 'error': str, 'data': Dict}, ...]
        """
        from utils.validators import validate_expense

        imported = 0
        skipped = 0
        skipped_rows = []

        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except Exception as e:
            raise DataImportError(str(e), filepath=file_path)

        expenses_df = self.load_expenses()

        for idx, row in df.iterrows():
            try:
                # Map columns
                expense_data = {}
                for our_col, csv_col in mapping.items():
                    if csv_col and csv_col in row.index:
                        expense_data[our_col] = row[csv_col]

                # Validate
                errors = validate_expense(expense_data)
                if errors:
                    skipped += 1
                    skipped_rows.append({
                        'row': idx + 2,  # +2 for header and 0-indexing
                        'error': '; '.join([f"{f}: {e}" for f, e in errors]),
                        'data': expense_data
                    })
                    continue

                # Add to expenses
                # (Actual addition handled by ExpenseManager)
                imported += 1

            except Exception as e:
                skipped += 1
                skipped_rows.append({
                    'row': idx + 2,
                    'error': str(e),
                    'data': dict(row)
                })

        return imported, skipped, skipped_rows
```

### Task 7.1.11: Implement utility methods
- [ ] Add disk space check and stats:
```python
    def check_disk_space(self, required_mb: int = 100) -> Tuple[bool, int]:
        """
        Check if sufficient disk space is available.

        Args:
            required_mb: Required space in MB

        Returns:
            Tuple of (has_space, available_mb)
        """
        try:
            stat = shutil.disk_usage(self.data_dir)
            available_mb = stat.free // (1024 * 1024)
            return available_mb >= required_mb, available_mb
        except Exception:
            return True, -1  # Assume OK if can't check

    def get_data_stats(self) -> Dict:
        """
        Get statistics about stored data.

        Returns:
            Dictionary with data statistics
        """
        stats = {
            'expenses_count': 0,
            'budgets_count': 0,
            'templates_count': 0,
            'data_dir_size_kb': 0,
            'backup_count': 0
        }

        try:
            if self.expenses_path.exists():
                df = pd.read_csv(self.expenses_path)
                stats['expenses_count'] = len(df)

            if self.budgets_path.exists():
                df = pd.read_csv(self.budgets_path)
                stats['budgets_count'] = len(df)

            if self.templates_path.exists():
                df = pd.read_csv(self.templates_path)
                stats['templates_count'] = len(df)

            # Calculate directory size
            total_size = sum(f.stat().st_size for f in self.data_dir.glob('*') if f.is_file())
            stats['data_dir_size_kb'] = total_size // 1024

            # Count backups
            stats['backup_count'] = len(list(self.backups_dir.glob('backup_*.zip')))

        except Exception as e:
            self.error_handler.log_warning(f"Error getting stats: {e}")

        return stats
```

### Task 7.1.12: Create DataManager tests
- [ ] Create `tests/test_persistence/__init__.py`
- [ ] Create `tests/test_persistence/test_data_manager.py`:
```python
"""Tests for DataManager class."""

import pytest
import os
import tempfile
import pandas as pd
from datetime import datetime
from persistence.data_manager import DataManager, EXPENSE_COLUMNS


class TestDataManager:
    """Tests for DataManager."""

    @pytest.fixture
    def temp_data_dir(self):
        """Create temporary data directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def manager(self, temp_data_dir):
        """Create DataManager with temp directory."""
        return DataManager(data_dir=temp_data_dir)

    def test_creates_directories(self, temp_data_dir):
        """Test that directories are created."""
        manager = DataManager(data_dir=temp_data_dir)
        assert os.path.exists(temp_data_dir)
        assert os.path.exists(os.path.join(temp_data_dir, 'backups'))

    def test_load_expenses_creates_file(self, manager):
        """Test loading expenses creates file if missing."""
        df = manager.load_expenses()
        assert manager.expenses_path.exists()
        assert list(df.columns) == EXPENSE_COLUMNS

    def test_save_and_load_expenses(self, manager):
        """Test saving and loading expenses."""
        # Create test data
        df = pd.DataFrame([{
            'expense_id': 'test-123',
            'amount': 1000.00,
            'date': '2024-01-15',
            'category': 'Supplies',
            'subcategory': 'Hair products',
            'vendor': 'Test Vendor',
            'payment_method': 'Cash',
            'description': 'Test',
            'tags': 'test,sample',
            'is_recurring': False,
            'recurring_type': None,
            'recurring_action': None,
            'next_due_date': None,
            'last_recurring_date': None,
            'recurring_parent_id': None,
            'is_deleted': False,
            'deleted_at': None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat()
        }])

        manager.save_expenses(df)
        loaded = manager.load_expenses()

        assert len(loaded) == 1
        assert loaded.iloc[0]['expense_id'] == 'test-123'

    def test_load_settings_creates_defaults(self, manager):
        """Test loading settings creates defaults if missing."""
        settings = manager.load_settings()
        assert 'general' in settings
        assert 'backup' in settings
        assert settings['general']['salon_name'] == 'Beauty Salon'

    def test_create_backup(self, manager):
        """Test backup creation."""
        # Create some data first
        manager.load_expenses()  # Creates empty file

        backup_path = manager.create_backup(name="test")
        assert os.path.exists(backup_path)
        assert "test" in backup_path

    def test_list_backups(self, manager):
        """Test listing backups."""
        manager.load_expenses()
        manager.create_backup(name="backup1")
        manager.create_backup(name="backup2")

        backups = manager.list_backups()
        assert len(backups) == 2

    def test_check_disk_space(self, manager):
        """Test disk space check."""
        has_space, available = manager.check_disk_space(required_mb=1)
        assert has_space is True
        assert available > 0
```

---

## Story 7.2: Auto-Save Functionality

**Prerequisites:** Story 7.1

### Task 7.2.1: Implement in managers
- [ ] Add auto-save after each CRUD operation in ExpenseManager
- [ ] Add auto-save after each CRUD operation in BudgetManager
- [ ] Add auto-save after each CRUD operation in TemplateManager

### Task 7.2.2: Add status tracking
- [ ] Track last save time
- [ ] Track save in progress flag
- [ ] Emit status updates for UI

---

## Story 7.3: Backup System

**Prerequisites:** Story 7.1

### Task 7.3.1: Implement automatic backup on startup
- [ ] Check last backup time on startup
- [ ] Create backup if > 24 hours since last

### Task 7.3.2: Implement backup cleanup
- [ ] Delete backups older than retention period
- [ ] Keep maximum number of backups

### Task 7.3.3: Create backup UI dialogs
- [ ] Create backup dialog (in Epic 10)
- [ ] Restore backup dialog (in Epic 10)

---

## Story 7.4: Data Import

**Prerequisites:** Story 7.1, Story 9.2 (validators)

### Task 7.4.1: Implement import wizard logic
- [ ] File selection and preview
- [ ] Column mapping
- [ ] Import execution with progress

### Task 7.4.2: Create import UI (in Epic 10)
- [ ] Import wizard dialog
- [ ] Column mapping interface
- [ ] Results summary dialog

---

## Completion Checklist

### Story 7.1: DataManager Class
- [ ] DataManager class created
- [ ] Expense load/save working
- [ ] Budget load/save working
- [ ] Template load/save working
- [ ] Settings load/save working
- [ ] Atomic write implemented
- [ ] Backup/restore working
- [ ] CSV import working
- [ ] Disk space check working
- [ ] All tests passing

### Story 7.2: Auto-Save
- [ ] Auto-save after add
- [ ] Auto-save after edit
- [ ] Auto-save after delete
- [ ] Status tracking working

### Story 7.3: Backup System
- [ ] Automatic backup on startup
- [ ] Manual backup working
- [ ] Restore working
- [ ] Backup cleanup working

### Story 7.4: Data Import
- [ ] Column mapping working
- [ ] Validation during import
- [ ] Progress tracking
- [ ] Results summary

---

## Next Steps

After completing Epic 7, proceed to:
- **Epic 2: Expense Management** - Uses DataManager for persistence
