# Epic 3: Dynamic Filtering & Sorting - Implementation Tasks

**Phase:** 5 (Core Features)
**Priority:** Medium
**Dependencies:** Epic 2 (CRUD Operations)
**Estimated Tasks:** 20+

---

## Story 3.1: FilterManager Class

**Prerequisites:** Epic 2 (ExpenseManager)

### Task 3.1.1: Create FilterCriteria dataclass
- [ ] Add to `managers/filter_manager.py`:
```python
"""
FilterManager - Manages filtering and sorting of expense data.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

import pandas as pd


@dataclass
class FilterCriteria:
    """Holds all filter parameters."""
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    categories: List[str] = field(default_factory=list)
    subcategories: List[str] = field(default_factory=list)
    vendors: List[str] = field(default_factory=list)
    payment_methods: List[str] = field(default_factory=list)
    amount_min: Optional[float] = None
    amount_max: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    search_text: str = ""
    include_recurring_only: bool = False
    include_deleted: bool = False

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
            not self.search_text and
            not self.include_recurring_only and
            not self.include_deleted
        )

    def get_active_count(self) -> int:
        """Count number of active filters."""
        count = 0
        if self.date_from or self.date_to:
            count += 1
        if self.categories:
            count += 1
        if self.subcategories:
            count += 1
        if self.vendors:
            count += 1
        if self.payment_methods:
            count += 1
        if self.amount_min is not None or self.amount_max is not None:
            count += 1
        if self.tags:
            count += 1
        if self.search_text:
            count += 1
        if self.include_recurring_only:
            count += 1
        return count

    def clear(self) -> None:
        """Reset all filters."""
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
        self.include_recurring_only = False
        self.include_deleted = False
```

### Task 3.1.2: Create FilterManager class
- [ ] Add FilterManager class:
```python
class FilterManager:
    """Manages filtering and sorting of expense data."""

    # Quick filter date ranges
    QUICK_FILTERS = {
        'today': lambda: (datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
                         datetime.now()),
        'this_week': lambda: (datetime.now() - timedelta(days=datetime.now().weekday()),
                             datetime.now()),
        'this_month': lambda: (datetime.now().replace(day=1), datetime.now()),
        'this_quarter': lambda: FilterManager._get_quarter_dates(),
        'this_year': lambda: (datetime.now().replace(month=1, day=1), datetime.now()),
        'last_month': lambda: FilterManager._get_last_month_dates(),
        'last_30_days': lambda: (datetime.now() - timedelta(days=30), datetime.now()),
    }

    # Amount presets
    AMOUNT_PRESETS = {
        'under_5k': (0, 5000),
        '5k_to_20k': (5000, 20000),
        '20k_to_50k': (20000, 50000),
        'over_50k': (50000, None),
    }

    def __init__(self):
        """Initialize with empty FilterCriteria."""
        self.current_criteria = FilterCriteria()

    @staticmethod
    def _get_quarter_dates():
        now = datetime.now()
        quarter = (now.month - 1) // 3
        start_month = quarter * 3 + 1
        return (now.replace(month=start_month, day=1), now)

    @staticmethod
    def _get_last_month_dates():
        now = datetime.now()
        if now.month == 1:
            start = now.replace(year=now.year - 1, month=12, day=1)
        else:
            start = now.replace(month=now.month - 1, day=1)
        end = now.replace(day=1) - timedelta(days=1)
        return (start, end.replace(hour=23, minute=59, second=59))
```

### Task 3.1.3: Implement filter methods
- [ ] Add filter methods:
```python
    def apply_filter(
        self,
        df: pd.DataFrame,
        criteria: FilterCriteria = None
    ) -> pd.DataFrame:
        """Apply all filter criteria to DataFrame."""
        if criteria is None:
            criteria = self.current_criteria

        if df.empty:
            return df

        result = df.copy()

        # Apply each filter
        if criteria.date_from:
            result = self.filter_by_date_from(result, criteria.date_from)
        if criteria.date_to:
            result = self.filter_by_date_to(result, criteria.date_to)
        if criteria.categories:
            result = self.filter_by_categories(result, criteria.categories)
        if criteria.subcategories:
            result = self.filter_by_subcategories(result, criteria.subcategories)
        if criteria.vendors:
            result = self.filter_by_vendors(result, criteria.vendors)
        if criteria.payment_methods:
            result = self.filter_by_payment_methods(result, criteria.payment_methods)
        if criteria.amount_min is not None or criteria.amount_max is not None:
            result = self.filter_by_amount_range(
                result, criteria.amount_min, criteria.amount_max
            )
        if criteria.tags:
            result = self.filter_by_tags(result, criteria.tags)
        if criteria.search_text:
            result = self.search(result, criteria.search_text)
        if criteria.include_recurring_only:
            result = result[result['is_recurring'] == True]
        if not criteria.include_deleted:
            result = result[result['is_deleted'] != True]

        return result

    def filter_by_date_from(self, df: pd.DataFrame, date_from: datetime) -> pd.DataFrame:
        """Filter expenses on or after date."""
        df['date'] = pd.to_datetime(df['date'])
        return df[df['date'] >= date_from]

    def filter_by_date_to(self, df: pd.DataFrame, date_to: datetime) -> pd.DataFrame:
        """Filter expenses on or before date."""
        df['date'] = pd.to_datetime(df['date'])
        return df[df['date'] <= date_to]

    def filter_by_categories(self, df: pd.DataFrame, categories: List[str]) -> pd.DataFrame:
        """Filter by list of categories."""
        return df[df['category'].isin(categories)]

    def filter_by_subcategories(self, df: pd.DataFrame, subcategories: List[str]) -> pd.DataFrame:
        """Filter by list of subcategories."""
        return df[df['subcategory'].isin(subcategories)]

    def filter_by_vendors(self, df: pd.DataFrame, vendors: List[str]) -> pd.DataFrame:
        """Filter by list of vendors."""
        return df[df['vendor'].isin(vendors)]

    def filter_by_payment_methods(self, df: pd.DataFrame, methods: List[str]) -> pd.DataFrame:
        """Filter by payment methods."""
        return df[df['payment_method'].isin(methods)]

    def filter_by_amount_range(
        self,
        df: pd.DataFrame,
        min_amount: Optional[float],
        max_amount: Optional[float]
    ) -> pd.DataFrame:
        """Filter by amount range."""
        result = df
        if min_amount is not None:
            result = result[result['amount'] >= min_amount]
        if max_amount is not None:
            result = result[result['amount'] <= max_amount]
        return result

    def filter_by_tags(self, df: pd.DataFrame, tags: List[str]) -> pd.DataFrame:
        """Filter expenses containing any of the specified tags."""
        def has_tag(expense_tags):
            if pd.isna(expense_tags):
                return False
            expense_tag_list = [t.strip() for t in str(expense_tags).split(',')]
            return any(tag in expense_tag_list for tag in tags)
        return df[df['tags'].apply(has_tag)]

    def search(self, df: pd.DataFrame, search_text: str) -> pd.DataFrame:
        """Search in vendor, description, and tags."""
        search_lower = search_text.lower()
        mask = (
            df['vendor'].str.lower().str.contains(search_lower, na=False) |
            df['description'].str.lower().str.contains(search_lower, na=False) |
            df['tags'].str.lower().str.contains(search_lower, na=False)
        )
        return df[mask]
```

