"""
Input validators for Beauty Salon Expense Manager.
"""

import re
from datetime import datetime, timedelta
from typing import Tuple, List, Any, Optional

# Import configuration
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (
    CATEGORIES, PAYMENT_METHODS, RECURRING_TYPES, RECURRING_ACTIONS,
    MAX_AMOUNT, MIN_AMOUNT, MAX_DESCRIPTION_LENGTH, MAX_VENDOR_LENGTH,
    MAX_TAG_LENGTH, MAX_TAGS_COUNT
)


# Validation result type: (is_valid, error_message)
ValidationResult = Tuple[bool, str]


def validate_amount(amount: Any) -> ValidationResult:
    """
    Validate expense/budget amount.

    Rules:
    - Must be a positive number
    - Maximum 10,000,000
    - Minimum 0.01
    - Maximum 2 decimal places

    Args:
        amount: Amount to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check if it can be converted to float
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False, "Amount must be a number"

    # Check minimum
    if amount < MIN_AMOUNT:
        return False, f"Amount must be at least {MIN_AMOUNT}"

    # Check maximum
    if amount > MAX_AMOUNT:
        return False, f"Amount cannot exceed {MAX_AMOUNT:,}"

    # Check decimal places
    decimal_part = str(amount).split('.')
    if len(decimal_part) > 1 and len(decimal_part[1]) > 2:
        return False, "Amount can have at most 2 decimal places"

    return True, ""


def validate_date(date_input: Any, allow_future: bool = False) -> ValidationResult:
    """
    Validate date input.

    Rules:
    - Must be a valid date
    - Not in the future (unless allowed)
    - Not older than 10 years

    Args:
        date_input: Date to validate (datetime or string)
        allow_future: Whether to allow future dates

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Parse if string
    if isinstance(date_input, str):
        formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y']
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
    elif not isinstance(date_input, datetime):
        return False, "Invalid date type"

    now = datetime.now()

    # Check future date
    if not allow_future and date_input > now:
        return False, "Date cannot be in the future"

    # Check too old
    min_date = now - timedelta(days=365 * 10)
    if date_input < min_date:
        return False, "Date cannot be more than 10 years old"

    return True, ""


def validate_category(category: str) -> ValidationResult:
    """
    Validate category exists in predefined list.

    Args:
        category: Category name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not category:
        return False, "Category is required"

    if category not in CATEGORIES:
        valid_categories = ", ".join(CATEGORIES.keys())
        return False, f"Invalid category. Valid options: {valid_categories}"

    return True, ""


def validate_subcategory(category: str, subcategory: str) -> ValidationResult:
    """
    Validate subcategory exists under category.

    Args:
        category: Parent category name
        subcategory: Subcategory name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Subcategory is optional
    if not subcategory:
        return True, ""

    if category not in CATEGORIES:
        return False, "Invalid parent category"

    valid_subcategories = CATEGORIES[category]["subcategories"]
    if subcategory not in valid_subcategories:
        return False, f"Invalid subcategory for {category}. Valid options: {', '.join(valid_subcategories)}"

    return True, ""


def validate_payment_method(method: str) -> ValidationResult:
    """
    Validate payment method is in allowed list.

    Args:
        method: Payment method to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not method:
        return False, "Payment method is required"

    if method not in PAYMENT_METHODS:
        return False, f"Invalid payment method. Valid options: {', '.join(PAYMENT_METHODS)}"

    return True, ""


def validate_vendor(vendor: str) -> ValidationResult:
    """
    Validate vendor name.

    Rules:
    - Required field
    - Maximum 100 characters
    - No special control characters

    Args:
        vendor: Vendor name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not vendor or not vendor.strip():
        return False, "Vendor name is required"

    vendor = vendor.strip()

    if len(vendor) > MAX_VENDOR_LENGTH:
        return False, f"Vendor name cannot exceed {MAX_VENDOR_LENGTH} characters"

    # Check for control characters
    if re.search(r'[\x00-\x1f\x7f]', vendor):
        return False, "Vendor name contains invalid characters"

    return True, ""


