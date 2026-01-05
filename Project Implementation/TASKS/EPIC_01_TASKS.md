# Epic 1: Core Data Models & Project Setup

**Priority:** High (Foundation)
**Dependencies:** None
**Stories:** 7

> Reference: [EPIC_01_CORE_DATA_MODELS.md](../EPIC_01_CORE_DATA_MODELS.md)

---

## Story 1.1: Project Structure Setup

**Prerequisites:** None

### Tasks

- [ ] **1.1.1** Create root project directory structure
  ```bash
  mkdir -p irsi-app/{models,managers,reports,visualization,persistence,exports,utils,data,logs,tests}
  mkdir -p irsi-app/ui/{forms,views,dashboard,charts,dialogs,components,widgets}
  mkdir -p irsi-app/tests/{test_models,test_managers,test_persistence,test_utils}
  ```

- [ ] **1.1.2** Create `__init__.py` files for all packages
  ```bash
  touch irsi-app/{models,managers,reports,visualization,persistence,exports,utils,ui}/__init__.py
  touch irsi-app/ui/{forms,views,dashboard,charts,dialogs,components,widgets}/__init__.py
  touch irsi-app/tests/{__init__,test_models/__init__,test_managers/__init__,test_persistence/__init__,test_utils/__init__}.py
  ```

- [ ] **1.1.3** Create `requirements.txt`
  ```
  numpy>=1.24.0
  pandas>=2.0.0
  matplotlib>=3.7.0
  seaborn>=0.12.0
  tkcalendar>=1.6.0
  openpyxl>=3.1.0
  reportlab>=4.0.0
  Pillow>=10.0.0
  python-dateutil>=2.8.0
  pytest>=7.0.0
  ```

- [ ] **1.1.4** Create `config.py` with application constants
  ```python
  # Application info
  APP_NAME = "Beauty Salon Expense Manager"
  VERSION = "1.0.0"

  # Currency
  CURRENCY_CODE = "ALL"
  CURRENCY_SYMBOL = "L"

  # Date formats
  DATE_FORMAT = "%d/%m/%Y"
  DATETIME_FORMAT = "%d/%m/%Y %H:%M"
  DATE_FORMAT_ISO = "%Y-%m-%d"

  # Paths
  import os
  BASE_DIR = os.path.dirname(os.path.abspath(__file__))
  DATA_DIR = os.path.join(BASE_DIR, "data")
  LOGS_DIR = os.path.join(BASE_DIR, "logs")
  BACKUP_DIR = os.path.join(DATA_DIR, "backups")

  # Validation limits
  MAX_AMOUNT = 10_000_000
  MIN_AMOUNT = 0.01
  MAX_DESCRIPTION_LENGTH = 500

  # Display settings
  DEFAULT_PAGE_SIZE = 50
  MAX_AUTO_BACKUPS = 7
  DEFAULT_WARNING_THRESHOLD = 80

  # Payment methods
  PAYMENT_METHODS = ["Cash", "Debit Card", "Credit Card", "Bank Transfer"]

  # Recurring types
  RECURRING_TYPES = ["daily", "weekly", "biweekly", "monthly", "quarterly", "annually"]
  RECURRING_ACTIONS = ["auto_generate", "reminder"]
  ```

- [ ] **1.1.5** Create `main.py` entry point (placeholder)
  ```python
  """Beauty Salon Expense Manager - Entry Point"""

  def main():
      """Application entry point."""
      print("Beauty Salon Expense Manager - Starting...")
      # TODO: Initialize application in Epic 10

  if __name__ == "__main__":
      main()
  ```

- [ ] **1.1.6** Create `app.py` application controller (placeholder)
  ```python
  """Application Controller"""

  class Application:
      """Main application controller."""

      def __init__(self):
          """Initialize application."""
          pass  # TODO: Implement in Epic 10

      def run(self):
          """Start the application."""
          pass  # TODO: Implement in Epic 10
  ```

- [ ] **1.1.7** Verify structure and run initial test
  ```bash
  pip install -r requirements.txt
  python main.py
  ```

### Completion Checklist
- [ ] All directories created
- [ ] All `__init__.py` files in place
- [ ] `requirements.txt` complete and dependencies install
- [ ] `config.py` has all constants
- [ ] `main.py` runs without error

---

## Story 1.2: Expense Data Model

