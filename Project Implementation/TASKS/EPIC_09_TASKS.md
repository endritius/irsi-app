# Epic 9: Error Handling & Validation - Implementation Tasks

**Phase:** 2 (Foundation)
**Priority:** High
**Dependencies:** Epic 1 (Core Data Models)
**Estimated Tasks:** 25+

---

## Story 9.1: Custom Exception Classes

**Prerequisites:** None (can start immediately after Epic 1)

### Task 9.1.1: Create utils package
- [ ] Create `utils/__init__.py`:
```python
"""
Utility modules for Beauty Salon Expense Manager.
Includes validators, error handling, exceptions, and formatters.
"""

from .exceptions import (
    ExpenseError,
    ValidationError,
    MultipleValidationError,
    FileError,
    DataFileNotFoundError,
    DataFilePermissionError,
    DataIntegrityError,
    BudgetError,
    BudgetExceededError,
    BudgetWarningError,
    ExportError,
    DataImportError,
    BackupError,
    ConfigurationError
)

__all__ = [
    'ExpenseError',
    'ValidationError',
    'MultipleValidationError',
    'FileError',
    'DataFileNotFoundError',
    'DataFilePermissionError',
    'DataIntegrityError',
    'BudgetError',
    'BudgetExceededError',
    'BudgetWarningError',
    'ExportError',
    'DataImportError',
    'BackupError',
    'ConfigurationError'
]
```

### Task 9.1.2: Create base exception class
- [ ] Create `utils/exceptions.py` with base class:
```python
"""
Custom exception classes for Beauty Salon Expense Manager.
All domain-specific exceptions inherit from ExpenseError.
"""

from typing import Optional, List, Dict, Any


class ExpenseError(Exception):
    """
    Base exception for all expense-related errors.

    Attributes:
        message: User-friendly error message
        technical_details: Technical details for debugging
        context: Additional context information
    """

    def __init__(
        self,
        message: str,
        technical_details: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.technical_details = technical_details
        self.context = context or {}

    def __str__(self) -> str:
        return self.message

    def get_full_details(self) -> str:
        """Get complete error information for logging."""
        details = f"Error: {self.message}"
        if self.technical_details:
            details += f"\nTechnical: {self.technical_details}"
        if self.context:
            details += f"\nContext: {self.context}"
        return details
```

### Task 9.1.3: Create validation exceptions
- [ ] Add validation exception classes:
```python
class ValidationError(ExpenseError):
    """
    Raised when input validation fails.

    Attributes:
        field: The field that failed validation
        value: The invalid value
        rule: The validation rule that was violated
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Any = None,
        rule: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.field = field
        self.value = value
        self.rule = rule


class MultipleValidationError(ExpenseError):
    """
    Raised when multiple validation errors occur.

    Attributes:
        errors: List of (field, error_message) tuples
    """

    def __init__(
        self,
        message: str = "Multiple validation errors occurred",
        errors: Optional[List[tuple]] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.errors = errors or []

    def add_error(self, field: str, error_message: str) -> None:
        """Add a validation error to the list."""
        self.errors.append((field, error_message))

    def has_errors(self) -> bool:
        """Check if any errors were collected."""
        return len(self.errors) > 0

    def get_error_dict(self) -> Dict[str, str]:
        """Get errors as a dictionary."""
        return {field: msg for field, msg in self.errors}
```

### Task 9.1.4: Create file operation exceptions
- [ ] Add file exception classes:
```python
class FileError(ExpenseError):
    """
    Raised for file operation errors.

    Attributes:
        filepath: Path to the file that caused the error
        operation: The operation that failed (read, write, delete)
    """

    def __init__(
        self,
        message: str,
        filepath: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.filepath = filepath
        self.operation = operation


class DataFileNotFoundError(FileError):
    """
    Raised when a required data file is not found.
    Distinct from Python's FileNotFoundError to allow domain-specific handling.
    """

    def __init__(self, filepath: str, **kwargs):
        message = f"Data file not found: {filepath}"
        super().__init__(message, filepath=filepath, operation="read", **kwargs)


class DataFilePermissionError(FileError):
    """
    Raised when data file permission is denied.
    Distinct from Python's PermissionError to allow domain-specific handling.
    """

    def __init__(self, filepath: str, operation: str = "access", **kwargs):
        message = f"Permission denied for {operation} on: {filepath}"
        super().__init__(message, filepath=filepath, operation=operation, **kwargs)
```

### Task 9.1.5: Create data integrity exception
- [ ] Add data integrity exception:
```python
class DataIntegrityError(ExpenseError):
    """
    Raised when data consistency check fails.

    Attributes:
        record_type: Type of record with issue (expense, budget, etc.)
        record_id: ID of the affected record
        issue: Description of the integrity issue
    """

    def __init__(
        self,
        message: str,
        record_type: Optional[str] = None,
        record_id: Optional[str] = None,
        issue: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.record_type = record_type
        self.record_id = record_id
        self.issue = issue
```

