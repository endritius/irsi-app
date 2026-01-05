"""
Budget dataclass - Core data model for budget records.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any
import uuid


@dataclass
class Budget:
    """
    Represents a budget for a category or subcategory.

    Attributes:
        budget_id: Unique identifier (UUID)
        category: Budget category
        subcategory: Optional subcategory (empty = entire category)
        amount: Budget amount in Albanian Lek
        period_type: monthly, quarterly, or yearly
        period_start: Start date of budget period
        warning_threshold: Percentage for warning alert (default 80%)
        critical_threshold: Percentage for critical alert (default 95%)
        rollover_enabled: Whether unused budget rolls over
        rollover_cap_percent: Maximum rollover as percentage (0-100)
        previous_rollover: Amount rolled over from previous period
        notes: Optional notes
        is_active: Whether budget is active
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    # Required fields
    category: str
    amount: float
    period_type: str  # monthly, quarterly, yearly
    period_start: datetime

    # Optional fields with defaults
    budget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subcategory: str = ""
    warning_threshold: float = 80.0
    critical_threshold: float = 95.0
    rollover_enabled: bool = False
    rollover_cap_percent: float = 50.0
    previous_rollover: float = 0.0
    notes: str = ""
    is_active: bool = True

    # Runtime tracking (not persisted, set by BudgetManager)
    spent: float = 0.0
    rollover_amount: float = 0.0
    allow_rollover: bool = False  # Alias for rollover_enabled

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and convert fields after initialization."""
        self.amount = float(self.amount)
        self.warning_threshold = float(self.warning_threshold)
        self.critical_threshold = float(self.critical_threshold)
        self.rollover_cap_percent = float(self.rollover_cap_percent)
        self.previous_rollover = float(self.previous_rollover)

        # Sync allow_rollover with rollover_enabled
        self.allow_rollover = self.rollover_enabled

        # Handle date parsing for period_start
        if self.period_start is None:
            self.period_start = datetime.now().replace(day=1)
        elif isinstance(self.period_start, str):
            try:
                self.period_start = datetime.strptime(self.period_start, '%Y-%m-%d')
            except ValueError:
                try:
                    self.period_start = datetime.strptime(self.period_start, '%d/%m/%Y')
                except ValueError:
                    self.period_start = datetime.now().replace(day=1)
        elif hasattr(self.period_start, 'to_pydatetime'):
            # Handle pandas Timestamp
            self.period_start = self.period_start.to_pydatetime()

    @property
    def period_end(self) -> datetime:
        """Calculate period end date based on period_type."""
        from dateutil.relativedelta import relativedelta

        if self.period_type == 'monthly':
            end = self.period_start + relativedelta(months=1, days=-1)
        elif self.period_type == 'quarterly':
            end = self.period_start + relativedelta(months=3, days=-1)
        elif self.period_type == 'yearly':
            end = self.period_start + relativedelta(years=1, days=-1)
        else:
            end = self.period_start + relativedelta(months=1, days=-1)

        return end

    @property
    def period_display(self) -> str:
        """Get human-readable period display."""
        if self.period_type == 'monthly':
            return self.period_start.strftime('%B %Y')
        elif self.period_type == 'quarterly':
            quarter = (self.period_start.month - 1) // 3 + 1
            return f"Q{quarter} {self.period_start.year}"
        elif self.period_type == 'yearly':
            return str(self.period_start.year)
        return self.period_start.strftime('%Y-%m-%d')

    @property
    def effective_budget(self) -> float:
        """Get effective budget including rollover."""
        if self.rollover_enabled:
            return self.amount + self.previous_rollover
        return self.amount

    def get_used_percentage(self) -> float:
        """Get percentage of budget used."""
        if self.amount <= 0:
            return 0.0
        return (self.spent / self.amount * 100)

    def get_remaining(self) -> float:
        """Get remaining budget amount."""
        return self.effective_budget - self.spent

    def calculate_rollover(self, spent: float) -> float:
        """
        Calculate rollover amount for next period.

        Args:
            spent: Amount spent in current period

        Returns:
            Rollover amount (capped by rollover_cap_percent)
        """
        if not self.rollover_enabled:
            return 0.0

        remaining = self.effective_budget - spent
        if remaining <= 0:
            return 0.0

        max_rollover = self.amount * (self.rollover_cap_percent / 100)
        return min(remaining, max_rollover)

    def get_status(self, spent: float) -> Dict[str, Any]:
        """
        Get budget status based on spending.

        Args:
            spent: Amount spent

        Returns:
            Dictionary with status information
        """
        effective = self.effective_budget
        remaining = effective - spent
        percentage = (spent / effective * 100) if effective > 0 else 0

        if percentage >= 100:
            status = 'exceeded'
        elif percentage >= self.critical_threshold:
            status = 'critical'
        elif percentage >= self.warning_threshold:
            status = 'warning'
        else:
            status = 'ok'

        return {
            'budget_id': self.budget_id,
            'category': self.category,
            'subcategory': self.subcategory,
            'budget_amount': self.amount,
            'effective_budget': effective,
            'spent': spent,
            'remaining': remaining,
            'percentage': percentage,
            'status': status,
            'period': self.period_display
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV storage."""
        return {
            'budget_id': self.budget_id,
            'category': self.category,
            'subcategory': self.subcategory or '',
            'amount': self.amount,
            'period_type': self.period_type,
            'period_start': self.period_start.strftime('%Y-%m-%d'),
            'warning_threshold': self.warning_threshold,
            'critical_threshold': self.critical_threshold,
            'rollover_enabled': self.rollover_enabled,
            'rollover_cap_percent': self.rollover_cap_percent,
            'previous_rollover': self.previous_rollover,
            'notes': self.notes or '',
            'is_active': self.is_active,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Budget':
        """Create Budget from dictionary."""
        # Parse boolean fields
        rollover_enabled = data.get('rollover_enabled')
        if isinstance(rollover_enabled, str):
            rollover_enabled = rollover_enabled.lower() in ('true', '1', 'yes')

        is_active = data.get('is_active', True)
        if isinstance(is_active, str):
            is_active = is_active.lower() in ('true', '1', 'yes')

        # Parse dates
        period_start = datetime.now().replace(day=1)
        if data.get('period_start'):
            try:
                period_start = datetime.strptime(data['period_start'], '%Y-%m-%d')
            except ValueError:
                pass

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
            budget_id=data.get('budget_id') or str(uuid.uuid4()),
            category=data.get('category', ''),
            subcategory=data.get('subcategory', ''),
            amount=float(data.get('amount', 0)),
            period_type=data.get('period_type', 'monthly'),
            period_start=period_start,
            warning_threshold=float(data.get('warning_threshold', 80.0)),
            critical_threshold=float(data.get('critical_threshold', 95.0)),
            rollover_enabled=rollover_enabled or False,
            rollover_cap_percent=float(data.get('rollover_cap_percent', 50.0)),
            previous_rollover=float(data.get('previous_rollover', 0.0)),
            notes=data.get('notes', ''),
            is_active=is_active,
            created_at=created_at,
            updated_at=updated_at
        )

    def update(self, **kwargs) -> None:
        """Update budget fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.now()