**Prerequisites:** Story 1.1

### Tasks

- [ ] **1.2.1** Create `models/expense.py` with imports
  ```python
  """Expense data model."""
  from dataclasses import dataclass, field
  from datetime import datetime
  from typing import List, Optional
  import uuid
  ```

- [ ] **1.2.2** Define Expense dataclass with all fields
  ```python
  @dataclass
  class Expense:
      """Represents a single expense record."""

      # Required fields
      amount: float
      date: datetime
      category: str
      subcategory: str
      vendor: str
      payment_method: str

      # Optional fields
      description: str = ""
      tags: List[str] = field(default_factory=list)

      # Recurring fields
      is_recurring: bool = False
      recurring_type: Optional[str] = None  # daily, weekly, biweekly, monthly, quarterly, annually
      recurring_action: Optional[str] = None  # auto_generate, reminder
      next_due_date: Optional[datetime] = None
      last_recurring_date: Optional[datetime] = None
      recurring_parent_id: Optional[str] = None  # ID of parent recurring expense

      # Soft delete
      is_deleted: bool = False
      deleted_at: Optional[datetime] = None

      # Metadata
      expense_id: str = field(default_factory=lambda: str(uuid.uuid4()))
      created_at: datetime = field(default_factory=datetime.now)
      updated_at: datetime = field(default_factory=datetime.now)
  ```

- [ ] **1.2.3** Implement `to_dict()` method
  ```python
  def to_dict(self) -> dict:
      """Convert expense to dictionary for CSV serialization."""
      return {
          'expense_id': self.expense_id,
          'amount': self.amount,
          'date': self.date.strftime('%Y-%m-%d') if self.date else '',
          'category': self.category,
          'subcategory': self.subcategory,
          'vendor': self.vendor,
          'payment_method': self.payment_method,
          'description': self.description,
          'tags': ','.join(self.tags) if self.tags else '',
          'is_recurring': self.is_recurring,
          'recurring_type': self.recurring_type or '',
          'recurring_action': self.recurring_action or '',
          'next_due_date': self.next_due_date.strftime('%Y-%m-%d') if self.next_due_date else '',
          'last_recurring_date': self.last_recurring_date.strftime('%Y-%m-%d') if self.last_recurring_date else '',
          'recurring_parent_id': self.recurring_parent_id or '',
          'is_deleted': self.is_deleted,
          'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else '',
          'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
          'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
      }
  ```

- [ ] **1.2.4** Implement `from_dict()` class method
  ```python
  @classmethod
  def from_dict(cls, data: dict) -> 'Expense':
      """Create Expense from dictionary (CSV row)."""
      from utils.formatters import parse_tags

      def parse_date(date_str, format='%Y-%m-%d'):
          if not date_str:
              return None
          try:
              return datetime.strptime(date_str, format)
          except ValueError:
              return None

      def parse_datetime(dt_str):
          if not dt_str:
              return None
          try:
              return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
          except ValueError:
              return None

      return cls(
          expense_id=data.get('expense_id', str(uuid.uuid4())),
          amount=float(data.get('amount', 0)),
          date=parse_date(data.get('date')) or datetime.now(),
          category=data.get('category', ''),
          subcategory=data.get('subcategory', ''),
          vendor=data.get('vendor', ''),
          payment_method=data.get('payment_method', ''),
          description=data.get('description', ''),
          tags=parse_tags(data.get('tags', '')),
          is_recurring=str(data.get('is_recurring', 'False')).lower() == 'true',
          recurring_type=data.get('recurring_type') or None,
          recurring_action=data.get('recurring_action') or None,
          next_due_date=parse_date(data.get('next_due_date')),
          last_recurring_date=parse_date(data.get('last_recurring_date')),
          recurring_parent_id=data.get('recurring_parent_id') or None,
          is_deleted=str(data.get('is_deleted', 'False')).lower() == 'true',
          deleted_at=parse_datetime(data.get('deleted_at')),
          created_at=parse_datetime(data.get('created_at')) or datetime.now(),
          updated_at=parse_datetime(data.get('updated_at')) or datetime.now(),
      )
  ```