### Task 9.1.6: Create budget exceptions
- [ ] Add budget exception classes:
```python
class BudgetError(ExpenseError):
    """
    Raised for budget-related errors.

    Attributes:
        category: Budget category affected
        budget_amount: The budget limit
        current_spending: Current spending amount
    """

    def __init__(
        self,
        message: str,
        category: Optional[str] = None,
        budget_amount: Optional[float] = None,
        current_spending: Optional[float] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.category = category
        self.budget_amount = budget_amount
        self.current_spending = current_spending


class BudgetExceededError(BudgetError):
    """
    Raised when an expense would exceed budget.

    Attributes:
        expense_amount: Amount of the expense causing the exceedance
        excess_amount: Amount by which budget is exceeded
    """

    def __init__(
        self,
        category: str,
        budget_amount: float,
        current_spending: float,
        expense_amount: float,
        **kwargs
    ):
        excess = (current_spending + expense_amount) - budget_amount
        message = (
            f"Budget exceeded for {category}: "
            f"L {expense_amount:,.2f} would exceed budget by L {excess:,.2f}"
        )
        super().__init__(
            message,
            category=category,
            budget_amount=budget_amount,
            current_spending=current_spending,
            **kwargs
        )
        self.expense_amount = expense_amount
        self.excess_amount = excess


class BudgetWarningError(BudgetError):
    """
    Raised when expense approaches budget threshold.

    Attributes:
        percentage_used: Current percentage of budget used
        threshold: Warning threshold percentage
    """

    def __init__(
        self,
        category: str,
        budget_amount: float,
        current_spending: float,
        threshold: float = 80.0,
        **kwargs
    ):
        percentage = (current_spending / budget_amount) * 100 if budget_amount > 0 else 0
        message = (
            f"Budget warning for {category}: "
            f"{percentage:.1f}% used (threshold: {threshold}%)"
        )
        super().__init__(
            message,
            category=category,
            budget_amount=budget_amount,
            current_spending=current_spending,
            **kwargs
        )
        self.percentage_used = percentage
        self.threshold = threshold
```

### Task 9.1.7: Create operation exceptions
- [ ] Add export, import, backup, and configuration exceptions:
```python
class ExportError(ExpenseError):
    """
    Raised when export operation fails.

    Attributes:
        export_type: Type of export (PDF, Excel, CSV, Image)
        filepath: Target file path
    """

    def __init__(
        self,
        message: str,
        export_type: Optional[str] = None,
        filepath: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.export_type = export_type
        self.filepath = filepath


class DataImportError(ExpenseError):
    """
    Raised when import operation fails.

    Attributes:
        filepath: Source file path
        row_number: Row where error occurred (if applicable)
        column: Column with issue (if applicable)
    """

    def __init__(
        self,
        message: str,
        filepath: Optional[str] = None,
        row_number: Optional[int] = None,
        column: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.filepath = filepath
        self.row_number = row_number
        self.column = column


class BackupError(ExpenseError):
    """
    Raised for backup/restore operation errors.

    Attributes:
        backup_path: Path to backup file
        operation: backup or restore
    """

    def __init__(
        self,
        message: str,
        backup_path: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.backup_path = backup_path
        self.operation = operation


class ConfigurationError(ExpenseError):
    """
    Raised for configuration-related errors.

    Attributes:
        setting: The setting that has an issue
        expected_type: Expected type/format
        actual_value: The invalid value
    """

    def __init__(
        self,
        message: str,
        setting: Optional[str] = None,
        expected_type: Optional[str] = None,
        actual_value: Any = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.setting = setting
        self.expected_type = expected_type
        self.actual_value = actual_value
```

### Task 9.1.8: Create exception tests
- [ ] Create `tests/test_utils/__init__.py`
- [ ] Create `tests/test_utils/test_exceptions.py`:
```python
"""Tests for custom exception classes."""

import pytest
from utils.exceptions import (
    ExpenseError,
    ValidationError,
    MultipleValidationError,
    FileError,
    DataFileNotFoundError,
    DataFilePermissionError,
    DataIntegrityError,
    BudgetError,
    BudgetExceededError,
    BudgetWarningError,
    ExportError,
    DataImportError,
    BackupError,
    ConfigurationError
)


class TestExpenseError:
    """Tests for base ExpenseError."""

    def test_basic_creation(self):
        error = ExpenseError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.message == "Something went wrong"

    def test_with_technical_details(self):
        error = ExpenseError(
            "User error",
            technical_details="Stack trace here"
        )
        assert "Stack trace here" in error.get_full_details()

    def test_with_context(self):
        error = ExpenseError(
            "Error",
            context={"user_id": "123", "action": "save"}
        )
        assert error.context["user_id"] == "123"

    def test_inheritance(self):
        error = ExpenseError("Test")
        assert isinstance(error, Exception)


class TestValidationError:
    """Tests for ValidationError."""

    def test_with_field_info(self):
        error = ValidationError(
            "Invalid amount",
            field="amount",
            value=-100,
            rule="must be positive"
        )
        assert error.field == "amount"
        assert error.value == -100
        assert error.rule == "must be positive"


class TestMultipleValidationError:
    """Tests for MultipleValidationError."""

    def test_add_errors(self):
        error = MultipleValidationError()
        error.add_error("amount", "Must be positive")
        error.add_error("date", "Cannot be in future")

        assert error.has_errors()
        assert len(error.errors) == 2

    def test_get_error_dict(self):
        error = MultipleValidationError()
        error.add_error("field1", "Error 1")
        error.add_error("field2", "Error 2")

        error_dict = error.get_error_dict()
        assert error_dict["field1"] == "Error 1"
        assert error_dict["field2"] == "Error 2"


class TestBudgetExceededError:
    """Tests for BudgetExceededError."""

    def test_excess_calculation(self):
        error = BudgetExceededError(
            category="Supplies",
            budget_amount=50000,
            current_spending=48000,
            expense_amount=5000
        )
        assert error.excess_amount == 3000  # 48000 + 5000 - 50000
        assert error.category == "Supplies"
        assert "Supplies" in str(error)


class TestDataFileNotFoundError:
    """Tests for DataFileNotFoundError."""

    def test_filepath_included(self):
        error = DataFileNotFoundError("data/expenses.csv")
        assert error.filepath == "data/expenses.csv"
        assert "data/expenses.csv" in str(error)
        assert error.operation == "read"
```

