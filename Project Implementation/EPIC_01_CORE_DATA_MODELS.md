# Epic 1: Core Data Models & Project Setup

**Priority:** High
**Dependencies:** None
**Stories:** 7

---

## Story 1.1: Project Structure Setup

**As a** developer
**I want** a well-organized project structure
**So that** code is maintainable and modular

### Acceptance Criteria

- [ ] Create directory structure:
  ```
  irsi-app/
  ├── main.py                    # Entry point
  ├── app.py                     # Application controller
  ├── config.py                  # Application constants
  ├── requirements.txt
  ├── models/                    # Data classes
  │   ├── expense.py
  │   ├── budget.py
  │   ├── category.py
  │   └── template.py
  ├── managers/                  # Business logic
  │   ├── expense_manager.py
  │   ├── budget_manager.py
  │   ├── filter_manager.py
  │   ├── template_manager.py
  │   └── recurring_handler.py
  ├── reports/
  │   └── report_generator.py
  ├── visualization/
  │   └── visualizer.py
  ├── persistence/
  │   └── data_manager.py
  ├── exports/
  │   ├── pdf_exporter.py
  │   ├── excel_exporter.py
  │   └── image_exporter.py
  ├── ui/                        # Tkinter GUI
  │   ├── main_window.py
  │   ├── forms/
  │   │   └── expense_form.py
  │   ├── views/
  │   │   ├── expense_list.py
  │   │   ├── budget_view.py
  │   │   └── reports_view.py
  │   ├── dashboard/
  │   │   └── dashboard_view.py
  │   ├── charts/
  │   │   ├── category_charts.py
  │   │   ├── trend_charts.py
  │   │   └── budget_charts.py
  │   ├── dialogs/
  │   │   ├── settings_dialog.py
  │   │   ├── expense_details.py
  │   │   ├── template_manager.py
  │   │   └── data_summary.py
  │   ├── components/
  │   │   └── filter_panel.py
  │   └── widgets/
  │       └── common_widgets.py
  ├── utils/
  │   ├── validators.py
  │   ├── error_handler.py
  │   ├── exceptions.py
  │   └── formatters.py
  ├── data/                      # Data storage
  │   ├── expenses.csv
  │   ├── budgets.csv
  │   ├── templates.csv
  │   └── settings.json
  ├── logs/
  └── tests/
  ```

- [ ] Create `requirements.txt`:
  ```
  numpy>=1.24.0
  pandas>=2.0.0
  matplotlib>=3.7.0
  seaborn>=0.12.0
  tkcalendar>=1.6.0
  openpyxl>=3.1.0
  reportlab>=4.0.0
  Pillow>=10.0.0
  pytest>=7.0.0
  ```

- [ ] Create `config.py` with constants:
  - APP_NAME, VERSION
  - CURRENCY_CODE ("ALL"), CURRENCY_SYMBOL ("L")
  - DATE_FORMAT ("%d/%m/%Y"), DATETIME_FORMAT
  - DATA_DIR, LOGS_DIR, BACKUP_DIR paths
  - Validation limits (MAX_AMOUNT: 10,000,000)
  - DEFAULT_PAGE_SIZE, MAX_AUTO_BACKUPS
  - DEFAULT_WARNING_THRESHOLD (80%)

---

## Story 1.2: Expense Data Model

**As a** developer
**I want** an Expense class to represent expense records
**So that** expense data is consistently structured

### Acceptance Criteria

- [ ] Create `models/expense.py` with dataclass:

  **Expense Fields:**
  | Field | Type | Description |
  |-------|------|-------------|
  | expense_id | str | UUID, auto-generated |
  | amount | float | Expense amount in ALL |
  | date | datetime | Expense date |
  | category | str | Main category |
  | subcategory | str | Subcategory |
  | vendor | str | Vendor/supplier name |
  | payment_method | str | Cash, Card, Transfer, etc. |
  | description | str | Optional description |
  | tags | List[str] | Optional tags |
  | is_recurring | bool | Recurring flag |
  | recurring_type | str | weekly, monthly, yearly |
  | recurring_action | str | auto_generate, reminder |
  | next_due_date | datetime | Next recurrence date |
  | last_recurring_date | datetime | Last generated date |
  | generated_from_id | str | Parent recurring ID |
  | is_deleted | bool | Soft delete flag |
  | deleted_at | datetime | Deletion timestamp |
  | created_at | datetime | Creation timestamp |
  | updated_at | datetime | Last update timestamp |

  **Methods:**
  ```python
  def to_dict(self) -> dict
      """Convert to dictionary for CSV serialization"""

  @classmethod
  def from_dict(cls, data: dict) -> 'Expense'
      """Create Expense from dictionary (CSV row)"""

  def validate(self) -> List[str]
      """Validate expense and return list of error messages"""

  def mark_deleted(self) -> None
      """Mark expense as soft deleted"""

  def restore(self) -> None
      """Restore soft-deleted expense"""
  ```

