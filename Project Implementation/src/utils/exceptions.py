"""
Custom exception classes for Beauty Salon Expense Manager.
"""

from typing import List, Dict, Any, Optional


class ExpenseError(Exception):
    """Base exception for all expense-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        return self.message


class ValidationError(ExpenseError):
    """Raised when input validation fails."""

    def __init__(self, field: str, message: str, value: Any = None):
        super().__init__(f"{field}: {message}")
        self.field = field
        self.value = value
        self.details = {'field': field, 'value': value}


class MultipleValidationError(ExpenseError):
    """Raised when multiple validation errors occur."""

    def __init__(self, errors: List[tuple]):
        """
        Args:
            errors: List of (field, message) tuples
        """
        self.errors = errors
        messages = [f"{field}: {msg}" for field, msg in errors]
        super().__init__("Multiple validation errors:\n" + "\n".join(messages))
        self.details = {'errors': errors}

    def get_error_dict(self) -> Dict[str, str]:
        """Get errors as field -> message dictionary."""
        return {field: msg for field, msg in self.errors}

    def get_field_errors(self, field: str) -> List[str]:
        """Get all errors for a specific field."""
        return [msg for f, msg in self.errors if f == field]


class FileError(ExpenseError):
    """Raised for file operation errors."""

    def __init__(self, message: str, filepath: Optional[str] = None):
        super().__init__(message)
        self.filepath = filepath
        self.details = {'filepath': filepath}


class DataFileNotFoundError(FileError):
    """Raised when a required data file is not found."""

    def __init__(self, filepath: str):
        super().__init__(f"Data file not found: {filepath}", filepath)


class DataFilePermissionError(FileError):
    """Raised when data file permission is denied."""

    def __init__(self, filepath: str, operation: str = "access"):
        super().__init__(
            f"Permission denied when trying to {operation} file: {filepath}",
            filepath
        )
        self.operation = operation
        self.details['operation'] = operation


class DataFileCorruptedError(FileError):
    """Raised when a data file is corrupted."""

    def __init__(self, filepath: str, reason: str = ""):
        message = f"Data file is corrupted: {filepath}"
        if reason:
            message += f" ({reason})"
        super().__init__(message, filepath)
        self.reason = reason
        self.details['reason'] = reason


class DataIntegrityError(ExpenseError):
    """Raised when data consistency check fails."""

    def __init__(self, message: str, record_type: str = "", record_id: str = ""):
        super().__init__(message)
        self.record_type = record_type
        self.record_id = record_id
        self.details = {
            'record_type': record_type,
            'record_id': record_id
        }


class DuplicateRecordError(DataIntegrityError):
    """Raised when a duplicate record is detected."""

    def __init__(self, record_type: str, record_id: str, existing_id: str = ""):
        super().__init__(
            f"Duplicate {record_type} record detected",
            record_type,
            record_id
        )
        self.existing_id = existing_id
        self.details['existing_id'] = existing_id


class BudgetError(ExpenseError):
    """Raised for budget-related errors."""

    def __init__(self, message: str, category: str = "", budget_id: str = ""):
        super().__init__(message)
        self.category = category
        self.budget_id = budget_id
        self.details = {
            'category': category,
            'budget_id': budget_id
        }


class BudgetExceededError(BudgetError):
    """Raised when an expense would exceed budget."""

    def __init__(self, category: str, budget_amount: float, spent: float, expense_amount: float):
        remaining = budget_amount - spent
        super().__init__(
            f"Expense of L {expense_amount:,.2f} would exceed budget. "
            f"Remaining: L {remaining:,.2f}",
            category
        )
        self.budget_amount = budget_amount
        self.spent = spent
        self.expense_amount = expense_amount
        self.remaining = remaining
        self.details.update({
            'budget_amount': budget_amount,
            'spent': spent,
            'expense_amount': expense_amount,
            'remaining': remaining
        })


class BudgetWarningError(BudgetError):
    """Raised when expense approaches budget threshold."""

    def __init__(self, category: str, percentage: float, threshold: float):
        super().__init__(
            f"Budget warning: {category} is at {percentage:.1f}% "
            f"(threshold: {threshold:.1f}%)",
            category
        )
        self.percentage = percentage
        self.threshold = threshold
        self.details.update({
            'percentage': percentage,
            'threshold': threshold
        })


class BudgetNotFoundError(BudgetError):
    """Raised when a budget is not found."""

    def __init__(self, category: str = "", period: str = ""):
        message = "Budget not found"
        if category:
            message += f" for category: {category}"
        if period:
            message += f" in period: {period}"
        super().__init__(message, category)
        self.period = period
        self.details['period'] = period


class ExportError(ExpenseError):
    """Raised when export operation fails."""

    def __init__(self, message: str, export_type: str = "", filepath: str = ""):
        super().__init__(message)
        self.export_type = export_type
        self.filepath = filepath
        self.details = {
            'export_type': export_type,
            'filepath': filepath
        }


class DataImportError(ExpenseError):
    """Raised when import operation fails."""

    def __init__(self, message: str, source: str = "", row_number: int = 0):
        super().__init__(message)
        self.source = source
        self.row_number = row_number
        self.details = {
            'source': source,
            'row_number': row_number
        }


class BackupError(ExpenseError):
    """Raised for backup/restore operation errors."""

    def __init__(self, message: str, backup_path: str = "", operation: str = ""):
        super().__init__(message)
        self.backup_path = backup_path
        self.operation = operation
        self.details = {
            'backup_path': backup_path,
            'operation': operation
        }


class RestoreError(BackupError):
    """Raised when restore operation fails."""
    pass


class ConfigurationError(ExpenseError):
    """Raised for configuration-related errors."""

    def __init__(self, message: str, setting: str = ""):
        super().__init__(message)
        self.setting = setting
        self.details = {'setting': setting}


class RecurringExpenseError(ExpenseError):
    """Raised for recurring expense processing errors."""

    def __init__(self, message: str, expense_id: str = ""):
        super().__init__(message)
        self.expense_id = expense_id
        self.details = {'expense_id': expense_id}


class TemplateError(ExpenseError):
    """Raised for template-related errors."""

    def __init__(self, message: str, template_id: str = ""):
        super().__init__(message)
        self.template_id = template_id
        self.details = {'template_id': template_id}


class TemplateNotFoundError(TemplateError):
    """Raised when a template is not found."""

    def __init__(self, template_id: str):
        super().__init__(f"Template not found: {template_id}", template_id)


class DiskSpaceError(FileError):
    """Raised when there is insufficient disk space."""

    def __init__(self, required_mb: int, available_mb: int):
        super().__init__(
            f"Insufficient disk space. Required: {required_mb}MB, "
            f"Available: {available_mb}MB"
        )
        self.required_mb = required_mb
        self.available_mb = available_mb
        self.details.update({
            'required_mb': required_mb,
            'available_mb': available_mb
        })


class OperationCancelledError(ExpenseError):
    """Raised when an operation is cancelled by the user."""

    def __init__(self, operation: str = "Operation"):
        super().__init__(f"{operation} was cancelled by user")
        self.operation = operation
        self.details = {'operation': operation}
