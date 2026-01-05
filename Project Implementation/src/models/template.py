"""
ExpenseTemplate dataclass - Template for quick expense entry.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid


@dataclass
class ExpenseTemplate:
    """
    Template for frequently used expenses.

    Attributes:
        template_id: Unique identifier (UUID)
        name: Template name (e.g., "Weekly Hair Supplies")
        category: Default category
        subcategory: Default subcategory
        vendor: Default vendor name
        typical_amount: Typical/default amount
        payment_method: Default payment method
        description: Default description
        tags: Default tags
        use_count: Number of times template was used
        last_used: Last usage timestamp
        created_at: Creation timestamp
    """

    # Required fields
    name: str
    category: str
    vendor: str

    # Optional fields with defaults
    template_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    subcategory: str = ""
    typical_amount: float = 0.0
    payment_method: str = "Cash"
    description: str = ""
    tags: List[str] = field(default_factory=list)
    use_count: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Validate and convert fields after initialization."""
        self.typical_amount = float(self.typical_amount)
        self.use_count = int(self.use_count)

        # Ensure tags is a list
        if isinstance(self.tags, str):
            self.tags = [t.strip() for t in self.tags.split(',') if t.strip()]
        elif self.tags is None:
            self.tags = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for CSV storage."""
        return {
            'template_id': self.template_id,
            'name': self.name,
            'category': self.category,
            'subcategory': self.subcategory or '',
            'vendor': self.vendor,
            'typical_amount': self.typical_amount,
            'payment_method': self.payment_method,
            'description': self.description or '',
            'tags': ','.join(self.tags) if self.tags else '',
            'use_count': self.use_count,
            'last_used': self.last_used.strftime('%Y-%m-%d %H:%M:%S') if self.last_used else '',
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExpenseTemplate':
        """Create ExpenseTemplate from dictionary."""
        # Parse tags
        tags = data.get('tags', '')
        if isinstance(tags, str):
            tags = [t.strip() for t in tags.split(',') if t.strip()]

        # Parse dates
        last_used = None
        if data.get('last_used'):
            try:
                last_used = datetime.strptime(data['last_used'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        created_at = datetime.now()
        if data.get('created_at'):
            try:
                created_at = datetime.strptime(data['created_at'], '%Y-%m-%d %H:%M:%S')
            except ValueError:
                pass

        return cls(
            template_id=data.get('template_id') or str(uuid.uuid4()),
            name=data.get('name', ''),
            category=data.get('category', ''),
            subcategory=data.get('subcategory', ''),
            vendor=data.get('vendor', ''),
            typical_amount=float(data.get('typical_amount', 0)),
            payment_method=data.get('payment_method', 'Cash'),
            description=data.get('description', ''),
            tags=tags,
            use_count=int(data.get('use_count', 0)),
            last_used=last_used,
            created_at=created_at
        )

    def record_use(self) -> None:
        """Record template usage."""
        self.use_count += 1
        self.last_used = datetime.now()

    def update(self, **kwargs) -> None:
        """Update template fields."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def validate(self) -> List[str]:
        """
        Validate template data.

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        if not self.name:
            errors.append("Template name is required")

        if not self.category:
            errors.append("Category is required")

        if not self.vendor:
            errors.append("Vendor is required")

        if self.typical_amount < 0:
            errors.append("Amount cannot be negative")

        return errors
