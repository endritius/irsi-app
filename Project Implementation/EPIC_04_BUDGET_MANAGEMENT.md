# Epic 4: Budget Tracking & Alerts

**Priority:** High
**Dependencies:** Epic 2 (CRUD Operations), Epic 7 (Data Persistence)
**Stories:** 5

---

## Story 4.1: BudgetManager Class

**As a** developer
**I want** a BudgetManager for budget operations
**So that** budget logic is centralized

### Acceptance Criteria

- [ ] Create `managers/budget_manager.py`:

  **Methods:**
  ```python
  class BudgetManager:
      """Manages budget operations and tracking"""

      def __init__(self, data_manager: DataManager, expense_manager: ExpenseManager)
          """Initialize with managers, load budgets into memory"""

      def load_budgets(self) -> None
          """Load budgets from CSV"""

      def save_budgets(self) -> None
          """Save all budgets to CSV"""

      def add_budget(self, budget: Budget) -> str
          """Add new budget, return budget_id"""

      def update_budget(self, budget_id: str, updates: Dict) -> bool
          """Update budget fields"""

      def delete_budget(self, budget_id: str) -> bool
          """Delete budget"""

      def get_budget(self, budget_id: str) -> Optional[Budget]
          """Get single budget by ID"""

      def get_all_budgets(self) -> List[Budget]
          """Get all budgets"""

      # Budget Queries
      def get_monthly_total_budget(self, month: int, year: int) -> Optional[Budget]
          """Get total budget for specific month"""

      def get_category_budget(self, category: str, month: int, year: int) -> Optional[Budget]
          """Get budget for specific category and month"""

      def get_category_budgets(self, month: int, year: int) -> List[Budget]
          """Get all category budgets for month"""

      def get_current_month_budgets(self) -> Dict[str, Budget]
          """Get all budgets for current month"""

      # Budget Status
      def get_budget_status(self, budget: Budget) -> Dict
          """Calculate budget status with spending details"""

      def get_all_statuses(self, month: int = None, year: int = None) -> List[Dict]
          """Get status for all budgets in a month"""

      # Alerts
      def get_all_alerts(self) -> List[Dict]
          """Get list of current budget alerts"""

      def check_expense_against_budget(self, expense) -> Optional[Dict]
          """Check if adding expense would trigger budget alert"""

      # Utilities
      def copy_budgets_from_month(self, source_month: int, source_year: int,
                                  target_month: int, target_year: int) -> int
          """Copy all budgets from one month to another"""

      def validate_category_budgets(self, month: int, year: int) -> Optional[Dict]
          """Check if category budgets sum exceeds total budget"""

      # Rollover Methods
      def process_month_end_rollover(self, month: int, year: int) -> Dict[str, float]
          """Calculate and apply rollover for all eligible budgets at month end"""

      def get_rollover_summary(self, month: int, year: int) -> List[Dict]
          """Get rollover amounts for all category budgets"""

      def apply_rollover_to_budget(self, budget_id: str, rollover_amount: float) -> bool
          """Apply rollover amount to a specific budget"""
  ```

### Budget Status Return Structure
```python
{
    'budget_amount': float,      # Base budget limit
    'rollover_amount': float,    # Rollover from previous month
    'effective_budget': float,   # budget_amount + rollover_amount
    'spent': float,              # Amount spent
    'remaining': float,          # Effective budget - Spent
    'percentage_used': float,    # Percentage of effective budget consumed
    'status': str,               # 'ok' | 'warning' | 'exceeded'
    'days_remaining': int,       # Days left in period
    'daily_average': float,      # Average daily spending
    'projected_total': float,    # Projected month-end total
    'projected_rollover': float  # Projected rollover to next month (if enabled)
}
```

### Technical Notes
- BudgetManager works with ExpenseManager for spending calculations
- Status calculation includes projections based on daily average
- Alert system supports both warning and exceeded states

---

## Story 4.2: Set Monthly Budget UI

**As a** user
**I want** to set my monthly expense budget
**So that** I can control spending

### Acceptance Criteria

- [ ] Budget management view accessible from:
  - Main menu: View > Budgets
  - Tab navigation
  - Dashboard budget section

