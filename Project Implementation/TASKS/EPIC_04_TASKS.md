# Epic 4: Budget Tracking & Alerts - Implementation Tasks

**Phase:** 6 (Core Features)
**Priority:** High
**Dependencies:** Epic 2, Epic 7
**Estimated Tasks:** 25+

---

## Story 4.1: BudgetManager Class

**Prerequisites:** Epic 2 (ExpenseManager), Epic 7 (DataManager)

### Task 4.1.1: Create BudgetManager class
- [ ] Create `managers/budget_manager.py`:
```python
"""
BudgetManager - Manages budget operations and tracking.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
import calendar

import pandas as pd

from models.budget import Budget
from persistence.data_manager import DataManager
from managers.expense_manager import ExpenseManager
from utils.error_handler import get_error_handler


class BudgetManager:
    """Manages budget operations and tracking."""

    def __init__(self, data_manager: DataManager, expense_manager: ExpenseManager):
        """Initialize with managers."""
        self.data_manager = data_manager
        self.expense_manager = expense_manager
        self.error_handler = get_error_handler()

        # In-memory cache
        self._budgets: Dict[str, Budget] = {}

        # Load budgets
        self.load_budgets()
```

### Task 4.1.2: Implement load/save methods
- [ ] Add load and save functionality:
```python
    def load_budgets(self) -> None:
        """Load budgets from CSV."""
        df = self.data_manager.load_budgets()
        self._budgets = {}

        for _, row in df.iterrows():
            try:
                budget = Budget.from_dict(row.to_dict())
                self._budgets[budget.budget_id] = budget
            except Exception as e:
                self.error_handler.log_warning(f"Failed to load budget: {e}")

        self.error_handler.log_info(f"Loaded {len(self._budgets)} budgets")

    def save_budgets(self) -> None:
        """Save all budgets to CSV."""
        data = [b.to_dict() for b in self._budgets.values()]
        df = pd.DataFrame(data)
        self.data_manager.save_budgets(df)
```

### Task 4.1.3: Implement CRUD operations
- [ ] Add CRUD methods:
```python
    def add_budget(self, budget: Budget) -> str:
        """Add new budget, return budget_id."""
        if not budget.budget_id:
            budget.budget_id = str(uuid.uuid4())

        budget.created_at = datetime.now()
        budget.updated_at = datetime.now()

        self._budgets[budget.budget_id] = budget
        self.save_budgets()

        self.error_handler.log_info(f"Added budget: {budget.budget_id}")
        return budget.budget_id

    def update_budget(self, budget_id: str, updates: Dict) -> bool:
        """Update budget fields."""
        budget = self._budgets.get(budget_id)
        if not budget:
            return False

        for field, value in updates.items():
            if hasattr(budget, field):
                setattr(budget, field, value)

        budget.updated_at = datetime.now()
        self._budgets[budget_id] = budget
        self.save_budgets()

        return True

    def delete_budget(self, budget_id: str) -> bool:
        """Delete budget."""
        if budget_id not in self._budgets:
            return False

        del self._budgets[budget_id]
        self.save_budgets()
        return True

    def get_budget(self, budget_id: str) -> Optional[Budget]:
        """Get single budget by ID."""
        return self._budgets.get(budget_id)

    def get_all_budgets(self) -> List[Budget]:
        """Get all budgets."""
        return list(self._budgets.values())
```

### Task 4.1.4: Implement budget queries
- [ ] Add query methods:
```python
    def get_monthly_total_budget(self, month: int, year: int) -> Optional[Budget]:
        """Get total budget for specific month."""
        for budget in self._budgets.values():
            if (budget.budget_type == 'total' and
                budget.month == month and
                budget.year == year and
                budget.is_active):
                return budget
        return None

    def get_category_budget(self, category: str, month: int, year: int) -> Optional[Budget]:
        """Get budget for specific category and month."""
        for budget in self._budgets.values():
            if (budget.budget_type == 'category' and
                budget.category == category and
                budget.month == month and
                budget.year == year and
                budget.is_active):
                return budget
        return None

    def get_category_budgets(self, month: int, year: int) -> List[Budget]:
        """Get all category budgets for month."""
        return [b for b in self._budgets.values()
                if b.budget_type == 'category' and
                   b.month == month and
                   b.year == year and
                   b.is_active]

    def get_current_month_budgets(self) -> Dict[str, Budget]:
        """Get all budgets for current month."""
        now = datetime.now()
        result = {}

        for budget in self._budgets.values():
            if budget.month == now.month and budget.year == now.year and budget.is_active:
                key = f"{budget.budget_type}_{budget.category or 'total'}"
                result[key] = budget

        return result
```

