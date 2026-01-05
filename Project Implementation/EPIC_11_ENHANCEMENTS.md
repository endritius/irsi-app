# Epic 11: Optional Enhancements

**Priority:** Low (Future Enhancement)
**Dependencies:** All Core Epics
**Stories:** 6

These stories are optional enhancements that can be implemented after the core functionality is complete.

---

## Story 11.1: Undo/Redo System

**As a** user
**I want** to undo accidental changes
**So that** I can recover from mistakes

### Acceptance Criteria

- [ ] Create `managers/undo_manager.py`:

  **UndoManager Methods:**
  ```python
  class UndoManager:
      """Manages undo/redo stack for expense operations"""

      MAX_UNDO_HISTORY = 10

      def __init__(self)
          """Initialize empty stacks and callbacks dict"""

      def register_callback(self, name: str, callback: Callable) -> None
          """Register callback for undo/redo operations"""

      def record_action(self, action_type: ActionType, entity_id: str, data_before: Dict, data_after: Dict, description: str = "") -> None
          """Record an action for potential undo"""

      def can_undo(self) -> bool
          """Check if undo is available"""

      def can_redo(self) -> bool
          """Check if redo is available"""

      def undo(self) -> Optional[UndoAction]
          """Undo the last action"""

      def redo(self) -> Optional[UndoAction]
          """Redo the last undone action"""

      def get_undo_description(self) -> Optional[str]
          """Get description of next undo action"""

      def get_redo_description(self) -> Optional[str]
          """Get description of next redo action"""

      def clear_history(self) -> None
          """Clear all undo/redo history"""
  ```

- [ ] **Keyboard Shortcuts:**
  - Ctrl+Z: Undo last action
  - Ctrl+Y: Redo last undone action

- [ ] **Supported Actions:**
  - Add expense, Edit expense, Delete expense (soft delete)
  - Add budget, Edit budget, Delete budget

- [ ] **UI Integration:**
  - Edit menu: Undo (with description)
  - Edit menu: Redo (with description)
  - Disable when not available

- [ ] **History Limit:** Keep last 10 actions in memory

### Technical Notes
- Deep copy data to preserve state
- Register callbacks for each action type
- Update menu state on stack changes
- Do not persist undo history

---

## Story 11.2: Keyboard Navigation

**As a** user
**I want** keyboard shortcuts
**So that** I can work efficiently

### Acceptance Criteria

- [ ] **Global Shortcuts:**
  | Shortcut | Action |
  |----------|--------|
  | Ctrl+N | New expense |
  | Ctrl+E | Edit selected expense |
  | Delete | Delete selected expense |
  | Ctrl+F | Focus search box |
  | F5 | Refresh current view |
  | Ctrl+S | Force save |
  | Ctrl+Z | Undo |
  | Ctrl+Y | Redo |
  | Escape | Close dialog / Clear selection |
  | Ctrl+Q | Exit application |

- [ ] **Navigation Shortcuts:**
  | Shortcut | Action |
  |----------|--------|
  | Ctrl+1 | Switch to Dashboard |
  | Ctrl+2 | Switch to Expenses |
  | Ctrl+3 | Switch to Budgets |
  | Ctrl+4 | Switch to Reports |
  | Tab | Move to next field |
  | Shift+Tab | Move to previous field |

- [ ] **List Navigation:**
  | Shortcut | Action |
  |----------|--------|
  | Up/Down | Select previous/next item |
  | Home | Select first item |
  | End | Select last item |
  | Space | Toggle selection |
  | Enter | Open selected item |

### Wireframe: Keyboard Shortcuts Dialog

