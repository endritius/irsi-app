# Epic 9: Error Handling & Validation

**Priority:** High
**Dependencies:** Epic 1 (Core Data Models)
**Stories:** 5

---

## Story 9.1: Custom Exception Classes

**As a** developer
**I want** custom exceptions for domain-specific errors
**So that** errors are meaningful and catchable

### Acceptance Criteria

- [ ] Create `utils/exceptions.py`:

  **Exception Hierarchy:**
  ```python
  class ExpenseError(Exception)
      """Base exception for all expense-related errors"""

  class ValidationError(ExpenseError)
      """Raised when input validation fails"""

  class MultipleValidationError(ExpenseError)
      """Raised when multiple validation errors occur"""

  class FileError(ExpenseError)
      """Raised for file operation errors"""

  class DataFileNotFoundError(FileError)
      """Raised when a required data file is not found"""

  class DataFilePermissionError(FileError)
      """Raised when data file permission is denied"""

  class DataIntegrityError(ExpenseError)
      """Raised when data consistency check fails"""

  class BudgetError(ExpenseError)
      """Raised for budget-related errors"""

  class BudgetExceededError(BudgetError)
      """Raised when an expense would exceed budget"""

  class BudgetWarningError(BudgetError)
      """Raised when expense approaches budget threshold"""

  class ExportError(ExpenseError)
      """Raised when export operation fails"""

  class DataImportError(ExpenseError)
      """Raised when import operation fails"""

  class BackupError(ExpenseError)
      """Raised for backup/restore operation errors"""

  class ConfigurationError(ExpenseError)
      """Raised for configuration-related errors"""
  ```

### Technical Notes
- All exceptions inherit from base `ExpenseError`
- Include context information for debugging
- Support both user-friendly and technical error messages

---

## Story 9.2: Input Validators

**As a** user
**I want** my inputs validated before saving
**So that** data integrity is maintained

### Acceptance Criteria

- [ ] Create `utils/validators.py`:

  **Validation Functions:**
  ```python
  def validate_amount(amount: Any) -> Tuple[bool, str]
      """Validate expense amount (positive, max 10M, max 2 decimals)"""

  def validate_date(date_input: Any, allow_future: bool = False) -> Tuple[bool, str]
      """Validate date (not future unless allowed, not older than 10 years)"""

  def validate_category(category: str) -> Tuple[bool, str]
      """Validate category exists in predefined list"""

  def validate_subcategory(category: str, subcategory: str) -> Tuple[bool, str]
      """Validate subcategory exists under category"""

  def validate_payment_method(method: str) -> Tuple[bool, str]
      """Validate payment method is in allowed list"""

  def validate_vendor(vendor: str) -> Tuple[bool, str]
      """Validate vendor name (required, max 100 chars, allowed chars)"""

  def validate_description(description: str) -> Tuple[bool, str]
      """Validate description (optional, max 500 chars)"""

  def validate_tags(tags: List[str]) -> Tuple[bool, str]
      """Validate tags (max 10 tags, each max 30 chars, alphanumeric)"""

  def validate_recurring_type(recurring_type: str) -> Tuple[bool, str]
      """Validate recurring type (weekly, monthly, yearly)"""

  def validate_recurring_action(action: str) -> Tuple[bool, str]
      """Validate recurring action (auto_generate, reminder)"""

  def validate_expense(expense) -> List[Tuple[str, str]]
      """Validate entire expense, return list of (field, error) tuples"""

  def validate_budget_amount(amount: Any) -> Tuple[bool, str]
      """Validate budget amount (non-negative, max 10M)"""

  def validate_threshold(threshold: Any) -> Tuple[bool, str]
      """Validate warning threshold (0-100%)"""
  ```

### Technical Notes
- Each validator returns (is_valid: bool, error_message: str)
- Empty error_message when valid
- Use regex for pattern matching where appropriate
- Date validation supports multiple formats

---

## Story 9.3: Error Handler Service

**As a** developer
**I want** centralized error handling
**So that** errors are logged and user-friendly messages are shown

### Acceptance Criteria