- [ ] **1.2.5** Implement `validate()` method
  ```python
  def validate(self) -> List[str]:
      """Validate expense and return list of error messages."""
      errors = []

      # Amount validation
      if self.amount <= 0:
          errors.append("Amount must be positive")
      if self.amount > 10_000_000:
          errors.append("Amount exceeds maximum (10,000,000)")

      # Required fields
      if not self.category:
          errors.append("Category is required")
      if not self.subcategory:
          errors.append("Subcategory is required")
      if not self.vendor:
          errors.append("Vendor is required")
      if not self.payment_method:
          errors.append("Payment method is required")
      if not self.date:
          errors.append("Date is required")

      # Date validation
      if self.date and self.date > datetime.now():
          errors.append("Date cannot be in the future")

      # Recurring validation
      if self.is_recurring:
          if not self.recurring_type:
              errors.append("Recurring type required for recurring expenses")
          if not self.recurring_action:
              errors.append("Recurring action required for recurring expenses")

      return errors
  ```

- [ ] **1.2.6** Implement `mark_deleted()` and `restore()` methods
  ```python
  def mark_deleted(self) -> None:
      """Mark expense as soft deleted."""
      self.is_deleted = True
      self.deleted_at = datetime.now()
      self.updated_at = datetime.now()

  def restore(self) -> None:
      """Restore soft-deleted expense."""
      self.is_deleted = False
      self.deleted_at = None
      self.updated_at = datetime.now()
  ```

- [ ] **1.2.7** Create unit tests in `tests/test_models/test_expense.py`
  ```python
  """Tests for Expense model."""
  import pytest
  from datetime import datetime
  from models.expense import Expense

  class TestExpense:
      def test_create_expense(self):
          expense = Expense(
              amount=5000.00,
              date=datetime.now(),
              category="Supplies",
              subcategory="Hair products",
              vendor="Hair Store",
              payment_method="Cash"
          )
          assert expense.amount == 5000.00
          assert expense.expense_id is not None

      def test_to_dict_from_dict_roundtrip(self):
          original = Expense(
              amount=1000.00,
              date=datetime(2024, 1, 15),
              category="Supplies",
              subcategory="Hair products",
              vendor="Test Vendor",
              payment_method="Cash",
              tags=["monthly", "supplies"]
          )
          data = original.to_dict()
          restored = Expense.from_dict(data)
          assert restored.amount == original.amount
          assert restored.category == original.category

      def test_validate_valid_expense(self):
          expense = Expense(
              amount=5000.00,
              date=datetime.now(),
              category="Supplies",
              subcategory="Hair products",
              vendor="Hair Store",
              payment_method="Cash"
          )
          errors = expense.validate()
          assert len(errors) == 0

      def test_validate_negative_amount(self):
          expense = Expense(
              amount=-100,
              date=datetime.now(),
              category="Supplies",
              subcategory="Hair products",
              vendor="Test",
              payment_method="Cash"
          )
          errors = expense.validate()
          assert "Amount must be positive" in errors

      def test_soft_delete(self):
          expense = Expense(
              amount=100,
              date=datetime.now(),
              category="Supplies",
              subcategory="Hair products",
              vendor="Test",
              payment_method="Cash"
          )
          expense.mark_deleted()
          assert expense.is_deleted is True
          assert expense.deleted_at is not None

          expense.restore()
          assert expense.is_deleted is False
          assert expense.deleted_at is None
  ```

- [ ] **1.2.8** Run tests and verify
  ```bash
  python -m pytest tests/test_models/test_expense.py -v
  ```

### Completion Checklist
- [ ] Expense dataclass created with all fields
- [ ] `to_dict()` method working
- [ ] `from_dict()` method working
- [ ] `validate()` method catches all errors
- [ ] Soft delete methods working
- [ ] All unit tests passing

---

## Story 1.3: Category Model

**Prerequisites:** Story 1.1

### Tasks

