# Beauty Salon Expense Management Application

## Project Description

A Python application designed to help beauty salon owners and managers track, analyze, and optimize their business expenses. The application enables users to record expenses across salon-specific categories, set budgets, monitor spending patterns, and generate insightful reports to improve financial decision-making.

**Technology Stack:** Python 3.x, NumPy, Pandas, Matplotlib/Seaborn, Tkinter

---

## Configuration Decisions

| Setting | Decision |
|---------|----------|
| **User Interface** | GUI with Tkinter |
| **Currency** | ALL (Albanian Lek) - symbol: L |
| **Date Format** | DD/MM/YYYY |
| **Budget Period** | Calendar month (1st to end of month) |
| **Payment Methods** | Cash, Debit Card, Credit Card, Bank Transfer |
| **Recurring Expenses** | User chooses per expense: auto-generate OR reminder only |
| **Locations** | Single salon location |

---

## Epic 1: Core Data Models & Project Setup

**Goal:** Establish the foundational architecture and data structures for the application.

### User Stories

1.1 **Project Initialization**
- Set up Python project structure with modular organization
- Create `requirements.txt` with dependencies (numpy, pandas, matplotlib, seaborn)
- Establish CSV file structure for data persistence

1.2 **Expense Data Model**
- Create `Expense` class with salon-specific attributes:
  - `expense_id`: Unique identifier
  - `amount`: Expense amount (float)
  - `date`: Date of expense (datetime)
  - `category`: Salon expense category (see categories below)
  - `subcategory`: Detailed subcategory
  - `vendor`: Supplier/vendor name
  - `payment_method`: Cash, Card, Bank Transfer, etc.
  - `description`: Notes about the expense
  - `recurring`: Boolean flag for recurring expenses
  - `tags`: Custom tags for flexible categorization

1.3 **Salon Expense Categories**
Define domain-specific categories:
| Category | Subcategories |
|----------|---------------|
| Supplies | Hair products, Nail products, Skincare, Disposables, Cleaning supplies |
| Equipment | Styling tools, Furniture, Technology, Maintenance/Repairs |
| Facilities | Rent, Utilities (electric, water, gas), Internet, Insurance |
| Staff | Salaries, Commissions, Training, Uniforms |
| Marketing | Advertising, Social media, Promotions, Loyalty programs |
| Administrative | Software subscriptions, Accounting, Licenses, Bank fees |

### Deliverables
- [ ] `models/expense.py` - Expense data class
- [ ] `models/category.py` - Category definitions and validation
- [ ] `data/expenses.csv` - CSV template with headers
- [ ] `requirements.txt` - Project dependencies

---

## Epic 2: Expense Management (CRUD Operations)

**Goal:** Implement core functionality to add, view, edit, and delete expense records.

### User Stories

2.1 **Add Expense**
- Input form for all expense fields
- Auto-suggest vendors based on history
- Validate amount (positive numbers), date format, and category
- Support for recurring expense setup (weekly, monthly, yearly)

2.2 **View Expenses**
- Display all expenses in tabular format
- Show summary statistics at the top (total, count, average)
- Pagination for large datasets

2.3 **Edit Expense**
- Select expense by ID or from filtered list
- Modify any field with validation
- Track modification timestamp

2.4 **Delete Expense**
- Soft delete with confirmation prompt
- Option to permanently remove or archive
- Bulk delete capability for selected records

### Deliverables
- [ ] `managers/expense_manager.py` - ExpenseManager class with CRUD methods
- [ ] Input validation utilities
- [ ] Unit tests for CRUD operations

---

## Epic 3: Dynamic Filtering & Sorting

**Goal:** Enable users to quickly find and organize expenses based on various criteria.

### User Stories

3.1 **Filter by Date Range**
- Quick filters: Today, This Week, This Month, This Quarter, This Year
- Custom date range picker
- Compare periods (e.g., this month vs. last month)

3.2 **Filter by Category/Subcategory**
- Single or multi-select category filtering
- Hierarchical filtering (category → subcategory)

3.3 **Filter by Amount Range**
- Min/max amount filters
- Preset ranges: Under $50, $50-$200, $200-$500, Over $500