- [ ] Create `utils/error_handler.py`:

  **ErrorHandler Methods:**
  ```python
  class ErrorHandler:
      """Centralized error handling service"""

      def __init__(self, log_dir: str = LOGS_DIR)
          """Initialize with log directory, setup logger"""

      def set_notification_callback(self, callback: Callable) -> None
          """Set callback for toast notifications"""

      def log_error(self, error: Exception, context: str = "") -> None
          """Log error with full stack trace"""

      def log_warning(self, message: str, context: str = "") -> None
          """Log warning message"""

      def log_info(self, message: str) -> None
          """Log info message"""

      def log_debug(self, message: str) -> None
          """Log debug message"""

      def get_user_message(self, error: Exception) -> str
          """Convert technical error to user-friendly message"""

      def show_error_dialog(self, parent: tk.Widget, error: Exception, title: str = "Error") -> None
          """Show Tkinter error dialog"""

      def show_warning_dialog(self, parent: tk.Widget, message: str, title: str = "Warning") -> None
          """Show Tkinter warning dialog"""

      def show_info_dialog(self, parent: tk.Widget, message: str, title: str = "Information") -> None
          """Show Tkinter info dialog"""

      def confirm_action(self, parent: tk.Widget, message: str, title: str = "Confirm") -> bool
          """Show confirmation dialog, return True if confirmed"""

      def confirm_destructive_action(self, parent: tk.Widget, message: str, title: str = "Confirm Delete") -> bool
          """Show warning confirmation for destructive actions"""

      def show_toast(self, message: str, toast_type: str = "info") -> None
          """Show toast notification if callback is set"""

      def handle_exception(self, error: Exception, context: str = "", parent: tk.Widget = None, show_dialog: bool = True) -> None
          """Handle exception with logging and optional dialog"""

      def cleanup_old_logs(self, days: int = 30) -> int
          """Remove log files older than specified days"""

  def get_error_handler() -> ErrorHandler
      """Get or create global error handler instance"""
  ```

### Wireframe: Error Dialog

```
+---------------------------------------------+
|                   Error                  [X] |
+---------------------------------------------+
|                                              |
|                     [X]                      |
|                                              |
|   An error occurred while saving the expense.|
|                                              |
|   Error details:                             |
|   +----------------------------------------+ |
|   | Unable to write to file:               | |
|   | data/expenses.csv                      | |
|   |                                        | |
|   | The file may be open in another        | |
|   | application or you may not have        | |
|   | write permissions.                     | |
|   +----------------------------------------+ |
|                                              |
|   What you can do:                           |
|   - Close any applications using this file   |
|   - Check file permissions                   |
|   - Try saving to a different location       |
|                                              |
|       [Copy Error]     [Report Bug]    [OK]  |
|                                              |
+---------------------------------------------+
```

### Wireframe: Toast Notifications

```
Success (Green):
+--------------------------------+
| [check] Expense saved          |
|   L 5,200.00 - Hair Store      |
+--------------------------------+

Warning (Yellow):
+--------------------------------+
| [!] Budget warning             |
|   Supplies at 85%              |
+--------------------------------+

Error (Red):
+--------------------------------+
| [X] Save failed                |
|   Check disk space             |
+--------------------------------+
```

### Technical Notes
- Log format: `[YYYY-MM-DD HH:MM:SS] [LEVEL] [context] message`
- Log file rotation: daily files, cleanup after 30 days
- Support for both dialogs and toast notifications
- Global singleton pattern for easy access

---

## Story 9.4: File Error Recovery

**As a** user
**I want** the application to handle file errors gracefully
**So that** I don't lose data

### Acceptance Criteria

- [ ] **Handle missing files:**
  - If `expenses.csv` missing → create with headers, log warning
  - If `budgets.csv` missing → create with headers, log warning
  - If `templates.csv` missing → create with headers, log warning
  - If `settings.json` missing → create with defaults, log warning

- [ ] **Handle corrupted files:**
  - Detect malformed CSV (wrong column count, invalid data types)
  - Attempt to recover valid rows
  - Create backup of corrupted file as `filename.corrupted.YYYYMMDD_HHMMSS`
  - Report number of recovered vs. lost records
  - Log details of each corrupted row