- [ ] **1.3.1** Create `models/category.py` with CategoryManager class
  ```python
  """Category management for expense categorization."""
  from typing import List, Dict, Optional

  class CategoryManager:
      """Manages expense categories and subcategories."""

      # Predefined categories with subcategories
      CATEGORIES: Dict[str, List[str]] = {
          "Supplies": [
              "Hair products",
              "Nail products",
              "Skincare products",
              "Disposables",
              "Cleaning supplies"
          ],
          "Equipment": [
              "Styling tools",
              "Furniture",
              "Technology",
              "Maintenance/Repairs"
          ],
          "Facilities": [
              "Rent",
              "Electricity",
              "Water",
              "Gas",
              "Internet",
              "Insurance"
          ],
          "Staff": [
              "Salaries",
              "Commissions",
              "Training",
              "Uniforms"
          ],
          "Marketing": [
              "Advertising",
              "Social media",
              "Promotions",
              "Loyalty programs"
          ],
          "Administrative": [
              "Software subscriptions",
              "Accounting",
              "Licenses",
              "Bank fees"
          ]
      }

      # Category colors for charts
      CATEGORY_COLORS: Dict[str, str] = {
          "Supplies": "#FF6B9D",       # Pink
          "Equipment": "#9B59B6",      # Purple
          "Facilities": "#3498DB",     # Blue
          "Staff": "#2ECC71",          # Green
          "Marketing": "#F39C12",      # Orange
          "Administrative": "#95A5A6", # Gray
      }
  ```

- [ ] **1.3.2** Implement class methods
  ```python
      @classmethod
      def get_categories(cls) -> List[str]:
          """Get list of all category names."""
          return list(cls.CATEGORIES.keys())

      @classmethod
      def get_subcategories(cls, category: str) -> List[str]:
          """Get subcategories for a given category."""
          return cls.CATEGORIES.get(category, [])

      @classmethod
      def get_all_subcategories(cls) -> Dict[str, List[str]]:
          """Get all categories with their subcategories."""
          return cls.CATEGORIES.copy()

      @classmethod
      def is_valid_category(cls, category: str) -> bool:
          """Check if category is valid."""
          return category in cls.CATEGORIES

      @classmethod
      def is_valid_subcategory(cls, category: str, subcategory: str) -> bool:
          """Check if subcategory is valid for the given category."""
          if category not in cls.CATEGORIES:
              return False
          return subcategory in cls.CATEGORIES[category]

      @classmethod
      def get_category_color(cls, category: str) -> str:
          """Get color for category (for charts)."""
          return cls.CATEGORY_COLORS.get(category, "#95A5A6")

      @classmethod
      def get_all_colors(cls) -> Dict[str, str]:
          """Get all category colors."""
          return cls.CATEGORY_COLORS.copy()
  ```

- [ ] **1.3.3** Create unit tests in `tests/test_models/test_category.py`
  ```python
  """Tests for CategoryManager."""
  import pytest
  from models.category import CategoryManager

  class TestCategoryManager:
      def test_get_categories(self):
          categories = CategoryManager.get_categories()
          assert "Supplies" in categories
          assert "Equipment" in categories
          assert len(categories) == 6

      def test_get_subcategories(self):
          subcats = CategoryManager.get_subcategories("Supplies")
          assert "Hair products" in subcats
          assert len(subcats) == 5

      def test_get_subcategories_invalid(self):
          subcats = CategoryManager.get_subcategories("Invalid")
          assert subcats == []

      def test_is_valid_category(self):
          assert CategoryManager.is_valid_category("Supplies") is True
          assert CategoryManager.is_valid_category("Invalid") is False

      def test_is_valid_subcategory(self):
          assert CategoryManager.is_valid_subcategory("Supplies", "Hair products") is True
          assert CategoryManager.is_valid_subcategory("Supplies", "Invalid") is False
          assert CategoryManager.is_valid_subcategory("Invalid", "Hair products") is False

      def test_get_category_color(self):
          color = CategoryManager.get_category_color("Supplies")
          assert color == "#FF6B9D"

      def test_get_category_color_default(self):
          color = CategoryManager.get_category_color("Unknown")
          assert color == "#95A5A6"  # Default gray
  ```

- [ ] **1.3.4** Run tests
  ```bash
  python -m pytest tests/test_models/test_category.py -v
  ```

### Completion Checklist
- [ ] CategoryManager class created
- [ ] All 6 categories defined with subcategories
- [ ] Category colors defined
- [ ] All class methods implemented
- [ ] All unit tests passing

---

## Story 1.4: Budget Data Model

**Prerequisites:** Story 1.1

### Tasks

- [ ] **1.4.1** Create `models/budget.py` with imports
  ```python
  """Budget data model."""
  from dataclasses import dataclass, field
  from datetime import datetime, date
  from typing import Optional
  from calendar import monthrange
  import uuid
  ```

