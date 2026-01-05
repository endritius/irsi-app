"""
Formatters - Utility functions for consistent formatting across the application.
"""

from datetime import datetime
from typing import Optional, List
import calendar

# Import config constants
CURRENCY_SYMBOL = "L"
DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M"


def format_currency(amount: float, include_symbol: bool = True) -> str:
    """
    Format amount as currency with thousand separators.

    Args:
        amount: Amount to format
        include_symbol: Whether to include currency symbol

    Returns:
        Formatted string (e.g., 'L 1,234.56')
    """
    formatted = f"{amount:,.2f}"
    if include_symbol:
        return f"{CURRENCY_SYMBOL} {formatted}"
    return formatted


def format_date(dt: datetime) -> str:
    """
    Format datetime as DD/MM/YYYY.

    Args:
        dt: Datetime to format

    Returns:
        Formatted date string (e.g., '15/01/2024')
    """
    if dt is None:
        return ""
    return dt.strftime(DATE_FORMAT)


def format_datetime(dt: datetime) -> str:
    """
    Format datetime with time.

    Args:
        dt: Datetime to format

    Returns:
        Formatted datetime string (e.g., '15/01/2024 14:30')
    """
    if dt is None:
        return ""
    return dt.strftime(DATETIME_FORMAT)


def format_date_iso(dt: datetime) -> str:
    """
    Format datetime as ISO date (YYYY-MM-DD).

    Args:
        dt: Datetime to format

    Returns:
        ISO date string (e.g., '2024-01-15')
    """
    if dt is None:
        return ""
    return dt.strftime("%Y-%m-%d")


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse DD/MM/YYYY format to datetime.

    Args:
        date_str: Date string to parse

    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, DATE_FORMAT)
    except ValueError:
        return None


def parse_date_iso(date_str: str) -> Optional[datetime]:
    """
    Parse ISO date format (YYYY-MM-DD) to datetime.

    Args:
        date_str: Date string to parse

    Returns:
        Datetime object or None if parsing fails
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        return None


def parse_date_flexible(date_str: str) -> Optional[datetime]:
    """
    Parse date with multiple format support.

    Supported formats:
    - DD/MM/YYYY
    - YYYY-MM-DD
    - DD-MM-YYYY
    - DD.MM.YYYY

    Args:
        date_str: Date string to parse

    Returns:
        Datetime object or None if all formats fail
    """
    if not date_str:
        return None

    formats = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


def truncate_text(text: str, max_length: int = 30, suffix: str = "...") -> str:
    """
    Truncate text with ellipsis if too long.

    Args:
        text: Text to truncate
        max_length: Maximum length before truncation
        suffix: Suffix to add when truncated

    Returns:
        Truncated text or original if within limit
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage.

    Args:
        value: Value to format (0-100 scale)
        decimals: Number of decimal places

    Returns:
        Formatted percentage (e.g., '85.5%')
    """
    return f"{value:.{decimals}f}%"


def format_number(value: float, decimals: int = 2) -> str:
    """
    Format number with thousand separators.

    Args:
        value: Number to format
        decimals: Number of decimal places

    Returns:
        Formatted number (e.g., '1,234.56')
    """
    return f"{value:,.{decimals}f}"


def format_integer(value: int) -> str:
    """
    Format integer with thousand separators.

    Args:
        value: Integer to format

    Returns:
        Formatted integer (e.g., '1,234')
    """
    return f"{value:,}"


def format_period(month: int, year: int) -> str:
    """
    Format month/year as period string.

    Args:
        month: Month number (1-12)
        year: Year number

    Returns:
        Formatted period (e.g., 'January 2024')
    """
    if month < 1 or month > 12:
        return f"Invalid Month {year}"
    month_name = calendar.month_name[month]
    return f"{month_name} {year}"


def format_period_short(month: int, year: int) -> str:
    """
    Format month/year as short period string.

    Args:
        month: Month number (1-12)
        year: Year number

    Returns:
        Formatted period (e.g., 'Jan 2024')
    """
    if month < 1 or month > 12:
        return f"??? {year}"
    month_abbr = calendar.month_abbr[month]
    return f"{month_abbr} {year}"


def format_tags(tags: List[str]) -> str:
    """
    Convert tag list to comma-separated string.

    Args:
        tags: List of tags

    Returns:
        Comma-separated string
    """
    if not tags:
        return ""
    return ", ".join(tags)


def parse_tags(tags_str: str) -> List[str]:
    """
    Convert comma-separated string to tag list.

    Args:
        tags_str: Comma-separated tags string

    Returns:
        List of tags (stripped, non-empty)
    """
    if not tags_str:
        return []
    return [tag.strip() for tag in tags_str.split(',') if tag.strip()]


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size (e.g., '1.5 MB')
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration (e.g., '2h 30m')
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s" if secs else f"{minutes}m"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m" if minutes else f"{hours}h"


def format_day_of_week(day: int) -> str:
    """
    Get day name from day number.

    Args:
        day: Day number (0=Monday, 6=Sunday)

    Returns:
        Day name
    """
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if 0 <= day <= 6:
        return days[day]
    return "Unknown"


def format_change(current: float, previous: float) -> str:
    """
    Format change between two values.

    Args:
        current: Current value
        previous: Previous value

    Returns:
        Formatted change with sign and percentage
    """
    if previous == 0:
        if current == 0:
            return "No change"
        return "+100.0%" if current > 0 else "-100.0%"

    change = ((current - previous) / previous) * 100
    sign = "+" if change > 0 else ""
    return f"{sign}{change:.1f}%"


def sanitize_filename(filename: str) -> str:
    """
    Remove invalid characters from filename.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename safe for filesystem
    """
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename.strip()
