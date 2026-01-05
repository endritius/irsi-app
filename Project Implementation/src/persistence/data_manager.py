"""
DataManager - Centralized file operations for all data persistence.
"""

import os
import json
import shutil
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import pandas as pd

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    DATA_DIR, BACKUPS_DIR, LOGS_DIR,
    EXPENSES_FILE, BUDGETS_FILE, TEMPLATES_FILE, SETTINGS_FILE
)
from utils.exceptions import (
    FileError, DataFileNotFoundError, DataFilePermissionError,
    DataFileCorruptedError, BackupError, RestoreError, DiskSpaceError
)
from utils.error_handler import get_error_handler, log_info, log_warning, log_error


# Column definitions
EXPENSE_COLUMNS = [
    'expense_id', 'amount', 'date', 'category', 'subcategory',
    'vendor', 'payment_method', 'description', 'tags',
    'is_recurring', 'recurring_type', 'recurring_action',
    'next_due_date', 'last_recurring_date', 'recurring_parent_id',
    'is_deleted', 'deleted_at', 'created_at', 'updated_at'
]

BUDGET_COLUMNS = [
    'budget_id', 'category', 'subcategory', 'amount',
    'period_type', 'period_start', 'warning_threshold',
    'critical_threshold', 'rollover_enabled', 'rollover_cap_percent',
    'previous_rollover', 'notes', 'is_active', 'created_at', 'updated_at'
]

TEMPLATE_COLUMNS = [
    'template_id', 'name', 'category', 'subcategory', 'vendor',
    'typical_amount', 'payment_method', 'description', 'tags',
    'use_count', 'last_used', 'created_at'
]

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
        "backup_location": "backups",
        "retention_days": 30,
        "max_backups": 10
    },
    "alerts": {
        "warning_threshold": 80,
        "critical_threshold": 95,
        "show_notifications": True,
        "show_recurring_reminders": True
    },
    "display": {
        "theme": "default",
        "default_view": "expenses",
        "page_size": 50,
        "show_deleted": False,
        "compact_mode": False
    },
    "data": {
        "auto_save": True,
        "duplicate_detection": True,
        "duplicate_threshold_days": 7,
        "confirm_delete": True
    },
    "reports": {
        "default_period": "monthly",
        "include_charts": True,
        "chart_style": "seaborn"
    }
}


