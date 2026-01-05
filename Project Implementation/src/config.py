"""
Configuration constants for Beauty Salon Expense Manager.
"""

from pathlib import Path
from typing import List, Dict

# Application info
APP_NAME = "Beauty Salon Expense Manager"
APP_VERSION = "1.0.0"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"
BACKUPS_DIR = BASE_DIR / "backups"

# Data files
EXPENSES_FILE = DATA_DIR / "expenses.csv"
BUDGETS_FILE = DATA_DIR / "budgets.csv"
TEMPLATES_FILE = DATA_DIR / "templates.csv"
SETTINGS_FILE = DATA_DIR / "settings.json"

# Currency
CURRENCY_CODE = "ALL"
DEFAULT_CURRENCY = "ALL"  # Alias for compatibility
CURRENCY_SYMBOL = "L"

# Date format
DATE_FORMAT = "%d/%m/%Y"
DATE_FORMAT_DISPLAY = "DD/MM/YYYY"  # Display format string
DATE_DISPLAY_FORMAT = DATE_FORMAT  # Alias for compatibility
DATE_FORMAT_STORAGE = "%Y-%m-%d"

# Amount limits
MAX_AMOUNT = 10_000_000
MIN_AMOUNT = 0.01

# Payment methods
PAYMENT_METHODS = ["Cash", "Debit Card", "Credit Card", "Bank Transfer"]

# Recurring types
RECURRING_TYPES = ["daily", "weekly", "biweekly", "monthly", "quarterly", "annually"]
RECURRING_ACTIONS = ["auto_generate", "reminder"]

# Budget settings
DEFAULT_WARNING_THRESHOLD = 80.0
DEFAULT_CRITICAL_THRESHOLD = 95.0
WARNING_THRESHOLD = DEFAULT_WARNING_THRESHOLD  # Alias for compatibility
CRITICAL_THRESHOLD = DEFAULT_CRITICAL_THRESHOLD  # Alias for compatibility

# UI settings
DEFAULT_ROWS_PER_PAGE = 50
MAX_DESCRIPTION_LENGTH = 500
MAX_VENDOR_LENGTH = 100
MAX_TAG_LENGTH = 30
MAX_TAGS_COUNT = 10

# Window dimensions
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800

# Categories with subcategories and colors
CATEGORIES: Dict[str, Dict] = {
    "Supplies": {
        "subcategories": [
            "Hair products",
            "Nail products",
            "Skincare",
            "Disposables",
            "Cleaning"
        ],
        "color": "#FF6B6B"
    },
    "Equipment": {
        "subcategories": [
            "Styling tools",
            "Furniture",
            "Technology",
            "Maintenance"
        ],
        "color": "#4ECDC4"
    },
    "Facilities": {
        "subcategories": [
            "Rent",
            "Electricity",
            "Water",
            "Gas",
            "Internet",
            "Insurance"
        ],
        "color": "#45B7D1"
    },
    "Staff": {
        "subcategories": [
            "Salaries",
            "Commissions",
            "Training",
            "Uniforms"
        ],
        "color": "#96CEB4"
    },
    "Marketing": {
        "subcategories": [
            "Advertising",
            "Social media",
            "Promotions",
            "Loyalty programs"
        ],
        "color": "#FFEAA7"
    },
    "Administrative": {
        "subcategories": [
            "Software",
            "Accounting",
            "Licenses",
            "Bank fees"
        ],
        "color": "#DDA0DD"
    }
}


def get_categories() -> List[str]:
    """Get list of category names."""
    return list(CATEGORIES.keys())


def get_subcategories(category: str) -> List[str]:
    """Get subcategories for a category."""
    if category in CATEGORIES:
        return CATEGORIES[category]["subcategories"]
    return []


def get_category_color(category: str) -> str:
    """Get color for a category."""
    if category in CATEGORIES:
        return CATEGORIES[category]["color"]
    return "#808080"


def is_valid_category(category: str) -> bool:
    """Check if category is valid."""
    return category in CATEGORIES


def is_valid_subcategory(category: str, subcategory: str) -> bool:
    """Check if subcategory is valid for category."""
    if category in CATEGORIES:
        return subcategory in CATEGORIES[category]["subcategories"]
    return False


def is_valid_payment_method(method: str) -> bool:
    """Check if payment method is valid."""
    return method in PAYMENT_METHODS


def get_payment_methods() -> List[str]:
    """Get list of payment methods."""
    return PAYMENT_METHODS.copy()
