# Epic 6: Visual Analytics & Dashboards

**Priority:** Medium-Low
**Dependencies:** Epic 5 (Reporting)
**Stories:** 5

---

## Story 6.1: Visualizer Class

**As a** developer
**I want** a Visualizer class for charts
**So that** chart generation is centralized

### Acceptance Criteria

- [ ] Create `visualization/visualizer.py`:

  **Class Constants:**
  ```python
  # Category colors (matches Story 1.3 definitions)
  CATEGORY_COLORS = {
      'Supplies': '#FF6B9D',       # Pink
      'Equipment': '#9B59B6',      # Purple
      'Facilities': '#3498DB',     # Blue
      'Staff': '#2ECC71',          # Green
      'Marketing': '#F39C12',      # Orange
      'Administrative': '#95A5A6', # Gray
  }

  # Fallback palette for additional categories or subcategories
  SALON_PALETTE = [
      '#E91E63',  # Pink
      '#9C27B0',  # Purple
      '#3F51B5',  # Indigo
      '#00BCD4',  # Cyan
      '#4CAF50',  # Green
      '#FF9800',  # Orange
      '#795548',  # Brown
      '#607D8B',  # Blue Grey
  ]

  # Status colors for budget indicators
  STATUS_COLORS = {
      'ok': '#4CAF50',      # Green
      'warning': '#FF9800',  # Orange
      'exceeded': '#F44336'  # Red
  }
  ```

  **Methods:**
  ```python
  class Visualizer:
      """Generates charts and visualizations for expense data"""

      def __init__(self)
          """Initialize with default settings, set seaborn style"""

      def create_category_pie_chart(self, data: pd.DataFrame, figsize: Tuple = None,
                                    title: str = "Expenses by Category") -> Figure
          """Create pie chart of expenses by category"""

      def create_category_bar_chart(self, data: pd.DataFrame, figsize: Tuple = None,
                                    title: str = "Expenses by Category",
                                    horizontal: bool = True) -> Figure
          """Create bar chart of expenses by category"""

      def create_monthly_trend_line(self, data: pd.DataFrame, figsize: Tuple = None,
                                    title: str = "Monthly Expense Trend") -> Figure
          """Create line chart of monthly expenses"""

      def create_yearly_trend_line(self, data: pd.DataFrame, figsize: Tuple = None,
                                   title: str = "Yearly Expense Trend") -> Figure
          """Create line chart of yearly expenses"""

      def create_budget_vs_actual_bar(self, budget_data: List[Dict], figsize: Tuple = None,
                                      title: str = "Budget vs Actual") -> Figure
          """Create grouped bar chart comparing budget vs actual spending"""

      def create_vendor_bar_chart(self, data: pd.DataFrame, top_n: int = 10,
                                  figsize: Tuple = None, title: str = "Top Vendors") -> Figure
          """Create horizontal bar chart of top vendors"""

      def create_payment_method_pie(self, data: pd.DataFrame, figsize: Tuple = None,
                                    title: str = "Expenses by Payment Method") -> Figure
          """Create pie chart of expenses by payment method"""

      def create_cumulative_area_chart(self, data: pd.DataFrame, figsize: Tuple = None,
                                       title: str = "Cumulative Spending") -> Figure
          """Create area chart of cumulative spending over time"""

      def create_budget_progress_gauge(self, percentage: float, figsize: Tuple = None,
                                       title: str = "Budget Usage") -> Figure
          """Create gauge/donut chart showing budget progress"""

      def embed_in_tkinter(self, figure: Figure, parent: tk.Widget) -> FigureCanvasTkAgg
          """Embed a matplotlib figure in a Tkinter widget"""

      def update_embedded_chart(self, canvas: FigureCanvasTkAgg, new_figure: Figure) -> None
          """Update an embedded chart with new data"""

      def save_chart(self, figure: Figure, filepath: str, dpi: int = 150) -> None
          """Save a chart as an image file (PNG, JPG, etc.)"""

      def close_figure(self, figure: Figure) -> None
          """Close a figure to free memory"""
  ```

### Technical Notes
- Uses Matplotlib for chart generation
- Uses Seaborn for styling and color palettes
- Colors match category colors from CategoryManager
- Status colors: green (ok), orange (warning), red (exceeded)
- All charts handle empty data gracefully
- FigureCanvasTkAgg for Tkinter embedding

---

## Story 6.2: Dashboard View

**As a** user
**I want** a dashboard with key metrics
**So that** I get a quick overview

### Acceptance Criteria

- [ ] Create `ui/dashboard/dashboard_view.py`:

  **KPI Cards Row:**
  - Total Spent (with % change from last month)
  - Budget Usage (with progress bar)
  - Top Category (with amount)
  - Transaction Count
  - Average Expense
  - Recurring Due Count

  **Charts Grid (2x2):**
  - Category Distribution (Pie Chart)
  - Monthly Trend (Line Chart)
  - Budget vs Actual (Bar Chart)
  - Top Vendors (Horizontal Bars)

  **Alerts Section:**
  - Show active budget alerts
  - Color-coded by severity
  - Link to view all alerts
  - Click alert to view budget details

  **Controls:**
  - Month/Period selector
  - Previous/Next navigation
  - Refresh button

  **Quick Actions:**
  - [+ Add Expense]
  - [View Reports]
  - [Manage Budgets]
  - [Trend Analysis]

