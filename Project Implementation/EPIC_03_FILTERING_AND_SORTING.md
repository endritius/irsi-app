# Epic 3: Dynamic Filtering & Sorting

**Priority:** Medium
**Dependencies:** Epic 2 (CRUD Operations)
**Stories:** 3

---

## Story 3.1: FilterManager Class

**As a** developer
**I want** a FilterManager for filtering logic
**So that** filtering is reusable

### Acceptance Criteria

- [ ] Create `managers/filter_manager.py`:

  **FilterCriteria Dataclass:**
  ```python
  @dataclass
  class FilterCriteria:
      """Holds all filter parameters"""
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

      def is_empty(self) -> bool
          """Check if no filters are applied"""

      def get_active_count(self) -> int
          """Count number of active filters"""

      def clear(self) -> None
          """Reset all filters"""
  ```

  **FilterManager Methods:**
  ```python
  class FilterManager:
      """Manages filtering and sorting of expense data"""

      def __init__(self)
          """Initialize with empty FilterCriteria"""

      def apply_filter(self, df: pd.DataFrame, criteria: FilterCriteria = None) -> pd.DataFrame
          """Apply all filter criteria to DataFrame"""

      def filter_by_date_from(self, df: pd.DataFrame, date_from: datetime) -> pd.DataFrame
          """Filter expenses on or after date"""

      def filter_by_date_to(self, df: pd.DataFrame, date_to: datetime) -> pd.DataFrame
          """Filter expenses on or before date"""

      def filter_by_categories(self, df: pd.DataFrame, categories: List[str]) -> pd.DataFrame
          """Filter by list of categories"""

      def filter_by_subcategories(self, df: pd.DataFrame, subcategories: List[str]) -> pd.DataFrame
          """Filter by list of subcategories"""

      def filter_by_vendors(self, df: pd.DataFrame, vendors: List[str]) -> pd.DataFrame
          """Filter by list of vendors"""

      def filter_by_payment_methods(self, df: pd.DataFrame, methods: List[str]) -> pd.DataFrame
          """Filter by payment methods"""

      def filter_by_tags(self, df: pd.DataFrame, tags: List[str]) -> pd.DataFrame
          """Filter expenses containing any of the specified tags"""

      def search(self, df: pd.DataFrame, search_text: str) -> pd.DataFrame
          """Search in vendor, description, and tags"""

      def get_quick_filter(self, filter_name: str) -> FilterCriteria
          """Get predefined filter (today, this_week, this_month, etc.)"""

      def get_amount_preset(self, preset_name: str) -> Tuple[Optional[float], Optional[float]]
          """Get predefined amount ranges (under_5k, 5k_to_20k, etc.)"""

      def sort_dataframe(self, df: pd.DataFrame, column: str, ascending: bool = True) -> pd.DataFrame
          """Sort DataFrame by single column"""

      def multi_sort(self, df: pd.DataFrame, sort_columns: List[Tuple[str, bool]]) -> pd.DataFrame
          """Sort by multiple columns"""

      def get_default_sort(self) -> List[Tuple[str, bool]]
          """Get default sort order (newest first)"""
  ```

### Quick Filters
| Filter Name | Date Range |
|-------------|------------|
| today | Today only |
| this_week | Monday to now |
| this_month | 1st of month to now |
| this_quarter | Start of quarter to now |
| this_year | Jan 1st to now |
| last_month | Previous full month |
| last_30_days | Past 30 days |

### Amount Presets
| Preset | Range |
|--------|-------|
| under_5k | 0 - 5,000 L |
| 5k_to_20k | 5,000 - 20,000 L |
| 20k_to_50k | 20,000 - 50,000 L |
| over_50k | 50,000+ L |

### Technical Notes
- FilterCriteria is a dataclass for easy serialization
- All filter methods work with DataFrame
- Quick filters provide common date ranges
- Sorting handles different data types correctly

---

## Story 3.2: Filter Panel UI

**As a** user
**I want** a filter panel to find expenses
**So that** I can narrow down my search

### Acceptance Criteria

- [ ] Create `ui/filter_panel.py` with collapsible panel:

  **Quick Filter Buttons:**
  - [Today] [This Week] [This Month] [This Quarter] [This Year]
  - Click applies immediately, active highlighted
  - Click active button to deselect

  **Date Range Filter:**
  - From/To DateEntry widgets
  - "Last 30 days" quick option

  **Category Filter:**
  - Checkboxes with expense count per category
  - Color indicators matching category colors
  - [Select All] / [Clear All] buttons

  **Subcategory Filter:**
  - Expandable tree view
  - Appears when category expanded
  - Shows selection count

  **Amount Range Filter:**
  - Min/Max entry fields
  - Preset buttons: [<5kL] [5-20kL] [20-50kL] [>50kL]

  **Vendor Filter:**
  - Searchable dropdown
  - Multi-select capability

  **Payment Method Filter:**
  - Checkboxes for each method

  **Text Search:**
  - Search box with icon
  - Real-time filtering (debounced 300ms)
  - Clear button (X)

  **Special Filters:**
  - [ ] Recurring expenses only
  - [ ] Show deleted items

- [ ] **Filter Panel Header:**
  - Collapsible (expand/collapse)
  - Shows active count: "Filters (3 active)"
  - [Clear All] button