### Task 4.1.5: Implement budget status calculations
- [ ] Add status calculation:
```python
    def get_budget_status(self, budget: Budget) -> Dict:
        """Calculate budget status with spending details."""
        # Get expenses for this budget period
        df = self.expense_manager.get_expenses_dataframe()
        if df.empty:
            spent = 0
        else:
            df['date'] = pd.to_datetime(df['date'])
            period_expenses = df[
                (df['date'].dt.month == budget.month) &
                (df['date'].dt.year == budget.year) &
                (df['is_deleted'] != True)
            ]

            if budget.budget_type == 'category' and budget.category:
                period_expenses = period_expenses[
                    period_expenses['category'] == budget.category
                ]

            spent = period_expenses['amount'].sum()

        # Calculate effective budget (including rollover)
        effective_budget = budget.amount + budget.rollover_amount

        # Calculate remaining and percentage
        remaining = effective_budget - spent
        percentage = (spent / effective_budget * 100) if effective_budget > 0 else 0

        # Determine status
        if percentage > 100:
            status = 'exceeded'
        elif percentage >= budget.warning_threshold:
            status = 'warning'
        else:
            status = 'ok'

        # Calculate days remaining
        _, last_day = calendar.monthrange(budget.year, budget.month)
        month_end = datetime(budget.year, budget.month, last_day)
        days_remaining = max(0, (month_end - datetime.now()).days)

        # Calculate projections
        days_elapsed = datetime.now().day
        daily_average = spent / days_elapsed if days_elapsed > 0 else 0
        projected_total = daily_average * last_day

        # Projected rollover (if enabled and under budget)
        projected_rollover = 0
        if budget.enable_rollover and projected_total < effective_budget:
            potential_rollover = effective_budget - projected_total
            max_rollover = budget.amount * (budget.rollover_cap_percent / 100)
            projected_rollover = min(potential_rollover, max_rollover)

        return {
            'budget_amount': budget.amount,
            'rollover_amount': budget.rollover_amount,
            'effective_budget': effective_budget,
            'spent': spent,
            'remaining': remaining,
            'percentage_used': percentage,
            'status': status,
            'days_remaining': days_remaining,
            'daily_average': daily_average,
            'projected_total': projected_total,
            'projected_rollover': projected_rollover
        }

    def get_all_statuses(self, month: int = None, year: int = None) -> List[Dict]:
        """Get status for all budgets in a month."""
        if month is None:
            month = datetime.now().month
        if year is None:
            year = datetime.now().year

        statuses = []
        for budget in self._budgets.values():
            if budget.month == month and budget.year == year and budget.is_active:
                status = self.get_budget_status(budget)
                status['budget'] = budget
                statuses.append(status)

        return statuses
```

### Task 4.1.6: Implement alerts
- [ ] Add alert methods:
```python
    def get_all_alerts(self) -> List[Dict]:
        """Get list of current budget alerts."""
        alerts = []
        statuses = self.get_all_statuses()

        for status in statuses:
            if status['status'] in ('warning', 'exceeded'):
                alerts.append({
                    'type': 'budget',
                    'severity': 'error' if status['status'] == 'exceeded' else 'warning',
                    'budget': status['budget'],
                    'percentage': status['percentage_used'],
                    'remaining': status['remaining'],
                    'message': self._format_alert_message(status)
                })

        return alerts

    def _format_alert_message(self, status: Dict) -> str:
        """Format alert message."""
        budget = status['budget']
        name = budget.category or 'Total'

        if status['status'] == 'exceeded':
            return f"{name} budget exceeded: {status['percentage_used']:.1f}% used"
        else:
            return f"{name} budget warning: {status['percentage_used']:.1f}% used"

    def check_expense_against_budget(self, expense) -> Optional[Dict]:
        """Check if adding expense would trigger budget alert."""
        budget = self.get_category_budget(
            expense.category,
            expense.date.month,
            expense.date.year
        )

        if not budget:
            return None

        status = self.get_budget_status(budget)
        new_spent = status['spent'] + expense.amount
        new_percentage = (new_spent / status['effective_budget'] * 100)

        if new_percentage > 100:
            return {
                'type': 'exceeded',
                'budget': budget,
                'current_spent': status['spent'],
                'expense_amount': expense.amount,
                'new_total': new_spent,
                'new_percentage': new_percentage
            }
        elif new_percentage >= budget.warning_threshold and status['status'] == 'ok':
            return {
                'type': 'warning',
                'budget': budget,
                'current_spent': status['spent'],
                'expense_amount': expense.amount,
                'new_total': new_spent,
                'new_percentage': new_percentage
            }

        return None
```