- [ ] **1.4.2** Define Budget dataclass
  ```python
  @dataclass
  class Budget:
      """Represents a budget configuration."""

      # Budget identification
      name: str
      budget_type: str  # "total" or "category"
      amount: float
      month: int  # 1-12
      year: int

      # Optional category (for category budgets)
      category: Optional[str] = None

      # Warning threshold
      warning_threshold: float = 80.0  # Percentage

      # Rollover settings
      enable_rollover: bool = False
      rollover_amount: float = 0.0
      rollover_cap_percent: float = 50.0

      # Status
      is_active: bool = True

      # Metadata
      budget_id: str = field(default_factory=lambda: str(uuid.uuid4()))
      created_at: datetime = field(default_factory=datetime.now)
      updated_at: datetime = field(default_factory=datetime.now)
  ```

- [ ] **1.4.3** Implement `to_dict()` and `from_dict()` methods
  ```python
  def to_dict(self) -> dict:
      """Convert to dictionary for CSV serialization."""
      return {
          'budget_id': self.budget_id,
          'name': self.name,
          'budget_type': self.budget_type,
          'category': self.category or '',
          'amount': self.amount,
          'month': self.month,
          'year': self.year,
          'warning_threshold': self.warning_threshold,
          'enable_rollover': self.enable_rollover,
          'rollover_amount': self.rollover_amount,
          'rollover_cap_percent': self.rollover_cap_percent,
          'is_active': self.is_active,
          'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
          'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
      }

  @classmethod
  def from_dict(cls, data: dict) -> 'Budget':
      """Create Budget from dictionary."""
      def parse_datetime(dt_str):
          if not dt_str:
              return datetime.now()
          try:
              return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
          except ValueError:
              return datetime.now()

      return cls(
          budget_id=data.get('budget_id', str(uuid.uuid4())),
          name=data.get('name', ''),
          budget_type=data.get('budget_type', 'total'),
          category=data.get('category') or None,
          amount=float(data.get('amount', 0)),
          month=int(data.get('month', 1)),
          year=int(data.get('year', datetime.now().year)),
          warning_threshold=float(data.get('warning_threshold', 80)),
          enable_rollover=str(data.get('enable_rollover', 'False')).lower() == 'true',
          rollover_amount=float(data.get('rollover_amount', 0)),
          rollover_cap_percent=float(data.get('rollover_cap_percent', 50)),
          is_active=str(data.get('is_active', 'True')).lower() == 'true',
          created_at=parse_datetime(data.get('created_at')),
          updated_at=parse_datetime(data.get('updated_at')),
      )
  ```

- [ ] **1.4.4** Implement period methods
  ```python
  def get_period_start(self) -> date:
      """Get first day of the budget month."""
      return date(self.year, self.month, 1)

  def get_period_end(self) -> date:
      """Get last day of the budget month."""
      _, last_day = monthrange(self.year, self.month)
      return date(self.year, self.month, last_day)

  def is_current_period(self) -> bool:
      """Check if budget is for the current month."""
      today = date.today()
      return self.month == today.month and self.year == today.year

  def get_period_display(self) -> str:
      """Get display string (e.g., 'January 2024')."""
      month_names = [
          "", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"
      ]
      return f"{month_names[self.month]} {self.year}"
  ```

- [ ] **1.4.5** Implement rollover methods
  ```python
  def get_effective_budget(self) -> float:
      """Get budget amount including any rollover."""
      if self.enable_rollover:
          return self.amount + self.rollover_amount
      return self.amount

  def calculate_rollover(self, spent: float) -> float:
      """Calculate rollover amount for next month (capped by rollover_cap_percent)."""
      if not self.enable_rollover:
          return 0.0

      remaining = self.get_effective_budget() - spent
      if remaining <= 0:
          return 0.0

      max_rollover = self.amount * (self.rollover_cap_percent / 100)
      return min(remaining, max_rollover)
  ```