### Technical Notes
- Use `uuid.uuid4()` for expense_id generation
- Tags: All models use `List[str]` internally; stored as comma-separated string in CSV
- Use `formatters.format_tags()` and `formatters.parse_tags()` for conversion
- Dates use ISO format for storage, DD/MM/YYYY for display

---

## Story 1.3: Category Model

**As a** developer
**I want** a Category system with predefined salon categories
**So that** expenses are consistently categorized

### Acceptance Criteria

- [ ] Create `models/category.py` with CategoryManager class:

  **Predefined Categories:**
  | Category | Subcategories |
  |----------|---------------|
  | Supplies | Hair products, Nail products, Skincare products, Disposables, Cleaning supplies |
  | Equipment | Styling tools, Furniture, Technology, Maintenance/Repairs |
  | Facilities | Rent, Electricity, Water, Gas, Internet, Insurance |
  | Staff | Salaries, Commissions, Training, Uniforms |
  | Marketing | Advertising, Social media, Promotions, Loyalty programs |
  | Administrative | Software subscriptions, Accounting, Licenses, Bank fees |

  **Category Colors (for charts):**
  | Category | Color |
  |----------|-------|
  | Supplies | #FF6B9D (Pink) |
  | Equipment | #9B59B6 (Purple) |
  | Facilities | #3498DB (Blue) |
  | Staff | #2ECC71 (Green) |
  | Marketing | #F39C12 (Orange) |
  | Administrative | #95A5A6 (Gray) |

  **Methods:**
  ```python
  @classmethod
  def get_categories(cls) -> List[str]
      """Get list of all category names"""

  @classmethod
  def get_subcategories(cls, category: str) -> List[str]
      """Get subcategories for a given category"""

  @classmethod
  def is_valid_category(cls, category: str) -> bool
      """Check if category is valid"""

  @classmethod
  def is_valid_subcategory(cls, category: str, subcategory: str) -> bool
      """Check if subcategory is valid for the given category"""

  @classmethod
  def get_category_color(cls, category: str) -> str
      """Get color for category (for charts)"""
  ```

---

## Story 1.4: Budget Data Model

**As a** developer
**I want** a Budget class to represent budget configurations
**So that** budget tracking is properly structured

### Acceptance Criteria

- [ ] Create `models/budget.py` with dataclass:

  **Budget Fields:**
  | Field | Type | Description |
  |-------|------|-------------|
  | budget_id | str | UUID, auto-generated |
  | name | str | Budget name (e.g., "Monthly Total") |
  | budget_type | str | "total" or "category" |
  | category | str | Category name (if type is "category") |
  | amount | float | Budget amount in ALL |
  | month | int | Month (1-12) |
  | year | int | Year |
  | warning_threshold | float | Percentage for warning (default 80) |
  | enable_rollover | bool | Enable unused budget rollover (default False) |
  | rollover_amount | float | Amount rolled over from previous month |
  | rollover_cap_percent | float | Max rollover as % of budget (default 50) |
  | is_active | bool | Active vs archived |
  | created_at | datetime | Creation timestamp |
  | updated_at | datetime | Last update timestamp |

  **Methods:**
  ```python
  def to_dict(self) -> dict
      """Convert to dictionary for CSV serialization"""

  @classmethod
  def from_dict(cls, data: dict) -> 'Budget'
      """Create Budget from dictionary"""

  def get_period_start(self) -> date
      """Get first day of the budget month"""

  def get_period_end(self) -> date
      """Get last day of the budget month"""

  def is_current_period(self) -> bool
      """Check if budget is for the current month"""

  def get_period_display(self) -> str
      """Get display string (e.g., 'January 2024')"""

  def get_effective_budget(self) -> float
      """Get budget amount including any rollover"""

  def calculate_rollover(self, spent: float) -> float
      """Calculate rollover amount for next month (capped by rollover_cap_percent)"""
  ```