3.4 **Filter by Vendor**
- Search vendors by name
- Top vendors quick-select

3.5 **Filter by Payment Method**
- Filter by specific payment types
- Useful for reconciliation

3.6 **Advanced Sorting**
- Sort by any column (date, amount, category, vendor)
- Ascending/descending toggle
- Multi-column sorting

3.7 **Search by Tags/Description**
- Free-text search across description and tags
- Tag-based filtering

### Deliverables
- [ ] `managers/filter_manager.py` - Filtering logic
- [ ] Filter presets configuration
- [ ] Combined filter/sort functionality

---

## Epic 4: Budget Tracking & Alerts

**Goal:** Help salon owners set budgets and receive alerts when approaching or exceeding limits.

### User Stories

4.1 **Set Monthly Budget**
- Define overall monthly expense budget
- Track spending against budget in real-time
- Visual progress bar showing budget consumption

4.2 **Category-Specific Budgets**
- Set individual budgets per category (e.g., Supplies: $2,000/month)
- Independent tracking for each category
- Rollover option for unused budget

4.3 **Overspending Alerts**
- Warning at 80% of budget consumed
- Critical alert when budget exceeded
- Summary notifications on application startup

4.4 **Budget History**
- Track budget vs. actual over time
- Identify consistently over/under budget categories
- Suggest budget adjustments based on trends

### Deliverables
- [ ] `models/budget.py` - Budget data model
- [ ] `managers/budget_manager.py` - Budget tracking logic
- [ ] `data/budgets.csv` - Budget configuration storage
- [ ] Alert notification system

---

## Epic 5: Advanced Reporting & Analytics

**Goal:** Generate comprehensive reports to understand spending patterns and support business decisions.

### User Stories

5.1 **Statistical Summary Reports**
Using NumPy for calculations:
- Total expenses (overall and by category)
- Average expense amount
- Median expense (typical spending)
- Min/Max expenses
- Standard deviation (spending consistency)

5.2 **Category Analysis**
- Category-wise totals with percentages of total spend
- Subcategory breakdown within each category
- Category comparison (current vs. previous period)

5.3 **Trend Analysis**
- Monthly expense trends (line charts)
- Quarterly summaries
- Year-over-year comparison
- Identify seasonal patterns (e.g., higher supply costs in summer)

5.4 **Vendor Analysis**
- Top N vendors by total spend
- Vendor payment frequency
- Average transaction size per vendor

5.5 **Top Expenses Report**
- Identify largest N expenses
- Highlight unusual/outlier expenses
- Recurring large expenses tracking

5.6 **Custom Date Range Reports**
- Flexible start/end date selection
- Compare any two periods
- Export custom reports

5.7 **Cash Flow Analysis**
- Daily/weekly/monthly cash outflow
- Payment method distribution
- Recurring vs. one-time expense ratio

### Deliverables
- [ ] `reports/report_generator.py` - ReportGenerator class
- [ ] Statistical calculation methods using NumPy
- [ ] Report templates for each report type

---

## Epic 6: Visual Analytics & Dashboards

**Goal:** Provide clear, informative charts and visualizations for expense data.

### User Stories

6.1 **Category Distribution Charts**
- Pie chart: Percentage of total spend by category
- Bar chart: Absolute amounts by category
- Horizontal bar for easy comparison

6.2 **Trend Visualization**
- Line chart: Monthly expense trend
- Line chart: Yearly expense trend with year-over-year comparison
- Area chart: Cumulative spending over time
- Multi-line for category comparison

6.3 **Budget vs. Actual Charts**
- Grouped bar chart comparing budget to actual
- Gauge charts for budget consumption
- Traffic light indicators (green/yellow/red)

6.4 **Vendor Insights**
- Bar chart: Top 10 vendors
- Treemap: Spend distribution across vendors

6.5 **Payment Method Analysis**
- Pie chart: Payment method distribution
- Stacked bar: Payment methods over time

6.6 **Interactive Dashboard**
- Summary KPIs at top (Total, Budget Status, Top Category)
- Multiple charts on single view
- Filter controls affecting all charts