- [ ] **Active Filter Indicators:**
  - Show chips below search: [Date: 01/01-31/01 X] [Category: Supplies X]
  - Click X to remove individual filter

### Wireframe: Filter Panel

```
+-------------------------------------------------------------------------------------+
| Filters (3 active)                                               [Clear All] [^]    |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Quick Filters:  [Today] [This Week] [This Month] [This Quarter] [This Year]        |
|                                                                                      |
|  +---------------------------------+  +---------------------------------+           |
|  | Date Range                      |  | Categories                      |           |
|  |                                 |  |                                 |           |
|  | From: [01/01/2024] [C]          |  | [x] Supplies    [x] Equipment   |           |
|  | To:   [31/01/2024] [C]          |  | [ ] Facilities  [ ] Staff       |           |
|  |                                 |  | [x] Marketing   [ ] Admin       |           |
|  +---------------------------------+  +---------------------------------+           |
|                                                                                      |
|  +---------------------------------+  +---------------------------------+           |
|  | Amount Range                    |  | Payment Method                  |           |
|  |                                 |  |                                 |           |
|  | Min: [________] Max: [________] |  | [x] Cash        [x] Debit Card  |           |
|  |                                 |  | [x] Credit Card [ ] Bank Trans. |           |
|  | [<5kL] [5-20kL] [20-50kL] [>50kL]|  |                                 |           |
|  +---------------------------------+  +---------------------------------+           |
|                                                                                      |
|  +---------------------------------+  +---------------------------------+           |
|  | Vendor                          |  | Other Options                   |           |
|  |                                 |  |                                 |           |
|  | [Search vendor..._________]     |  | [ ] Recurring expenses only     |           |
|  |                                 |  | [ ] Show deleted items          |           |
|  +---------------------------------+  +---------------------------------+           |
|                                                                                      |
|                                                    [Reset]    [Apply Filters]        |
+-------------------------------------------------------------------------------------+
```

### Wireframe: Category/Subcategory Tree

```
+-------------------------------------------------------------------------------------+
| Categories & Subcategories                                                           |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  v [x] Supplies                                                                      |
|      [x] Hair products                                                               |
|      [x] Nail products                                                               |
|      [ ] Skincare products                                                           |
|      [x] Disposables                                                                 |
|      [ ] Cleaning supplies                                                           |
|                                                                                      |
|  > [ ] Equipment                                                                     |
|                                                                                      |
|  > [x] Facilities (all selected)                                                     |
|                                                                                      |
|  > [ ] Staff                                                                         |
|                                                                                      |
|  > [x] Marketing (2 of 4 selected)                                                   |
|                                                                                      |
|  > [ ] Administrative                                                                |
|                                                                                      |
|  [Select All]  [Clear All]                                                           |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Wireframe: Active Filter Indicators

```
+-------------------------------------------------------------------------------------+
|                                    Expenses                                          |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Active Filters: [Date: 01/01 - 31/01 x] [Category: Supplies x] [Amount: >5000 x]   |
|                                                                                      |
|  Showing 25 of 100 expenses                                [Clear All Filters]       |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Technical Notes
- Use debouncing for search (300ms delay)
- Update expense list on filter change
- Preserve filter state when switching views

---

## Story 3.3: Column Sorting

**As a** user
**I want** to sort expenses by clicking columns
**So that** I can organize my view

### Acceptance Criteria

- [ ] **Single Column Sort:**
  - Click header: sort ascending
  - Click again: sort descending
  - Click third time: remove sort (default)
  - Visual indicator: Triangle-Up (asc) or Triangle-Down (desc)

- [ ] **Sortable Columns:**
  | Column | Default | Notes |
  |--------|---------|-------|
  | Date | Descending | Newest first |
  | Category | - | Alphabetical |
  | Vendor | - | Alphabetical |
  | Amount | - | Numeric |
  | Payment Method | - | Alphabetical |

- [ ] **Multi-Column Sort:**
  - Shift+Click to add secondary sort
  - Show priority: Date v1, Amount ^2
  - Maximum 3 sort columns
  - Right-click header > "Reset Sort"

- [ ] **Visual Feedback:**
  - Header highlight on hover
  - Cursor change to indicate sortable

- [ ] **Sort Persistence:**
  - Remember sort order during session
  - Default: Date descending

### Wireframe: Sort Options Dropdown

```
+-----------------------------+
| Sort by:                    |
+-----------------------------+
| o Date (Newest first)       |
| o Date (Oldest first)       |
| o Amount (Highest first)    |
| o Amount (Lowest first)     |
| o Category (A-Z)            |
| o Category (Z-A)            |
| o Vendor (A-Z)              |
| o Vendor (Z-A)              |
+-----------------------------+
```

### Technical Notes
- Treeview column header binding
- Store sort state in view component
- Update FilterManager with sort criteria

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 3.1 | 2.1 |
| 3.2 | 3.1, 2.3 |
| 3.3 | 2.3 |

---

## Testing Requirements

- [ ] Unit tests for FilterManager (all filter methods)
- [ ] Unit tests for quick filters (date calculations)
- [ ] Unit tests for sort functionality
- [ ] Integration tests for filter + sort combination
- [ ] Performance tests with large datasets
- [ ] UI tests for filter panel interactions
