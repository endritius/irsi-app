"""
SettingsManager - Application settings management.
"""

from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from copy import deepcopy

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from persistence.data_manager import get_data_manager, DEFAULT_SETTINGS
from utils.error_handler import log_info, log_warning


class SettingsManager:
    """
    Manages application settings with change notifications.
    """

    def __init__(self):
        """Initialize settings manager."""
        self.data_manager = get_data_manager()
        self._observers: List[Callable[[str, Any], None]] = []
        self._settings_cache: Optional[Dict] = None

    @property
    def settings(self) -> Dict:
        """Get current settings."""
        if self._settings_cache is None:
            self._settings_cache = self.data_manager.load_settings()
        return deepcopy(self._settings_cache)

    def reload_settings(self) -> Dict:
        """Force reload settings from file."""
        self._settings_cache = None
        return self.settings

    def save_settings(self, settings: Dict) -> None:
        """
        Save settings to file.

        Args:
            settings: Complete settings dictionary
        """
        self.data_manager.save_settings(settings)
        self._settings_cache = deepcopy(settings)
        self._notify_observers('all', settings)

    def get(self, section: str, key: str = None, default: Any = None) -> Any:
        """
        Get a setting value.

        Args:
            section: Settings section (e.g., 'general', 'backup')
            key: Optional key within section
            default: Default value if not found

        Returns:
            Setting value
        """
        settings = self.settings
        if section not in settings:
            return default

        if key is None:
            return settings[section]

        return settings[section].get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """
        Set a setting value.

        Args:
            section: Settings section
            key: Key within section
            value: New value
        """
        settings = self.settings

        if section not in settings:
            settings[section] = {}

        old_value = settings[section].get(key)
        settings[section][key] = value

        self.save_settings(settings)

        if old_value != value:
            self._notify_observers(f"{section}.{key}", value)

    def update_section(self, section: str, updates: Dict) -> None:
        """
        Update multiple values in a section.

        Args:
            section: Settings section
            updates: Dictionary of key-value pairs to update
        """
        settings = self.settings

        if section not in settings:
            settings[section] = {}

        for key, value in updates.items():
            settings[section][key] = value

        self.save_settings(settings)
        self._notify_observers(section, settings[section])

    def reset_to_defaults(self, section: str = None) -> None:
        """
        Reset settings to defaults.

        Args:
            section: Optional specific section to reset (None = all)
        """
        if section is None:
            self.save_settings(deepcopy(DEFAULT_SETTINGS))
            log_info("All settings reset to defaults")
        elif section in DEFAULT_SETTINGS:
            settings = self.settings
            settings[section] = deepcopy(DEFAULT_SETTINGS[section])
            self.save_settings(settings)
            log_info(f"Settings section '{section}' reset to defaults")

    def add_observer(self, callback: Callable[[str, Any], None]) -> None:
        """
        Add settings change observer.

        Args:
            callback: Function called with (setting_path, new_value)
        """
        if callback not in self._observers:
            self._observers.append(callback)

    def remove_observer(self, callback: Callable[[str, Any], None]) -> None:
        """Remove settings change observer."""
        if callback in self._observers:
            self._observers.remove(callback)

    def _notify_observers(self, path: str, value: Any) -> None:
        """Notify all observers of setting change."""
        for observer in self._observers:
            try:
                observer(path, value)
            except Exception as e:
                log_warning(f"Settings observer error: {e}")

    # ===== Convenience Properties =====

    @property
    def salon_name(self) -> str:
        """Get salon name."""
        return self.get('general', 'salon_name', 'Beauty Salon')

    @salon_name.setter
    def salon_name(self, value: str) -> None:
        self.set('general', 'salon_name', value)

    @property
    def date_format(self) -> str:
        """Get date format string."""
        return self.get('general', 'date_format', 'DD/MM/YYYY')

    @property
    def auto_backup_enabled(self) -> bool:
        """Check if auto backup is enabled."""
        return self.get('backup', 'auto_backup', True)

    @auto_backup_enabled.setter
    def auto_backup_enabled(self, value: bool) -> None:
        self.set('backup', 'auto_backup', value)

    @property
    def warning_threshold(self) -> float:
        """Get budget warning threshold percentage."""
        return float(self.get('alerts', 'warning_threshold', 80))

    @warning_threshold.setter
    def warning_threshold(self, value: float) -> None:
        self.set('alerts', 'warning_threshold', value)

    @property
    def critical_threshold(self) -> float:
        """Get budget critical threshold percentage."""
        return float(self.get('alerts', 'critical_threshold', 95))

    @critical_threshold.setter
    def critical_threshold(self, value: float) -> None:
        self.set('alerts', 'critical_threshold', value)

    @property
    def show_notifications(self) -> bool:
        """Check if notifications are enabled."""
        return self.get('alerts', 'show_notifications', True)

    @property
    def page_size(self) -> int:
        """Get default page size for lists."""
        return int(self.get('display', 'page_size', 50))

    @page_size.setter
    def page_size(self, value: int) -> None:
        self.set('display', 'page_size', value)

    @property
    def auto_save_enabled(self) -> bool:
        """Check if auto save is enabled."""
        return self.get('data', 'auto_save', True)

    @property
    def duplicate_detection_enabled(self) -> bool:
        """Check if duplicate detection is enabled."""
        return self.get('data', 'duplicate_detection', True)

    @property
    def confirm_delete(self) -> bool:
        """Check if delete confirmation is required."""
        return self.get('data', 'confirm_delete', True)

    @property
    def theme(self) -> str:
        """Get current theme."""
        return self.get('display', 'theme', 'default')

    @theme.setter
    def theme(self, value: str) -> None:
        self.set('display', 'theme', value)

    def export_settings(self) -> Dict:
        """
        Export settings for backup or sharing.

        Returns:
            Complete settings dictionary
        """
        return self.settings

    def import_settings(self, settings: Dict, merge: bool = True) -> None:
        """
        Import settings.

        Args:
            settings: Settings dictionary to import
            merge: If True, merge with existing; if False, replace
        """
        if merge:
            current = self.settings
            self._merge_dict(current, settings)
            self.save_settings(current)
        else:
            self.save_settings(settings)

        log_info("Settings imported")

    def _merge_dict(self, base: Dict, updates: Dict) -> None:
        """Recursively merge updates into base dictionary."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._merge_dict(base[key], value)
            else:
                base[key] = value


# Singleton instance
_settings_manager: Optional[SettingsManager] = None


def get_settings_manager() -> SettingsManager:
    """Get or create global SettingsManager instance."""
    global _settings_manager
    if _settings_manager is None:
        _settings_manager = SettingsManager()
    return _settings_manager
