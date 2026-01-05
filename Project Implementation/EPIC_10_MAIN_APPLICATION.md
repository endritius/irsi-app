# Epic 10: Main Application & Integration

**Priority:** High (Foundation for UI)
**Dependencies:** All other Epics
**Stories:** 5

---

## Story 10.1: Main Window

**As a** user
**I want** a main application window
**So that** I can access all features

### Acceptance Criteria

- [ ] Create `ui/main_window.py`:

  **MainWindow Methods:**
  ```python
  class MainWindow:
      """Main application window with menu bar and tab navigation"""

      WINDOW_TITLE = "Beauty Salon Expense Manager"
      MIN_WIDTH = 1024
      MIN_HEIGHT = 768
      DEFAULT_WIDTH = 1280
      DEFAULT_HEIGHT = 800

      def __init__(self, app: 'Application')
          """Initialize with Application instance"""

      def _setup_window(self) -> None
          """Configure main window properties"""

      def _create_menu_bar(self) -> None
          """Create application menu bar"""

      def _create_toolbar(self) -> None
          """Create toolbar with quick action buttons"""

      def _create_tab_navigation(self) -> None
          """Create tab-based navigation"""

      def _create_status_bar(self) -> None
          """Create status bar at bottom"""

      def _bind_shortcuts(self) -> None
          """Bind keyboard shortcuts"""

      def _switch_tab(self, index: int) -> None
          """Switch to tab by index"""

      def set_status(self, message: str) -> None
          """Update status bar message"""

      def update_filter_indicator(self, active_count: int) -> None
          """Update filter indicator in status bar"""

      def update_record_count(self, count: int) -> None
          """Update record count in status bar"""

      def update_save_time(self, time_str: str) -> None
          """Update last save time in status bar"""

      def update_alert_indicator(self, alert_count: int) -> None
          """Update alert indicator in status bar"""

      def run(self) -> None
          """Start the main event loop"""
  ```

### Wireframe: Main Application Window

```
+-------------------------------------------------------------------------------------+
| Beauty Salon Expense Manager                                           [_] [O] [X]  |
+-------------------------------------------------------------------------------------+
| File    Edit    View    Reports    Help                                             |
+-------------------------------------------------------------------------------------+
| [+ New Expense]  [Dashboard]  [Expenses]  [Budgets]  [Reports]     Search: [______] |
+-------------------------------------------------------------------------------------+
|                                                                                     |
| +---------------------------------------------------------------------------------+ |
| | [Dashboard] | [Expenses] | [Budgets] | [Reports]                                | |
| +---------------------------------------------------------------------------------+ |
| |                                                                                 | |
| |                                                                                 | |
| |                          << MAIN CONTENT AREA >>                                | |
| |                                                                                 | |
| |                   (Dashboard / Expenses / Budgets / Reports)                    | |
| |                                                                                 | |
| |                                                                                 | |
| +---------------------------------------------------------------------------------+ |
|                                                                                     |
+-------------------------------------------------------------------------------------+
| Records: 234  |  Filtered: 50  |  Last saved: 14:32  |  [!] 2 Budget Alerts        |
+-------------------------------------------------------------------------------------+
```

### Menu Structure

**File Menu:**
- New Expense (Ctrl+N)
- Import from CSV...
- Export > To Excel... / To PDF...
- Create Backup...
- Restore Backup...
- Settings...
- Exit (Alt+F4)

**Edit Menu:**
- Edit Selected (Ctrl+E)
- Delete Selected (Delete)
- Select All (Ctrl+A)
- Undo (Ctrl+Z)
- Redo (Ctrl+Y)

**View Menu:**
- Dashboard (F1)
- Expenses (F2)
- Budgets (F3)
- Reports (F4)
- Deleted Items...
- Refresh (F5)

**Reports Menu:**
- Summary Report...
- Category Analysis...
- Trend Analysis...
- Vendor Analysis...
- Custom Report...
- Export as PDF...

**Help Menu:**
- User Guide
- Keyboard Shortcuts
- About...

### Technical Notes
- Use ttk.Notebook for tabs
- Menu accelerators for keyboard shortcuts
- Responsive layout with pack/grid
- Protocol handler for window close

---

## Story 10.2: Application Startup

**As a** user
**I want** the app to load smoothly
**So that** I can start working quickly

### Acceptance Criteria

