# Implementation Order & Dependencies

This document outlines the recommended implementation order for the Beauty Salon Expense Manager application.

---

## Phase 1: Foundation (Must Complete First)

### Epic 1: Core Data Models & Project Setup
**Duration:** First
**Dependencies:** None
**Key Deliverables:**
- Project directory structure
- `requirements.txt` with all dependencies
- `config.py` with constants
- Expense dataclass with all fields
- Budget dataclass with rollover support
- CategoryManager with 6 categories
- Formatters utility module
- CSV file templates

**Files Created:**
- `config.py`
- `models/expense.py`
- `models/budget.py`
- `models/category.py`
- `utils/formatters.py`
- `data/*.csv` (templates)
- `data/settings.json`

---

### Epic 9: Error Handling & Validation
**Duration:** After Epic 1
**Dependencies:** Epic 1 (config, models)
**Key Deliverables:**
- Custom exception hierarchy
- Input validators for all fields
- ErrorHandler singleton service
- DataCorrection utilities

**Files Created:**
- `utils/exceptions.py`
- `utils/validators.py`
- `utils/error_handler.py`
- `utils/data_correction.py`

---

## Phase 2: Core Functionality

### Epic 7: Data Persistence
**Duration:** After Epic 9
**Dependencies:** Epic 1 (models), Epic 9 (error handling)
**Key Deliverables:**
- DataManager class for CSV I/O
- Atomic file writes (temp + rename)
- Backup/restore with ZIP
- Settings management

**Files Created:**
- `persistence/data_manager.py`
- `persistence/backup_manager.py`
- `persistence/settings_manager.py`

---

### Epic 2: Expense Management CRUD
**Duration:** After Epic 7
**Dependencies:** Epic 1, Epic 7, Epic 9
**Key Deliverables:**
- ExpenseManager with full CRUD
- UndoManager for reversible operations
- Duplicate detection
- ExpenseTemplate model
- TemplateManager

**Files Created:**
- `managers/expense_manager.py`
- `managers/undo_manager.py`
- `managers/template_manager.py`
- `models/template.py`

---

## Phase 3: Business Logic

### Epic 3: Filtering & Sorting
**Duration:** After Epic 2
**Dependencies:** Epic 1 (models), Epic 2 (ExpenseManager)
**Key Deliverables:**
- FilterCriteria dataclass
- FilterManager with all filters
- Sorting by multiple fields
- Date range presets

**Files Created:**
- `models/filter_criteria.py`
- `managers/filter_manager.py`

---

### Epic 4: Budget Management
**Duration:** After Epic 3
**Dependencies:** Epic 1, Epic 2, Epic 3, Epic 7
**Key Deliverables:**
- BudgetManager with CRUD
- Budget tracking (spent, remaining)
- Warning alerts
- Rollover calculations

**Files Created:**
- `managers/budget_manager.py`

---

## Phase 4: Analytics & Visualization

### Epic 5: Reporting & Analytics
**Duration:** After Epic 4
**Dependencies:** Epic 1-4
**Key Deliverables:**
- ReportGenerator with statistics
- StatisticalSummary dataclass
- Trend analysis
- Comparative reports

**Files Created:**
- `reports/report_generator.py`
- `models/statistical_summary.py`

---

### Epic 6: Visualization & Dashboards
**Duration:** After Epic 5
**Dependencies:** Epic 5 (ReportGenerator)
**Key Deliverables:**
- Visualizer with chart creation
- Dashboard widgets
- Interactive chart UI
- All chart types (pie, bar, line, heatmap)

**Files Created:**
- `visualization/visualizer.py`
- `visualization/chart_widgets.py`
- `ui/dashboard/` components

---

## Phase 5: Export & Integration

### Epic 8: Export Functionality
**Duration:** After Epic 6
**Dependencies:** Epic 5, Epic 6
**Key Deliverables:**
- PDF exporter (ReportLab)
- Excel exporter (openpyxl)
- Chart image exporter
- Print functionality

**Files Created:**
- `exports/pdf_exporter.py`
- `exports/excel_exporter.py`
- `exports/image_exporter.py`

---

