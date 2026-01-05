"""
FilterManager - Manages filtering and sorting of expense data.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Optional
import pandas as pd
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from models.filter_criteria import FilterCriteria
from utils.error_handler import log_info


class FilterManager:
    """
    Manages filtering and sorting of expense data.
    Works with pandas DataFrames for efficient filtering.
    """

    def __init__(self):
        """Initialize FilterManager."""
        self.current_criteria = FilterCriteria()
        self._sort_columns: List[Tuple[str, bool]] = [('date', False)]  # Default: date descending

    def apply_filter(
        self,
        df: pd.DataFrame,
        criteria: FilterCriteria = None
    ) -> pd.DataFrame:
        """
        Apply all filter criteria to DataFrame.

        Args:
            df: DataFrame to filter
            criteria: FilterCriteria to apply (uses current if None)

        Returns:
            Filtered DataFrame
        """
        if criteria is None:
            criteria = self.current_criteria

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

        if criteria.amount_min is not None:
            result = self.filter_by_amount_min(result, criteria.amount_min)

        if criteria.amount_max is not None:
            result = self.filter_by_amount_max(result, criteria.amount_max)

        if criteria.tags:
            result = self.filter_by_tags(result, criteria.tags)

        if criteria.search_text:
            result = self.search(result, criteria.search_text)

        if criteria.include_recurring_only:
            result = self.filter_recurring_only(result)

        if not criteria.include_deleted:
            result = self.filter_exclude_deleted(result)

        return result

    def filter_by_date_from(self, df: pd.DataFrame, date_from: datetime) -> pd.DataFrame:
        """Filter expenses on or after date."""
        if df.empty:
            return df

        # Ensure date column is datetime
        df = self._ensure_datetime_column(df, 'date')
        date_from_date = date_from.date() if isinstance(date_from, datetime) else date_from
        return df[df['date'].dt.date >= date_from_date]

    def filter_by_date_to(self, df: pd.DataFrame, date_to: datetime) -> pd.DataFrame:
        """Filter expenses on or before date."""
        if df.empty:
            return df

        df = self._ensure_datetime_column(df, 'date')
        date_to_date = date_to.date() if isinstance(date_to, datetime) else date_to
        return df[df['date'].dt.date <= date_to_date]

    def filter_by_categories(self, df: pd.DataFrame, categories: List[str]) -> pd.DataFrame:
        """Filter by list of categories."""
        if df.empty or not categories:
            return df
        return df[df['category'].isin(categories)]

    def filter_by_subcategories(self, df: pd.DataFrame, subcategories: List[str]) -> pd.DataFrame:
        """Filter by list of subcategories."""
        if df.empty or not subcategories:
            return df
        return df[df['subcategory'].isin(subcategories)]

    def filter_by_vendors(self, df: pd.DataFrame, vendors: List[str]) -> pd.DataFrame:
        """Filter by list of vendors."""
        if df.empty or not vendors:
            return df
        vendors_lower = [v.lower() for v in vendors]
        return df[df['vendor'].str.lower().isin(vendors_lower)]

    def filter_by_payment_methods(self, df: pd.DataFrame, methods: List[str]) -> pd.DataFrame:
        """Filter by payment methods."""
        if df.empty or not methods:
            return df
        return df[df['payment_method'].isin(methods)]

    def filter_by_amount_min(self, df: pd.DataFrame, amount_min: float) -> pd.DataFrame:
        """Filter by minimum amount."""
        if df.empty:
            return df
        df = self._ensure_numeric_column(df, 'amount')
        return df[df['amount'] >= amount_min]

    def filter_by_amount_max(self, df: pd.DataFrame, amount_max: float) -> pd.DataFrame:
        """Filter by maximum amount."""
        if df.empty:
            return df
        df = self._ensure_numeric_column(df, 'amount')
        return df[df['amount'] <= amount_max]

    def filter_by_tags(self, df: pd.DataFrame, tags: List[str]) -> pd.DataFrame:
        """Filter expenses containing any of the specified tags."""
        if df.empty or not tags:
            return df

        tags_lower = [t.lower() for t in tags]

        def has_any_tag(row_tags):
            if not row_tags:
                return False
            # Handle both string and list
            if isinstance(row_tags, str):
                row_tag_list = [t.strip().lower() for t in row_tags.split(',')]
            else:
                row_tag_list = [t.lower() for t in row_tags]
            return any(tag in row_tag_list for tag in tags_lower)

        return df[df['tags'].apply(has_any_tag)]

    def search(self, df: pd.DataFrame, search_text: str) -> pd.DataFrame:
        """Search in vendor, description, and tags."""
        if df.empty or not search_text:
            return df

        search_lower = search_text.lower()

        def matches_search(row):
            vendor = str(row.get('vendor', '')).lower()
            description = str(row.get('description', '')).lower()
            tags = str(row.get('tags', '')).lower()

            return (search_lower in vendor or
                    search_lower in description or
                    search_lower in tags)

        mask = df.apply(matches_search, axis=1)
        return df[mask]

    def filter_recurring_only(self, df: pd.DataFrame) -> pd.DataFrame:
        """Filter to show only recurring expenses."""
        if df.empty:
            return df

        def is_recurring(val):
            if isinstance(val, bool):
                return val
            return str(val).lower() in ('true', '1', 'yes')

        return df[df['is_recurring'].apply(is_recurring)]

    def filter_exclude_deleted(self, df: pd.DataFrame) -> pd.DataFrame:
        """Exclude soft-deleted expenses."""
        if df.empty:
            return df

        def is_deleted(val):
            if isinstance(val, bool):
                return val
            return str(val).lower() in ('true', '1', 'yes')

        return df[~df['is_deleted'].apply(is_deleted)]

    # ===== QUICK FILTERS =====

    def get_quick_filter(self, filter_name: str) -> FilterCriteria:
        """
        Get predefined filter criteria.

        Args:
            filter_name: Name of quick filter

        Returns:
            FilterCriteria with appropriate date range
        """
        today = datetime.now()
        criteria = FilterCriteria()

        if filter_name == 'today':
            criteria.date_from = today.replace(hour=0, minute=0, second=0, microsecond=0)
            criteria.date_to = today

        elif filter_name == 'this_week':
            # Start from Monday
            days_since_monday = today.weekday()
            start = today - timedelta(days=days_since_monday)
            criteria.date_from = start.replace(hour=0, minute=0, second=0, microsecond=0)
            criteria.date_to = today

        elif filter_name == 'this_month':
            criteria.date_from = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            criteria.date_to = today

        elif filter_name == 'this_quarter':
            quarter = (today.month - 1) // 3
            start_month = quarter * 3 + 1
            criteria.date_from = today.replace(month=start_month, day=1, hour=0, minute=0, second=0, microsecond=0)
            criteria.date_to = today

        elif filter_name == 'this_year':
            criteria.date_from = today.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            criteria.date_to = today

        elif filter_name == 'last_month':
            first_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_prev_month = first_this_month - timedelta(days=1)
            first_prev_month = last_prev_month.replace(day=1)
            criteria.date_from = first_prev_month
            criteria.date_to = last_prev_month.replace(hour=23, minute=59, second=59)

        elif filter_name == 'last_30_days':
            criteria.date_from = today - timedelta(days=30)
            criteria.date_to = today

        elif filter_name == 'last_7_days':
            criteria.date_from = today - timedelta(days=7)
            criteria.date_to = today

        return criteria

    def get_amount_preset(self, preset_name: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Get predefined amount ranges.

        Args:
            preset_name: Name of amount preset

        Returns:
            Tuple of (min_amount, max_amount)
        """
        presets = {
            'under_5k': (None, 5000),
            '5k_to_20k': (5000, 20000),
            '20k_to_50k': (20000, 50000),
            'over_50k': (50000, None),
            'under_1k': (None, 1000),
            '1k_to_5k': (1000, 5000),
        }
        return presets.get(preset_name, (None, None))

    # ===== SORTING =====

    def sort_dataframe(
        self,
        df: pd.DataFrame,
        column: str,
        ascending: bool = True
    ) -> pd.DataFrame:
        """
        Sort DataFrame by single column.

        Args:
            df: DataFrame to sort
            column: Column name to sort by
            ascending: Sort direction

        Returns:
            Sorted DataFrame
        """
        if df.empty or column not in df.columns:
            return df

        # Ensure proper data types for sorting
        if column == 'date':
            df = self._ensure_datetime_column(df, column)
        elif column == 'amount':
            df = self._ensure_numeric_column(df, column)

        return df.sort_values(by=column, ascending=ascending)

    def multi_sort(
        self,
        df: pd.DataFrame,
        sort_columns: List[Tuple[str, bool]]
    ) -> pd.DataFrame:
        """
        Sort by multiple columns.

        Args:
            df: DataFrame to sort
            sort_columns: List of (column_name, ascending) tuples

        Returns:
            Sorted DataFrame
        """
        if df.empty or not sort_columns:
            return df

        columns = [col for col, _ in sort_columns if col in df.columns]
        ascending_list = [asc for col, asc in sort_columns if col in df.columns]

        if not columns:
            return df

        # Ensure proper data types
        if 'date' in columns:
            df = self._ensure_datetime_column(df, 'date')
        if 'amount' in columns:
            df = self._ensure_numeric_column(df, 'amount')

        return df.sort_values(by=columns, ascending=ascending_list)

    def get_default_sort(self) -> List[Tuple[str, bool]]:
        """Get default sort order (newest first)."""
        return [('date', False)]

    def set_sort(self, column: str, ascending: bool) -> None:
        """Set current sort column."""
        self._sort_columns = [(column, ascending)]

    def add_sort(self, column: str, ascending: bool, max_sorts: int = 3) -> None:
        """Add secondary sort column."""
        # Remove if already exists
        self._sort_columns = [(c, a) for c, a in self._sort_columns if c != column]
        # Add new sort
        self._sort_columns.append((column, ascending))
        # Limit number of sort columns
        if len(self._sort_columns) > max_sorts:
            self._sort_columns = self._sort_columns[-max_sorts:]

    def clear_sort(self) -> None:
        """Reset to default sort."""
        self._sort_columns = self.get_default_sort()

    # ===== HELPER METHODS =====

    def _ensure_datetime_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Ensure column is datetime type."""
        if column not in df.columns:
            return df
        if df[column].dtype != 'datetime64[ns]':
            df = df.copy()
            df[column] = pd.to_datetime(df[column], errors='coerce')
        return df

    def _ensure_numeric_column(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """Ensure column is numeric type."""
        if column not in df.columns:
            return df
        if not pd.api.types.is_numeric_dtype(df[column]):
            df = df.copy()
            df[column] = pd.to_numeric(df[column], errors='coerce')
        return df

    def set_criteria(self, criteria: FilterCriteria) -> None:
        """Set current filter criteria."""
        self.current_criteria = criteria

    def clear_criteria(self) -> None:
        """Clear current filter criteria."""
        self.current_criteria = FilterCriteria()

    def get_active_filter_count(self) -> int:
        """Get number of active filters."""
        count = 0
        c = self.current_criteria

        if c.date_from or c.date_to:
            count += 1
        if c.categories:
            count += 1
        if c.subcategories:
            count += 1
        if c.vendors:
            count += 1
        if c.payment_methods:
            count += 1
        if c.amount_min is not None or c.amount_max is not None:
            count += 1
        if c.tags:
            count += 1
        if c.search_text:
            count += 1
        if c.include_recurring_only:
            count += 1

        return count


# Singleton instance
_filter_manager: Optional[FilterManager] = None


def get_filter_manager() -> FilterManager:
    """Get or create global FilterManager instance."""
    global _filter_manager
    if _filter_manager is None:
        _filter_manager = FilterManager()
    return _filter_manager
