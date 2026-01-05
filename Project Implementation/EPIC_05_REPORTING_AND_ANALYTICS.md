# Epic 5: Advanced Reporting & Analytics

**Priority:** Medium
**Dependencies:** Epic 2 (CRUD Operations), Epic 3 (Filtering)
**Stories:** 7

---

## Story 5.1: ReportGenerator Class

**As a** developer
**I want** a ReportGenerator for analytics
**So that** reporting logic is centralized

### Acceptance Criteria

- [ ] Create `reports/report_generator.py`:

  **StatisticalSummary Dataclass:**
  ```python
  @dataclass
  class StatisticalSummary:
      """Statistical summary of expenses"""
      total: float
      average: float
      median: float
      minimum: float
      maximum: float
      std_deviation: float
      count: int
      date_range: Tuple[datetime, datetime]
  ```

  **ReportGenerator Methods:**
  ```python
  class ReportGenerator:
      """Generates statistical reports and analytics for expenses"""

      def __init__(self, expense_manager: ExpenseManager, filter_manager: FilterManager)
          """Initialize with managers"""

      def get_statistical_summary(self, df: pd.DataFrame = None) -> StatisticalSummary
          """Calculate statistical summary using NumPy"""

      def get_category_summary(self, df: pd.DataFrame = None) -> pd.DataFrame
          """Get category breakdown with statistics"""

      def get_subcategory_summary(self, category: str, df: pd.DataFrame = None) -> pd.DataFrame
          """Get subcategory breakdown for a specific category"""

      def get_monthly_trend(self, months: int = 12) -> pd.DataFrame
          """Get monthly expense totals for trend analysis"""

      def get_quarterly_summary(self, year: int) -> pd.DataFrame
          """Get quarterly breakdown for a specific year"""

      def get_yearly_trend(self, years: int = 3) -> pd.DataFrame
          """Get yearly expense totals for long-term trend"""

      def get_vendor_analysis(self, top_n: int = 10, df: pd.DataFrame = None) -> pd.DataFrame
          """Analyze spending by vendor"""

      def get_top_expenses(self, n: int = 10, df: pd.DataFrame = None) -> pd.DataFrame
          """Get the N largest individual expenses"""

      def get_payment_method_distribution(self, df: pd.DataFrame = None) -> pd.DataFrame
          """Get expense distribution by payment method"""

      def get_recurring_vs_onetime(self, df: pd.DataFrame = None) -> Dict
          """Compare recurring vs one-time expenses"""

      def compare_periods(self, period1: Tuple[datetime, datetime],
                          period2: Tuple[datetime, datetime]) -> Dict
          """Compare spending between two time periods"""

      def get_tag_analysis(self, df: pd.DataFrame = None) -> pd.DataFrame
          """Analyze expenses by tags"""

      def identify_seasonal_patterns(self, df: pd.DataFrame = None) -> Dict
          """Identify high/low spending months"""

      # Cash Flow Analysis Methods (Story 5.7)
      def get_daily_cash_flow(self, days: int = 30) -> pd.DataFrame
          """Get daily expense totals for cash flow analysis"""

      def get_weekly_cash_flow(self, weeks: int = 12) -> pd.DataFrame
          """Get weekly expense totals"""

      def get_peak_spending_analysis(self, df: pd.DataFrame = None) -> Dict
          """Identify peak spending days (day of week, day of month)"""

      def get_recurring_ratio(self, df: pd.DataFrame = None) -> Dict
          """Calculate recurring vs one-time expense ratio"""
  ```

### Return Structures

**Category Summary DataFrame Columns:**
- category, total, percentage, count, average, min_amount, max_amount

**Monthly Trend DataFrame Columns:**
- year_month, year, month, total, count, average

**Vendor Analysis DataFrame Columns:**
- vendor, total, count, average, last_transaction, percentage

### Technical Notes
- Uses NumPy for statistical calculations
- Uses Pandas for data aggregation and grouping
- All methods accept optional DataFrame for filtered data
- Returns DataFrames for easy display in UI tables

---

## Story 5.2: Summary Statistics View

**As a** user
**I want** to see expense statistics
**So that** I understand my spending patterns

### Acceptance Criteria

- [ ] Create `ui/reports/summary_statistics.py`:

  **KPI Cards:** Total, Transaction Count, Average

  **Detailed Statistics Table:**
  - Median, Highest, Lowest expense
  - Standard deviation
  - Date range

  **Period Selector:** This Month, Last Month, Quarter, Year, Custom

  **Period Comparison:** Compare button, show difference and % change