def validate_description(description: str) -> ValidationResult:
    """
    Validate description.

    Rules:
    - Optional field
    - Maximum 500 characters

    Args:
        description: Description to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description:
        return True, ""

    if len(description) > MAX_DESCRIPTION_LENGTH:
        return False, f"Description cannot exceed {MAX_DESCRIPTION_LENGTH} characters"

    # Check for control characters (except newline, tab)
    if re.search(r'[\x00-\x08\x0b-\x1f\x7f]', description):
        return False, "Description contains invalid characters"

    return True, ""


def validate_tags(tags: Any) -> ValidationResult:
    """
    Validate tags list.

    Rules:
    - Maximum 10 tags
    - Each tag maximum 30 characters
    - Tags should be alphanumeric with spaces/hyphens

    Args:
        tags: List of tags or comma-separated string

    Returns:
        Tuple of (is_valid, error_message)
    """
    # Parse if string
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(',') if t.strip()]
    elif not isinstance(tags, list):
        return False, "Tags must be a list or comma-separated string"

    if len(tags) > MAX_TAGS_COUNT:
        return False, f"Maximum {MAX_TAGS_COUNT} tags allowed"

    for tag in tags:
        if not tag or not tag.strip():
            continue

        tag = tag.strip()

        if len(tag) > MAX_TAG_LENGTH:
            return False, f"Each tag cannot exceed {MAX_TAG_LENGTH} characters"

        # Allow alphanumeric, spaces, hyphens, underscores
        if not re.match(r'^[\w\s\-]+$', tag, re.UNICODE):
            return False, f"Tag '{tag}' contains invalid characters"

    return True, ""


def validate_single_tag(tag: str) -> ValidationResult:
    """
    Validate a single tag.

    Args:
        tag: Tag string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tag or not tag.strip():
        return False, "Tag cannot be empty"

    tag = tag.strip()

    if len(tag) > MAX_TAG_LENGTH:
        return False, f"Tag cannot exceed {MAX_TAG_LENGTH} characters"

    if not re.match(r'^[\w\s\-]+$', tag, re.UNICODE):
        return False, "Tag contains invalid characters"

    return True, ""


def validate_recurring_type(recurring_type: str) -> ValidationResult:
    """
    Validate recurring type.

    Args:
        recurring_type: Recurring type to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not recurring_type:
        return True, ""  # Optional for non-recurring expenses

    if recurring_type not in RECURRING_TYPES:
        return False, f"Invalid recurring type. Valid options: {', '.join(RECURRING_TYPES)}"

    return True, ""


def validate_recurring_action(action: str) -> ValidationResult:
    """
    Validate recurring action.

    Args:
        action: Recurring action to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not action:
        return True, ""  # Optional for non-recurring expenses

    if action not in RECURRING_ACTIONS:
        return False, f"Invalid recurring action. Valid options: {', '.join(RECURRING_ACTIONS)}"

    return True, ""


def validate_expense(expense) -> List[Tuple[str, str]]:
    """
    Validate entire expense object.

    Args:
        expense: Expense object to validate

    Returns:
        List of (field, error_message) tuples for invalid fields
    """
    errors = []

    # Validate amount
    valid, msg = validate_amount(expense.amount)
    if not valid:
        errors.append(('amount', msg))

    # Validate date
    valid, msg = validate_date(expense.date)
    if not valid:
        errors.append(('date', msg))

    # Validate category
    valid, msg = validate_category(expense.category)
    if not valid:
        errors.append(('category', msg))

    # Validate subcategory
    valid, msg = validate_subcategory(expense.category, expense.subcategory)
    if not valid:
        errors.append(('subcategory', msg))

    # Validate vendor
    valid, msg = validate_vendor(expense.vendor)
    if not valid:
        errors.append(('vendor', msg))

    # Validate payment method
    valid, msg = validate_payment_method(expense.payment_method)
    if not valid:
        errors.append(('payment_method', msg))

    # Validate description
    valid, msg = validate_description(expense.description)
    if not valid:
        errors.append(('description', msg))

    # Validate tags
    valid, msg = validate_tags(expense.tags)
    if not valid:
        errors.append(('tags', msg))

    # Validate recurring fields if recurring
    if expense.is_recurring:
        valid, msg = validate_recurring_type(expense.recurring_type)
        if not valid:
            errors.append(('recurring_type', msg))

        valid, msg = validate_recurring_action(expense.recurring_action)
        if not valid:
            errors.append(('recurring_action', msg))

    return errors


def validate_budget_amount(amount: Any) -> ValidationResult:
    """
    Validate budget amount.

    Rules:
    - Must be non-negative
    - Maximum 10,000,000

    Args:
        amount: Budget amount to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        amount = float(amount)
    except (TypeError, ValueError):
        return False, "Budget amount must be a number"

    if amount < 0:
        return False, "Budget amount cannot be negative"

    if amount > MAX_AMOUNT:
        return False, f"Budget amount cannot exceed {MAX_AMOUNT:,}"

    return True, ""


def validate_threshold(threshold: Any) -> ValidationResult:
    """
    Validate warning/critical threshold.

    Rules:
    - Must be 0-100 percentage

    Args:
        threshold: Threshold percentage to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        threshold = float(threshold)
    except (TypeError, ValueError):
        return False, "Threshold must be a number"

    if threshold < 0 or threshold > 100:
        return False, "Threshold must be between 0 and 100"

    return True, ""