- [ ] **1.4.6** Create unit tests in `tests/test_models/test_budget.py`
  ```python
  """Tests for Budget model."""
  import pytest
  from datetime import datetime, date
  from models.budget import Budget

  class TestBudget:
      def test_create_budget(self):
          budget = Budget(
              name="Monthly Total",
              budget_type="total",
              amount=375000,
              month=1,
              year=2024
          )
          assert budget.amount == 375000
          assert budget.budget_id is not None

      def test_period_start_end(self):
          budget = Budget(
              name="Test",
              budget_type="total",
              amount=100000,
              month=1,
              year=2024
          )
          assert budget.get_period_start() == date(2024, 1, 1)
          assert budget.get_period_end() == date(2024, 1, 31)

      def test_period_display(self):
          budget = Budget(
              name="Test",
              budget_type="total",
              amount=100000,
              month=3,
              year=2024
          )
          assert budget.get_period_display() == "March 2024"

      def test_effective_budget_no_rollover(self):
          budget = Budget(
              name="Test",
              budget_type="total",
              amount=100000,
              month=1,
              year=2024,
              enable_rollover=False
          )
          assert budget.get_effective_budget() == 100000

      def test_effective_budget_with_rollover(self):
          budget = Budget(
              name="Test",
              budget_type="total",
              amount=100000,
              month=1,
              year=2024,
              enable_rollover=True,
              rollover_amount=15000
          )
          assert budget.get_effective_budget() == 115000

      def test_calculate_rollover_capped(self):
          budget = Budget(
              name="Test",
              budget_type="total",
              amount=100000,
              month=1,
              year=2024,
              enable_rollover=True,
              rollover_cap_percent=50
          )
          # Remaining 80000, cap is 50000
          rollover = budget.calculate_rollover(spent=20000)
          assert rollover == 50000  # Capped at 50%

      def test_to_dict_from_dict_roundtrip(self):
          original = Budget(
              name="Supplies Budget",
              budget_type="category",
              category="Supplies",
              amount=50000,
              month=1,
              year=2024
          )
          data = original.to_dict()
          restored = Budget.from_dict(data)
          assert restored.name == original.name
          assert restored.amount == original.amount
  ```

- [ ] **1.4.7** Run tests
  ```bash
  python -m pytest tests/test_models/test_budget.py -v
  ```

### Completion Checklist
- [ ] Budget dataclass created with all fields
- [ ] `to_dict()` and `from_dict()` methods working
- [ ] Period calculation methods working
- [ ] Rollover calculation methods working
- [ ] All unit tests passing

---

## Story 1.5: Payment Method Constants

**Prerequisites:** Story 1.1

### Tasks

- [ ] **1.5.1** Verify PAYMENT_METHODS in `config.py`
  ```python
  PAYMENT_METHODS = ["Cash", "Debit Card", "Credit Card", "Bank Transfer"]
  ```

- [ ] **1.5.2** Add helper functions to `config.py`
  ```python
  def is_valid_payment_method(method: str) -> bool:
      """Check if payment method is valid."""
      return method in PAYMENT_METHODS

  def get_payment_methods() -> list:
      """Get list of valid payment methods."""
      return PAYMENT_METHODS.copy()
  ```

- [ ] **1.5.3** Create test in `tests/test_config.py`
  ```python
  """Tests for config module."""
  import pytest
  from config import (
      PAYMENT_METHODS, is_valid_payment_method, get_payment_methods,
      CURRENCY_SYMBOL, DATE_FORMAT, MAX_AMOUNT
  )

  class TestConfig:
      def test_payment_methods_defined(self):
          assert len(PAYMENT_METHODS) == 4
          assert "Cash" in PAYMENT_METHODS

      def test_is_valid_payment_method(self):
          assert is_valid_payment_method("Cash") is True
          assert is_valid_payment_method("Invalid") is False

      def test_get_payment_methods(self):
          methods = get_payment_methods()
          assert methods == PAYMENT_METHODS
          # Verify it returns a copy
          methods.append("Test")
          assert "Test" not in PAYMENT_METHODS

      def test_currency_symbol(self):
          assert CURRENCY_SYMBOL == "L"

      def test_date_format(self):
          assert DATE_FORMAT == "%d/%m/%Y"

      def test_max_amount(self):
          assert MAX_AMOUNT == 10_000_000
  ```

### Completion Checklist
- [ ] PAYMENT_METHODS constant defined
- [ ] Helper functions implemented
- [ ] Tests passing

---

## Story 1.6: CSV File Templates

**Prerequisites:** Story 1.1

### Tasks