### Wireframe: Summary Statistics

```
+-------------------------------------------------------------+
| Expense Statistics                          [This Month v]   |
+-------------------------------------------------------------+
|                                                              |
|  +--------------+  +--------------+  +--------------+        |
|  | L 296,500    |  | 100          |  | L 2,965      |        |
|  | Total        |  | Transactions |  | Average      |        |
|  +--------------+  +--------------+  +--------------+        |
|                                                              |
|  +----------------------------------------------------------+
|  | Statistical Details                                       |
|  +----------------------------------------------------------+
|  | Median:              L 1,200.00                          |
|  | Highest:             L 45,000.00                         |
|  | Lowest:              L 50.00                             |
|  | Std. Deviation:      L 8,543.21                          |
|  | Date Range:          01/01/2024 - 31/01/2024             |
|  +----------------------------------------------------------+
|                                                              |
|  [Compare with Previous Period]                              |
|                                                              |
+-------------------------------------------------------------+
```

---

## Story 5.3: Category Analysis Report

**As a** user
**I want** category breakdown reports
**So that** I know where money goes

### Acceptance Criteria

- [ ] Create `ui/reports/category_analysis.py`:

  **Category Summary Table Columns:**
  | Column | Description |
  |--------|-------------|
  | Category | With color indicator |
  | Total | Amount spent |
  | % | Percentage of total |
  | Count | Transaction count |
  | Average | Per transaction |
  | Actions | Drill-down button |

  **Subcategory Drill-Down:** View subcategories within category

  **Period Selector:** Month, Quarter, Year, Custom

  **Interactive Features:**
  - Click row to view expenses
  - Sort by any column
  - Export report

### Wireframe: Category Analysis

```
+----------------------------------------------------------------------+
| Category Analysis                           Period: [January 2024]    |
+----------------------------------------------------------------------+
|                                                                       |
| Category        | Total      | %     | Count | Average | Actions     |
+-----------------+------------+-------+-------+---------+-------------+
| # Supplies      | L 85,000   | 28.6% | 45    | L 1,889 | [Detail]    |
| # Equipment     | L 65,000   | 21.9% | 12    | L 5,417 | [Detail]    |
| # Facilities    | L 80,000   | 27.0% | 23    | L 3,478 | [Detail]    |
| # Staff         | L 40,000   | 13.5% | 8     | L 5,000 | [Detail]    |
| # Marketing     | L 18,000   | 6.1%  | 15    | L 1,200 | [Detail]    |
| # Administrative| L 8,500    | 2.9%  | 5     | L 1,700 | [Detail]    |
+-----------------+------------+-------+-------+---------+-------------+
| TOTAL           | L 296,500  | 100%  | 108   | L 2,745 |             |
+----------------------------------------------------------------------+
```

### Wireframe: Subcategory Drill-Down

```
+-------------------------------------------------------------+
| Supplies - Subcategories                          [<- Back]  |
+-------------------------------------------------------------+
| Subcategory       | Total    | %     | Count | Average       |
+-------------------+----------+-------+-------+---------------+
| Hair products     | L 35,000 | 41.2% | 20    | L 1,750       |
| Nail products     | L 25,000 | 29.4% | 12    | L 2,083       |
| Skincare products | L 15,000 | 17.6% | 8     | L 1,875       |
| Disposables       | L 10,000 | 11.8% | 5     | L 2,000       |
+-------------------------------------------------------------+
```

---

## Story 5.4: Trend Analysis Report

**As a** user
**I want** to see spending trends
**So that** I can identify patterns

### Acceptance Criteria

- [ ] Create `ui/reports/trend_analysis.py`:

  **Trend Types:**
  - Monthly (last 12 months)
  - Quarterly (last 4-8 quarters)
  - Yearly (last 3-5 years)
  - Category-specific

  **Data Table:**
  - Period, Total, Count, Average, % Change

  **Pattern Identification:**
  - Highlight highest/lowest periods
  - Calculate overall average
  - Identify trends (increasing/decreasing)

  **Category-Specific Trends:**
  - Select category dropdown
  - Compare multiple categories

### Wireframe: Trend Analysis