```
+-------------------------------------------------------------+
|                  Keyboard Shortcuts                      [X] |
+-------------------------------------------------------------+
|                                                              |
|  General                                                     |
|  -------                                                     |
|  Ctrl+N          New expense                                 |
|  Ctrl+E          Edit selected                               |
|  Delete          Delete selected                             |
|  Ctrl+F          Focus search                                |
|  F5              Refresh                                     |
|  Ctrl+S          Save                                        |
|  Ctrl+Z          Undo                                        |
|  Ctrl+Y          Redo                                        |
|  Escape          Close/Clear                                 |
|                                                              |
|  Navigation                                                  |
|  ----------                                                  |
|  Ctrl+1-4        Switch tabs                                 |
|  Tab             Next field                                  |
|  Shift+Tab       Previous field                              |
|                                                              |
|  List Navigation                                             |
|  ---------------                                             |
|  Up/Down         Select item                                 |
|  Enter           Open item                                   |
|  Home/End        First/Last item                             |
|                                                              |
|                                              [Close]         |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Use bind() for keyboard events
- Handle focus properly
- Test on different platforms

---

## Story 11.3: Enhanced Data Validation Summary

**As a** user
**I want** detailed control over data validation display
**So that** I can customize how issues are reported

**Note:** This story enhances the basic Data Load Summary from Story 10.5. The core validation logic is in Story 9.5 (DataIntegrityValidator).

### Acceptance Criteria

- [ ] **Enhanced Display Features** (extends Story 10.5):
  - Severity column (Warning vs Error levels)
  - Table view with sortable columns: Severity, Issue, Location, Action
  - Critical issues highlighted separately
  - "View All" button for detailed issue list

- [ ] **User Preferences:**
  - "Don't show for auto-corrected issues" checkbox
  - Enable/disable validation summary on startup (Settings)
  - Choose to show only errors (hide warnings)

### Wireframe: Data Validation Summary

```
+-------------------------------------------------------------+
|            Data Load Summary                             [X] |
+-------------------------------------------------------------+
|                                                              |
| [check] Loaded 234 expenses                                  |
| [check] Loaded 8 budgets                                     |
| [!] 3 data issue(s) were found and corrected                 |
| [X] 1 critical issue requires attention                      |
|                                                              |
| Issues Found:                                                |
| +-----------------------------------------------------------+
| | Severity | Issue           | Location | Action            |
| +----------+-----------------+----------+-------------------+
| | Warning  | Invalid date    | Row 45   | Set to today      |
| | Warning  | Unknown category| Row 67   | Set to Admin      |
| | Warning  | Negative amount | Row 89   | Made positive     |
| | Error    | Missing vendor  | Row 102  | Review needed     |
| +-----------------------------------------------------------+
|                                                              |
| [ ] Don't show for auto-corrected issues                     |
|                                                              |
|                    [View All] [Export] [OK]                  |
|                                                              |
+-------------------------------------------------------------+
```

---

## Story 11.4: Enhanced Template Manager UI

**As a** user
**I want** a dedicated template management interface
**So that** I can easily manage and organize my expense templates

**Note:** This story enhances the core template functionality defined in Story 2.10 (Quick Add Templates). The ExpenseTemplate model and TemplateManager class are defined in Epic 2.

### Acceptance Criteria

- [ ] Create `ui/dialogs/template_manager_dialog.py`:

- [ ] **Enhanced Template Features:**
  - Dedicated template management dialog (beyond quick-add panel)
  - Sort templates by: most used, name, category, last used
  - Search/filter templates
  - Bulk delete capability
  - Template usage statistics

### Wireframe: Template Manager

```
+-------------------------------------------------------------+
|                  Expense Templates                       [X] |
+-------------------------------------------------------------+
|                                                              |
| Quick Add:                                                   |
| +-----------------------------------------------------------+
| | [Rent Payment] [Electricity] [Internet] [Hair Prod] [+New] |
| +-----------------------------------------------------------+
|                                                              |
| All Templates:                                               |
| +-----------------------------------------------------------+
| | Name              | Category     | Amount   | Uses | Act  |
| +-------------------+--------------+----------+------+------+
| | Rent Payment      | Facilities   | L 36,000 | 12   | [Use]|
| | Electricity       | Facilities   | L 8,500  | 12   | [Use]|
| | Hair Products     | Supplies     | L 5,000  | 8    | [Use]|
| | Staff Salary      | Staff        | L 25,000 | 4    | [Use]|
| +-----------------------------------------------------------+
|                                                              |
|         [New Template]    [Import from Expense]    [Close]   |
|                                                              |
+-------------------------------------------------------------+
```

---

## Story 11.5: Print Support

**As a** user
**I want** to print reports directly
**So that** I have physical records

### Acceptance Criteria

- [ ] **Printable Items:**
  - Expense list (filtered view)
  - Summary report
  - Category breakdown
  - Budget vs actual
  - Custom report

- [ ] **Page Setup:**
  - Paper size (A4, Letter)
  - Orientation (Portrait, Landscape)
  - Margins
  - Header/footer options

- [ ] **Print Preview:**
  - Show how printed page will look
  - Navigate through pages
  - Zoom in/out

- [ ] **Print Actions:**
  - Print to system printer
  - Print to PDF
  - Save as PDF

### Wireframe: Print Dialog

```
+-------------------------------------------------------------+
|                        Print                             [X] |
+-------------------------------------------------------------+
|                                                              |
| What to Print:                                               |
| (o) Current View (Expense List)                              |
| ( ) Summary Report                                           |
| ( ) Category Report                                          |
| ( ) Custom Selection                                         |
|                                                              |
| Page Setup:                                                  |
| Paper Size:     [A4 v]                                       |
| Orientation:    (o) Portrait  ( ) Landscape                  |
|                                                              |
| Include:                                                     |
| [x] Header (salon name, date)                                |
| [x] Footer (page numbers)                                    |
| [ ] Charts                                                   |
|                                                              |
| +-----------------------------------------------------------+
| |                    [PRINT PREVIEW]                        |
| +-----------------------------------------------------------+
|                                                              |
|            [Page Setup...]    [Print]    [Cancel]            |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Use reportlab for print formatting
- System print dialog via win32print or CUPS
- Preview using canvas widget
- Handle pagination properly