- [ ] **Handle permission errors:**
  - Detect read-only files
  - Show user-friendly message with suggestions
  - Offer to save to alternate location

- [ ] **Handle disk space errors:**
  - Check available space before large operations
  - Warn if disk space is low (< 100MB free)
  - Prevent save if insufficient space

- [ ] **Recovery functions in DataManager:**
  ```python
  def recover_corrupted_csv(self, filepath: str) -> Tuple[int, int, str]
      """Attempt to recover data from corrupted CSV. Returns (recovered, lost, backup_path)"""

  def check_disk_space(self, required_mb: int = 100) -> Tuple[bool, int]
      """Check if sufficient disk space. Returns (has_space, available_mb)"""

  def safe_write(self, filepath: str, content: str) -> bool
      """Safely write file with temp file and atomic rename. Returns success"""
  ```

### Technical Notes
- Always create temp file first, then rename (atomic save)
- Keep corrupted files for manual recovery if needed
- Log all recovery attempts with details

---

## Story 9.5: Data Integrity Validation on Load

**As a** user
**I want** data validated when loaded
**So that** corrupted data doesn't cause crashes

### Acceptance Criteria

- [ ] On application startup, validate all loaded data:

  **Expense validation:**
  - All expense IDs are unique (detect duplicates)
  - All dates are valid format and reasonable range
  - All categories exist in predefined list
  - All subcategories valid for their category
  - All amounts are positive numbers
  - All payment methods are valid
  - All required fields are present (not empty)

  **Budget validation:**
  - All budget IDs are unique
  - Month values are 1-12
  - Year values are reasonable (current year +/- 5)
  - Amounts are non-negative
  - Warning thresholds are 0-100

- [ ] For invalid records, apply auto-corrections where safe:
  - Invalid date → use created_at date
  - Unknown category → set to "Administrative"
  - Negative amount → convert to positive
  - Missing payment method → set to "Cash"
  - Future date → set to today

- [ ] Track all corrections with DataCorrection dataclass

- [ ] Show summary dialog after loading if issues found

### Wireframe: Data Load Summary

```
+---------------------------------------------+
|            Data Load Summary             [X] |
+---------------------------------------------+
|                                              |
|   Application loaded with some warnings:     |
|                                              |
|   +----------------------------------------+ |
|   | [check] Loaded 234 expenses            | |
|   | [check] Loaded 8 budgets               | |
|   | [check] Loaded 12 templates            | |
|   +----------------------------------------+ |
|                                              |
|   [!] Issues found:                          |
|   +----------------------------------------+ |
|   | - 3 expenses had invalid dates         | |
|   |   (corrected to original create date)  | |
|   | - 1 expense had unknown category       | |
|   |   (set to "Administrative")            | |
|   | - 2 expenses had negative amounts      | |
|   |   (converted to positive)              | |
|   +----------------------------------------+ |
|                                              |
|        [View Details]           [OK]         |
|                                              |
+---------------------------------------------+
```

### Technical Notes
- Don't halt startup for fixable issues
- Always log all validation issues to `logs/validation_YYYYMMDD.log`
- Auto-corrections applied silently without user confirmation
- Store original values in correction log: `logs/data_corrections_YYYYMMDD.csv`
  - Columns: timestamp, record_type, record_id, field, original_value, corrected_value, rule
- User can review corrections via Data Load Summary dialog (Story 10.5)
- Corrections are reversible by restoring from backup

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 9.1 | Epic 1 |
| 9.2 | 9.1, 1.3 |
| 9.3 | 9.1 |
| 9.4 | 9.1, 9.3 |
| 9.5 | 9.1, 9.2, 9.3 |

---

## Testing Requirements

- [ ] Unit tests for each validator function
- [ ] Unit tests for exception classes
- [ ] Unit tests for error message generation
- [ ] Integration tests for file recovery
- [ ] Integration tests for data integrity validation
- [ ] Test corrupted file handling with sample bad data