### Technical Notes
- Budget period is always calendar month (1st to last day)
- Warning threshold triggers alert at specified percentage
- Rollover is calculated as min(remaining, budget * rollover_cap_percent / 100)

---

## Story 1.5: Payment Method Constants

**As a** developer
**I want** predefined payment methods
**So that** payment tracking is consistent

### Acceptance Criteria

- [ ] Define in `config.py`:
  ```python
  PAYMENT_METHODS = [
      "Cash",
      "Debit Card",
      "Credit Card",
      "Bank Transfer"
  ]
  ```

- [ ] Helper functions:
  ```python
  def is_valid_payment_method(method: str) -> bool
      """Check if payment method is valid"""

  def get_payment_methods() -> list
      """Get list of valid payment methods"""
  ```

---

## Story 1.6: CSV File Templates

**As a** developer
**I want** CSV file templates with proper headers
**So that** data files are ready for use

### Acceptance Criteria

- [ ] Create `data/expenses.csv` with headers:
  ```
  expense_id,amount,date,category,subcategory,vendor,payment_method,
  description,tags,is_recurring,recurring_type,recurring_action,
  next_due_date,last_recurring_date,generated_from_id,is_deleted,
  deleted_at,created_at,updated_at
  ```

- [ ] Create `data/budgets.csv` with headers:
  ```
  budget_id,name,budget_type,category,amount,month,year,
  warning_threshold,enable_rollover,rollover_amount,rollover_cap_percent,
  is_active,created_at,updated_at
  ```

- [ ] Create `data/templates.csv` with headers:
  ```
  template_id,name,category,subcategory,vendor,typical_amount,
  payment_method,description,tags,use_count,last_used,created_at
  ```

- [ ] Create `data/settings.json` with default settings:
  - General: salon_name, salon_address, date_format
  - Backup: auto_backup, backup_location, retention_days
  - Alerts: warning_threshold, show_notifications
  - Display: theme, default_view, page_size
  - Data: auto_save, duplicate_detection

---

## Story 1.7: Formatters Utility

**As a** developer
**I want** consistent formatting utilities
**So that** display is uniform across the application

### Acceptance Criteria

- [ ] Create `utils/formatters.py`:

  **Functions:**
  ```python
  def format_currency(amount: float, include_symbol: bool = True) -> str
      """Format as 'L 1,234.56'"""

  def format_date(dt: datetime) -> str
      """Format as '15/01/2024'"""

  def format_datetime(dt: datetime) -> str
      """Format as '15/01/2024 14:30'"""

  def parse_date(date_str: str) -> Optional[datetime]
      """Parse 'DD/MM/YYYY' to datetime"""

  def parse_date_flexible(date_str: str) -> Optional[datetime]
      """Parse with multiple format support"""

  def truncate_text(text: str, max_length: int = 30) -> str
      """Truncate with ellipsis"""

  def format_percentage(value: float, decimals: int = 1) -> str
      """Format as '85.5%'"""

  def format_number(value: float, decimals: int = 2) -> str
      """Format with thousand separators"""

  def format_period(month: int, year: int) -> str
      """Format as 'January 2024'"""

  def format_tags(tags: list) -> str
      """Convert list to comma-separated string"""

  def parse_tags(tags_str: str) -> list
      """Convert comma-separated string to list"""
  ```

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 1.2 | 1.1 |
| 1.3 | 1.1 |
| 1.4 | 1.1 |
| 1.5 | 1.1 |
| 1.6 | 1.1 |
| 1.7 | 1.1 |

---

## Testing Requirements

- [ ] Unit tests for Expense model (to_dict, from_dict, validate)
- [ ] Unit tests for Budget model (period calculations)
- [ ] Unit tests for CategoryManager (all validation methods)
- [ ] Unit tests for formatters (all format/parse functions)
- [ ] Integration test: save and load expense through full cycle
