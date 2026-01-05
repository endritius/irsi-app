"""
BudgetManager - Manages budget CRUD and tracking operations.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models import Budget, Expense
from persistence.data_manager import get_data_manager, DataManager
from utils.validators import validate_budget
from utils.exceptions import MultipleValidationError, BudgetNotFoundError, BudgetExistsError
from utils.error_handler import log_info, log_warning, log_error
from config import WARNING_THRESHOLD, CRITICAL_THRESHOLD


class BudgetStatus(Enum):
    """Budget status levels."""
    UNDER_BUDGET = "under_budget"
    WARNING = "warning"
    CRITICAL = "critical"
    OVER_BUDGET = "over_budget"


class BudgetManager:
    """
    Manages budget CRUD and tracking operations.
    Provides budget vs actual comparison and alerts.
    """

    def __init__(self, data_manager: DataManager = None):
        """
        Initialize BudgetManager.

        Args:
            data_manager: DataManager instance (uses global if None)
        """
        self.data_manager = data_manager or get_data_manager()
        self._budgets: Dict[str, Budget] = {}
        self._loaded = False

        # Thresholds
        self.warning_threshold = WARNING_THRESHOLD
        self.critical_threshold = CRITICAL_THRESHOLD

        # Load budgets on init
        self.load_budgets()

    def load_budgets(self) -> None:
        """Load budgets from CSV into memory cache."""
        try:
            df = self.data_manager.load_budgets()
            self._budgets = {}

            for _, row in df.iterrows():
                try:
                    budget = Budget.from_dict(row.to_dict())
                    self._budgets[budget.budget_id] = budget
                except Exception as e:
                    log_warning(f"Failed to parse budget row: {e}")

            self._loaded = True
            log_info(f"Loaded {len(self._budgets)} budgets")

        except Exception as e:
            log_error(e, "load_budgets")
            self._budgets = {}
            self._loaded = True

    def save_budgets(self) -> None:
        """Save all budgets to CSV."""
        try:
            data = [b.to_dict() for b in self._budgets.values()]
            df = pd.DataFrame(data)
            self.data_manager.save_budgets(df)
        except Exception as e:
            log_error(e, "save_budgets")
            raise

    # ===== CRUD OPERATIONS =====

    def add_budget(self, budget: Budget) -> str:
        """
        Add new budget.

        Args:
            budget: Budget object to add

        Returns:
            budget_id of added budget

        Raises:
            MultipleValidationError: If validation fails
            BudgetExistsError: If budget for same category/period exists
        """
        # Validate
        errors = validate_budget(budget)
        if errors:
            raise MultipleValidationError(errors)

        # Check for existing budget for same category and period
        existing = self.get_budget_for_period(
            budget.category,
            budget.period_start,
            budget.period_end
        )
        if existing:
            raise BudgetExistsError(
                budget.category,
                budget.period_start,
                budget.period_end
            )

        # Add to cache
        self._budgets[budget.budget_id] = budget

        # Auto-save
        self.save_budgets()

        log_info(f"Added budget: {budget.budget_id} - {budget.category}")
        return budget.budget_id

    def get_budget(self, budget_id: str) -> Optional[Budget]:
        """
        Get budget by ID.

        Args:
            budget_id: Budget ID

        Returns:
            Budget object or None if not found
        """
        return self._budgets.get(budget_id)

    def update_budget(self, budget_id: str, updates: Dict) -> bool:
        """
        Update budget fields.

        Args:
            budget_id: Budget ID
            updates: Dictionary of field updates

        Returns:
            True on success

        Raises:
            MultipleValidationError: If validation fails
        """
        budget = self._budgets.get(budget_id)
        if not budget:
            return False

        # Apply updates
        for key, value in updates.items():
            if hasattr(budget, key):
                setattr(budget, key, value)

        # Validate updated budget
        errors = validate_budget(budget)
        if errors:
            # Rollback - reload from storage
            self.load_budgets()
            raise MultipleValidationError(errors)

        # Auto-save
        self.save_budgets()

        log_info(f"Updated budget: {budget_id}")
        return True

    def delete_budget(self, budget_id: str) -> bool:
        """
        Delete budget.

        Args:
            budget_id: Budget ID

        Returns:
            True on success
        """
        if budget_id not in self._budgets:
            return False

        del self._budgets[budget_id]
        self.save_budgets()

        log_info(f"Deleted budget: {budget_id}")
        return True

    # ===== QUERY METHODS =====

    def get_all_budgets(self) -> List[Budget]:
        """
        Get all budgets sorted by period.

        Returns:
            List of budgets (most recent first)
        """
        budgets = list(self._budgets.values())
        budgets.sort(key=lambda b: b.period_start, reverse=True)
        return budgets

    def get_active_budgets(self) -> List[Budget]:
        """
        Get currently active budgets.

        Returns:
            List of active budgets
        """
        today = datetime.now().date()
        return [b for b in self._budgets.values()
                if b.period_start.date() <= today <= b.period_end.date()]

    def get_budget_for_period(
        self,
        category: str,
        period_start: datetime,
        period_end: datetime
    ) -> Optional[Budget]:
        """
        Get budget for specific category and period.

        Args:
            category: Category name
            period_start: Period start date
            period_end: Period end date

        Returns:
            Budget or None if not found
        """
        for budget in self._budgets.values():
            if (budget.category == category and
                budget.period_start.date() == period_start.date() and
                budget.period_end.date() == period_end.date()):
                return budget
        return None

    def get_budgets_by_category(self, category: str) -> List[Budget]:
        """
        Get all budgets for a category.

        Args:
            category: Category name

        Returns:
            List of budgets for category
        """
        return [b for b in self._budgets.values() if b.category == category]

    def get_current_budget_for_category(self, category: str) -> Optional[Budget]:
        """
        Get current active budget for category.

        Args:
            category: Category name

        Returns:
            Current budget or None
        """
        today = datetime.now().date()
        for budget in self._budgets.values():
            if (budget.category == category and
                budget.period_start.date() <= today <= budget.period_end.date()):
                return budget
        return None

    # ===== BUDGET TRACKING =====

    def calculate_spent(
        self,
        budget: Budget,
        expenses: List[Expense]
    ) -> float:
        """
        Calculate total spent for a budget from expenses.

        Args:
            budget: Budget to calculate for
            expenses: List of expenses

        Returns:
            Total amount spent
        """
        total = 0.0
        for expense in expenses:
            if expense.is_deleted:
                continue
            if expense.category != budget.category:
                continue
            # Check if expense is within budget period
            expense_date = expense.date.date() if isinstance(expense.date, datetime) else expense.date
            start_date = budget.period_start.date() if isinstance(budget.period_start, datetime) else budget.period_start
            end_date = budget.period_end.date() if isinstance(budget.period_end, datetime) else budget.period_end

            if start_date <= expense_date <= end_date:
                total += expense.amount

        return total

    def update_budget_spent(
        self,
        budget_id: str,
        expenses: List[Expense]
    ) -> float:
        """
        Update a budget's spent amount from expenses.

        Args:
            budget_id: Budget ID
            expenses: List of expenses

        Returns:
            Updated spent amount
        """
        budget = self._budgets.get(budget_id)
        if not budget:
            return 0.0

        budget.spent = self.calculate_spent(budget, expenses)
        self.save_budgets()

        return budget.spent

    def update_all_budgets_spent(self, expenses: List[Expense]) -> None:
        """
        Update spent amounts for all budgets.

        Args:
            expenses: List of all expenses
        """
        for budget in self._budgets.values():
            budget.spent = self.calculate_spent(budget, expenses)

        self.save_budgets()

    def get_budget_status(self, budget: Budget) -> BudgetStatus:
        """
        Get status of a budget based on spent percentage.

        Args:
            budget: Budget to check

        Returns:
            BudgetStatus enum value
        """
        if budget.amount <= 0:
            return BudgetStatus.UNDER_BUDGET

        percentage = budget.get_used_percentage()

        if percentage >= 100:
            return BudgetStatus.OVER_BUDGET
        elif percentage >= self.critical_threshold:
            return BudgetStatus.CRITICAL
        elif percentage >= self.warning_threshold:
            return BudgetStatus.WARNING
        else:
            return BudgetStatus.UNDER_BUDGET

    def get_budget_summary(
        self,
        budget: Budget
    ) -> Dict:
        """
        Get detailed summary for a budget.

        Args:
            budget: Budget to summarize

        Returns:
            Dictionary with budget details
        """
        status = self.get_budget_status(budget)
        remaining = budget.get_remaining()
        percentage = budget.get_used_percentage()

        return {
            'budget_id': budget.budget_id,
            'category': budget.category,
            'amount': budget.amount,
            'spent': budget.spent,
            'remaining': remaining,
            'percentage': percentage,
            'status': status.value,
            'period_start': budget.period_start,
            'period_end': budget.period_end,
            'is_over_budget': percentage >= 100,
            'is_warning': status == BudgetStatus.WARNING,
            'is_critical': status == BudgetStatus.CRITICAL
        }

    def get_all_budget_summaries(self) -> List[Dict]:
        """
        Get summaries for all active budgets.

        Returns:
            List of budget summary dictionaries
        """
        return [self.get_budget_summary(b) for b in self.get_active_budgets()]

    # ===== ALERTS =====

    def get_budget_alerts(self) -> List[Dict]:
        """
        Get list of budgets that need attention.

        Returns:
            List of alert dictionaries
        """
        alerts = []

        for budget in self.get_active_budgets():
            status = self.get_budget_status(budget)

            if status in (BudgetStatus.WARNING, BudgetStatus.CRITICAL, BudgetStatus.OVER_BUDGET):
                percentage = budget.get_used_percentage()
                remaining = budget.get_remaining()

                alert = {
                    'budget_id': budget.budget_id,
                    'category': budget.category,
                    'status': status.value,
                    'percentage': percentage,
                    'remaining': remaining,
                    'amount': budget.amount,
                    'spent': budget.spent
                }

                if status == BudgetStatus.OVER_BUDGET:
                    alert['message'] = f"{budget.category}: Over budget by {abs(remaining):,.0f} L"
                    alert['severity'] = 'error'
                elif status == BudgetStatus.CRITICAL:
                    alert['message'] = f"{budget.category}: {percentage:.1f}% used - Critical!"
                    alert['severity'] = 'warning'
                else:
                    alert['message'] = f"{budget.category}: {percentage:.1f}% used"
                    alert['severity'] = 'info'

                alerts.append(alert)

        # Sort by severity (most critical first)
        severity_order = {'error': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda a: severity_order.get(a['severity'], 3))

        return alerts

    def check_expense_against_budget(
        self,
        expense: Expense,
        expenses: List[Expense]
    ) -> Optional[Dict]:
        """
        Check if adding an expense would trigger budget alerts.

        Args:
            expense: Expense to check
            expenses: Current list of expenses

        Returns:
            Alert dictionary if budget warning triggered, None otherwise
        """
        budget = self.get_current_budget_for_category(expense.category)
        if not budget:
            return None

        # Calculate what spent would be with new expense
        current_spent = self.calculate_spent(budget, expenses)
        new_spent = current_spent + expense.amount
        new_percentage = (new_spent / budget.amount * 100) if budget.amount > 0 else 0

        # Check thresholds
        old_percentage = budget.get_used_percentage()

        if new_percentage >= 100 and old_percentage < 100:
            return {
                'type': 'over_budget',
                'category': budget.category,
                'percentage': new_percentage,
                'message': f"This expense will put {budget.category} over budget!"
            }
        elif new_percentage >= self.critical_threshold and old_percentage < self.critical_threshold:
            return {
                'type': 'critical',
                'category': budget.category,
                'percentage': new_percentage,
                'message': f"Warning: {budget.category} budget at {new_percentage:.1f}%"
            }
        elif new_percentage >= self.warning_threshold and old_percentage < self.warning_threshold:
            return {
                'type': 'warning',
                'category': budget.category,
                'percentage': new_percentage,
                'message': f"Note: {budget.category} budget at {new_percentage:.1f}%"
            }

        return None

    # ===== ROLLOVER =====

    def calculate_rollover(
        self,
        budget: Budget,
        rollover_cap_percentage: float = 100.0
    ) -> float:
        """
        Calculate rollover amount from a budget.

        Args:
            budget: Budget to calculate rollover from
            rollover_cap_percentage: Max percentage of budget to roll over

        Returns:
            Rollover amount
        """
        if not budget.allow_rollover:
            return 0.0

        remaining = budget.get_remaining()
        if remaining <= 0:
            return 0.0

        # Apply cap
        max_rollover = budget.amount * (rollover_cap_percentage / 100)
        return min(remaining, max_rollover)

    def create_next_period_budget(
        self,
        budget: Budget,
        include_rollover: bool = True,
        rollover_cap_percentage: float = 100.0
    ) -> Budget:
        """
        Create budget for next period based on current budget.

        Args:
            budget: Current budget
            include_rollover: Whether to include unused amount as rollover
            rollover_cap_percentage: Max percentage to roll over

        Returns:
            New Budget for next period
        """
        from dateutil.relativedelta import relativedelta

        # Calculate next period
        period_length = (budget.period_end - budget.period_start).days + 1

        # Assume monthly periods
        next_start = budget.period_end + relativedelta(days=1)
        next_end = next_start + relativedelta(months=1) - relativedelta(days=1)

        # Calculate rollover
        rollover = 0.0
        if include_rollover:
            rollover = self.calculate_rollover(budget, rollover_cap_percentage)

        # Create new budget
        new_budget = Budget(
            category=budget.category,
            amount=budget.amount,
            period_start=next_start,
            period_end=next_end,
            spent=0.0,
            notes=budget.notes,
            allow_rollover=budget.allow_rollover,
            rollover_amount=rollover
        )

        return new_budget

    def apply_rollover(
        self,
        from_budget_id: str,
        to_budget_id: str,
        rollover_cap_percentage: float = 100.0
    ) -> float:
        """
        Apply rollover from one budget to another.

        Args:
            from_budget_id: Source budget ID
            to_budget_id: Destination budget ID
            rollover_cap_percentage: Max percentage to roll over

        Returns:
            Amount rolled over
        """
        from_budget = self._budgets.get(from_budget_id)
        to_budget = self._budgets.get(to_budget_id)

        if not from_budget or not to_budget:
            return 0.0

        if from_budget.category != to_budget.category:
            log_warning("Cannot roll over between different categories")
            return 0.0

        rollover = self.calculate_rollover(from_budget, rollover_cap_percentage)
        if rollover > 0:
            to_budget.rollover_amount = rollover
            self.save_budgets()
            log_info(f"Rolled over {rollover:,.0f} L to budget {to_budget_id}")

        return rollover

    # ===== STATISTICS =====

    def get_budget_count(self) -> int:
        """Get total budget count."""
        return len(self._budgets)

    def get_total_budgeted(self) -> float:
        """Get total budgeted amount for active budgets."""
        return sum(b.amount for b in self.get_active_budgets())

    def get_total_spent(self) -> float:
        """Get total spent across active budgets."""
        return sum(b.spent for b in self.get_active_budgets())

    def get_categories_over_budget(self) -> List[str]:
        """Get list of categories that are over budget."""
        over_budget = []
        for budget in self.get_active_budgets():
            if budget.get_used_percentage() >= 100:
                over_budget.append(budget.category)
        return over_budget

    def get_budget_health_score(self) -> float:
        """
        Calculate overall budget health score (0-100).
        Higher is better.

        Returns:
            Health score percentage
        """
        active_budgets = self.get_active_budgets()
        if not active_budgets:
            return 100.0

        # Calculate average of (100 - percentage used), capped at 0
        scores = []
        for budget in active_budgets:
            percentage = budget.get_used_percentage()
            score = max(0, 100 - percentage)
            scores.append(score)

        return sum(scores) / len(scores)


# Singleton instance
_budget_manager: Optional[BudgetManager] = None


def get_budget_manager() -> BudgetManager:
    """Get or create global BudgetManager instance."""
    global _budget_manager
    if _budget_manager is None:
        _budget_manager = BudgetManager()
    return _budget_manager