### Deliverables
- [ ] `visualization/visualizer.py` - Visualizer class
- [ ] Chart generation methods using Matplotlib/Seaborn
- [ ] Dashboard layout configuration
- [ ] Color scheme aligned with salon branding

---

## Epic 7: Data Persistence & File Management

**Goal:** Ensure reliable saving and loading of all application data.

### User Stories

7.1 **CSV Data Storage**
- Save expenses to `data/expenses.csv`
- Save budgets to `data/budgets.csv`
- Save settings to `data/settings.csv`

7.2 **Data Loading**
- Load all data into Pandas DataFrames at startup
- Handle missing files gracefully (create defaults)
- Validate data integrity on load

7.3 **Auto-Save**
- Save changes automatically on each modification
- Backup previous version before overwriting
- Save on application close

7.4 **Data Backup & Recovery**
- Manual backup creation
- Restore from backup option
- Export full data archive

7.5 **Data Import**
- Import expenses from external CSV
- Map columns to expected format
- Validate and report import results

### Deliverables
- [ ] `persistence/data_manager.py` - File I/O operations
- [ ] Backup/restore utilities
- [ ] Import validation and mapping

---

## Epic 8: Export & Reporting Output

**Goal:** Enable users to export data and reports for sharing and record-keeping.

### User Stories

8.1 **PDF Report Export**
- Generate formatted PDF reports
- Include summary statistics and charts
- Professional layout with salon branding option

8.2 **Excel Export**
- Export filtered expense data to Excel (.xlsx)
- Multiple sheets (Summary, Details, Charts)
- Formatted tables with headers

8.3 **Chart Image Export**
- Save individual charts as PNG/JPG
- High resolution for printing
- Batch export all dashboard charts

8.4 **Scheduled Reports**
- Configure automatic report generation
- Monthly expense summary email-ready export
- End-of-year financial summary

### Deliverables
- [ ] `exports/pdf_exporter.py` - PDF generation
- [ ] `exports/excel_exporter.py` - Excel export
- [ ] `exports/image_exporter.py` - Chart image export
- [ ] Report templates

---

## Epic 9: Error Handling & Validation

**Goal:** Ensure the application handles errors gracefully and validates all user inputs.

### User Stories

9.1 **Input Validation**
- Validate expense amount (positive numbers, reasonable range)
- Validate date format (consistent format, not future dates for expenses)
- Validate category (must exist in predefined list)
- Validate payment method (must be valid option)
- Validate required fields are not empty

9.2 **File Error Handling**
- Handle missing CSV files gracefully (create with defaults)
- Handle malformed/corrupted CSV files (report error, offer recovery)
- Handle file permission errors (read-only, locked files)
- Handle disk space issues during save

9.3 **Data Integrity Errors**
- Handle duplicate expense IDs
- Handle invalid data types in loaded files
- Handle missing required columns in CSV
- Validate data consistency on load

9.4 **User Feedback**
- Display clear, actionable error messages
- Log errors for debugging (with timestamps)
- Provide recovery suggestions where possible
- Confirmation prompts for destructive actions

9.5 **Graceful Degradation**
- Continue operation when non-critical errors occur
- Partial data recovery from corrupted files
- Fallback defaults when configuration is invalid

### Deliverables
- [ ] `utils/validators.py` - Input validation functions
- [ ] `utils/error_handler.py` - Centralized error handling
- [ ] `logs/` - Error logging directory
- [ ] Custom exception classes for domain-specific errors

---

## Technical Architecture

### Class Structure (OOP)

