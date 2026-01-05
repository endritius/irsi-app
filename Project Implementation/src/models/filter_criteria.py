"""
FilterCriteria dataclass - Defines filtering options for expense queries.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any


@dataclass
class FilterCriteria:
    """
    Criteria for filtering expenses.

    Attributes:
        date_from: Start date for range filter
        date_to: End date for range filter
        categories: List of categories to include (empty = all)
        subcategories: List of subcategories to include (empty = all)
        vendors: List of vendors to include (empty = all)
        payment_methods: List of payment methods to include (empty = all)
        amount_min: Minimum amount filter
        amount_max: Maximum amount filter
        tags: Tags to filter by (any match)
        search_text: Text search in vendor/description
        include_deleted: Whether to include soft-deleted records
        include_recurring_only: Filter only recurring expenses
        sort_by: Field to sort by
        sort_descending: Sort in descending order
    """

    # Date range
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    # Category filters
    categories: List[str] = field(default_factory=list)
    subcategories: List[str] = field(default_factory=list)

    # Vendor filter
    vendors: List[str] = field(default_factory=list)

    # Payment method filter
    payment_methods: List[str] = field(default_factory=list)

    # Amount range
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None

    # Tags filter
    tags: List[str] = field(default_factory=list)

    # Text search
    search_text: str = ""

    # Special filters
    include_deleted: bool = False
    include_recurring_only: bool = False

    # Sorting
    sort_by: str = "date"
    sort_descending: bool = True

    def is_empty(self) -> bool:
        """Check if no filters are applied."""
        return (
            self.date_from is None and
            self.date_to is None and
            not self.categories and
            not self.subcategories and
            not self.vendors and
            not self.payment_methods and
            self.amount_min is None and
            self.amount_max is None and
            not self.tags and
            not self.search_text
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'date_from': self.date_from.strftime('%Y-%m-%d') if self.date_from else None,
            'date_to': self.date_to.strftime('%Y-%m-%d') if self.date_to else None,
            'categories': self.categories.copy(),
            'subcategories': self.subcategories.copy(),
            'vendors': self.vendors.copy(),
            'payment_methods': self.payment_methods.copy(),
            'amount_min': self.amount_min,
            'amount_max': self.amount_max,
            'tags': self.tags.copy(),
            'search_text': self.search_text,
            'include_deleted': self.include_deleted,
            'include_recurring_only': self.include_recurring_only,
            'sort_by': self.sort_by,
            'sort_descending': self.sort_descending
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FilterCriteria':
        """Create FilterCriteria from dictionary."""
        date_from = None
        if data.get('date_from'):
            try:
                date_from = datetime.strptime(data['date_from'], '%Y-%m-%d')
            except ValueError:
                pass

        date_to = None
        if data.get('date_to'):
            try:
                date_to = datetime.strptime(data['date_to'], '%Y-%m-%d')
            except ValueError:
                pass

        return cls(
            date_from=date_from,
            date_to=date_to,
            categories=data.get('categories', []),
            subcategories=data.get('subcategories', []),
            vendors=data.get('vendors', []),
            payment_methods=data.get('payment_methods', []),
            amount_min=data.get('amount_min'),
            amount_max=data.get('amount_max'),
            tags=data.get('tags', []),
            search_text=data.get('search_text', ''),
            include_deleted=data.get('include_deleted', False),
            include_recurring_only=data.get('include_recurring_only', False),
            sort_by=data.get('sort_by', 'date'),
            sort_descending=data.get('sort_descending', True)
        )

    def clear(self) -> None:
        """Reset all filters to defaults."""
        self.date_from = None
        self.date_to = None
        self.categories = []
        self.subcategories = []
        self.vendors = []
        self.payment_methods = []
        self.amount_min = None
        self.amount_max = None
        self.tags = []
        self.search_text = ""
        self.include_deleted = False
        self.include_recurring_only = False
        self.sort_by = "date"
        self.sort_descending = True

    def copy(self) -> 'FilterCriteria':
        """Create a copy of this filter criteria."""
        return FilterCriteria(
            date_from=self.date_from,
            date_to=self.date_to,
            categories=self.categories.copy(),
            subcategories=self.subcategories.copy(),
            vendors=self.vendors.copy(),
            payment_methods=self.payment_methods.copy(),
            amount_min=self.amount_min,
            amount_max=self.amount_max,
            tags=self.tags.copy(),
            search_text=self.search_text,
            include_deleted=self.include_deleted,
            include_recurring_only=self.include_recurring_only,
            sort_by=self.sort_by,
            sort_descending=self.sort_descending
        )

    @classmethod
    def this_month(cls) -> 'FilterCriteria':
        """Create filter for current month."""
        today = datetime.now()
        start = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        return cls(date_from=start, date_to=today)

    @classmethod
    def last_month(cls) -> 'FilterCriteria':
        """Create filter for previous month."""
        today = datetime.now()
        first_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_prev_month = first_this_month - timedelta(days=1)
        first_prev_month = last_prev_month.replace(day=1)
        return cls(date_from=first_prev_month, date_to=last_prev_month)

    @classmethod
    def this_year(cls) -> 'FilterCriteria':
        """Create filter for current year."""
        today = datetime.now()
        start = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        return cls(date_from=start, date_to=today)

    @classmethod
    def last_30_days(cls) -> 'FilterCriteria':
        """Create filter for last 30 days."""
        today = datetime.now()
        start = today - timedelta(days=30)
        return cls(date_from=start, date_to=today)

    @classmethod
    def last_7_days(cls) -> 'FilterCriteria':
        """Create filter for last 7 days."""
        today = datetime.now()
        start = today - timedelta(days=7)
        return cls(date_from=start, date_to=today)

    def get_description(self) -> str:
        """Get human-readable description of active filters."""
        parts = []

        if self.date_from and self.date_to:
            parts.append(f"Date: {self.date_from.strftime('%d/%m/%Y')} - {self.date_to.strftime('%d/%m/%Y')}")
        elif self.date_from:
            parts.append(f"From: {self.date_from.strftime('%d/%m/%Y')}")
        elif self.date_to:
            parts.append(f"Until: {self.date_to.strftime('%d/%m/%Y')}")

        if self.categories:
            parts.append(f"Categories: {', '.join(self.categories)}")

        if self.vendors:
            parts.append(f"Vendors: {', '.join(self.vendors)}")

        if self.payment_methods:
            parts.append(f"Payment: {', '.join(self.payment_methods)}")

        if self.amount_min is not None or self.amount_max is not None:
            if self.amount_min and self.amount_max:
                parts.append(f"Amount: {self.amount_min} - {self.amount_max}")
            elif self.amount_min:
                parts.append(f"Min amount: {self.amount_min}")
            else:
                parts.append(f"Max amount: {self.amount_max}")

        if self.search_text:
            parts.append(f"Search: '{self.search_text}'")

        if self.tags:
            parts.append(f"Tags: {', '.join(self.tags)}")

        return " | ".join(parts) if parts else "No filters"