---

## Story 9.2: Input Validators

**Prerequisites:** Story 9.1 (Custom Exceptions), Story 1.3 (CategoryManager)

### Task 9.2.1: Create validators module structure
- [ ] Create `utils/validators.py` with imports and constants:
```python
"""
Input validation functions for expense and budget data.
Each validator returns (is_valid: bool, error_message: str).
"""

import re
from datetime import datetime, timedelta
from typing import Any, Tuple, List, Optional

from models.category import CategoryManager

# Validation constants
MAX_AMOUNT = 10_000_000
MAX_DESCRIPTION_LENGTH = 500
MAX_VENDOR_LENGTH = 100
MAX_TAG_LENGTH = 30
MAX_TAGS_COUNT = 10

# Albanian Lek formatting
CURRENCY_SYMBOL = "L"
```

### Task 9.2.2: Implement amount validator
- [ ] Add amount validation function:
```python
def validate_amount(amount: Any) -> Tuple[bool, str]:
    """
    Validate expense amount.

    Rules:
    - Must be a number (int or float)
    - Must be positive (> 0)
    - Maximum 10,000,000
    - Maximum 2 decimal places

    Args:
        amount: The amount to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if numeric
    if amount is None:
        return False, "Amount is required"

    try:
        amount_float = float(amount)
    except (TypeError, ValueError):
        return False, "Amount must be a number"

    # Check positive
    if amount_float <= 0:
        return False, "Amount must be positive"

    # Check maximum
    if amount_float > MAX_AMOUNT:
        return False, f"Amount cannot exceed L {MAX_AMOUNT:,.2f}"

    # Check decimal places
    amount_str = str(amount_float)
    if '.' in amount_str:
        decimal_places = len(amount_str.split('.')[1])
        if decimal_places > 2:
            return False, "Amount can have at most 2 decimal places"

    return True, ""
```

### Task 9.2.3: Implement date validator
- [ ] Add date validation function:
```python
def validate_date(
    date_input: Any,
    allow_future: bool = False
) -> Tuple[bool, str]:
    """
    Validate expense date.

    Rules:
    - Must be a valid date
    - Cannot be in the future (unless allow_future=True)
    - Cannot be older than 10 years

    Args:
        date_input: The date to validate (datetime, date, or string)
        allow_future: Whether to allow future dates

    Returns:
        Tuple of (is_valid, error_message)
    """
    if date_input is None:
        return False, "Date is required"

    # Convert to datetime if needed
    if isinstance(date_input, str):
        # Try multiple formats
        formats = ["%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"]
        parsed_date = None
        for fmt in formats:
            try:
                parsed_date = datetime.strptime(date_input, fmt)
                break
            except ValueError:
                continue
        if parsed_date is None:
            return False, "Invalid date format. Use DD/MM/YYYY"
        date_input = parsed_date

    if not isinstance(date_input, datetime):
        try:
            # Handle date objects
            date_input = datetime.combine(date_input, datetime.min.time())
        except (TypeError, AttributeError):
            return False, "Invalid date type"

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    # Check future date
    if not allow_future and date_input.date() > today.date():
        return False, "Date cannot be in the future"

    # Check too old (10 years)
    ten_years_ago = today - timedelta(days=3650)
    if date_input < ten_years_ago:
        return False, "Date cannot be more than 10 years ago"

    return True, ""
```