### Epic 10: Main Application Integration
**Duration:** After Epic 8
**Dependencies:** All previous Epics
**Key Deliverables:**
- MainWindow with menus and toolbar
- Application controller
- SplashScreen
- RecurringHandler
- SettingsDialog
- All UI forms and dialogs

**Files Created:**
- `main.py`
- `app.py`
- `ui/main_window.py`
- `ui/splash_screen.py`
- `ui/settings_dialog.py`
- `managers/recurring_handler.py`
- All `ui/forms/`, `ui/dialogs/` components

---

### Epic 11: Optional Enhancements (If Time Permits)
**Duration:** After Epic 10
**Dependencies:** All Epics
**Key Deliverables:**
- Bulk operations UI
- Template management UI
- Import from external sources
- Enhanced duplicate detection

---

## Critical Path

```
Epic 1 -> Epic 9 -> Epic 7 -> Epic 2 -> Epic 3 -> Epic 4 -> Epic 5 -> Epic 6 -> Epic 8 -> Epic 10 -> Epic 11
```

## Parallel Development Opportunities

Once Epic 2 is complete, the following can be developed in parallel:
- Epic 3, 4, 5 can be developed concurrently (different teams/developers)
- Epic 6 must wait for Epic 5
- Epic 8 must wait for Epic 5, 6
- Epic 10 integrates everything

## Key Interface Points

| From Epic | To Epic | Interface |
|-----------|---------|-----------|
| Epic 1 | All | Expense, Budget dataclasses |
| Epic 9 | All | ErrorHandler, validators, exceptions |
| Epic 7 | Epic 2, 4 | DataManager |
| Epic 2 | Epic 3, 5, 10 | ExpenseManager |
| Epic 4 | Epic 5, 10 | BudgetManager |
| Epic 5 | Epic 6, 8 | ReportGenerator |
| Epic 6 | Epic 8, 10 | Visualizer |

## Discrepancies Fixed (Review Notes)

The following inconsistencies were identified and corrected during review:

1. **Recurring Types Standardized**
   - Old: `weekly, monthly, yearly`
   - New: `daily, weekly, biweekly, monthly, quarterly, annually`
   - Updated in: EPIC_01, EPIC_09, EPIC_10

2. **Field Name Standardized**
   - Old: `generated_from_id`
   - New: `recurring_parent_id`
   - Updated in: EPIC_01, EPIC_07

3. **Dependency Added**
   - Added `python-dateutil>=2.8.0` for `relativedelta` support
   - Updated in: EPIC_01 requirements.txt, CLAUDE.md

4. **RecurringHandler Field Reference Fixed**
   - Old: `expense.recurring_frequency`
   - New: `expense.recurring_type`
   - Updated in: EPIC_10

5. **MainWindow Constructor Fixed (Second Review)**
   - Issue: MainWindow was creating its own `tk.Tk()` root, causing duplicate root windows
   - Fix: MainWindow now accepts `root` as first parameter from main.py
   - Updated in: EPIC_10 (Task 10.1.2, Task 10.2.2)

6. **DataManager Settings Methods Added (Second Review)**
   - Added: `get_settings()` - returns cached settings
   - Added: `update_settings()` - updates and saves settings
   - Updated in: EPIC_07 (Task 7.1.7)

7. **TemplateManager Full Implementation Added (Second Review)**
   - Added complete implementation with all CRUD methods
   - Methods: save_templates, get_all_templates, get_template, add_template, update_template, delete_template, create_from_expense, search_templates
   - Updated in: EPIC_02 (Task 2.10.2)

8. **StartupAlertsDialog Implementation Added (Second Review)**
   - Added `show_startup_alerts()` function used by main.py
   - Added full `StartupAlertsDialog` class implementation
   - Updated in: EPIC_10 (Task 10.5.2)

---

## Testing Strategy

Each Epic should be tested before moving to the next:

1. **Unit Tests:** Required for all models and managers
2. **Integration Tests:** Required between dependent Epics
3. **Manual Testing:** UI components in Epic 10

Run tests after each Epic:
```bash
python -m pytest tests/ -v
```

---

## Definition of Done

An Epic is considered complete when:
- [ ] All tasks marked complete
- [ ] All unit tests passing
- [ ] All integration points verified
- [ ] Code follows project standards (PEP 8)
- [ ] Error handling integrated
- [ ] Logging implemented
