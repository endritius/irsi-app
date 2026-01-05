"""
Expense dataclass - Core data model for expense records.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


def parse_date(date_value) -> Optional[datetime]:
    """Parse date string or datetime to datetime."""
    if date_value is None:
        return None

    # Already a datetime
    if isinstance(date_value, datetime):
        return date_value

    # Handle pandas Timestamp
    if hasattr(date_value, 'to_pydatetime'):
        return date_value.to_pydatetime()

    # Convert to string if needed
    date_str = str(date_value).strip()
    if not date_str or date_str.lower() in ('nan', 'nat', 'none', ''):
        return None

    # Try various date formats
    formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%Y-%m-%d %H:%M:%S',
        '%d/%m/%Y %H:%M:%S',
        '%Y/%m/%d',
        '%m/%d/%Y'
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    return None


@dataclass
class Expense:
    """
    Represents a single expense record.

    Attributes:
        expense_id: Unique identifier (UUID)
        amount: Expense amount in Albanian Lek
        date: Date of expense
        category: Main category
        subcategory: Subcategory within main category
        vendor: Vendor/supplier name
        payment_method: Payment method used
        description: Optional description
        tags: List of tags for categorization
        is_recurring: Whether this is a recurring expense template
        recurring_type: Frequency (daily, weekly, biweekly, monthly, quarterly, annually)
        recurring_action: auto_generate or reminder
        next_due_date: Next date for recurring expense
        last_recurring_date: Last time recurring expense was processed
        recurring_parent_id: ID of parent recurring expense (for generated expenses)
        is_deleted: Soft delete flag
        deleted_at: Timestamp of deletion
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    # Required fields
    amount: float
    date: datetime
    category: str
    vendor: str
    payment_method: str

    # Optional fields with defaults
    expense_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subcategory: str = ""
    description: str = ""
    tags: List[str] = field(default_factory=list)

    # Recurring expense fields
    is_recurring: bool = False
    recurring_type: Optional[str] = None  # daily, weekly, biweekly, monthly, quarterly, annually
    recurring_action: Optional[str] = None  # auto_generate, reminder
    next_due_date: Optional[datetime] = None
    last_recurring_date: Optional[datetime] = None
    recurring_parent_id: Optional[str] = None  # ID of parent recurring expense

    # Soft delete fields
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and convert fields after initialization."""
        # Ensure amount is float
        self.amount = float(self.amount)

        # Ensure date is datetime
        if isinstance(self.date, str):
            self.date = parse_date(self.date) or datetime.now()

        # Ensure tags is a list
        if isinstance(self.tags, str):
            self.tags = [t.strip() for t in self.tags.split(',') if t.strip()]
        elif self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV storage."""
        return {
            'expense_id': self.expense_id,
            'amount': self.amount,
            'date': self.date.strftime('%Y-%m-%d'),
            'category': self.category,
            'subcategory': self.subcategory or '',
            'vendor': self.vendor,
            'payment_method': self.payment_method,
            'description': self.description or '',
            'tags': ','.join(self.tags) if self.tags else '',
            'is_recurring': self.is_recurring,
            'recurring_type': self.recurring_type or '',
            'recurring_action': self.recurring_action or '',
            'next_due_date': self.next_due_date.strftime('%Y-%m-%d') if self.next_due_date else '',
            'last_recurring_date': self.last_recurring_date.strftime('%Y-%m-%d') if self.last_recurring_date else '',
            'recurring_parent_id': self.recurring_parent_id or '',
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Expense':
        """Create Expense from dictionary."""
        # Parse boolean fields
        is_recurring = data.get('is_recurring')
        if isinstance(is_recurring, str):
            is_recurring = is_recurring.lower() in ('true', '1', 'yes')

        is_deleted = data.get('is_deleted')
        if isinstance(is_deleted, str):
            is_deleted = is_deleted.lower() in ('true', '1', 'yes')

        # Parse tags
        tags = data.get('tags', '')
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        # Parse deleted_at
        deleted_at = None
        if data.get('deleted_at'):
            try:
                deleted_at = datetime.strptime(data['deleted_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        # Parse timestamps
        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        updated_at = datetime.now()
        if data.get('updated_at'):
            try:
                updated_at = datetime.strptime(data['updated_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        return cls(
            expense_id=data.get('expense_id') or str(uuid.uuid4()),
            amount=float(data.get('amount', 0)),
            date=parse_date(data.get('date')) or datetime.now(),
            category=data.get('category', ''),
            subcategory=data.get('subcategory', ''),
            vendor=data.get('vendor', ''),
            payment_method=data.get('payment_method', ''),
            description=data.get('description', ''),
            tags=tags,
            is_recurring=is_recurring or False,
            recurring_type=data.get('recurring_type') or None,
            recurring_action=data.get('recurring_action') or None,
            next_due_date=parse_date(data.get('next_due_date')),
            last_recurring_date=parse_date(data.get('last_recurring_date')),
            recurring_parent_id=data.get('recurring_parent_id') or None,
            is_deleted=is_deleted or False,
            deleted_at=deleted_at,
            created_at=created_at,
            updated_at=updated_at
        )

    def soft_delete(self) -> None:
        """Mark expense as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.now()
        self.updated_at = datetime.now()

    def restore(self) -> None:
        """Restore a soft-deleted expense."""
        self.is_deleted = False
        self.deleted_at = None
        self.updated_at = datetime.now()

    def update(self, **kwargs) -> None:
        """Update expense fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()

    def validate(self) -> List[str]:
        """
        Validate expense data.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if self.amount <= 0:
            errors.append("Amount must be positive")

        if self.amount > 10_000_000:
            errors.append("Amount cannot exceed 10,000,000")

        if not self.category:
            errors.append("Category is required")

        if not self.vendor:
            errors.append("Vendor is required")

        if not self.payment_method:
            errors.append("Payment method is required")

        if self.date > datetime.now():
            errors.append("Date cannot be in the future")

        if self.is_recurring:
            if not self.recurring_type:
                errors.append("Recurring type is required for recurring expenses")
            if not self.recurring_action:
                errors.append("Recurring action is required for recurring expenses")

        return errors

    def copy(self) -> 'Expense':
        """Create a copy of this expense with new ID."""
        return Expense(
            amount=self.amount,
            date=self.date,
            category=self.category,
            subcategory=self.subcategory,
            vendor=self.vendor,
            payment_method=self.payment_method,
            description=self.description,
            tags=self.tags.copy(),
            is_recurring=self.is_recurring,
            recurring_type=self.recurring_type,
            recurring_action=self.recurring_action,
            next_due_date=self.next_due_date,
            last_recurring_date=self.last_recurring_date
        )