### Task 9.2.4: Implement category validators
- [ ] Add category and subcategory validation:
```python
def validate_category(category: str) -> Tuple[bool, str]:
    """
    Validate that category exists in predefined list.

    Args:
        category: The category name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not category or not category.strip():
        return False, "Category is required"

    category = category.strip()
    valid_categories = CategoryManager.get_categories()

    if category not in valid_categories:
        valid_list = ", ".join(valid_categories)
        return False, f"Unknown category. Valid categories: {valid_list}"

    return True, ""


def validate_subcategory(category: str, subcategory: str) -> Tuple[bool, str]:
    """
    Validate that subcategory exists under the given category.

    Args:
        category: The parent category
        subcategory: The subcategory to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not subcategory or not subcategory.strip():
        return True, ""  # Subcategory is optional

    subcategory = subcategory.strip()
    valid_subcategories = CategoryManager.get_subcategories(category)

    if not valid_subcategories:
        return False, f"Category '{category}' has no subcategories defined"

    if subcategory not in valid_subcategories:
        valid_list = ", ".join(valid_subcategories)
        return False, f"Unknown subcategory. Valid options: {valid_list}"

    return True, ""
```

### Task 9.2.5: Implement payment method validator
- [ ] Add payment method validation:
```python
# Payment method constants
VALID_PAYMENT_METHODS = ["Cash", "Debit Card", "Credit Card", "Bank Transfer"]


def validate_payment_method(method: str) -> Tuple[bool, str]:
    """
    Validate payment method is in allowed list.

    Args:
        method: The payment method to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not method or not method.strip():
        return False, "Payment method is required"

    method = method.strip()

    if method not in VALID_PAYMENT_METHODS:
        valid_list = ", ".join(VALID_PAYMENT_METHODS)
        return False, f"Invalid payment method. Valid options: {valid_list}"

    return True, ""
```

### Task 9.2.6: Implement vendor and description validators
- [ ] Add text field validators:
```python
def validate_vendor(vendor: str) -> Tuple[bool, str]:
    """
    Validate vendor name.

    Rules:
    - Required field
    - Maximum 100 characters
    - Allowed characters: letters, numbers, spaces, common punctuation

    Args:
        vendor: The vendor name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not vendor or not vendor.strip():
        return False, "Vendor is required"

    vendor = vendor.strip()

    if len(vendor) > MAX_VENDOR_LENGTH:
        return False, f"Vendor name cannot exceed {MAX_VENDOR_LENGTH} characters"

    # Check for valid characters
    if not re.match(r'^[\w\s\-.,&\'\"()]+$', vendor, re.UNICODE):
        return False, "Vendor name contains invalid characters"

    return True, ""


def validate_description(description: str) -> Tuple[bool, str]:
    """
    Validate description field.

    Rules:
    - Optional field
    - Maximum 500 characters

    Args:
        description: The description to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description:
        return True, ""  # Optional field

    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters"

    return True, ""
```

### Task 9.2.7: Implement tag validator
- [ ] Add tag validation:
```python
def validate_tags(tags: List[str]) -> Tuple[bool, str]:
    """
    Validate tags list.

    Rules:
    - Maximum 10 tags
    - Each tag maximum 30 characters
    - Tags should be alphanumeric (with spaces and hyphens)

    Args:
        tags: List of tag strings

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tags:
        return True, ""  # Tags are optional

    if len(tags) > MAX_TAGS_COUNT:
        return False, f"Maximum {MAX_TAGS_COUNT} tags allowed"

    for tag in tags:
        if not tag or not tag.strip():
            continue

        tag = tag.strip()

        if len(tag) > MAX_TAG_LENGTH:
            return False, f"Tag '{tag[:20]}...' exceeds {MAX_TAG_LENGTH} characters"

        if not re.match(r'^[\w\s\-]+$', tag, re.UNICODE):
            return False, f"Tag '{tag}' contains invalid characters"

    return True, ""
```

### Task 9.2.8: Implement recurring validators
- [ ] Add recurring expense validation:
```python
VALID_RECURRING_TYPES = ["daily", "weekly", "biweekly", "monthly", "quarterly", "annually"]
VALID_RECURRING_ACTIONS = ["auto_generate", "reminder"]


def validate_recurring_type(recurring_type: str) -> Tuple[bool, str]:
    """
    Validate recurring type.

    Args:
        recurring_type: The recurring type to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not recurring_type:
        return True, ""  # Optional field

    recurring_type = recurring_type.lower().strip()

    if recurring_type not in VALID_RECURRING_TYPES:
        valid_list = ", ".join(VALID_RECURRING_TYPES)
        return False, f"Invalid recurring type. Valid options: {valid_list}"

    return True, ""


def validate_recurring_action(action: str) -> Tuple[bool, str]:
    """
    Validate recurring action.

    Args:
        action: The recurring action to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not action:
        return True, ""  # Optional field

    action = action.lower().strip()

    if action not in VALID_RECURRING_ACTIONS:
        valid_list = ", ".join(VALID_RECURRING_ACTIONS)
        return False, f"Invalid recurring action. Valid options: {valid_list}"

    return True, ""
```