- [ ] **Monthly Budget Setup:**
  - Month/Year selector
  - Total Monthly Budget amount field
  - Warning threshold percentage (default 80%)
  - Enable Rollover checkbox (for unused budget to carry forward)
  - Rollover Cap percentage field (default 50%, max rollover as % of budget)
  - Display effective budget when rollover exists: "Budget: L X + L Y rollover = L Z"
  - Save/Cancel buttons

- [ ] **Copy from Previous Month:**
  - Button: "Copy from Previous Month"
  - Copies total and all category budgets
  - Confirmation before copying

- [ ] **Budget History:**
  - View budgets from past months (read-only)
  - Compare with current month

- [ ] **Validation:**
  - Amount must be positive
  - Warning threshold 0-100%

### Wireframe: Budget Management View

```
+-------------------------------------------------------------------------------------+
|                              Budget Management                                       |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Month: [January 2024        v]    [< Previous]  [Next >]    [Copy from Last Month] |
|                                                                                      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  +-------------------------------------------------------------------------------+  |
|  |                         Monthly Total Budget                                   |  |
|  |                                                                               |  |
|  |     Budget: L 375,000.00        Spent: L 296,500.00        Remaining: L 78,500|  |
|  |                                                                               |  |
|  |     [============================================...........]  79%           |  |
|  |                                                                               |  |
|  |     Warning threshold: 80%                               [Edit Budget]        |  |
|  +-------------------------------------------------------------------------------+  |
|                                                                                      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  [Category Budgets Section - See Story 4.3]                                          |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

---

## Story 4.3: Category Budgets UI

**As a** user
**I want** to set budgets per category
**So that** I can control spending in each area

### Acceptance Criteria

- [ ] **Category Budget Table:**
  | Column | Description |
  |--------|-------------|
  | Category | Category name |
  | Budget | Budget amount |
  | Spent | Current spending |
  | Remaining | Budget - Spent |
  | Status | Progress bar with % |
  | Actions | Edit button |

  - Color coding: Green (<80%), Yellow (80-100%), Red (>100%)
  - Sortable by any column

- [ ] **Adding/Editing Category Budget:**
  - Dialog with category (read-only), amount, threshold
  - [Save] [Delete] [Cancel] buttons

- [ ] **Quick Edit:**
  - Double-click amount to edit inline
  - Enter to save, Escape to cancel

- [ ] **Budget Validation:**
  - Warn if category budgets sum > total budget
  - Show comparison and allow override

- [ ] **Budget Rollover Option:**
  - Per-category setting to enable rollover
  - Unused budget carries forward to next month
  - Rollover amount shown in budget view
  - Cap rollover at X% of monthly budget (configurable, default 50%)
  - Track rollover history for audit

- [ ] **Summary Row:**
  - Total of all category budgets
  - Comparison with monthly total

### Wireframe: Category Budgets Table

```
+---------------------------------------------------------------------------------+
|  Category Budgets                                            [+ Add Budget]      |
+---------------------------------------------------------------------------------+
|                                                                                  |
|  +--------------+------------+------------+------------+--------------+---------+
|  | Category     | Budget     | Spent      | Remaining  | Status       | Actions |
|  +--------------+------------+------------+------------+--------------+---------+
|  | Supplies     | L 50,000   | L 42,500   | L 7,500    | [========.] 85%| [Edit]  |
|  | Equipment    | L 20,000   | L 20,400   | -L 400     | [==========] 102%| [Edit]  |
|  | Facilities   | L 80,000   | L 80,000   | L 0        | [==========] 100%| [Edit]  |
|  | Staff        | L 200,000  | L 150,000  | L 50,000   | [=======...] 75%| [Edit]  |
|  | Marketing    | L 15,000   | L 8,000    | L 7,000    | [=====.....] 53%| [Edit]  |
|  | Admin        | L 10,000   | L 5,000    | L 5,000    | [=====.....] 50%| [Edit]  |
|  +--------------+------------+------------+------------+--------------+---------+
|                                                                                  |
|  Legend: Green Under 80%   Yellow 80-100%   Red Over 100%                        |
|                                                                                  |
|  Warning: Category budgets total (L 375,000) equals monthly budget               |
|                                                                                  |
+---------------------------------------------------------------------------------+
```

### Wireframe: Edit Category Budget Dialog

```
+-------------------------------------------------+
|              Edit Category Budget            [X] |
+-------------------------------------------------+
|                                                  |
|  Category: Supplies                              |
|  Month: January 2024                             |
|                                                  |
|  Budget Amount (L)                               |
|  +-------------------------------------------+  |
|  | 50,000.00                                 |  |
|  +-------------------------------------------+  |
|                                                  |
|  Warning Threshold (%)                           |
|  +-------------------------------------------+  |
|  | 80                                        |  |
|  +-------------------------------------------+  |
|                                                  |
|  Current spending: L 42,500.00 (85%)             |
|                                                  |
|         [Save]      [Delete]      [Cancel]       |
|                                                  |
+-------------------------------------------------+
```

---

## Story 4.4: Budget Alerts System

**As a** user
**I want** to be alerted when approaching budget limits
**So that** I can adjust spending

### Acceptance Criteria

- [ ] **Alert Triggers:**
  - Warning at configurable threshold (default 80%)
  - Exceeded at 100%
  - Configurable per budget

- [ ] **Alert Display Locations:**
  - Dashboard: Alert summary panel
  - Status Bar: Alert icon with count
  - Startup: Show alerts dialog
  - Before Save: Warn when expense would exceed budget

- [ ] **Alert Types:**
  | Type | Icon | Description |
  |------|------|-------------|
  | Warning | Yellow | Budget at warning threshold |
  | Exceeded | Red | Budget over 100% |

- [ ] **Pre-Save Budget Check:**
  - Show dialog before saving expense that exceeds budget
  - Options: [Continue] [Cancel]

- [ ] **Alert Settings:**
  - Enable/disable notifications
  - Warning threshold percentage
  - Show on startup option

### Wireframe: Budget Warning Dialog

```
+-------------------------------------------------+
|           Budget Warning                     [X] |
+-------------------------------------------------+
|                                                  |
|   Warning: This expense will exceed your budget  |
|                                                  |
|   Category: Supplies                             |
|   Budget: L 50,000.00                            |
|   Current spending: L 47,000.00                  |
|   This expense: L 5,200.00                       |
|   -----------------------------------------      |
|   New total: L 52,200.00 (104%)                  |
|                                                  |
|   Do you want to continue?                       |
|                                                  |
|        [Continue]          [Cancel]              |
|                                                  |
+-------------------------------------------------+
```

### Wireframe: Budget Alerts on Startup

```
+-------------------------------------------------+
|           Budget Alerts                      [X] |
+-------------------------------------------------+
|                                                  |
|   Budget warnings for January 2024:              |
|                                                  |
|   +------------------------------------------+   |
|   | [!] Equipment budget exceeded            |   |
|   |     Budget: L 20,000 | Spent: L 20,400   |   |
|   |     102% - Exceeded by L 400             |   |
|   +------------------------------------------+   |
|   | [!] Facilities budget at limit           |   |
|   |     Budget: L 80,000 | Spent: L 80,000   |   |
|   |     100% - No remaining budget           |   |
|   +------------------------------------------+   |
|   | [W] Supplies budget warning              |   |
|   |     Budget: L 50,000 | Spent: L 42,500   |   |
|   |     85% - L 7,500 remaining              |   |
|   +------------------------------------------+   |
|                                                  |
|   [ ] Don't show this again today                |
|                                                  |
|        [View Budgets]          [Dismiss]         |
|                                                  |
+-------------------------------------------------+
```

### Wireframe: All Alerts View

```
+-------------------------------------------------------------+
|                       All Alerts                         [X] |
+-------------------------------------------------------------+
|                                                              |
|  Budget Alerts (3)                                           |
|  +----------------------------------------------------------+
|  | [!] Facilities budget EXCEEDED                            |
|  |     Budget: L 80,000 | Spent: L 80,000 | 100%            |
|  |     [View Budget]                                        |
|  +----------------------------------------------------------+
|  | [W] Equipment budget exceeded                             |
|  |     Budget: L 20,000 | Spent: L 20,400 | 102%            |
|  |     Exceeded by: L 400                                   |
|  |     [View Budget]                                        |
|  +----------------------------------------------------------+
|  | [W] Supplies budget warning                               |
|  |     Budget: L 50,000 | Spent: L 42,500 | 85%             |
|  |     Remaining: L 7,500                                   |
|  |     [View Budget]                                        |
|  +----------------------------------------------------------+
|                                                              |
|  Recurring Expense Reminders (2)                             |
|  +----------------------------------------------------------+
|  | [i] Hair Products Order due                               |
|  |     Amount: L 5,000 | Due: 15/01/2024                    |
|  |     [Add Expense]  [Dismiss]                             |
|  +----------------------------------------------------------+
|  | [i] Staff Salary - Ana due                                |
|  |     Amount: L 45,000 | Due: 25/01/2024                   |
|  |     [Add Expense]  [Dismiss]                             |
|  +----------------------------------------------------------+
|                                                              |
|                         [Dismiss All]         [Close]        |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Warning threshold can be set globally in settings (default for new budgets)
- Each budget can have its own warning_threshold override
- Per-budget threshold takes precedence over global setting
- Threshold range: 0-100%