- [ ] **1.6.1** Create `data/expenses.csv` with headers
  ```csv
  expense_id,amount,date,category,subcategory,vendor,payment_method,description,tags,is_recurring,recurring_type,recurring_action,next_due_date,last_recurring_date,recurring_parent_id,is_deleted,deleted_at,created_at,updated_at
  ```

- [ ] **1.6.2** Create `data/budgets.csv` with headers
  ```csv
  budget_id,name,budget_type,category,amount,month,year,warning_threshold,enable_rollover,rollover_amount,rollover_cap_percent,is_active,created_at,updated_at
  ```

- [ ] **1.6.3** Create `data/templates.csv` with headers
  ```csv
  template_id,name,category,subcategory,vendor,typical_amount,payment_method,description,tags,use_count,last_used,created_at
  ```

- [ ] **1.6.4** Create `data/settings.json` with defaults
  ```json
  {
      "general": {
          "salon_name": "Beauty Salon",
          "salon_address": "",
          "salon_contact": "",
          "language": "en",
          "date_format": "DD/MM/YYYY"
      },
      "backup": {
          "auto_backup": true,
          "backup_location": "data/backups/",
          "retention_days": 30,
          "max_backups": 7
      },
      "alerts": {
          "warning_threshold": 80,
          "show_notifications": true,
          "show_on_startup": true
      },
      "display": {
          "theme": "default",
          "default_view": "dashboard",
          "page_size": 50
      },
      "data": {
          "auto_save": true,
          "duplicate_detection": true,
          "duplicate_days_threshold": 3
      }
  }
  ```

- [ ] **1.6.5** Verify all files created and readable
  ```python
  # Quick verification script
  import os
  import json
  import csv

  data_dir = "data"
  files = ["expenses.csv", "budgets.csv", "templates.csv", "settings.json"]

  for f in files:
      path = os.path.join(data_dir, f)
      assert os.path.exists(path), f"Missing: {path}"
      print(f"✓ {f} exists")
  ```

### Completion Checklist
- [ ] expenses.csv created with correct headers
- [ ] budgets.csv created with correct headers
- [ ] templates.csv created with correct headers
- [ ] settings.json created with default values

---

## Story 1.7: Formatters Utility

**Prerequisites:** Story 1.1

### Tasks

- [ ] **1.7.1** Create `utils/formatters.py` with imports
  ```python
  """Formatting utilities for consistent display."""
  from datetime import datetime
  from typing import Optional, List
  from config import CURRENCY_SYMBOL, DATE_FORMAT, DATETIME_FORMAT
  ```

- [ ] **1.7.2** Implement currency formatting
  ```python
  def format_currency(amount: float, include_symbol: bool = True) -> str:
      """Format amount as currency (e.g., 'L 1,234.56')."""
      formatted = f"{amount:,.2f}"
      if include_symbol:
          return f"{CURRENCY_SYMBOL} {formatted}"
      return formatted

  def parse_currency(currency_str: str) -> float:
      """Parse currency string to float."""
      # Remove currency symbol and commas
      cleaned = currency_str.replace(CURRENCY_SYMBOL, "").replace(",", "").strip()
      return float(cleaned)
  ```

- [ ] **1.7.3** Implement date formatting
  ```python
  def format_date(dt: datetime) -> str:
      """Format datetime as date string (e.g., '15/01/2024')."""
      if not dt:
          return ""
      return dt.strftime(DATE_FORMAT)

  def format_datetime(dt: datetime) -> str:
      """Format datetime with time (e.g., '15/01/2024 14:30')."""
      if not dt:
          return ""
      return dt.strftime(DATETIME_FORMAT)

  def parse_date(date_str: str) -> Optional[datetime]:
      """Parse date string in DD/MM/YYYY format."""
      if not date_str:
          return None
      try:
          return datetime.strptime(date_str, DATE_FORMAT)
      except ValueError:
          return None

  def parse_date_flexible(date_str: str) -> Optional[datetime]:
      """Parse date with multiple format support."""
      if not date_str:
          return None

      formats = [
          DATE_FORMAT,           # DD/MM/YYYY
          "%Y-%m-%d",           # ISO format
          "%d-%m-%Y",           # DD-MM-YYYY
          "%m/%d/%Y",           # US format
      ]

      for fmt in formats:
          try:
              return datetime.strptime(date_str, fmt)
          except ValueError:
              continue
      return None
  ```