### Task 9.2.9: Implement budget validators
- [ ] Add budget amount and threshold validation:
```python
def validate_budget_amount(amount: Any) -> Tuple[bool, str]:
    """
    Validate budget amount.

    Rules:
    - Must be a number
    - Must be non-negative (>= 0)
    - Maximum 10,000,000

    Args:
        amount: The budget amount to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount is None:
        return False, "Budget amount is required"

    try:
        amount_float = float(amount)
    except (TypeError, ValueError):
        return False, "Budget amount must be a number"

    if amount_float < 0:
        return False, "Budget amount cannot be negative"

    if amount_float > MAX_AMOUNT:
        return False, f"Budget amount cannot exceed L {MAX_AMOUNT:,.2f}"

    return True, ""


def validate_threshold(threshold: Any) -> Tuple[bool, str]:
    """
    Validate warning threshold percentage.

    Rules:
    - Must be a number
    - Must be between 0 and 100

    Args:
        threshold: The threshold percentage to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if threshold is None:
        return True, ""  # Uses default if not provided

    try:
        threshold_float = float(threshold)
    except (TypeError, ValueError):
        return False, "Threshold must be a number"

    if threshold_float < 0 or threshold_float > 100:
        return False, "Threshold must be between 0 and 100"

    return True, ""
```

### Task 9.2.10: Implement full expense validator
- [ ] Add complete expense validation:
```python
def validate_expense(expense) -> List[Tuple[str, str]]:
    """
    Validate an entire expense object.

    Args:
        expense: Expense object or dict with expense fields

    Returns:
        List of (field, error_message) tuples for all validation errors
    """
    errors = []

    # Get field values (handle both object and dict)
    if hasattr(expense, '__dict__'):
        data = expense.__dict__
    else:
        data = expense

    # Validate amount
    is_valid, msg = validate_amount(data.get('amount'))
    if not is_valid:
        errors.append(('amount', msg))

    # Validate date
    is_valid, msg = validate_date(data.get('date'))
    if not is_valid:
        errors.append(('date', msg))

    # Validate category
    category = data.get('category', '')
    is_valid, msg = validate_category(category)
    if not is_valid:
        errors.append(('category', msg))
    else:
        # Validate subcategory only if category is valid
        is_valid, msg = validate_subcategory(
            category,
            data.get('subcategory', '')
        )
        if not is_valid:
            errors.append(('subcategory', msg))

    # Validate vendor
    is_valid, msg = validate_vendor(data.get('vendor'))
    if not is_valid:
        errors.append(('vendor', msg))

    # Validate payment method
    is_valid, msg = validate_payment_method(data.get('payment_method'))
    if not is_valid:
        errors.append(('payment_method', msg))

    # Validate description
    is_valid, msg = validate_description(data.get('description', ''))
    if not is_valid:
        errors.append(('description', msg))

    # Validate tags
    tags = data.get('tags', [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    is_valid, msg = validate_tags(tags)
    if not is_valid:
        errors.append(('tags', msg))

    # Validate recurring fields if expense is recurring
    if data.get('is_recurring'):
        is_valid, msg = validate_recurring_type(data.get('recurring_type'))
        if not is_valid:
            errors.append(('recurring_type', msg))

        is_valid, msg = validate_recurring_action(data.get('recurring_action'))
        if not is_valid:
            errors.append(('recurring_action', msg))

    return errors
```

### Task 9.2.11: Create validator tests
- [ ] Create `tests/test_utils/test_validators.py`:
```python
"""Tests for input validators."""

import pytest
from datetime import datetime, timedelta
from utils.validators import (
    validate_amount,
    validate_date,
    validate_category,
    validate_subcategory,
    validate_payment_method,
    validate_vendor,
    validate_description,
    validate_tags,
    validate_recurring_type,
    validate_recurring_action,
    validate_expense,
    validate_budget_amount,
    validate_threshold
)


class TestValidateAmount:
    """Tests for amount validation."""

    def test_valid_amount(self):
        assert validate_amount(100)[0] is True
        assert validate_amount(1000.50)[0] is True
        assert validate_amount("500")[0] is True

    def test_invalid_none(self):
        is_valid, msg = validate_amount(None)
        assert is_valid is False
        assert "required" in msg.lower()

    def test_invalid_negative(self):
        is_valid, msg = validate_amount(-100)
        assert is_valid is False
        assert "positive" in msg.lower()

    def test_invalid_zero(self):
        is_valid, msg = validate_amount(0)
        assert is_valid is False

    def test_exceeds_maximum(self):
        is_valid, msg = validate_amount(20_000_000)
        assert is_valid is False
        assert "exceed" in msg.lower()

    def test_too_many_decimals(self):
        is_valid, msg = validate_amount(100.123)
        assert is_valid is False
        assert "decimal" in msg.lower()


class TestValidateDate:
    """Tests for date validation."""

    def test_valid_date(self):
        assert validate_date(datetime.now())[0] is True
        assert validate_date("15/01/2024")[0] is True

    def test_future_date_not_allowed(self):
        future = datetime.now() + timedelta(days=10)
        is_valid, msg = validate_date(future)
        assert is_valid is False
        assert "future" in msg.lower()

    def test_future_date_allowed(self):
        future = datetime.now() + timedelta(days=10)
        is_valid, _ = validate_date(future, allow_future=True)
        assert is_valid is True

    def test_too_old_date(self):
        old_date = datetime.now() - timedelta(days=4000)
        is_valid, msg = validate_date(old_date)
        assert is_valid is False
        assert "10 years" in msg.lower()


class TestValidateCategory:
    """Tests for category validation."""

    def test_valid_category(self):
        assert validate_category("Supplies")[0] is True
        assert validate_category("Equipment")[0] is True

    def test_invalid_empty(self):
        is_valid, msg = validate_category("")
        assert is_valid is False
        assert "required" in msg.lower()

    def test_invalid_unknown(self):
        is_valid, msg = validate_category("Unknown Category")
        assert is_valid is False
        assert "unknown" in msg.lower()


# Add more test classes for other validators...
```