class DataManager:
    """
    Centralized file operations for all data persistence.
    Handles CSV and JSON file operations with atomic writes.
    """

    def __init__(self, data_dir: Path = None):
        """
        Initialize DataManager.

        Args:
            data_dir: Data directory path (defaults to config DATA_DIR)
        """
        self.data_dir = Path(data_dir) if data_dir else DATA_DIR
        self.backups_dir = BACKUPS_DIR
        self.logs_dir = LOGS_DIR

        self.expenses_file = self.data_dir / "expenses.csv"
        self.budgets_file = self.data_dir / "budgets.csv"
        self.templates_file = self.data_dir / "templates.csv"
        self.settings_file = self.data_dir / "settings.json"

        # Cache for settings
        self._settings_cache: Optional[Dict] = None

        # Ensure directories exist
        self.ensure_data_dir()

    def ensure_data_dir(self) -> None:
        """Create data directories if they don't exist."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        # Create CSV files with headers if they don't exist
        if not self.expenses_file.exists():
            self._create_empty_csv(self.expenses_file, EXPENSE_COLUMNS)
            log_info(f"Created expenses file: {self.expenses_file}")

        if not self.budgets_file.exists():
            self._create_empty_csv(self.budgets_file, BUDGET_COLUMNS)
            log_info(f"Created budgets file: {self.budgets_file}")

        if not self.templates_file.exists():
            self._create_empty_csv(self.templates_file, TEMPLATE_COLUMNS)
            log_info(f"Created templates file: {self.templates_file}")

        # Create settings file if it doesn't exist
        if not self.settings_file.exists():
            self.save_settings(DEFAULT_SETTINGS.copy())
            log_info(f"Created settings file: {self.settings_file}")

    def _create_empty_csv(self, filepath: Path, columns: List[str]) -> None:
        """Create an empty CSV file with headers."""
        df = pd.DataFrame(columns=columns)
        df.to_csv(filepath, index=False)

    # ===== EXPENSE OPERATIONS =====

    def load_expenses(self) -> pd.DataFrame:
        """
        Load expenses CSV into DataFrame.

        Returns:
            DataFrame with expense data

        Raises:
            DataFileNotFoundError: If file doesn't exist
            DataFileCorruptedError: If file is corrupted
        """
        if not self.expenses_file.exists():
            self._create_empty_csv(self.expenses_file, EXPENSE_COLUMNS)
            return pd.DataFrame(columns=EXPENSE_COLUMNS)

        try:
            df = pd.read_csv(self.expenses_file, dtype=str, keep_default_na=False)

            # Add missing columns
            for col in EXPENSE_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
                    log_warning(f"Added missing column to expenses: {col}")

            return df

        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=EXPENSE_COLUMNS)
        except Exception as e:
            log_error(e, "load_expenses")
            raise DataFileCorruptedError(str(self.expenses_file), str(e))

    def save_expenses(self, df: pd.DataFrame) -> None:
        """
        Save DataFrame to expenses CSV using atomic write.

        Args:
            df: DataFrame to save

        Raises:
            FileError: If save fails
        """
        self._atomic_write_csv(self.expenses_file, df, EXPENSE_COLUMNS)
        log_info(f"Saved {len(df)} expenses")

    # ===== BUDGET OPERATIONS =====

    def load_budgets(self) -> pd.DataFrame:
        """
        Load budgets CSV into DataFrame.

        Returns:
            DataFrame with budget data
        """
        if not self.budgets_file.exists():
            self._create_empty_csv(self.budgets_file, BUDGET_COLUMNS)
            return pd.DataFrame(columns=BUDGET_COLUMNS)

        try:
            df = pd.read_csv(self.budgets_file, dtype=str, keep_default_na=False)

            # Add missing columns
            for col in BUDGET_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
                    log_warning(f"Added missing column to budgets: {col}")

            return df

        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=BUDGET_COLUMNS)
        except Exception as e:
            log_error(e, "load_budgets")
            raise DataFileCorruptedError(str(self.budgets_file), str(e))

    def save_budgets(self, df: pd.DataFrame) -> None:
        """
        Save DataFrame to budgets CSV using atomic write.

        Args:
            df: DataFrame to save
        """
        self._atomic_write_csv(self.budgets_file, df, BUDGET_COLUMNS)
        log_info(f"Saved {len(df)} budgets")

    # ===== TEMPLATE OPERATIONS =====

    def load_templates(self) -> pd.DataFrame:
        """
        Load templates CSV into DataFrame.

        Returns:
            DataFrame with template data
        """
        if not self.templates_file.exists():
            self._create_empty_csv(self.templates_file, TEMPLATE_COLUMNS)
            return pd.DataFrame(columns=TEMPLATE_COLUMNS)

        try:
            df = pd.read_csv(self.templates_file, dtype=str, keep_default_na=False)

            # Add missing columns
            for col in TEMPLATE_COLUMNS:
                if col not in df.columns:
                    df[col] = ""
                    log_warning(f"Added missing column to templates: {col}")

            return df

        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=TEMPLATE_COLUMNS)
        except Exception as e:
            log_error(e, "load_templates")
            raise DataFileCorruptedError(str(self.templates_file), str(e))

    def save_templates(self, df: pd.DataFrame) -> None:
        """
        Save DataFrame to templates CSV using atomic write.

        Args:
            df: DataFrame to save
        """
        self._atomic_write_csv(self.templates_file, df, TEMPLATE_COLUMNS)
        log_info(f"Saved {len(df)} templates")

    # ===== SETTINGS OPERATIONS =====

    def load_settings(self) -> Dict:
        """
        Load settings from JSON, create defaults if missing.

        Returns:
            Settings dictionary
        """
        if self._settings_cache is not None:
            return self._settings_cache.copy()

        if not self.settings_file.exists():
            self._settings_cache = DEFAULT_SETTINGS.copy()
            self.save_settings(self._settings_cache)
            return self._settings_cache.copy()

        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)

            # Merge with defaults to handle new settings
            settings = self._merge_settings(DEFAULT_SETTINGS.copy(), loaded)
            self._settings_cache = settings
            return settings.copy()

        except json.JSONDecodeError as e:
            log_warning(f"Settings file corrupted, using defaults: {e}")
            self._settings_cache = DEFAULT_SETTINGS.copy()
            return self._settings_cache.copy()
        except Exception as e:
            log_error(e, "load_settings")
            self._settings_cache = DEFAULT_SETTINGS.copy()
            return self._settings_cache.copy()

    def save_settings(self, settings: Dict) -> None:
        """
        Save settings to JSON.

        Args:
            settings: Settings dictionary to save
        """
        try:
            # Atomic write for settings too
            temp_file = self.settings_file.with_suffix('.tmp')
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4)

            temp_file.replace(self.settings_file)
            self._settings_cache = settings.copy()
            log_info("Settings saved")

        except Exception as e:
            log_error(e, "save_settings")
            if temp_file.exists():
                temp_file.unlink()
            raise FileError(f"Failed to save settings: {e}")

    def get_settings(self) -> Dict:
        """
        Get cached settings.

        Returns:
            Current settings dictionary
        """
        if self._settings_cache is None:
            return self.load_settings()
        return self._settings_cache.copy()

    def update_settings(self, updates: Dict) -> None:
        """
        Update specific settings and save.

        Args:
            updates: Dictionary of settings to update
        """
        settings = self.get_settings()
        settings = self._merge_settings(settings, updates)
        self.save_settings(settings)

    def _merge_settings(self, base: Dict, updates: Dict) -> Dict:
        """Recursively merge settings dictionaries."""
        result = base.copy()
        for key, value in updates.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result

    # ===== BACKUP OPERATIONS =====

    def create_backup(self, name: str = None) -> str:
        """
        Create timestamped backup of all data files.

        Args:
            name: Optional backup name

        Returns:
            Path to created backup file

        Raises:
            BackupError: If backup fails
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if name:
            # Sanitize name
            name = "".join(c for c in name if c.isalnum() or c in ('_', '-'))
            backup_name = f"backup_{timestamp}_{name}.zip"
        else:
            backup_name = f"backup_{timestamp}.zip"

        backup_path = self.backups_dir / backup_name

        try:
            # Check disk space
            has_space, available = self.check_disk_space(50)
            if not has_space:
                raise DiskSpaceError(50, available)

            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                # Add all data files
                if self.expenses_file.exists():
                    zf.write(self.expenses_file, "expenses.csv")
                if self.budgets_file.exists():
                    zf.write(self.budgets_file, "budgets.csv")
                if self.templates_file.exists():
                    zf.write(self.templates_file, "templates.csv")
                if self.settings_file.exists():
                    zf.write(self.settings_file, "settings.json")

                # Add backup metadata
                metadata = {
                    'created_at': datetime.now().isoformat(),
                    'name': name or 'auto',
                    'version': '1.0'
                }
                zf.writestr('backup_metadata.json', json.dumps(metadata))

            log_info(f"Backup created: {backup_path}")

            # Cleanup old backups
            self._cleanup_old_backups()

            return str(backup_path)

        except Exception as e:
            log_error(e, "create_backup")
            if backup_path.exists():
                backup_path.unlink()
            raise BackupError(f"Failed to create backup: {e}")

    def restore_backup(self, backup_path: str) -> bool:
        """
        Restore from backup file.

        Args:
            backup_path: Path to backup ZIP file

        Returns:
            True if successful

        Raises:
            RestoreError: If restore fails
        """
        backup_path = Path(backup_path)
        if not backup_path.exists():
            raise RestoreError(f"Backup file not found: {backup_path}")

        try:
            # Create safety backup first
            safety_backup = self.create_backup("pre_restore_safety")
            log_info(f"Created safety backup: {safety_backup}")

            # Extract and replace files
            with zipfile.ZipFile(backup_path, 'r') as zf:
                for filename in zf.namelist():
                    if filename == 'backup_metadata.json':
                        continue

                    # Determine target path
                    if filename == 'expenses.csv':
                        target = self.expenses_file
                    elif filename == 'budgets.csv':
                        target = self.budgets_file
                    elif filename == 'templates.csv':
                        target = self.templates_file
                    elif filename == 'settings.json':
                        target = self.settings_file
                    else:
                        continue

                    # Extract to temp file, then atomic rename
                    with zf.open(filename) as source:
                        content = source.read()
                        temp_file = target.with_suffix('.restore_tmp')
                        with open(temp_file, 'wb') as tf:
                            tf.write(content)
                        temp_file.replace(target)

            # Clear settings cache
            self._settings_cache = None

            log_info(f"Restored from backup: {backup_path}")
            return True

        except Exception as e:
            log_error(e, "restore_backup")
            raise RestoreError(f"Failed to restore backup: {e}")

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
                info = {
                    'path': str(backup_file),
                    'name': backup_file.name,
                    'size': stat.st_size,
                    'size_display': self._format_size(stat.st_size),
                    'created': datetime.fromtimestamp(stat.st_mtime),
                    'created_display': datetime.fromtimestamp(stat.st_mtime).strftime('%d/%m/%Y %H:%M'),
                    'type': 'auto'
                }

                # Try to get metadata from zip
                with zipfile.ZipFile(backup_file, 'r') as zf:
                    if 'backup_metadata.json' in zf.namelist():
                        metadata = json.loads(zf.read('backup_metadata.json'))
                        info['type'] = metadata.get('name', 'auto')

                    # Count expenses in backup
                    if 'expenses.csv' in zf.namelist():
                        content = zf.read('expenses.csv').decode('utf-8')
                        info['expense_count'] = max(0, content.count('\n') - 1)

                backups.append(info)

            except Exception as e:
                log_warning(f"Error reading backup {backup_file}: {e}")

        # Sort by creation time, newest first
        backups.sort(key=lambda x: x['created'], reverse=True)
        return backups

    def _cleanup_old_backups(self) -> int:
        """
        Remove old backups based on settings.

        Returns:
            Number of backups deleted
        """
        settings = self.get_settings()
        max_backups = settings.get('backup', {}).get('max_backups', 10)

        backups = self.list_backups()
        deleted = 0

        # Keep only max_backups
        if len(backups) > max_backups:
            for backup in backups[max_backups:]:
                try:
                    Path(backup['path']).unlink()
                    deleted += 1
                    log_info(f"Deleted old backup: {backup['name']}")
                except Exception as e:
                    log_warning(f"Failed to delete backup: {e}")

        return deleted

    # ===== IMPORT OPERATIONS =====

    def import_csv(
        self,
        file_path: str,
        mapping: Dict[str, str]
    ) -> Tuple[int, int, List[Dict]]:
        """
        Import external CSV with column mapping.

        Args:
            file_path: Path to CSV file
            mapping: Dict mapping our fields to CSV columns

        Returns:
            Tuple of (imported_count, skipped_count, skipped_rows)
        """
        from utils.validators import validate_expense
        from models import Expense

        file_path = Path(file_path)
        if not file_path.exists():
            raise DataFileNotFoundError(str(file_path))

        imported = 0
        skipped = 0
        skipped_rows = []

        try:
            # Load existing expenses
            existing_df = self.load_expenses()

            # Read import file
            import_df = pd.read_csv(file_path, dtype=str, keep_default_na=False)

            new_expenses = []

            for idx, row in import_df.iterrows():
                try:
                    # Map columns
                    expense_data = {}
                    for our_field, csv_column in mapping.items():
                        if csv_column and csv_column in row:
                            expense_data[our_field] = row[csv_column]

                    # Create expense object for validation
                    expense = Expense.from_dict(expense_data)
                    errors = validate_expense(expense)

                    if errors:
                        skipped += 1
                        skipped_rows.append({
                            'row': idx + 2,  # +2 for header and 0-indexing
                            'error': '; '.join([f"{f}: {m}" for f, m in errors]),
                            'data': dict(row)
                        })
                        continue

                    new_expenses.append(expense.to_dict())
                    imported += 1

                except Exception as e:
                    skipped += 1
                    skipped_rows.append({
                        'row': idx + 2,
                        'error': str(e),
                        'data': dict(row)
                    })

            # Append new expenses
            if new_expenses:
                new_df = pd.DataFrame(new_expenses)
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                self.save_expenses(combined_df)

            log_info(f"Imported {imported} expenses, skipped {skipped}")
            return imported, skipped, skipped_rows

        except Exception as e:
            log_error(e, "import_csv")
            raise

    # ===== UTILITY METHODS =====

    def _atomic_write_csv(
        self,
        filepath: Path,
        df: pd.DataFrame,
        columns: List[str]
    ) -> None:
        """
        Write DataFrame to CSV using atomic operation.

        Args:
            filepath: Target file path
            df: DataFrame to write
            columns: Expected columns
        """
        temp_file = filepath.with_suffix('.tmp')

        try:
            # Ensure columns exist and are in order
            for col in columns:
                if col not in df.columns:
                    df[col] = ""

            df = df[columns]

            # Write to temp file
            df.to_csv(temp_file, index=False)

            # Verify temp file
            verify_df = pd.read_csv(temp_file, nrows=1)
            if list(verify_df.columns) != columns:
                raise FileError("Column verification failed")

            # Atomic rename
            temp_file.replace(filepath)

        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise FileError(f"Failed to save file: {e}")

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
            return True, 0  # Assume OK if check fails

    def get_data_stats(self) -> Dict:
        """
        Get statistics about stored data.

        Returns:
            Dictionary with data statistics
        """
        stats = {
            'expenses': 0,
            'budgets': 0,
            'templates': 0,
            'total_size': 0,
            'last_backup': None,
            'backup_count': 0
        }

        try:
            # Count records
            if self.expenses_file.exists():
                df = self.load_expenses()
                stats['expenses'] = len(df)
                stats['total_size'] += self.expenses_file.stat().st_size

            if self.budgets_file.exists():
                df = self.load_budgets()
                stats['budgets'] = len(df)
                stats['total_size'] += self.budgets_file.stat().st_size

            if self.templates_file.exists():
                df = self.load_templates()
                stats['templates'] = len(df)
                stats['total_size'] += self.templates_file.stat().st_size

            # Backup info
            backups = self.list_backups()
            stats['backup_count'] = len(backups)
            if backups:
                stats['last_backup'] = backups[0]['created_display']

            stats['total_size_display'] = self._format_size(stats['total_size'])

        except Exception as e:
            log_warning(f"Error getting stats: {e}")

        return stats

    def _format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def recover_corrupted_csv(self, filepath: str) -> Tuple[int, int, str]:
        """
        Attempt to recover data from corrupted CSV.

        Args:
            filepath: Path to corrupted file

        Returns:
            Tuple of (recovered_count, lost_count, backup_path)
        """
        filepath = Path(filepath)
        if not filepath.exists():
            return 0, 0, ""

        # Create backup of corrupted file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = filepath.with_name(f"{filepath.stem}.corrupted.{timestamp}{filepath.suffix}")
        shutil.copy2(filepath, backup_path)

        recovered = 0
        lost = 0
        recovered_rows = []

        try:
            with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
                lines = f.readlines()

            if not lines:
                return 0, 0, str(backup_path)

            # First line should be header
            header = lines[0].strip().split(',')

            for i, line in enumerate(lines[1:], start=2):
                try:
                    values = line.strip().split(',')
                    if len(values) == len(header):
                        recovered_rows.append(line)
                        recovered += 1
                    else:
                        lost += 1
                        log_warning(f"Line {i}: Column count mismatch")
                except Exception as e:
                    lost += 1
                    log_warning(f"Line {i}: Parse error - {e}")

            # Write recovered data
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(lines[0])
                f.writelines(recovered_rows)

            log_info(f"Recovery: {recovered} recovered, {lost} lost. Backup: {backup_path}")

        except Exception as e:
            log_error(e, "recover_corrupted_csv")

        return recovered, lost, str(backup_path)

    def safe_write(self, filepath: str, content: str) -> bool:
        """
        Safely write file with temp file and atomic rename.

        Args:
            filepath: Target file path
            content: Content to write

        Returns:
            True if successful
        """
        filepath = Path(filepath)
        temp_file = filepath.with_suffix('.tmp')

        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(content)

            temp_file.replace(filepath)
            return True

        except Exception as e:
            log_error(e, "safe_write")
            if temp_file.exists():
                temp_file.unlink()
            return False


# Singleton instance
_data_manager: Optional[DataManager] = None


def get_data_manager() -> DataManager:
    """
    Get or create global DataManager instance.

    Returns:
        DataManager singleton instance
    """
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager
