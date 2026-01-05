"""
BackupManager - Automated backup management.
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import threading

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from persistence.data_manager import get_data_manager
from utils.error_handler import log_info, log_warning, log_error


class BackupManager:
    """
    Manages automated and scheduled backups.
    """

    def __init__(self):
        """Initialize backup manager."""
        self.data_manager = get_data_manager()
        self._last_auto_backup: Optional[datetime] = None
        self._backup_lock = threading.Lock()

    def check_auto_backup_needed(self) -> bool:
        """
        Check if automatic backup is needed.

        Returns:
            True if backup should be created
        """
        settings = self.data_manager.get_settings()

        if not settings.get('backup', {}).get('auto_backup', True):
            return False

        # Check last backup
        backups = self.data_manager.list_backups()
        if not backups:
            return True

        last_backup = backups[0]['created']
        hours_since = (datetime.now() - last_backup).total_seconds() / 3600

        # Backup if last one is > 24 hours old
        return hours_since > 24

    def run_auto_backup(self) -> Optional[str]:
        """
        Run automatic backup if needed.

        Returns:
            Backup path if created, None otherwise
        """
        with self._backup_lock:
            if not self.check_auto_backup_needed():
                return None

            try:
                backup_path = self.data_manager.create_backup("auto")
                self._last_auto_backup = datetime.now()
                log_info(f"Auto backup created: {backup_path}")
                return backup_path
            except Exception as e:
                log_error(e, "run_auto_backup")
                return None

    def run_scheduled_backup(self) -> Optional[str]:
        """
        Run scheduled backup.

        Returns:
            Backup path if created, None otherwise
        """
        with self._backup_lock:
            try:
                backup_path = self.data_manager.create_backup("scheduled")
                log_info(f"Scheduled backup created: {backup_path}")
                return backup_path
            except Exception as e:
                log_error(e, "run_scheduled_backup")
                return None

    def create_manual_backup(self, name: str = "") -> Optional[str]:
        """
        Create a manual backup.

        Args:
            name: Optional backup name

        Returns:
            Backup path if created, None otherwise
        """
        with self._backup_lock:
            try:
                backup_name = name if name else "manual"
                backup_path = self.data_manager.create_backup(backup_name)
                log_info(f"Manual backup created: {backup_path}")
                return backup_path
            except Exception as e:
                log_error(e, "create_manual_backup")
                return None

    def get_backup_info(self) -> Dict:
        """
        Get backup system information.

        Returns:
            Dictionary with backup info
        """
        backups = self.data_manager.list_backups()
        settings = self.data_manager.get_settings()

        return {
            'enabled': settings.get('backup', {}).get('auto_backup', True),
            'backup_count': len(backups),
            'max_backups': settings.get('backup', {}).get('max_backups', 10),
            'last_backup': backups[0]['created_display'] if backups else 'Never',
            'last_backup_size': backups[0]['size_display'] if backups else '0 B',
            'next_auto_backup': self._estimate_next_backup(),
            'backups': backups[:5]  # Last 5 backups
        }

    def _estimate_next_backup(self) -> str:
        """Estimate when next auto backup will occur."""
        if self._last_auto_backup:
            next_backup = self._last_auto_backup + timedelta(hours=24)
            if next_backup > datetime.now():
                return next_backup.strftime('%d/%m/%Y %H:%M')
        return "On next startup"

    def cleanup_old_backups(self) -> int:
        """
        Remove old backups based on retention settings.

        Returns:
            Number of backups deleted
        """
        settings = self.data_manager.get_settings()
        retention_days = settings.get('backup', {}).get('retention_days', 30)
        max_backups = settings.get('backup', {}).get('max_backups', 10)

        backups = self.data_manager.list_backups()
        deleted = 0
        cutoff = datetime.now() - timedelta(days=retention_days)

        for i, backup in enumerate(backups):
            should_delete = False

            # Delete if over max count
            if i >= max_backups:
                should_delete = True

            # Delete if older than retention period
            if backup['created'] < cutoff:
                should_delete = True

            if should_delete:
                try:
                    Path(backup['path']).unlink()
                    deleted += 1
                    log_info(f"Deleted old backup: {backup['name']}")
                except Exception as e:
                    log_warning(f"Failed to delete backup: {e}")

        return deleted

    def verify_backup(self, backup_path: str) -> bool:
        """
        Verify backup file integrity.

        Args:
            backup_path: Path to backup file

        Returns:
            True if backup is valid
        """
        import zipfile

        try:
            with zipfile.ZipFile(backup_path, 'r') as zf:
                # Check ZIP integrity
                bad_file = zf.testzip()
                if bad_file:
                    log_warning(f"Corrupted file in backup: {bad_file}")
                    return False

                # Check required files exist
                required = ['expenses.csv', 'budgets.csv']
                for req in required:
                    if req not in zf.namelist():
                        log_warning(f"Missing file in backup: {req}")
                        return False

                return True

        except Exception as e:
            log_error(e, "verify_backup")
            return False


# Singleton instance
_backup_manager: Optional[BackupManager] = None


def get_backup_manager() -> BackupManager:
    """Get or create global BackupManager instance."""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupManager()
    return _backup_manager