### Wireframe

```
+-------------------------------------------------------------------------------------+
|                              Dashboard - January 2024                               |
|                                                                    [< Prev] [Next >]|
+-------------------------------------------------------------------------------------+
|                                                                                     |
|  +---------------------+  +---------------------+  +---------------------+          |
|  |     L 296,500       |  |        79%          |  |      Supplies       |          |
|  |   Total Expenses    |  |   Budget Used       |  |   Top Category      |          |
|  |   +12% vs last mo   |  |   [========..] OK   |  |   L 85,000 (29%)    |          |
|  +---------------------+  +---------------------+  +---------------------+          |
|                                                                                     |
|  +---------------------+  +---------------------+  +---------------------+          |
|  |        100          |  |      L 2,965        |  |     4 Recurring     |          |
|  |   Transactions      |  |   Average Expense   |  |   Due This Month    |          |
|  +---------------------+  +---------------------+  +---------------------+          |
|                                                                                     |
+-------------------------------------------------------------------------------------+
|                                                                                     |
|  +-----------------------------------+  +-----------------------------------+       |
|  |     Expenses by Category          |  |        Monthly Trend              |       |
|  |                                   |  |                                   |       |
|  |          [PIE CHART]              |  |         [LINE CHART]              |       |
|  |                                   |  |                                   |       |
|  +-----------------------------------+  +-----------------------------------+       |
|                                                                                     |
|  +-----------------------------------+  +-----------------------------------+       |
|  |      Budget vs Actual             |  |        Top 5 Vendors              |       |
|  |                                   |  |                                   |       |
|  |     [HORIZONTAL BARS]             |  |       [HORIZONTAL BARS]           |       |
|  |                                   |  |                                   |       |
|  +-----------------------------------+  +-----------------------------------+       |
|                                                                                     |
+-------------------------------------------------------------------------------------+
| Alerts                                                               [View All]     |
+-------------------------------------------------------------------------------------+
| [Y] Equipment budget at 102% - exceeded by L 400                                    |
| [R] Facilities budget at 100% - limit reached                                       |
| [B] Recurring expense due: Monthly rent (L 80,000)                                  |
+-------------------------------------------------------------------------------------+
```

### Technical Notes
- Use ttk.Frame with grid layout
- Embed Matplotlib figures with FigureCanvasTkAgg
- Update charts on period change
- Cache chart data for performance

---

## Story 6.3: Category Charts

**As a** user
**I want** category visualizations
**So that** I see where money goes

### Acceptance Criteria

- [ ] Create `ui/charts/category_charts.py`:

  **Chart Types:**
  - Pie chart (default)
  - Horizontal bar chart
  - Vertical bar chart
  - Donut chart

  **Chart Selector:** Dropdown to switch chart types

  **Period Selector:** This Month, Last Month, Quarter, Year, Custom Range

  **Interactive Features:**
  - Click segment/bar to drill into subcategories
  - Hover shows exact values
  - Legend shows all categories with %

  **Subcategory Drill-Down:**
  - Back button to return to main view
  - Subcategory chart for selected category

  **Context Menu (Right-Click):**
  - Save as PNG/JPG
  - Copy to clipboard
  - View data table
  - Export data

### Wireframe: Category Chart View

```
+--------------------------------------------------------------+
| Category Analysis                    [Pie v] [This Month v]   |
+--------------------------------------------------------------+
|                                                               |
|  +-----------------------------------------------------------+
|  |                                                           |
|  |                   [MAIN CHART]                            |
|  |                                                           |
|  |            (Pie or Bar based on selection)                |
|  |                                                           |
|  +-----------------------------------------------------------+
|                                                               |
|  Legend:                                                      |
|  # Supplies (28.6%)  # Equipment (21.9%)  # Facilities (27%) |
|  # Staff (13.5%)     # Marketing (6.1%)   # Admin (2.9%)     |
|                                                               |
|          [Save Chart]    [View Data Table]                    |
|                                                               |
+--------------------------------------------------------------+
```

### Chart Options Dialog

```
+---------------------------------------------+
|              Chart Options               [X] |
+---------------------------------------------+
|                                              |
|  Chart Type:                                 |
|  +----------------------------------------+  |
|  | o Pie Chart                            |  |
|  | o Bar Chart                            |  |
|  | o Line Chart                           |  |
|  | o Stacked Bar                          |  |
|  +----------------------------------------+  |
|                                              |
|  Display Options:                            |
|  +----------------------------------------+  |
|  | [x] Show values on chart               |  |
|  | [x] Show legend                        |  |
|  | [x] Show percentages                   |  |
|  | [ ] Show grid lines                    |  |
|  +----------------------------------------+  |
|                                              |
|  Color Scheme:                               |
|  +----------------------------------------+  |
|  | [Salon Theme (Purple/Pink)          v] |  |
|  +----------------------------------------+  |
|                                              |
|            [Apply]          [Cancel]         |
|                                              |
+---------------------------------------------+
```