```
+-------------------------------------------------------------------------------------+
|                              Trend Analysis Report                                   |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Period: [Last 12 Months v]    Compare by: [Category v]         [Export] [Print]    |
|                                                                                      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Monthly Expense Trend                                                               |
|  +-------------------------------------------------------------------------+        |
|  |                                                                         |        |
|  |  350k |                                    ___                          |        |
|  |       |                              _____/   \___                      |        |
|  |  300k |                         ___/              \___                  |        |
|  |       |                    ___/                      \___               |        |
|  |  250k |               ___/                               \___           |        |
|  |       |          ___/                                        \___       |        |
|  |  200k |     ___/                                                 \_     |        |
|  |       |___/                                                             |        |
|  |  150k |                                                                 |        |
|  |       +----+----+----+----+----+----+----+----+----+----+----+----     |        |
|  |        Feb  Mar  Apr  May  Jun  Jul  Aug  Sep  Oct  Nov  Dec  Jan      |        |
|  +-------------------------------------------------------------------------+        |
|                                                                                      |
|  Monthly Summary                                                                     |
|  +----------+------------+----------+--------------+--------+----------------+      |
|  | Month    | Total      | vs Prev  | Highest Cat  | Lowest | # Trans        |      |
|  +----------+------------+----------+--------------+--------+----------------+      |
|  | Jan 2024 | L 296,500  | +12%     | Supplies     | Admin  | 100            |      |
|  | Dec 2023 | L 264,732  | +8%      | Staff        | Admin  | 95             |      |
|  | Nov 2023 | L 245,123  | -3%      | Staff        | Mktg   | 88             |      |
|  +----------+------------+----------+--------------+--------+----------------+      |
|                                                                                      |
|  Insights:                                                                           |
|  - Expenses trending upward - 12% increase vs last month                            |
|  - Peak month: January 2024 (L 296,500)                                             |
|  - Lowest month: February 2023 (L 185,000)                                          |
|  - Average monthly expense: L 245,000                                               |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

---

## Story 5.5: Vendor Analysis Report

**As a** user
**I want** vendor spending analysis
**So that** I can negotiate or switch suppliers

### Acceptance Criteria

- [ ] Create `ui/reports/vendor_analysis.py`:

  **Vendor Table Columns:**
  - Vendor name, Total spent, %, Count, Average, Last transaction

  **Vendor Search:** Filter vendors as user types

  **View Transactions:** Click vendor to see all transactions

  **Export Options:** CSV, PDF

  **Controls:** Show top N, Sort, Date filter

### Wireframe: Vendor Analysis

```
+-------------------------------------------------------------------------------------+
|                              Vendor Analysis Report                                  |
|                                 January 2024                                         |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  [Search vendor...__________________]                            [Export] [Print]    |
|                                                                                      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Top 10 Vendors by Total Spend                                                       |
|  +------------------+--------------+---------+-----------+---------------+-------+  |
|  | Vendor           | Total Spent  | # Trans | Average   | Last Purchase | %     |  |
|  +------------------+--------------+---------+-----------+---------------+-------+  |
|  | Ana Koci         | L 135,000    | 3       | L 45,000  | 25/01/2024    | 45.5% |  |
|  | Hair Store       | L 45,000     | 9       | L 5,000   | 15/01/2024    | 15.2% |  |
|  | KEK              | L 36,000     | 3       | L 12,000  | 14/01/2024    | 12.1% |  |
|  | Nail World       | L 25,500     | 3       | L 8,500   | 12/01/2024    | 8.6%  |  |
|  | Beauty Supply    | L 20,400     | 3       | L 6,800   | 09/01/2024    | 6.9%  |  |
|  | ...              |              |         |           |               |       |  |
|  +------------------+--------------+---------+-----------+---------------+-------+  |
|                                                                                      |
|  Click vendor row to see all transactions                                            |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Wireframe: Vendor Detail (Expandable)