def validate_budget(budget) -> List[Tuple[str, str]]:
    """
    Validate entire budget object.

    Args:
        budget: Budget object to validate

    Returns:
        List of (field, error_message) tuples for invalid fields
    """
    errors = []

    # Validate amount
    valid, msg = validate_budget_amount(budget.amount)
    if not valid:
        errors.append(('amount', msg))

    # Validate category
    valid, msg = validate_category(budget.category)
    if not valid:
        errors.append(('category', msg))

    # Validate thresholds
    valid, msg = validate_threshold(budget.warning_threshold)
    if not valid:
        errors.append(('warning_threshold', msg))

    valid, msg = validate_threshold(budget.critical_threshold)
    if not valid:
        errors.append(('critical_threshold', msg))

    # Validate threshold order
    if budget.warning_threshold >= budget.critical_threshold:
        errors.append(('warning_threshold', 'Warning threshold must be less than critical threshold'))

    # Validate rollover cap
    valid, msg = validate_threshold(budget.rollover_cap_percent)
    if not valid:
        errors.append(('rollover_cap_percent', msg))

    return errors


def validate_template(template) -> List[Tuple[str, str]]:
    """
    Validate expense template.

    Args:
        template: ExpenseTemplate object to validate

    Returns:
        List of (field, error_message) tuples for invalid fields
    """
    errors = []

    # Validate name
    if not template.name or not template.name.strip():
        errors.append(('name', 'Template name is required'))
    elif len(template.name) > 100:
        errors.append(('name', 'Template name cannot exceed 100 characters'))

    # Validate category
    valid, msg = validate_category(template.category)
    if not valid:
        errors.append(('category', msg))

    # Validate subcategory
    valid, msg = validate_subcategory(template.category, template.subcategory)
    if not valid:
        errors.append(('subcategory', msg))

    # Validate vendor
    valid, msg = validate_vendor(template.vendor)
    if not valid:
        errors.append(('vendor', msg))

    # Validate amount if set
    if template.typical_amount > 0:
        valid, msg = validate_amount(template.typical_amount)
        if not valid:
            errors.append(('typical_amount', msg))

    # Validate payment method
    valid, msg = validate_payment_method(template.payment_method)
    if not valid:
        errors.append(('payment_method', msg))

    # Validate tags
    valid, msg = validate_tags(template.tags)
    if not valid:
        errors.append(('tags', msg))

    return errors


def validate_email(email: str) -> ValidationResult:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return True, ""  # Optional

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Invalid email format"

    return True, ""


def validate_phone(phone: str) -> ValidationResult:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return True, ""  # Optional

    # Remove common formatting characters
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)

    if not cleaned.isdigit():
        return False, "Phone number should contain only digits"

    if len(cleaned) < 9 or len(cleaned) > 15:
        return False, "Phone number should be 9-15 digits"

    return True, ""


def validate_file_path(path: str, must_exist: bool = True) -> ValidationResult:
    """
    Validate file path.

    Args:
        path: File path to validate
        must_exist: Whether file must exist

    Returns:
        Tuple of (is_valid, error_message)
    """
    from pathlib import Path as PathLib

    if not path:
        return False, "File path is required"

    try:
        file_path = PathLib(path)

        if must_exist and not file_path.exists():
            return False, "File does not exist"

        # Check for invalid characters
        invalid_chars = '<>"|?*'
        for char in invalid_chars:
            if char in path:
                return False, f"Path contains invalid character: {char}"

        return True, ""
    except Exception as e:
        return False, f"Invalid file path: {str(e)}"


def validate_positive_integer(value: Any, field_name: str = "Value") -> ValidationResult:
    """
    Validate that a value is a positive integer.

    Args:
        value: Value to validate
        field_name: Name of field for error message

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        int_value = int(value)
    except (TypeError, ValueError):
        return False, f"{field_name} must be an integer"

    if int_value <= 0:
        return False, f"{field_name} must be positive"

    return True, ""


def sanitize_string(text: str, max_length: int = 0) -> str:
    """
    Sanitize string by removing control characters and trimming.

    Args:
        text: Text to sanitize
        max_length: Maximum length (0 = no limit)

    Returns:
        Sanitized string
    """
    if not text:
        return ""

    # Remove control characters except newline and tab
    sanitized = re.sub(r'[\x00-\x08\x0b-\x1f\x7f]', '', text)

    # Trim whitespace
    sanitized = sanitized.strip()

    # Limit length
    if max_length > 0 and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]

    return sanitized