---

## Story 6.4: Trend Charts

**As a** user
**I want** trend visualizations
**So that** I see spending over time

### Acceptance Criteria

- [ ] Create `ui/charts/trend_charts.py`:

  **Trend Types:**
  - Monthly (last 12 months)
  - Quarterly (last 8 quarters)
  - Yearly (last 5 years)
  - Cumulative (area chart)

  **Category Filter:**
  - All categories (total)
  - Specific category
  - Compare multiple categories (multi-line)

  **Chart Features:**
  - Line chart with markers
  - Area fill (optional)
  - Grid lines
  - Axis labels with currency

  **Summary Statistics:**
  - Average per period
  - Overall trend (increasing/decreasing)
  - Peak period (highest)
  - Lowest period

  **Multi-Category Comparison:**
  - Select multiple categories
  - Multi-line chart with legend

### Wireframe: Trend Chart View

```
+----------------------------------------------------------------------+
| Spending Trends                   [Monthly v] [Category: All v]       |
+----------------------------------------------------------------------+
|                                                                       |
|  +------------------------------------------------------------------+ |
|  |                                                                  | |
|  |  L                                                               | |
|  |  350k |                    ___                                   | |
|  |  300k |              _____/   \_____                             | |
|  |  250k |     ________/               \_______                     | |
|  |  200k |____/                                \____                | |
|  |       +-----+-----+-----+-----+-----+-----+-----                 | |
|  |            Jul   Aug   Sep   Oct   Nov   Dec                     | |
|  |                                                                  | |
|  +------------------------------------------------------------------+ |
|                                                                       |
|  Summary:                                                             |
|  - Average: L 275,000/month                                           |
|  - Trend: Increasing (+3.2% avg month-over-month)                     |
|  - Peak: December 2024 (L 320,000)                                    |
|  - Lowest: August 2024 (L 210,000)                                    |
|                                                                       |
|            [Compare Categories]    [Save Chart]                       |
|                                                                       |
+----------------------------------------------------------------------+
```

---

## Story 6.5: Budget Charts

**As a** user
**I want** budget vs actual charts
**So that** I see financial performance

### Acceptance Criteria

- [ ] Create `ui/charts/budget_charts.py`:

  **Overall Progress Gauge:**
  - Donut/gauge chart showing total budget usage
  - Percentage in center
  - Color based on status (green/yellow/red)
  - Text showing amounts and days remaining

  **Category Comparison Chart:**
  - Grouped bar chart
  - Budget bar (blue/gray)
  - Actual bar (colored by status)
  - Percentage labels

  **Color Coding:**
  - Green: Under 80% used
  - Yellow/Orange: 80-100% used
  - Red: Over 100% (exceeded)

  **Period Selector:** Month picker, historical months

  **Interactive Features:**
  - Click category for detailed breakdown
  - Hover for exact values
  - View budget details button

  **Historical Comparison Table:**
  | Month | Budget | Actual | Variance | Status |
  |-------|--------|--------|----------|--------|
  | Jan 2024 | L 375,000 | L 296,500 | -L 78,500 | 79% |
  | Dec 2023 | L 350,000 | L 362,000 | +L 12,000 | 103% |

### Wireframe: Budget vs Actual View

```
+----------------------------------------------------------------------+
| Budget vs Actual                              [January 2024 v]        |
+----------------------------------------------------------------------+
|                                                                       |
|  Overall Budget Progress                                              |
|  +------------------------------------------------------------------+ |
|  |                                                                  | |
|  |           [GAUGE CHART - 79%]                                    | |
|  |                                                                  | |
|  |      L 296,500 spent of L 375,000 budget                         | |
|  |      L 78,500 remaining - 10 days left in month                  | |
|  |                                                                  | |
|  +------------------------------------------------------------------+ |
|                                                                       |
|  Category Breakdown                                                   |
|  +------------------------------------------------------------------+ |
|  |                                                                  | |
|  |      [GROUPED BAR CHART - Budget vs Actual by Category]          | |
|  |                                                                  | |
|  |   [##] Budget    [##] Actual (green/yellow/red)                  | |
|  |                                                                  | |
|  +------------------------------------------------------------------+ |
|                                                                       |
|  Status Legend:                                                       |
|  # Under 80% (On Track)   # 80-100% (Warning)   # Over 100% (Over)   |
|                                                                       |
|            [View Details]    [Save Chart]                             |
|                                                                       |
+----------------------------------------------------------------------+
```

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 6.1 | 1.3 (CategoryManager) |
| 6.2 | 6.1, 5.1, 4.1 |
| 6.3 | 6.1, 5.1 |
| 6.4 | 6.1, 5.1 |
| 6.5 | 6.1, 4.1 |

---

## Testing Requirements

- [ ] Unit tests for all Visualizer chart methods
- [ ] Tests with empty data sets
- [ ] Tests with single data point
- [ ] Tests with large data sets (performance)
- [ ] Tests for chart embedding in Tkinter
- [ ] Tests for chart save functionality
- [ ] Memory leak tests (figure cleanup)
- [ ] UI tests for dashboard interactions