- [ ] Create `app.py` with Application class:

  **Application Methods:**
  ```python
  class Application:
      """Central application controller coordinating all managers"""

      VERSION = "1.0.0"
      APP_NAME = "Beauty Salon Expense Manager"

      def __init__(self)
          """Initialize manager references"""

      def initialize(self, progress_callback=None) -> bool
          """Initialize all components with progress callback"""

      def shutdown(self) -> None
          """Clean shutdown with final save"""

      def get_startup_summary(self) -> Dict
          """Get summary of startup results"""
  ```

- [ ] Create `main.py` entry point

- [ ] Create `ui/splash_screen.py`:

  **SplashScreen Methods:**
  ```python
  class SplashScreen:
      """Splash screen shown during application startup"""

      def __init__(self, parent)
          """Create splash window"""

      def update_progress(self, message: str, percentage: int)
          """Update progress display"""

      def close(self)
          """Close splash screen"""
  ```

### Wireframe: Splash Screen

```
+-------------------------------------------------------------+
|                                                             |
|                      [Salon Icon]                           |
|                                                             |
|              Beauty Salon Expense Manager                   |
|                    Version 1.0.0                            |
|                                                             |
|         [============================........]  70%         |
|                                                             |
|                  Loading expenses...                        |
|                                                             |
+-------------------------------------------------------------+
```

### Startup Sequence

1. Show splash screen
2. Initialize ErrorHandler
3. Initialize DataManager
4. Load settings
5. Load expenses (with validation)
6. Load budgets
7. Load templates
8. Initialize managers (ExpenseManager, BudgetManager, FilterManager, TemplateManager)
9. Initialize RecurringHandler
10. Check for budget alerts
11. Process recurring expenses (via RecurringHandler)
12. Show main window
13. Display startup alerts if any

### Technical Notes
- Splash screen updates during loading with step descriptions
- Progress callback for visual feedback (percentage updates)
- Data validation on load (see Story 9.5)
- Logging throughout startup to `logs/startup_YYYYMMDD.log`
- Step 11 (Process recurring): Auto-generate expenses where recurring_action='auto_generate' and next_due_date <= today
- Recurring reminders (recurring_action='reminder') shown in startup alerts dialog
- If any step fails, show error and allow user to continue or exit

---

## Story 10.3: Recurring Expense Handler

**As a** user
**I want** recurring expenses handled
**So that** regular expenses are tracked

### Acceptance Criteria

- [ ] Create `managers/recurring_handler.py`:

  **RecurringHandler Methods:**
  ```python
  class RecurringHandler:
      """Handles recurring expense generation and reminders"""

      def __init__(self, expense_manager: ExpenseManager)
          """Initialize with ExpenseManager"""

      def check_due_expenses(self) -> Tuple[List, List]
          """Check for due recurring expenses. Returns (auto_generate, reminders)"""

      def process_auto_generate(self, due_expenses: List) -> List[str]
          """Auto-generate expenses. Returns list of generated IDs"""

      def _calculate_next_due_date(self, expense) -> Optional[datetime]
          """Calculate next due date based on frequency"""

      def _create_from_recurring(self, original, due_date: datetime) -> Expense
          """Create new expense from recurring template"""
  ```

### Wireframe: Recurring Expense Reminder

