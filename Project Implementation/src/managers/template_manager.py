"""
TemplateManager - Manages expense template operations.
"""

from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import ExpenseTemplate, Expense
from persistence.data_manager import get_data_manager, DataManager
from utils.validators import validate_template
from utils.exceptions import MultipleValidationError, TemplateNotFoundError
from utils.error_handler import log_info, log_warning, log_error


class TemplateManager:
    """
    Manages expense template operations.
    Provides template CRUD and quick expense creation.
    """

    def __init__(self, data_manager: DataManager = None):
        """
        Initialize TemplateManager.

        Args:
            data_manager: DataManager instance (uses global if None)
        """
        self.data_manager = data_manager or get_data_manager()
        self._templates: Dict[str, ExpenseTemplate] = {}
        self._loaded = False

        # Load templates on init
        self.load_templates()

    def load_templates(self) -> None:
        """Load templates from CSV."""
        try:
            df = self.data_manager.load_templates()
            self._templates = {}

            for _, row in df.iterrows():
                try:
                    template = ExpenseTemplate.from_dict(row.to_dict())
                    self._templates[template.template_id] = template
                except Exception as e:
                    log_warning(f"Failed to parse template row: {e}")

            self._loaded = True
            log_info(f"Loaded {len(self._templates)} templates")

        except Exception as e:
            log_error(e, "load_templates")
            self._templates = {}
            self._loaded = True

    def save_templates(self) -> None:
        """Save templates to CSV."""
        try:
            data = [t.to_dict() for t in self._templates.values()]
            df = pd.DataFrame(data)
            self.data_manager.save_templates(df)
        except Exception as e:
            log_error(e, "save_templates")
            raise

    # ===== CRUD OPERATIONS =====

    def add_template(self, template: ExpenseTemplate) -> str:
        """
        Add new template.

        Args:
            template: ExpenseTemplate object to add

        Returns:
            template_id of added template

        Raises:
            MultipleValidationError: If validation fails
        """
        # Validate
        errors = validate_template(template)
        if errors:
            raise MultipleValidationError(errors)

        # Add to cache
        self._templates[template.template_id] = template

        # Auto-save
        self.save_templates()

        log_info(f"Added template: {template.template_id} - {template.name}")
        return template.template_id

    def get_template(self, template_id: str) -> Optional[ExpenseTemplate]:
        """
        Get template by ID.

        Args:
            template_id: Template ID

        Returns:
            ExpenseTemplate or None if not found
        """
        return self._templates.get(template_id)

    def update_template(self, template_id: str, updates: Dict) -> bool:
        """
        Update template fields.

        Args:
            template_id: Template ID
            updates: Dictionary of field updates

        Returns:
            True on success
        """
        template = self._templates.get(template_id)
        if not template:
            return False

        # Apply updates
        template.update(**updates)

        # Validate
        errors = validate_template(template)
        if errors:
            self.load_templates()  # Rollback
            raise MultipleValidationError(errors)

        # Auto-save
        self.save_templates()

        log_info(f"Updated template: {template_id}")
        return True

    def delete_template(self, template_id: str) -> bool:
        """
        Delete template.

        Args:
            template_id: Template ID

        Returns:
            True on success
        """
        if template_id not in self._templates:
            return False

        del self._templates[template_id]
        self.save_templates()

        log_info(f"Deleted template: {template_id}")
        return True

    # ===== QUERY METHODS =====

    def get_all_templates(self) -> List[ExpenseTemplate]:
        """
        Get all templates sorted by use_count (most used first).

        Returns:
            List of templates
        """
        templates = list(self._templates.values())
        templates.sort(key=lambda t: t.use_count, reverse=True)
        return templates

    def get_top_templates(self, n: int = 5) -> List[ExpenseTemplate]:
        """
        Get top N most used templates.

        Args:
            n: Number of templates to return

        Returns:
            List of most used templates
        """
        return self.get_all_templates()[:n]

    def get_recent_templates(self, n: int = 5) -> List[ExpenseTemplate]:
        """
        Get recently used templates.

        Args:
            n: Number of templates to return

        Returns:
            List of recently used templates
        """
        templates = [t for t in self._templates.values() if t.last_used]
        templates.sort(key=lambda t: t.last_used, reverse=True)
        return templates[:n]

    def search_templates(self, query: str) -> List[ExpenseTemplate]:
        """
        Search templates by name, vendor, or category.

        Args:
            query: Search query string

        Returns:
            List of matching templates
        """
        query_lower = query.lower()
        results = []

        for template in self._templates.values():
            if (query_lower in template.name.lower() or
                query_lower in template.vendor.lower() or
                query_lower in template.category.lower()):
                results.append(template)

        # Sort by relevance (name match first)
        results.sort(key=lambda t: (
            0 if query_lower in t.name.lower() else 1,
            -t.use_count
        ))

        return results

    def get_templates_by_category(self, category: str) -> List[ExpenseTemplate]:
        """
        Get templates for a specific category.

        Args:
            category: Category name

        Returns:
            List of templates in category
        """
        return [t for t in self._templates.values() if t.category == category]

    # ===== EXPENSE CREATION =====

    def create_expense_from_template(
        self,
        template_id: str,
        date: datetime = None,
        amount: float = None
    ) -> Expense:
        """
        Create an expense from a template.

        Args:
            template_id: Template ID
            date: Override date (default today)
            amount: Override amount (default template's typical_amount)

        Returns:
            New Expense object

        Raises:
            TemplateNotFoundError: If template not found
        """
        template = self._templates.get(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)

        # Create expense
        expense = Expense(
            amount=amount if amount is not None else template.typical_amount,
            date=date or datetime.now(),
            category=template.category,
            subcategory=template.subcategory,
            vendor=template.vendor,
            payment_method=template.payment_method,
            description=template.description,
            tags=template.tags.copy() if template.tags else []
        )

        # Record template usage
        template.record_use()
        self.save_templates()

        return expense

    def create_from_expense(self, expense: Expense, name: str) -> ExpenseTemplate:
        """
        Create a template from an existing expense.

        Args:
            expense: Expense to use as source
            name: Template name

        Returns:
            New ExpenseTemplate
        """
        template = ExpenseTemplate(
            name=name,
            category=expense.category,
            subcategory=expense.subcategory,
            vendor=expense.vendor,
            typical_amount=expense.amount,
            payment_method=expense.payment_method,
            description=expense.description,
            tags=expense.tags.copy() if expense.tags else []
        )

        self.add_template(template)
        return template

    # ===== STATISTICS =====

    def get_template_count(self) -> int:
        """Get total template count."""
        return len(self._templates)

    def get_most_used_template(self) -> Optional[ExpenseTemplate]:
        """Get the most frequently used template."""
        if not self._templates:
            return None
        return max(self._templates.values(), key=lambda t: t.use_count)


# Singleton instance
_template_manager: Optional[TemplateManager] = None


def get_template_manager() -> TemplateManager:
    """Get or create global TemplateManager instance."""
    global _template_manager
    if _template_manager is None:
        _template_manager = TemplateManager()
    return _template_manager