```
+-------------------------------------------------------------------------------------+
|  Vendor: Hair Store                                               [Collapse ^]       |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Summary: 9 transactions | Total: L 45,000 | Average: L 5,000                        |
|                                                                                      |
|  Transactions:                                                                       |
|  +--------------+----------------+-------------------------------+----------------+ |
|  | Date         | Category       | Description                   | Amount         | |
|  +--------------+----------------+-------------------------------+----------------+ |
|  | 15/01/2024   | Supplies/Hair  | Monthly shampoo order         | L 5,200.00     | |
|  | 08/01/2024   | Supplies/Hair  | Conditioners                  | L 4,800.00     | |
|  | 02/01/2024   | Supplies/Hair  | Hair dyes and treatments      | L 5,000.00     | |
|  +--------------+----------------+-------------------------------+----------------+ |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

---

## Story 5.6: Custom Report Builder

**As a** user
**I want** to create custom reports
**So that** I can analyze specific aspects

### Acceptance Criteria

- [ ] Create `ui/reports/custom_report_builder.py`:

  **Configuration Options:**
  | Section | Options |
  |---------|---------|
  | Date Range | From/To dates, Quick selects |
  | Categories | Checkboxes, Select/Clear All |
  | Metrics | Total, Count, Average, Median, Min/Max, StdDev |
  | Group By | Category, Subcategory, Vendor, Month, Payment Method, None |
  | Charts | Pie, Bar, Trend Line |

  **Actions:**
  - Preview Report
  - Export to PDF
  - Export to Excel

### Wireframe: Custom Report Builder

```
+-------------------------------------------------------------+
|                    Custom Report Builder                 [X] |
+-------------------------------------------------------------+
|                                                              |
|  Report Name                                                 |
|  +----------------------------------------------------------+
|  | Q4 2023 Supplies Analysis                                |
|  +----------------------------------------------------------+
|                                                              |
|  Date Range                                                  |
|  +---------------------+    +---------------------+          |
|  | From: 01/10/2023 [C]|    | To: 31/12/2023  [C] |          |
|  +---------------------+    +---------------------+          |
|                                                              |
|  Include Categories:                                         |
|  +----------------------------------------------------------+
|  | [x] Supplies    [x] Equipment    [ ] Facilities          |
|  | [ ] Staff       [ ] Marketing    [ ] Administrative      |
|  +----------------------------------------------------------+
|                                                              |
|  Group By:                         Include Metrics:          |
|  +-------------------------+      +-----------------------+  |
|  | o Category              |      | [x] Total             |  |
|  | o Subcategory           |      | [x] Average           |  |
|  | o Vendor                |      | [x] Count             |  |
|  | o Month                 |      | [ ] Median            |  |
|  | o Payment Method        |      | [ ] Min/Max           |  |
|  +-------------------------+      +-----------------------+  |
|                                                              |
|  Include Charts:                                             |
|  +----------------------------------------------------------+
|  | [x] Pie chart (distribution)                             |
|  | [x] Bar chart (comparison)                               |
|  | [ ] Trend line (over time)                               |
|  +----------------------------------------------------------+
|                                                              |
|      [Preview]     [Generate PDF]     [Generate Excel]       |
|                                                              |
+-------------------------------------------------------------+
```

### Wireframe: Report Preview

```
+-------------------------------------------------------------------------------------+
|                              Report Preview                                      [X] |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  +-------------------------------------------------------------------------------+  |
|  |                    Q4 2023 SUPPLIES ANALYSIS                                   |  |
|  |                    October - December 2023                                     |  |
|  |                                                                               |  |
|  |  SUMMARY BY SUBCATEGORY                                                       |  |
|  |  +-----------------+-------------+-------+-----------+                        |  |
|  |  | Subcategory     | Total       | Count | Average   |                        |  |
|  |  +-----------------+-------------+-------+-----------+                        |  |
|  |  | Hair products   | L 45,000    |  15   | L 3,000   |                        |  |
|  |  | Nail products   | L 25,500    |   9   | L 2,833   |                        |  |
|  |  | Skincare        | L 20,400    |   6   | L 3,400   |                        |  |
|  |  | Disposables     | L 12,600    |  12   | L 1,050   |                        |  |
|  |  | Cleaning        | L 8,500     |   8   | L 1,063   |                        |  |
|  |  +-----------------+-------------+-------+-----------+                        |  |
|  |                                                                               |  |
|  |  [PIE CHART]                    [BAR CHART]                                   |  |
|  +-------------------------------------------------------------------------------+  |
|                                                                                      |
|  [Edit Report]              [Export PDF]              [Export Excel]                 |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

---

## Story 5.7: Cash Flow Analysis

**As a** user
**I want** to see cash flow patterns
**So that** I can manage salon liquidity

### Acceptance Criteria