```
+-------------------------------------------------------------+
|                  Recurring Expenses Due                  [X] |
+-------------------------------------------------------------+
|                                                              |
|   The following recurring expenses are due:                  |
|                                                              |
|   +----------------------------------------------------------+
|   | [x] | Expense              | Amount   | Due    | Action  |
|   +-----+----------------------+----------+--------+---------+
|   | [x] | Monthly Rent         | L 80,000 | 01/01  | Auto    |
|   | [x] | Internet Bill        | L 3,000  | 05/01  | Auto    |
|   | [ ] | Hair Products Order  | L 5,000  | 15/01  | Remind  |
|   | [ ] | Staff Salary - Ana   | L 45,000 | 25/01  | Remind  |
|   +----------------------------------------------------------+
|                                                              |
|   Auto = Will be automatically created                       |
|   Remind = Manual entry required                             |
|                                                              |
|   [ ] Don't show this again today                            |
|                                                              |
|      [Generate Selected]    [Add Manually]    [Dismiss]      |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Run recurring check on each startup
- Handle edge cases for month-end dates
- Store last_recurring_date on expense
- Link generated expenses to template

---

## Story 10.4: Settings Dialog

**As a** user
**I want** to configure application settings
**So that** it works how I prefer

### Acceptance Criteria

- [ ] Create `ui/dialogs/settings_dialog.py` with tabbed interface:

  **General Tab:**
  - Salon name, address, contact (for reports)
  - Date format (DD/MM/YYYY - fixed)
  - Currency (Albanian Lek - fixed)
  - Duplicate check on/off
  - Validate on startup on/off

  **Backup Tab:**
  - Enable automatic backup
  - Backup frequency
  - Backup location
  - Keep backups for X days
  - Create Backup Now button
  - Restore from Backup button

  **Alerts Tab:**
  - Enable budget alerts
  - Warning threshold percentage
  - Show alerts on startup
  - Show alert before exceeding budget
  - Recurring expense reminders

  **Display Tab:**
  - Default view on startup
  - Rows per page
  - Alternating row colors
  - Show data labels on charts

### Wireframe: Settings Dialog

```
+-------------------------------------------------------------+
|                          Settings                        [X] |
+-------------------------------------------------------------+
|                                                              |
|  [General] [Backup] [Alerts] [Display]                       |
|                                                              |
+-------------------------------------------------------------+
|                                                              |
|  GENERAL SETTINGS                                            |
|                                                              |
|  Salon Information                                           |
|  +----------------------------------------------------------+
|  | Salon Name: [Beauty Studio Tirana___________________]    |
|  | Address:    [Rruga e Durresit, Nr. 45______________]    |
|  | Contact:    [+355 69 123 4567______________________]    |
|  +----------------------------------------------------------+
|                                                              |
|  Data Options                                                |
|  +----------------------------------------------------------+
|  | [x] Auto-save after each change                          |
|  | [x] Check for duplicate expenses                         |
|  | [x] Validate data on startup                             |
|  +----------------------------------------------------------+
|                                                              |
|                              [Save]          [Cancel]        |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Use ttk widgets for native look
- Tab-based layout with ttk.Notebook
- Validate inputs before saving
- Apply some changes immediately, others on restart

---

## Story 10.5: Data Load Summary

**As a** user
**I want** to know if data has issues
**So that** I can fix problems

### Acceptance Criteria

- [ ] Create `ui/dialogs/data_summary_dialog.py`:

  **Issue Detection:**
  - Invalid dates
  - Unknown categories
  - Invalid amounts (negative, non-numeric)
  - Missing required fields
  - Orphaned references

  **Automatic Fixes:**
  - Invalid date → today's date
  - Unknown category → "Administrative"
  - Negative amount → absolute value
  - Missing vendor → "Unknown"

  **Summary Display:**
  - Total expenses loaded
  - Total budgets loaded
  - Issues found count
  - Details of each issue and fix

  **Export Issues:** Export issue report to CSV for review

### Wireframe: Data Summary Dialog

```
+---------------------------------------------+
|            Data Load Summary             [X] |
+---------------------------------------------+
|                                              |
| [check] Loaded 234 expenses                  |
| [check] Loaded 8 budgets                     |
|                                              |
| [!] 3 data issue(s) were found and corrected:|
|                                              |
| +------------------------------------------+ |
| | Issue                   | Action Taken   | |
| +-------------------------+----------------+ |
| | Invalid date in row 45  | Set to today   | |
| | Unknown category "Other"| Set to Admin   | |
| | Negative amount row 89  | Made positive  | |
| +------------------------------------------+ |
|                                              |
| [x] Don't show if no issues found            |
|                                              |
|                  [Export Issues]    [OK]     |
|                                              |
+---------------------------------------------+
```

### Technical Notes
- Run on startup after data load
- Store original values for possible revert
- Log all corrections made
- Option to suppress if no issues

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 10.1 | All other Epics (for integration) |
| 10.2 | 10.1, 7.1, 9.1 |
| 10.3 | 2.1, 10.2 |
| 10.4 | 10.1, 7.1 |
| 10.5 | 10.2, 9.5 |

---

## Testing Requirements

- [ ] Unit tests for Application class initialization
- [ ] Unit tests for RecurringHandler (due date calculations)
- [ ] Unit tests for settings load/save
- [ ] Integration tests for startup sequence
- [ ] Tests for error handling during startup
- [ ] Tests for recurring expense edge cases
- [ ] UI tests for main window navigation
- [ ] UI tests for settings dialog
- [ ] Performance tests for startup with large datasets