- [ ] **1.7.4** Implement other formatting functions
  ```python
  def truncate_text(text: str, max_length: int = 30) -> str:
      """Truncate text with ellipsis if too long."""
      if not text:
          return ""
      if len(text) <= max_length:
          return text
      return text[:max_length - 3] + "..."

  def format_percentage(value: float, decimals: int = 1) -> str:
      """Format number as percentage (e.g., '85.5%')."""
      return f"{value:.{decimals}f}%"

  def format_number(value: float, decimals: int = 2) -> str:
      """Format number with thousand separators."""
      return f"{value:,.{decimals}f}"

  def format_period(month: int, year: int) -> str:
      """Format month/year as display string (e.g., 'January 2024')."""
      month_names = [
          "", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"
      ]
      return f"{month_names[month]} {year}"
  ```

- [ ] **1.7.5** Implement tag formatting
  ```python
  def format_tags(tags: List[str]) -> str:
      """Convert list of tags to comma-separated string."""
      if not tags:
          return ""
      return ", ".join(tags)

  def parse_tags(tags_str: str) -> List[str]:
      """Convert comma-separated string to list of tags."""
      if not tags_str:
          return []
      return [tag.strip() for tag in tags_str.split(",") if tag.strip()]
  ```

- [ ] **1.7.6** Create unit tests in `tests/test_utils/test_formatters.py`
  ```python
  """Tests for formatters module."""
  import pytest
  from datetime import datetime
  from utils.formatters import (
      format_currency, parse_currency,
      format_date, parse_date, parse_date_flexible,
      format_percentage, format_number,
      truncate_text, format_period,
      format_tags, parse_tags
  )

  class TestCurrencyFormatting:
      def test_format_currency(self):
          assert format_currency(1234.56) == "L 1,234.56"
          assert format_currency(1234.56, include_symbol=False) == "1,234.56"

      def test_parse_currency(self):
          assert parse_currency("L 1,234.56") == 1234.56
          assert parse_currency("1,234.56") == 1234.56

  class TestDateFormatting:
      def test_format_date(self):
          dt = datetime(2024, 1, 15)
          assert format_date(dt) == "15/01/2024"

      def test_parse_date(self):
          result = parse_date("15/01/2024")
          assert result.day == 15
          assert result.month == 1
          assert result.year == 2024

      def test_parse_date_flexible(self):
          assert parse_date_flexible("2024-01-15").day == 15
          assert parse_date_flexible("15/01/2024").day == 15

  class TestTextFormatting:
      def test_truncate_text(self):
          assert truncate_text("Short") == "Short"
          assert truncate_text("This is a very long text", 10) == "This is..."

      def test_format_percentage(self):
          assert format_percentage(85.5) == "85.5%"
          assert format_percentage(85.567, 2) == "85.57%"

      def test_format_number(self):
          assert format_number(1234567.89) == "1,234,567.89"

      def test_format_period(self):
          assert format_period(1, 2024) == "January 2024"

  class TestTagFormatting:
      def test_format_tags(self):
          assert format_tags(["tag1", "tag2"]) == "tag1, tag2"
          assert format_tags([]) == ""

      def test_parse_tags(self):
          assert parse_tags("tag1, tag2") == ["tag1", "tag2"]
          assert parse_tags("") == []
          assert parse_tags("  tag1  ,  tag2  ") == ["tag1", "tag2"]
  ```

- [ ] **1.7.7** Run tests
  ```bash
  python -m pytest tests/test_utils/test_formatters.py -v
  ```

### Completion Checklist
- [ ] All formatting functions implemented
- [ ] All parsing functions implemented
- [ ] All unit tests passing
- [ ] Functions handle edge cases (None, empty strings)

---

## Epic 1 Completion Checklist

- [ ] All 7 stories completed
- [ ] All unit tests passing (`python -m pytest tests/ -v`)
- [ ] Directory structure matches specification
- [ ] All data files created with correct headers
- [ ] Config constants accessible from other modules
- [ ] Models can serialize/deserialize to/from dict

### Final Verification

```bash
# Run all Epic 1 tests
python -m pytest tests/test_models/ tests/test_utils/ tests/test_config.py -v

# Verify imports work
python -c "from models.expense import Expense; from models.budget import Budget; from models.category import CategoryManager; print('All imports successful')"
```