- [ ] Create `ui/reports/cash_flow_analysis.py`:

  **Cash Outflow Views:**
  - Daily view (last 30 days)
  - Weekly view (last 12 weeks)
  - Monthly view (last 12 months)

  **Analysis Components:**
  | Component | Description |
  |-----------|-------------|
  | Outflow Summary | Total cash out per period |
  | Payment Method Split | Breakdown by Cash vs Card vs Bank |
  | Recurring vs One-Time | Compare recurring expenses to ad-hoc |
  | Peak Spending Days | Identify high-expense days of week/month |

  **Calculations (add to ReportGenerator):**
  ```python
  def get_daily_cash_flow(self, days: int = 30) -> pd.DataFrame
      """Get daily expense totals for cash flow analysis"""

  def get_weekly_cash_flow(self, weeks: int = 12) -> pd.DataFrame
      """Get weekly expense totals"""

  def get_peak_spending_analysis(self, df: pd.DataFrame = None) -> Dict
      """Identify peak spending days (day of week, day of month)"""

  def get_recurring_ratio(self, df: pd.DataFrame = None) -> Dict
      """Calculate recurring vs one-time expense ratio"""
  ```

  **Period Selector:** Daily, Weekly, Monthly toggle

  **Export Options:** PDF, Excel

### Wireframe: Cash Flow Analysis

```
+-------------------------------------------------------------------------------------+
|                              Cash Flow Analysis                                      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  View: [Daily v]    Period: [Last 30 Days v]                    [Export] [Print]    |
|                                                                                      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Cash Outflow Summary                                                                |
|  +-------------------------------------------------------------------------------+  |
|  |                                                                               |  |
|  |  Total Outflow: L 296,500           Average Daily: L 9,883                    |  |
|  |  Peak Day: Monday (L 45,000)        Lowest Day: Sunday (L 2,100)              |  |
|  |                                                                               |  |
|  +-------------------------------------------------------------------------------+  |
|                                                                                      |
|  Daily Spending Chart                                                                |
|  +-------------------------------------------------------------------------------+  |
|  |                                                                               |  |
|  |  L                      _                                                     |  |
|  |  15k |    _            | |        _                                           |  |
|  |  10k |   | |  _   _   | |   _   | |   _                                       |  |
|  |   5k |  _| |_| |_| |__| |__| |__| |__| |__                                    |  |
|  |      +----+----+----+----+----+----+----+----                                 |  |
|  |        01   05   10   15   20   25   30                                       |  |
|  |                                                                               |  |
|  +-------------------------------------------------------------------------------+  |
|                                                                                      |
|  Payment Method Distribution          |  Recurring vs One-Time                       |
|  +----------------------------------+ | +----------------------------------+         |
|  |                                  | | |                                  |         |
|  |  Cash:          L 85,000 (29%)   | | |  Recurring:    L 180,000 (61%)   |         |
|  |  Debit Card:    L 95,000 (32%)   | | |  One-Time:     L 116,500 (39%)   |         |
|  |  Credit Card:   L 45,000 (15%)   | | |                                  |         |
|  |  Bank Transfer: L 71,500 (24%)   | | |  [PIE CHART]                     |         |
|  |                                  | | |                                  |         |
|  +----------------------------------+ | +----------------------------------+         |
|                                                                                      |
|  Peak Spending Patterns                                                              |
|  +-------------------------------------------------------------------------------+  |
|  | Day of Week:  Monday highest (rent due), Sunday lowest                        |  |
|  | Day of Month: 1st-5th highest (rent, salaries), 20th-25th second peak         |  |
|  +-------------------------------------------------------------------------------+  |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Technical Notes
- Use date grouping with Pandas resample/groupby
- Calculate rolling averages for trend indication
- Identify outlier days using standard deviation

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 5.1 | 2.1 (ExpenseManager), 3.1 (FilterManager) |
| 5.2 | 5.1 |
| 5.3 | 5.1 |
| 5.4 | 5.1, 6.1 (Visualizer) |
| 5.5 | 5.1 |
| 5.6 | 5.1, 6.1 (Visualizer), 8.1 (PDF), 8.2 (Excel) |
| 5.7 | 5.1, 6.1 (Visualizer), 8.1 (PDF), 8.2 (Excel) |

---

## Testing Requirements

- [ ] Unit tests for ReportGenerator (all calculation methods)
- [ ] Unit tests for StatisticalSummary dataclass
- [ ] Tests with empty data sets
- [ ] Tests with large data sets (performance)
- [ ] Tests for edge cases (single transaction, all same amount)
- [ ] Tests for period comparison calculations
- [ ] Tests for cash flow calculations (daily, weekly grouping)
- [ ] Tests for peak spending analysis
- [ ] Integration tests with filtered data
- [ ] UI tests for report navigation and drill-down