### Task 3.1.4: Implement quick filters and presets
- [ ] Add quick filter and preset methods:
```python
    def get_quick_filter(self, filter_name: str) -> FilterCriteria:
        """Get predefined filter (today, this_week, this_month, etc.)."""
        criteria = FilterCriteria()
        if filter_name in self.QUICK_FILTERS:
            date_from, date_to = self.QUICK_FILTERS[filter_name]()
            criteria.date_from = date_from
            criteria.date_to = date_to
        return criteria

    def get_amount_preset(self, preset_name: str) -> Tuple[Optional[float], Optional[float]]:
        """Get predefined amount ranges."""
        return self.AMOUNT_PRESETS.get(preset_name, (None, None))
```

### Task 3.1.5: Implement sorting methods
- [ ] Add sorting functionality:
```python
    def sort_dataframe(
        self,
        df: pd.DataFrame,
        column: str,
        ascending: bool = True
    ) -> pd.DataFrame:
        """Sort DataFrame by single column."""
        if column not in df.columns:
            return df
        return df.sort_values(by=column, ascending=ascending)

    def multi_sort(
        self,
        df: pd.DataFrame,
        sort_columns: List[Tuple[str, bool]]
    ) -> pd.DataFrame:
        """Sort by multiple columns."""
        if not sort_columns:
            return df

        columns = [col for col, _ in sort_columns]
        ascending = [asc for _, asc in sort_columns]

        return df.sort_values(by=columns, ascending=ascending)

    def get_default_sort(self) -> List[Tuple[str, bool]]:
        """Get default sort order (newest first)."""
        return [('date', False)]
```

### Task 3.1.6: Create FilterManager tests
- [ ] Create `tests/test_managers/test_filter_manager.py`

---

## Story 3.2: Filter Panel UI

**Prerequisites:** Story 3.1, Story 2.3

### Task 3.2.1: Create filter panel component
- [ ] Create `ui/components/filter_panel.py`:
  - Collapsible panel
  - Quick filter buttons
  - Date range filter
  - Category checkboxes
  - Amount range inputs
  - Vendor search
  - Payment method checkboxes
  - Special filters (recurring, deleted)

### Task 3.2.2: Implement active filter indicators
- [ ] Show chips below search for active filters
- [ ] Click X to remove individual filter

### Task 3.2.3: Integrate with expense list
- [ ] Update list on filter change
- [ ] Preserve filter state when switching views
- [ ] Debounce search (300ms)

---

## Story 3.3: Column Sorting

**Prerequisites:** Story 2.3

### Task 3.3.1: Implement column header sorting
- [ ] Click header: sort ascending
- [ ] Click again: sort descending
- [ ] Click third time: remove sort
- [ ] Visual indicator (triangle up/down)

### Task 3.3.2: Implement multi-column sort
- [ ] Shift+Click to add secondary sort
- [ ] Show priority indicators
- [ ] Maximum 3 sort columns

### Task 3.3.3: Add sort persistence
- [ ] Remember sort order during session
- [ ] Default to date descending

---

## Completion Checklist

### Story 3.1: FilterManager
- [ ] FilterCriteria dataclass created
- [ ] FilterManager class created
- [ ] All filter methods working
- [ ] Quick filters working
- [ ] Amount presets working
- [ ] Sorting methods working
- [ ] Tests passing

### Story 3.2: Filter Panel UI
- [ ] Filter panel component created
- [ ] All filter controls working
- [ ] Active filter indicators working
- [ ] Integration with expense list working

### Story 3.3: Column Sorting
- [ ] Single column sort working
- [ ] Multi-column sort working
- [ ] Visual indicators working
- [ ] Sort persistence working

---

## Next Steps

After completing Epic 3, proceed to:
- **Epic 4: Budget Management** - Uses filtering for budget calculations