```
├── models/
│   ├── expense.py          # Expense data class
│   ├── budget.py           # Budget data class
│   └── category.py         # Category definitions
├── managers/
│   ├── expense_manager.py  # CRUD operations
│   ├── budget_manager.py   # Budget tracking
│   └── filter_manager.py   # Filtering/sorting
├── reports/
│   └── report_generator.py # Statistical reports
├── visualization/
│   └── visualizer.py       # Charts and dashboards (Matplotlib/Seaborn)
├── persistence/
│   └── data_manager.py     # File I/O
├── exports/
│   ├── pdf_exporter.py     # ReportLab PDF generation
│   ├── excel_exporter.py   # openpyxl Excel export
│   └── image_exporter.py   # Chart image export
├── ui/                     # Tkinter GUI components
│   ├── main_window.py      # Main application window
│   ├── expense_form.py     # Add/Edit expense dialog
│   ├── expense_list.py     # Expense list with filters
│   ├── budget_view.py      # Budget management view
│   ├── reports_view.py     # Reports interface
│   ├── dashboard.py        # Dashboard with KPIs and charts
│   └── dialogs.py          # Common dialogs (confirm, error, etc.)
├── utils/
│   ├── validators.py       # Input validation
│   ├── error_handler.py    # Centralized error handling
│   ├── exceptions.py       # Custom exception classes
│   └── formatters.py       # Currency, date formatting
├── data/
│   ├── expenses.csv
│   ├── budgets.csv
│   └── settings.json
├── logs/                   # Error and activity logs
├── config.py               # Application constants
└── main.py                 # Application entry point
```

### Key Libraries Usage

| Library | Usage |
|---------|-------|
| **NumPy** | Statistical calculations (sum, mean, median, std, min, max) |
| **Pandas** | DataFrame operations, filtering, grouping, CSV I/O |
| **Matplotlib** | Bar charts, line charts, pie charts |
| **Seaborn** | Enhanced visualizations, color palettes |
| **Tkinter** | GUI framework (built-in) |
| **tkcalendar** | Date picker widget |
| **ReportLab** | PDF report generation |
| **openpyxl** | Excel file export |
| **Pillow** | Image processing for chart export |

### Data Structures

| Structure | Usage | Example |
|-----------|-------|---------|
| **Lists** | Ordered collections of expenses, categories, filter results | `expenses_list = [expense1, expense2, ...]` |
| **Dictionaries** | Key-value mappings for categories, settings, lookups | `categories = {"Supplies": ["Hair", "Nails"], ...}` |
| **Pandas DataFrame** | Primary in-memory storage for expense data, filtering, grouping, aggregation | `df = pd.DataFrame(expenses)` |
| **NumPy Arrays** | Numerical calculations on expense amounts | `amounts = np.array(df['amount'])` |
| **Sets** | Unique tags, vendors, payment methods for dropdowns | `unique_vendors = set(df['vendor'])` |
| **Tuples** | Immutable data like date ranges, min/max pairs | `date_range = (start_date, end_date)` |

---

## Implementation Priority

| Priority | Epic | Rationale |
|----------|------|-----------|
| 1 | Epic 1: Core Data Models | Foundation for all other features |
| 2 | Epic 9: Error Handling | Integrated early to ensure robust foundation |
| 3 | Epic 2: CRUD Operations | Essential functionality |
| 4 | Epic 7: Data Persistence | Required for usable application |
| 5 | Epic 3: Filtering & Sorting | Core usability feature |
| 6 | Epic 4: Budget Tracking | Key business value feature |
| 7 | Epic 5: Reporting | Business insights |
| 8 | Epic 6: Visualizations | Enhanced analytics |
| 9 | Epic 8: Export | Nice-to-have for sharing |

---

## Sample Expense Categories for Beauty Salons

### Supplies (Consumables)
- Hair: Shampoo, conditioner, hair dye, bleach, styling products, developer
- Nails: Polish, gel, acrylics, acetone, nail files, buffers
- Skincare: Cleansers, masks, moisturizers, serums, wax
- Disposables: Gloves, capes, towels, cotton pads, applicators

### Equipment
- Styling: Scissors, clippers, dryers, straighteners, curling irons
- Furniture: Styling chairs, wash stations, manicure tables
- Technology: POS system, booking software, computers

### Facilities
- Rent/Lease payments
- Utilities: Electricity, water, gas, HVAC
- Internet and phone
- Insurance (liability, property)

### Staff
- Wages and salaries
- Commissions
- Training and certifications
- Uniforms and dress code items

### Marketing
- Social media advertising
- Print materials (business cards, flyers)
- Website maintenance
- Loyalty program costs
- Promotions and discounts

### Administrative
- Accounting services
- Software subscriptions (booking, payroll)
- Business licenses and permits
- Bank fees and payment processing