---

## Story 9.3: Error Handler Service

**Prerequisites:** Story 9.1 (Custom Exceptions)

### Task 9.3.1: Create error handler module
- [ ] Create `utils/error_handler.py` with imports and constants:
```python
"""
Centralized error handling service.
Provides logging, user-friendly messages, and dialog display.
"""

import logging
import os
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Callable, Dict
import tkinter as tk
from tkinter import messagebox

from config import LOGS_DIR
from utils.exceptions import (
    ExpenseError,
    ValidationError,
    FileError,
    BudgetError,
    ExportError,
    BackupError
)

# Global error handler instance
_error_handler: Optional['ErrorHandler'] = None
```

### Task 9.3.2: Implement ErrorHandler class
- [ ] Create ErrorHandler class:
```python
class ErrorHandler:
    """
    Centralized error handling service.

    Provides:
    - Logging to daily log files
    - User-friendly error message conversion
    - Tkinter dialog display
    - Toast notification support
    """

    def __init__(self, log_dir: str = LOGS_DIR):
        """
        Initialize error handler with logging configuration.

        Args:
            log_dir: Directory for log files
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._notification_callback: Optional[Callable] = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure the logger with daily file rotation."""
        self.logger = logging.getLogger('expense_manager')
        self.logger.setLevel(logging.DEBUG)

        # Clear existing handlers
        self.logger.handlers = []

        # Create daily log file
        log_filename = f"app_{datetime.now().strftime('%Y%m%d')}.log"
        log_path = self.log_dir / log_filename

        # File handler
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Console handler for errors
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)

        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def set_notification_callback(self, callback: Callable) -> None:
        """
        Set callback for toast notifications.

        Args:
            callback: Function to call with (message, toast_type)
        """
        self._notification_callback = callback
```

### Task 9.3.3: Implement logging methods
- [ ] Add logging methods:
```python
    def log_error(self, error: Exception, context: str = "") -> None:
        """
        Log error with full stack trace.

        Args:
            error: The exception to log
            context: Additional context information
        """
        error_msg = str(error)
        stack_trace = traceback.format_exc()

        log_message = f"{context}: {error_msg}" if context else error_msg

        if isinstance(error, ExpenseError) and error.technical_details:
            log_message += f"\nTechnical: {error.technical_details}"

        self.logger.error(f"{log_message}\n{stack_trace}")

    def log_warning(self, message: str, context: str = "") -> None:
        """
        Log warning message.

        Args:
            message: Warning message
            context: Additional context
        """
        log_message = f"{context}: {message}" if context else message
        self.logger.warning(log_message)

    def log_info(self, message: str) -> None:
        """
        Log info message.

        Args:
            message: Info message
        """
        self.logger.info(message)

    def log_debug(self, message: str) -> None:
        """
        Log debug message.

        Args:
            message: Debug message
        """
        self.logger.debug(message)
```

### Task 9.3.4: Implement user message conversion
- [ ] Add user-friendly message generation:
```python
    # Error message mappings for user-friendly display
    _ERROR_MESSAGES: Dict[type, str] = {
        ValidationError: "Please check your input and try again.",
        FileError: "There was a problem accessing the file.",
        BudgetError: "There was an issue with the budget.",
        ExportError: "Failed to export the data.",
        BackupError: "Backup operation failed.",
    }

    def get_user_message(self, error: Exception) -> str:
        """
        Convert technical error to user-friendly message.

        Args:
            error: The exception to convert

        Returns:
            User-friendly error message
        """
        # Use the error's message if it's our custom exception
        if isinstance(error, ExpenseError):
            return error.message

        # Map common Python exceptions
        if isinstance(error, FileNotFoundError):
            return "The file could not be found."
        if isinstance(error, PermissionError):
            return "You don't have permission to access this file."
        if isinstance(error, ValueError):
            return "Invalid value provided."
        if isinstance(error, ConnectionError):
            return "Connection error. Please check your network."

        # Default message for unknown errors
        return "An unexpected error occurred. Please try again."
```