---

## Story 11.6: Auto-Export Scheduling

**As a** user
**I want** automatic monthly report generation
**So that** I have regular backups and summaries

### Acceptance Criteria

- [ ] **Schedule Options:**
  - Monthly (specific day)
  - Weekly
  - Custom interval (days)
  - On application startup if due

- [ ] **Export Formats:**
  - PDF Report
  - Excel workbook
  - CSV data files

- [ ] **Report Content:**
  - Summary statistics
  - Category breakdown
  - Budget vs actual
  - Full expense list (optional)

- [ ] **Execution:**
  - Check on startup if export is due
  - Run in background
  - Notify user when complete
  - Log export history

- [ ] **File Management:**
  - Customizable naming pattern
  - Create dated folders
  - Keep history of exports

### Wireframe: Auto-Export Settings

```
+-------------------------------------------------------------+
|                  Auto-Export Settings                    [X] |
+-------------------------------------------------------------+
|                                                              |
| [x] Enable automatic exports                                 |
|                                                              |
| Schedule:                                                    |
| Run on: [1st v] day of each month                            |
|         ( ) Or: Every [___] days                             |
|                                                              |
| Export Format:                                               |
| [x] PDF Report                                               |
| [x] Excel Data                                               |
| [ ] CSV Data                                                 |
|                                                              |
| Report Content:                                              |
| [x] Previous month summary                                   |
| [x] Category breakdown                                       |
| [x] Budget comparison                                        |
| [ ] Full expense list                                        |
|                                                              |
| Output Location:                                             |
| [C:\Users\...\Reports\               ] [Browse...]           |
|                                                              |
| File Naming:                                                 |
| Pattern: [expense_report_{year}_{month}]                     |
| Preview: expense_report_2024_01.pdf                          |
|                                                              |
| Last Export: January 1, 2024 at 09:00 AM                     |
| Next Export: February 1, 2024                                |
|                                                              |
|       [Run Now]            [Save]    [Cancel]                |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Store schedule in settings.json
- Check on each startup
- Use existing PDF/Excel exporters
- Background thread for export

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 11.1 | 2.1 (ExpenseManager), 4.1 (BudgetManager) |
| 11.2 | 10.1 (MainWindow) |
| 11.3 | 9.5 (DataIntegrityValidator), 10.5 (Data Load Summary) |
| 11.4 | 2.10 (Quick Add Templates), 10.1 (MainWindow) |
| 11.5 | 8.1 (PDF Export) |
| 11.6 | 8.1 (PDF), 8.2 (Excel), 10.2 (Startup) |

---

## Testing Requirements

- [ ] Unit tests for UndoManager (stack operations)
- [ ] Unit tests for template CRUD
- [ ] Integration tests for undo/redo with managers
- [ ] UI tests for keyboard shortcuts
- [ ] Tests for print preview generation
- [ ] Tests for scheduled export logic
- [ ] Tests for data validation rules
- [ ] Performance tests for large undo history
