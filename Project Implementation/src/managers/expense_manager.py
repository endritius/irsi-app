"""
ExpenseManager - Manages all expense CRUD operations.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import Expense
from persistence.data_manager import get_data_manager, DataManager
from utils.validators import validate_expense
from utils.exceptions import ValidationError, MultipleValidationError, DataIntegrityError
from utils.error_handler import log_info, log_warning, log_error


class ExpenseManager:
    """
    Manages all expense CRUD operations.
    Provides in-memory caching for fast access with auto-save.
    """

    def __init__(self, data_manager: DataManager = None):
        """
        Initialize ExpenseManager.

        Args:
            data_manager: DataManager instance (uses global if None)
        """
        self.data_manager = data_manager or get_data_manager()
        self._expenses: Dict[str, Expense] = {}
        self._vendor_cache: List[str] = []
        self._tag_cache: Set[str] = set()
        self._loaded = False

        # Load expenses on init
        self.load_expenses()

    def load_expenses(self) -> None:
        """Load expenses from CSV into memory cache."""
        try:
            df = self.data_manager.load_expenses()
            self._expenses = {}

            for _, row in df.iterrows():
                try:
                    expense = Expense.from_dict(row.to_dict())
                    self._expenses[expense.expense_id] = expense
                except Exception as e:
                    log_warning(f"Failed to parse expense row: {e}")

            # Build caches
            self._rebuild_caches()
            self._loaded = True
            log_info(f"Loaded {len(self._expenses)} expenses")

        except Exception as e:
            log_error(e, "load_expenses")
            self._expenses = {}
            self._loaded = True

    def save_expenses(self) -> None:
        """Save all expenses to CSV."""
        try:
            data = [exp.to_dict() for exp in self._expenses.values()]
            df = pd.DataFrame(data)
            self.data_manager.save_expenses(df)
        except Exception as e:
            log_error(e, "save_expenses")
            raise

    def _rebuild_caches(self) -> None:
        """Rebuild vendor and tag caches."""
        self._vendor_cache = []
        self._tag_cache = set()

        vendor_usage = {}
        for expense in self._expenses.values():
            if expense.is_deleted:
                continue

            # Track vendor usage
            if expense.vendor:
                vendor_usage[expense.vendor] = vendor_usage.get(expense.vendor, 0) + 1

            # Collect tags
            if expense.tags:
                self._tag_cache.update(expense.tags)

        # Sort vendors by usage count
        self._vendor_cache = sorted(vendor_usage.keys(),
                                   key=lambda v: vendor_usage[v],
                                   reverse=True)

    # ===== CRUD OPERATIONS =====

    def add_expense(self, expense: Expense) -> str:
        """
        Add new expense.

        Args:
            expense: Expense object to add

        Returns:
            expense_id of added expense

        Raises:
            MultipleValidationError: If validation fails
        """
        # Validate
        errors = validate_expense(expense)
        if errors:
            raise MultipleValidationError(errors)

        # Set timestamps
        now = datetime.now()
        expense.created_at = now
        expense.updated_at = now

        # Add to cache
        self._expenses[expense.expense_id] = expense

        # Update caches
        if expense.vendor and expense.vendor not in self._vendor_cache:
            self._vendor_cache.insert(0, expense.vendor)
        if expense.tags:
            self._tag_cache.update(expense.tags)

        # Auto-save
        self.save_expenses()

        log_info(f"Added expense: {expense.expense_id}")
        return expense.expense_id

    def get_expense(self, expense_id: str) -> Optional[Expense]:
        """
        Get single expense by ID.

        Args:
            expense_id: Expense ID

        Returns:
            Expense object or None if not found
        """
        return self._expenses.get(expense_id)

    def update_expense(self, expense_id: str, updates: Dict) -> bool:
        """
        Update expense fields.

        Args:
            expense_id: Expense ID
            updates: Dictionary of field updates

        Returns:
            True on success

        Raises:
            MultipleValidationError: If validation fails
        """
        expense = self._expenses.get(expense_id)
        if not expense:
            return False

        # Apply updates
        old_vendor = expense.vendor
        expense.update(**updates)

        # Validate updated expense
        errors = validate_expense(expense)
        if errors:
            # Rollback - reload from storage
            self.load_expenses()
            raise MultipleValidationError(errors)

        # Update vendor cache if changed
        if expense.vendor != old_vendor and expense.vendor not in self._vendor_cache:
            self._vendor_cache.insert(0, expense.vendor)

        # Update tag cache
        if expense.tags:
            self._tag_cache.update(expense.tags)

        # Auto-save
        self.save_expenses()

        log_info(f"Updated expense: {expense_id}")
        return True

    def delete_expense(self, expense_id: str, permanent: bool = False) -> bool:
        """
        Delete expense.

        Args:
            expense_id: Expense ID
            permanent: If True, permanently delete; if False, soft delete

        Returns:
            True on success
        """
        expense = self._expenses.get(expense_id)
        if not expense:
            return False

        if permanent:
            # Permanent delete
            del self._expenses[expense_id]
            log_info(f"Permanently deleted expense: {expense_id}")
        else:
            # Soft delete
            expense.soft_delete()
            log_info(f"Soft deleted expense: {expense_id}")

        # Rebuild caches
        self._rebuild_caches()

        # Auto-save
        self.save_expenses()

        return True

    def restore_expense(self, expense_id: str) -> bool:
        """
        Restore a soft-deleted expense.

        Args:
            expense_id: Expense ID

        Returns:
            True on success
        """
        expense = self._expenses.get(expense_id)
        if not expense or not expense.is_deleted:
            return False

        expense.restore()

        # Rebuild caches
        self._rebuild_caches()

        # Auto-save
        self.save_expenses()

        log_info(f"Restored expense: {expense_id}")
        return True

    def bulk_delete(self, expense_ids: List[str], permanent: bool = False) -> int:
        """
        Delete multiple expenses.

        Args:
            expense_ids: List of expense IDs
            permanent: If True, permanently delete

        Returns:
            Count of deleted expenses
        """
        deleted = 0
        for expense_id in expense_ids:
            if self.delete_expense(expense_id, permanent):
                deleted += 1

        return deleted

    # ===== QUERY METHODS =====

    def get_all_expenses(self, include_deleted: bool = False) -> List[Expense]:
        """
        Get all expenses.

        Args:
            include_deleted: Whether to include soft-deleted expenses

        Returns:
            List of expenses
        """
        expenses = list(self._expenses.values())
        if not include_deleted:
            expenses = [e for e in expenses if not e.is_deleted]
        return expenses

    def get_deleted_expenses(self) -> List[Expense]:
        """
        Get only soft-deleted expenses.

        Returns:
            List of deleted expenses
        """
        return [e for e in self._expenses.values() if e.is_deleted]

    def get_expenses_dataframe(self, include_deleted: bool = False) -> pd.DataFrame:
        """
        Get expenses as DataFrame for analysis.

        Args:
            include_deleted: Whether to include soft-deleted expenses

        Returns:
            DataFrame with expense data
        """
        expenses = self.get_all_expenses(include_deleted)
        if not expenses:
            from persistence.data_manager import EXPENSE_COLUMNS
            return pd.DataFrame(columns=EXPENSE_COLUMNS)

        data = [exp.to_dict() for exp in expenses]
        return pd.DataFrame(data)

    def get_unique_vendors(self) -> List[str]:
        """
        Get sorted list of unique vendors for autocomplete.

        Returns:
            List of vendor names (most used first)
        """
        return self._vendor_cache.copy()

    def get_unique_tags(self) -> Set[str]:
        """
        Get set of all used tags.

        Returns:
            Set of tag strings
        """
        return self._tag_cache.copy()

    def get_recent_vendors(self, n: int = 5) -> List[str]:
        """
        Get recently used vendors.

        Args:
            n: Number of vendors to return

        Returns:
            List of vendor names (most recent first)
        """
        # Sort by most recent date
        vendor_dates = {}
        for expense in self._expenses.values():
            if expense.is_deleted or not expense.vendor:
                continue
            if expense.vendor not in vendor_dates or expense.date > vendor_dates[expense.vendor]:
                vendor_dates[expense.vendor] = expense.date

        sorted_vendors = sorted(vendor_dates.keys(),
                               key=lambda v: vendor_dates[v],
                               reverse=True)
        return sorted_vendors[:n]

    # ===== DUPLICATE DETECTION =====

    def find_duplicates(self, expense: Expense, days_threshold: int = 3) -> List[Expense]:
        """
        Find potential duplicate expenses.

        Args:
            expense: Expense to check
            days_threshold: Days within which to consider duplicates

        Returns:
            List of potential duplicate expenses
        """
        duplicates = []
        threshold = timedelta(days=days_threshold)

        for existing in self._expenses.values():
            if existing.is_deleted:
                continue
            if existing.expense_id == expense.expense_id:
                continue

            # Check same vendor and amount
            if existing.vendor.lower() == expense.vendor.lower() and \
               abs(existing.amount - expense.amount) < 0.01:
                # Check date proximity
                date_diff = abs((existing.date - expense.date).days)
                if date_diff <= days_threshold:
                    duplicates.append(existing)

        return duplicates

    def check_exact_duplicate(self, expense: Expense) -> Optional[Expense]:
        """
        Check for exact duplicate (same vendor, amount, date).

        Args:
            expense: Expense to check

        Returns:
            Existing duplicate expense or None
        """
        for existing in self._expenses.values():
            if existing.is_deleted:
                continue
            if existing.expense_id == expense.expense_id:
                continue

            if (existing.vendor.lower() == expense.vendor.lower() and
                abs(existing.amount - expense.amount) < 0.01 and
                existing.date.date() == expense.date.date()):
                return existing

        return None

    # ===== RECURRING EXPENSES =====

    def get_recurring_expenses(self) -> List[Expense]:
        """
        Get all recurring expense definitions.

        Returns:
            List of recurring expenses
        """
        return [e for e in self._expenses.values()
                if e.is_recurring and not e.is_deleted]

    def get_due_recurring_expenses(self) -> List[Expense]:
        """
        Get recurring expenses that are due for generation/reminder.

        Returns:
            List of due recurring expenses
        """
        today = datetime.now().date()
        due = []

        for expense in self.get_recurring_expenses():
            if expense.next_due_date:
                if expense.next_due_date.date() <= today:
                    due.append(expense)

        return due

    # ===== STATISTICS =====

    def get_expense_count(self, include_deleted: bool = False) -> int:
        """Get total expense count."""
        if include_deleted:
            return len(self._expenses)
        return len([e for e in self._expenses.values() if not e.is_deleted])

    def get_total_amount(self, include_deleted: bool = False) -> float:
        """Get total expense amount."""
        expenses = self.get_all_expenses(include_deleted)
        return sum(e.amount for e in expenses)

    def get_expenses_by_category(self, category: str) -> List[Expense]:
        """Get expenses for a specific category."""
        return [e for e in self._expenses.values()
                if e.category == category and not e.is_deleted]

    def get_expenses_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        include_deleted: bool = False
    ) -> List[Expense]:
        """
        Get expenses within date range.

        Args:
            start_date: Start date
            end_date: End date
            include_deleted: Whether to include deleted

        Returns:
            List of expenses in range
        """
        expenses = []
        for expense in self._expenses.values():
            if not include_deleted and expense.is_deleted:
                continue
            if start_date <= expense.date <= end_date:
                expenses.append(expense)
        return expenses

    def get_expenses_by_vendor(self, vendor: str) -> List[Expense]:
        """Get expenses for a specific vendor."""
        return [e for e in self._expenses.values()
                if e.vendor.lower() == vendor.lower() and not e.is_deleted]

    def copy_expense(self, expense_id: str) -> Optional[Expense]:
        """
        Create a copy of an expense with new ID and current date.

        Args:
            expense_id: Expense ID to copy

        Returns:
            New expense copy or None if not found
        """
        original = self.get_expense(expense_id)
        if not original:
            return None

        copy = original.copy()
        copy.date = datetime.now()
        return copy


# Singleton instance
_expense_manager: Optional[ExpenseManager] = None


def get_expense_manager() -> ExpenseManager:
    """Get or create global ExpenseManager instance."""
    global _expense_manager
    if _expense_manager is None:
        _expense_manager = ExpenseManager()
    return _expense_manager