### Task 9.3.5: Implement dialog methods
- [ ] Add Tkinter dialog methods:
```python
    def show_error_dialog(
        self,
        parent: tk.Widget,
        error: Exception,
        title: str = "Error"
    ) -> None:
        """
        Show Tkinter error dialog.

        Args:
            parent: Parent widget for dialog
            error: The exception to display
            title: Dialog title
        """
        message = self.get_user_message(error)
        messagebox.showerror(title, message, parent=parent)

    def show_warning_dialog(
        self,
        parent: tk.Widget,
        message: str,
        title: str = "Warning"
    ) -> None:
        """
        Show Tkinter warning dialog.

        Args:
            parent: Parent widget for dialog
            message: Warning message to display
            title: Dialog title
        """
        messagebox.showwarning(title, message, parent=parent)

    def show_info_dialog(
        self,
        parent: tk.Widget,
        message: str,
        title: str = "Information"
    ) -> None:
        """
        Show Tkinter info dialog.

        Args:
            parent: Parent widget for dialog
            message: Info message to display
            title: Dialog title
        """
        messagebox.showinfo(title, message, parent=parent)

    def confirm_action(
        self,
        parent: tk.Widget,
        message: str,
        title: str = "Confirm"
    ) -> bool:
        """
        Show confirmation dialog.

        Args:
            parent: Parent widget for dialog
            message: Confirmation message
            title: Dialog title

        Returns:
            True if user confirmed, False otherwise
        """
        return messagebox.askyesno(title, message, parent=parent)

    def confirm_destructive_action(
        self,
        parent: tk.Widget,
        message: str,
        title: str = "Confirm Delete"
    ) -> bool:
        """
        Show warning confirmation for destructive actions.

        Args:
            parent: Parent widget for dialog
            message: Warning message
            title: Dialog title

        Returns:
            True if user confirmed, False otherwise
        """
        return messagebox.askyesno(
            title,
            message,
            icon=messagebox.WARNING,
            parent=parent
        )
```

### Task 9.3.6: Implement toast and exception handling
- [ ] Add toast notification and exception handling:
```python
    def show_toast(self, message: str, toast_type: str = "info") -> None:
        """
        Show toast notification if callback is set.

        Args:
            message: Notification message
            toast_type: Type of toast (info, success, warning, error)
        """
        if self._notification_callback:
            self._notification_callback(message, toast_type)

    def handle_exception(
        self,
        error: Exception,
        context: str = "",
        parent: tk.Widget = None,
        show_dialog: bool = True
    ) -> None:
        """
        Handle exception with logging and optional dialog.

        Args:
            error: The exception to handle
            context: Context description for logging
            parent: Parent widget for dialog
            show_dialog: Whether to show error dialog
        """
        # Log the error
        self.log_error(error, context)

        # Show dialog if requested and parent available
        if show_dialog and parent:
            self.show_error_dialog(parent, error)
        elif show_dialog:
            # Show toast if no parent
            self.show_toast(self.get_user_message(error), "error")
```

### Task 9.3.7: Implement log cleanup
- [ ] Add log cleanup functionality:
```python
    def cleanup_old_logs(self, days: int = 30) -> int:
        """
        Remove log files older than specified days.

        Args:
            days: Number of days to keep logs

        Returns:
            Number of files deleted
        """
        cutoff = datetime.now() - timedelta(days=days)
        deleted_count = 0

        for log_file in self.log_dir.glob("*.log"):
            try:
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff:
                    log_file.unlink()
                    deleted_count += 1
            except OSError as e:
                self.log_warning(f"Failed to delete old log: {log_file}", str(e))

        self.log_info(f"Cleaned up {deleted_count} old log files")
        return deleted_count


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
```

### Task 9.3.8: Create error handler tests
- [ ] Create `tests/test_utils/test_error_handler.py`:
```python
"""Tests for ErrorHandler service."""

import pytest
import os
import tempfile
from datetime import datetime
from unittest.mock import MagicMock, patch
from utils.error_handler import ErrorHandler, get_error_handler
from utils.exceptions import ValidationError, ExpenseError


class TestErrorHandler:
    """Tests for ErrorHandler class."""

    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    @pytest.fixture
    def handler(self, temp_log_dir):
        """Create ErrorHandler with temp directory."""
        return ErrorHandler(log_dir=temp_log_dir)

    def test_creates_log_directory(self, temp_log_dir):
        """Test that log directory is created."""
        log_dir = os.path.join(temp_log_dir, "logs")
        handler = ErrorHandler(log_dir=log_dir)
        assert os.path.exists(log_dir)

    def test_log_error_creates_file(self, handler, temp_log_dir):
        """Test that logging creates a log file."""
        handler.log_error(Exception("Test error"))
        log_files = list(os.listdir(temp_log_dir))
        assert len(log_files) > 0

    def test_get_user_message_custom_exception(self, handler):
        """Test user message for custom exceptions."""
        error = ValidationError("Invalid amount", field="amount")
        message = handler.get_user_message(error)
        assert message == "Invalid amount"

    def test_notification_callback(self, handler):
        """Test that notification callback is called."""
        mock_callback = MagicMock()
        handler.set_notification_callback(mock_callback)
        handler.show_toast("Test message", "info")
        mock_callback.assert_called_once_with("Test message", "info")

    def test_cleanup_old_logs(self, handler, temp_log_dir):
        """Test log cleanup functionality."""
        # Create old log file
        old_log = os.path.join(temp_log_dir, "old_20200101.log")
        with open(old_log, 'w') as f:
            f.write("Old log")

        # Set old modification time
        old_time = datetime(2020, 1, 1).timestamp()
        os.utime(old_log, (old_time, old_time))

        deleted = handler.cleanup_old_logs(days=30)
        assert deleted == 1


class TestGetErrorHandler:
    """Tests for singleton pattern."""

    def test_returns_same_instance(self):
        """Test that get_error_handler returns singleton."""
        handler1 = get_error_handler()
        handler2 = get_error_handler()
        assert handler1 is handler2
```