### Task 4.1.7: Implement rollover and utility methods
- [ ] Add rollover and copy methods:
```python
    def process_month_end_rollover(self, month: int, year: int) -> Dict[str, float]:
        """Calculate and apply rollover for all eligible budgets at month end."""
        rollovers = {}

        for budget in self.get_category_budgets(month, year):
            if not budget.enable_rollover:
                continue

            status = self.get_budget_status(budget)
            if status['remaining'] > 0:
                max_rollover = budget.amount * (budget.rollover_cap_percent / 100)
                rollover = min(status['remaining'], max_rollover)
                rollovers[budget.category] = rollover

        return rollovers

    def apply_rollover_to_budget(self, budget_id: str, rollover_amount: float) -> bool:
        """Apply rollover amount to a specific budget."""
        return self.update_budget(budget_id, {'rollover_amount': rollover_amount})

    def copy_budgets_from_month(
        self,
        source_month: int,
        source_year: int,
        target_month: int,
        target_year: int
    ) -> int:
        """Copy all budgets from one month to another."""
        source_budgets = [b for b in self._budgets.values()
                         if b.month == source_month and b.year == source_year]

        copied = 0
        for budget in source_budgets:
            new_budget = Budget(
                name=budget.name,
                budget_type=budget.budget_type,
                category=budget.category,
                amount=budget.amount,
                month=target_month,
                year=target_year,
                warning_threshold=budget.warning_threshold,
                enable_rollover=budget.enable_rollover,
                rollover_cap_percent=budget.rollover_cap_percent
            )
            self.add_budget(new_budget)
            copied += 1

        return copied

    def validate_category_budgets(self, month: int, year: int) -> Optional[Dict]:
        """Check if category budgets sum exceeds total budget."""
        total_budget = self.get_monthly_total_budget(month, year)
        if not total_budget:
            return None

        category_budgets = self.get_category_budgets(month, year)
        category_sum = sum(b.amount for b in category_budgets)

        if category_sum > total_budget.amount:
            return {
                'total_budget': total_budget.amount,
                'category_sum': category_sum,
                'difference': category_sum - total_budget.amount
            }

        return None
```

### Task 4.1.8: Create BudgetManager tests
- [ ] Create `tests/test_managers/test_budget_manager.py`

---

## Story 4.2: Set Monthly Budget UI

**Prerequisites:** Story 4.1

### Task 4.2.1: Create budget management view
- [ ] Create `ui/views/budget_view.py`:
  - Month/Year selector
  - Total budget display with progress bar
  - Edit budget button
  - Copy from previous month button

### Task 4.2.2: Create budget edit dialog
- [ ] Create `ui/dialogs/budget_dialog.py`:
  - Amount field
  - Warning threshold field
  - Enable rollover checkbox
  - Rollover cap percentage field
  - Effective budget display with rollover

---

## Story 4.3: Category Budgets UI

**Prerequisites:** Story 4.1, Story 4.2

### Task 4.3.1: Create category budget table
- [ ] Add to budget view:
  - Table with Category, Budget, Spent, Remaining, Status columns
  - Color-coded progress bars
  - Edit buttons per row

### Task 4.3.2: Implement quick edit
- [ ] Double-click amount to edit inline
- [ ] Enter to save, Escape to cancel

### Task 4.3.3: Implement budget validation warnings
- [ ] Warn if category sum > total budget
- [ ] Show comparison dialog

---

## Story 4.4: Budget Alerts System

**Prerequisites:** Story 4.1

### Task 4.4.1: Create alert components
- [ ] Dashboard alert panel
- [ ] Status bar alert indicator
- [ ] Startup alerts dialog

### Task 4.4.2: Implement pre-save budget check
- [ ] Check before saving expense
- [ ] Show warning dialog with Continue/Cancel

### Task 4.4.3: Create alerts settings
- [ ] Enable/disable notifications
- [ ] Warning threshold setting
- [ ] Show on startup option

---

## Story 4.5: Budget vs Actual Report

**Prerequisites:** Story 4.1, Story 5.1

### Task 4.5.1: Create budget report view
- [ ] Create `ui/reports/budget_report.py`:
  - Summary section
  - Category breakdown table
  - Historical comparison
  - Projections

### Task 4.5.2: Implement export
- [ ] Export to PDF
- [ ] Export to Excel

---

## Completion Checklist

### Story 4.1: BudgetManager
- [ ] Class created with all methods
- [ ] CRUD operations working
- [ ] Budget status calculations working
- [ ] Alerts working
- [ ] Rollover functionality working
- [ ] Copy budgets working
- [ ] Validation working
- [ ] Tests passing

### Story 4.2-4.4: UI Components
- [ ] Budget view created
- [ ] Category budget table working
- [ ] Alert components created
- [ ] Pre-save check working
- [ ] Settings working

### Story 4.5: Budget Report
- [ ] Report view created
- [ ] Export working

---

## Next Steps

After completing Epic 4, proceed to:
- **Epic 5: Reporting & Analytics** - Uses budget data for reports
