"""
ErrorHandler - Centralized error handling service.
"""

import logging
import traceback
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Callable, Optional, Any
import tkinter as tk
from tkinter import messagebox

# Configure paths
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import LOGS_DIR, APP_NAME


class ErrorHandler:
    """
    Centralized error handling service.
    Provides logging, dialogs, and toast notifications.
    """

    _instance: Optional['ErrorHandler'] = None

    def __init__(self, log_dir: str = None):
        """
        Initialize error handler.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir) if log_dir else LOGS_DIR
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # Setup logger
        self.logger = self._setup_logger()

        # Toast notification callback (set by UI)
        self._notification_callback: Optional[Callable] = None

        # Error message mappings
        self._user_messages = {
            'FileNotFoundError': "The requested file could not be found.",
            'PermissionError': "Permission denied. Please check file permissions.",
            'ValidationError': "The input data is invalid.",
            'DataIntegrityError': "A data consistency issue was detected.",
            'BudgetExceededError': "This expense would exceed your budget.",
            'ExportError': "Failed to export data. Please try again.",
            'BackupError': "Backup operation failed.",
            'DiskSpaceError': "Insufficient disk space available."
        }

    def __new__(cls, *args, **kwargs):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _setup_logger(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(APP_NAME)
        logger.setLevel(logging.DEBUG)

        # Remove existing handlers
        logger.handlers = []

        # Create daily log file
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.WARNING)

        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        return logger

    def set_notification_callback(self, callback: Callable) -> None:
        """
        Set callback for toast notifications.

        Args:
            callback: Function that accepts (message, toast_type)
        """
        self._notification_callback = callback

    def log_error(self, error: Exception, context: str = "") -> None:
        """
        Log error with full stack trace.

        Args:
            error: Exception to log
            context: Additional context information
        """
        error_type = type(error).__name__
        error_msg = str(error)
        stack_trace = traceback.format_exc()

        log_message = f"[{error_type}] {error_msg}"
        if context:
            log_message = f"[{context}] {log_message}"

        self.logger.error(log_message)
        self.logger.debug(f"Stack trace:\n{stack_trace}")

    def log_warning(self, message: str, context: str = "") -> None:
        """
        Log warning message.

        Args:
            message: Warning message
            context: Additional context
        """
        if context:
            message = f"[{context}] {message}"
        self.logger.warning(message)

    def log_info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(message)

    def log_debug(self, message: str) -> None:
        """Log debug message."""
        self.logger.debug(message)

    def get_user_message(self, error: Exception) -> str:
        """
        Convert technical error to user-friendly message.

        Args:
            error: Exception to convert

        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__

        # Check for specific exception types
        if error_type in self._user_messages:
            base_msg = self._user_messages[error_type]
            if hasattr(error, 'message') and error.message:
                return f"{base_msg}\n\nDetails: {error.message}"
            return base_msg

        # For custom exceptions with message attribute
        if hasattr(error, 'message'):
            return str(error.message)

        # Generic fallback
        return f"An error occurred: {str(error)}"

    def show_error_dialog(
        self,
        parent: Optional[tk.Widget],
        error: Exception,
        title: str = "Error"
    ) -> None:
        """
        Show Tkinter error dialog.

        Args:
            parent: Parent widget
            error: Exception to display
            title: Dialog title
        """
        user_message = self.get_user_message(error)
        messagebox.showerror(title, user_message, parent=parent)

    def show_warning_dialog(
        self,
        parent: Optional[tk.Widget],
        message: str,
        title: str = "Warning"
    ) -> None:
        """
        Show Tkinter warning dialog.

        Args:
            parent: Parent widget
            message: Warning message
            title: Dialog title
        """
        messagebox.showwarning(title, message, parent=parent)

    def show_info_dialog(
        self,
        parent: Optional[tk.Widget],
        message: str,
        title: str = "Information"
    ) -> None:
        """
        Show Tkinter info dialog.

        Args:
            parent: Parent widget
            message: Info message
            title: Dialog title
        """
        messagebox.showinfo(title, message, parent=parent)

    def confirm_action(
        self,
        parent: Optional[tk.Widget],
        message: str,
        title: str = "Confirm"
    ) -> bool:
        """
        Show confirmation dialog.

        Args:
            parent: Parent widget
            message: Confirmation message
            title: Dialog title

        Returns:
            True if user confirmed
        """
        return messagebox.askyesno(title, message, parent=parent)

    def confirm_destructive_action(
        self,
        parent: Optional[tk.Widget],
        message: str,
        title: str = "Confirm Delete"
    ) -> bool:
        """
        Show warning confirmation for destructive actions.

        Args:
            parent: Parent widget
            message: Warning message
            title: Dialog title

        Returns:
            True if user confirmed
        """
        return messagebox.askyesno(
            title,
            f"⚠️ Warning: This action cannot be undone.\n\n{message}",
            icon='warning',
            parent=parent
        )

    def show_toast(self, message: str, toast_type: str = "info") -> None:
        """
        Show toast notification if callback is set.

        Args:
            message: Notification message
            toast_type: Type (info, success, warning, error)
        """
        if self._notification_callback:
            try:
                self._notification_callback(message, toast_type)
            except Exception as e:
                self.log_warning(f"Failed to show toast: {e}")

    def handle_exception(
        self,
        error: Exception,
        context: str = "",
        parent: Optional[tk.Widget] = None,
        show_dialog: bool = True
    ) -> None:
        """
        Handle exception with logging and optional dialog.

        Args:
            error: Exception to handle
            context: Context for logging
            parent: Parent widget for dialog
            show_dialog: Whether to show error dialog
        """
        # Log the error
        self.log_error(error, context)

        # Show dialog if requested
        if show_dialog:
            self.show_error_dialog(parent, error)

    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Remove log files older than specified days.

        Args:
            days: Days to keep logs

        Returns:
            Number of files deleted
        """
        deleted = 0
        cutoff = datetime.now() - timedelta(days=days)

        try:
            for log_file in self.log_dir.glob("*.log"):
                file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_mtime < cutoff:
                    log_file.unlink()
                    deleted += 1
                    self.log_info(f"Deleted old log file: {log_file.name}")
        except Exception as e:
            self.log_warning(f"Error cleaning up logs: {e}")

        return deleted

    def get_recent_errors(self, limit: int = 10) -> list:
        """
        Get recent error entries from today's log.

        Args:
            limit: Maximum number of errors to return

        Returns:
            List of error log lines
        """
        errors = []
        log_file = self.log_dir / f"app_{datetime.now().strftime('%Y%m%d')}.log"

        if not log_file.exists():
            return errors

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if '[ERROR]' in line:
                        errors.append(line.strip())
        except Exception:
            pass

        return errors[-limit:]

    def export_logs(self, output_path: str, days: int = 7) -> bool:
        """
        Export recent logs to a file.

        Args:
            output_path: Path for output file
            days: Number of days to include

        Returns:
            True if successful
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            with open(output_path, 'w', encoding='utf-8') as out_file:
                for log_file in sorted(self.log_dir.glob("*.log")):
                    file_mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                    if file_mtime >= cutoff:
                        out_file.write(f"\n{'='*60}\n")
                        out_file.write(f"File: {log_file.name}\n")
                        out_file.write(f"{'='*60}\n")
                        with open(log_file, 'r', encoding='utf-8') as f:
                            out_file.write(f.read())
            return True
        except Exception as e:
            self.log_error(e, "export_logs")
            return False


# Global error handler instance
_error_handler: Optional[ErrorHandler] = None


def get_error_handler() -> ErrorHandler:
    """
    Get or create global error handler instance.

    Returns:
        ErrorHandler singleton instance
    """
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler


def handle_error(error: Exception, context: str = "", show_dialog: bool = False) -> None:
    """
    Convenience function for handling errors.

    Args:
        error: Exception to handle
        context: Context for logging
        show_dialog: Whether to show error dialog
    """
    handler = get_error_handler()
    handler.handle_exception(error, context, show_dialog=show_dialog)


def log_error(error: Exception, context: str = "") -> None:
    """Convenience function for logging errors."""
    get_error_handler().log_error(error, context)


def log_warning(message: str, context: str = "") -> None:
    """Convenience function for logging warnings."""
    get_error_handler().log_warning(message, context)


def log_info(message: str) -> None:
    """Convenience function for logging info."""
    get_error_handler().log_info(message)


def log_debug(message: str) -> None:
    """Convenience function for logging debug."""
    get_error_handler().log_debug(message)