---

## Story 4.5: Budget vs Actual Report

**As a** user
**I want** to see budget vs actual comparison
**So that** I can track my financial discipline

### Acceptance Criteria

- [ ] **Monthly Comparison View:**
  - Side-by-side: Budget vs Actual
  - Variance column (over/under)
  - Percentage of budget used
  - Visual bar chart comparison

- [ ] **Category Breakdown:**
  - Each category's budget vs actual
  - Identify biggest variances
  - Trend indicator (improving/worsening)

- [ ] **Historical Comparison:**
  - Last 6 months trend table
  - Year-to-date summary
  - Monthly average spending vs budget

- [ ] **Export:**
  - Export report to PDF
  - Export data to Excel

- [ ] **Projections:**
  - Based on current spending rate
  - Projected month-end total
  - Days remaining in period

### Report Layout

```
+-------------------------------------------------------------+
|              Budget vs Actual Report                         |
|              January 2024                                    |
+-------------------------------------------------------------+
|                                                              |
|  SUMMARY                                                     |
|  +----------------------------------------------------------+
|  | Total Budget:    L 375,000                                |
|  | Total Spent:     L 298,500                                |
|  | Remaining:       L 76,500                                 |
|  | % Used:          79.6%                                    |
|  | Days Remaining:  8                                        |
|  | Projected Total: L 385,000 (over by L 10,000)            |
|  +----------------------------------------------------------+
|                                                              |
|  CATEGORY BREAKDOWN                                          |
|  +--------------+----------+----------+----------+---------+ |
|  | Category     | Budget   | Actual   | Variance | %       | |
|  +--------------+----------+----------+----------+---------+ |
|  | Supplies     | L 50,000 | L 35,000 | -L 15,000| 70%     | |
|  | Equipment    | L 20,000 | L 23,000 | +L 3,000 | 115%    | |
|  | Facilities   | L 80,000 | L 82,000 | +L 2,000 | 102%    | |
|  | Staff        | L 200,000| L 150,000| -L 50,000| 75%     | |
|  | Marketing    | L 15,000 | L 8,000  | -L 7,000 | 53%     | |
|  | Admin        | L 10,000 | L 5,000  | -L 5,000 | 50%     | |
|  +--------------+----------+----------+----------+---------+ |
|                                                              |
|  6-MONTH TREND                                               |
|  [Chart: Budget vs Actual line graph]                        |
|                                                              |
+-------------------------------------------------------------+
```

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 4.1 | 7.1, 2.1 |
| 4.2 | 4.1 |
| 4.3 | 4.1 |
| 4.4 | 4.1 |
| 4.5 | 4.1, 5.1 |

---

## Testing Requirements

- [ ] Unit tests for BudgetManager (all methods)
- [ ] Unit tests for budget status calculations
- [ ] Unit tests for alert triggering logic
- [ ] Integration tests for expense-budget interaction
- [ ] Test copy budgets functionality
- [ ] Test budget validation (category sum vs total)
- [ ] Unit tests for rollover calculations (cap enforcement)
- [ ] Unit tests for process_month_end_rollover
- [ ] Integration tests for rollover across month boundaries
- [ ] Test effective budget calculations with rollover
- [ ] Unit tests for budget vs actual report calculations
- [ ] Test variance calculations (positive/negative)
- [ ] Test historical comparison data aggregation