---

## Story 9.4: File Error Recovery

**Prerequisites:** Stories 9.1, 9.3

### Task 9.4.1: Implement in DataManager (Epic 7)
- [ ] Add file recovery methods to `persistence/data_manager.py`:
  - `recover_corrupted_csv()` - Attempt to recover valid rows
  - `check_disk_space()` - Check available disk space
  - `safe_write()` - Atomic write with temp file

### Task 9.4.2: Handle missing files
- [ ] Create missing data files with headers when not found
- [ ] Log warning for each missing file created

### Task 9.4.3: Handle corrupted files
- [ ] Detect malformed CSV rows
- [ ] Backup corrupted file with timestamp
- [ ] Recover valid rows and report statistics

### Task 9.4.4: Handle permission errors
- [ ] Detect read-only files
- [ ] Offer alternative save location

---

## Story 9.5: Data Integrity Validation on Load

**Prerequisites:** Stories 9.1, 9.2, 9.3

### Task 9.5.1: Create DataCorrection dataclass
- [ ] Add to `utils/validators.py`:
```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class DataCorrection:
    """Record of an auto-correction made during data validation."""
    timestamp: datetime = field(default_factory=datetime.now)
    record_type: str = ""  # 'expense' or 'budget'
    record_id: str = ""
    field_name: str = ""
    original_value: Any = None
    corrected_value: Any = None
    rule: str = ""  # Description of correction rule

    def to_csv_row(self) -> list:
        """Convert to CSV row format."""
        return [
            self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            self.record_type,
            self.record_id,
            self.field_name,
            str(self.original_value),
            str(self.corrected_value),
            self.rule
        ]
```

### Task 9.5.2: Create validation on load logic
- [ ] Implement in DataManager.load_expenses():
  - Validate each expense after loading
  - Apply auto-corrections for fixable issues
  - Track corrections using DataCorrection dataclass
  - Return validation summary

### Task 9.5.3: Implement auto-correction rules
- [ ] Invalid date → use created_at date
- [ ] Unknown category → set to "Administrative"
- [ ] Negative amount → convert to positive
- [ ] Missing payment method → set to "Cash"
- [ ] Future date → set to today

### Task 9.5.4: Log corrections to CSV
- [ ] Log corrections to `logs/data_corrections_YYYYMMDD.csv`:
  - Columns: timestamp, record_type, record_id, field, original_value, corrected_value, rule

---

## Completion Checklist

### Story 9.1: Custom Exception Classes
- [ ] ExpenseError base class created
- [ ] ValidationError and MultipleValidationError created
- [ ] FileError hierarchy created
- [ ] BudgetError hierarchy created
- [ ] ExportError, DataImportError, BackupError created
- [ ] ConfigurationError created
- [ ] All exception tests passing

### Story 9.2: Input Validators
- [ ] Amount validator working
- [ ] Date validator working (with formats)
- [ ] Category/subcategory validators working
- [ ] Payment method validator working
- [ ] Vendor/description validators working
- [ ] Tag validator working
- [ ] Recurring validators working
- [ ] Budget validators working
- [ ] Full expense validator working
- [ ] All validator tests passing

### Story 9.3: Error Handler Service
- [ ] ErrorHandler class created
- [ ] Logging to daily files working
- [ ] User message conversion working
- [ ] Tkinter dialogs working
- [ ] Toast notification callback working
- [ ] Exception handling method working
- [ ] Log cleanup working
- [ ] Singleton pattern working
- [ ] All error handler tests passing

### Story 9.4: File Error Recovery
- [ ] Missing file handling working
- [ ] Corrupted file recovery working
- [ ] Permission error handling working
- [ ] Disk space checking working

### Story 9.5: Data Integrity Validation
- [ ] DataCorrection dataclass created
- [ ] Validation on load implemented
- [ ] Auto-correction rules implemented
- [ ] Correction logging working
- [ ] Validation summary returned

---

## Next Steps

After completing Epic 9, proceed to:
- **Epic 7: Data Persistence** - Uses error handling framework
