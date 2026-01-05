# Epic 7: Data Persistence & File Management

**Priority:** High
**Dependencies:** Epic 1 (Core Data Models), Epic 9 (Error Handling)
**Stories:** 4

---

## Story 7.1: DataManager Class

**As a** developer
**I want** a DataManager class for file operations
**So that** persistence is centralized

### Acceptance Criteria

- [ ] Create `persistence/data_manager.py`:

  **CSV Column Definitions:**
  ```python
  EXPENSE_COLUMNS = [
      'expense_id', 'amount', 'date', 'category', 'subcategory',
      'vendor', 'payment_method', 'description', 'tags',
      'is_recurring', 'recurring_type', 'recurring_action',
      'next_due_date', 'last_recurring_date', 'generated_from_id',
      'is_deleted', 'deleted_at', 'created_at', 'updated_at'
  ]

  BUDGET_COLUMNS = [
      'budget_id', 'name', 'budget_type', 'category', 'amount',
      'month', 'year', 'warning_threshold', 'enable_rollover',
      'rollover_amount', 'rollover_cap_percent', 'is_active',
      'created_at', 'updated_at'
  ]

  TEMPLATE_COLUMNS = [
      'template_id', 'name', 'category', 'subcategory', 'vendor',
      'typical_amount', 'payment_method', 'description', 'tags',
      'use_count', 'last_used', 'created_at'
  ]
  ```

  **Methods:**
  ```python
  class DataManager:
      """Centralized file operations for all data persistence"""

      def __init__(self, data_dir: str = DATA_DIR)
          """Initialize with data directory, ensure directories exist"""

      def ensure_data_dir(self) -> None
          """Create data directories if they don't exist"""

      # Expenses
      def load_expenses(self) -> pd.DataFrame
          """Load expenses CSV into DataFrame"""

      def save_expenses(self, df: pd.DataFrame) -> None
          """Save DataFrame to expenses CSV (atomic write)"""

      # Budgets
      def load_budgets(self) -> pd.DataFrame
          """Load budgets CSV into DataFrame"""

      def save_budgets(self, df: pd.DataFrame) -> None
          """Save DataFrame to budgets CSV"""

      # Templates
      def load_templates(self) -> pd.DataFrame
          """Load templates CSV into DataFrame"""

      def save_templates(self, df: pd.DataFrame) -> None
          """Save DataFrame to templates CSV"""

      # Settings
      def load_settings(self) -> Dict
          """Load settings from JSON, create defaults if missing"""

      def save_settings(self, settings: Dict) -> None
          """Save settings to JSON"""

      # Backup
      def create_backup(self, name: str = None) -> str
          """Create timestamped backup of all data files. Returns backup path"""

      def restore_backup(self, backup_path: str) -> bool
          """Restore from backup file. Creates safety backup first"""

      def list_backups(self) -> List[Dict]
          """List available backups with metadata"""

      # Import
      def import_csv(self, file_path: str, mapping: Dict[str, str]) -> Tuple[int, int, List[Dict]]
          """Import external CSV with column mapping.
          Returns: (imported_count, skipped_count, skipped_rows)
          skipped_rows format: [{'row': int, 'error': str, 'data': Dict}, ...]"""

      # Utilities
      def check_disk_space(self, required_mb: int = 100) -> Tuple[bool, int]
          """Check if sufficient disk space available"""

      def get_data_stats(self) -> Dict
          """Get statistics about stored data"""
  ```

### Default Settings Structure

```python
{
    "general": {
        "salon_name": "Beauty Salon",
        "salon_address": "",
        "salon_contact": "",
        "language": "en",
        "date_format": "DD/MM/YYYY"
    },
    "backup": {
        "auto_backup": True,
        "backup_location": "data/backups/",
        "retention_days": 30,
        "max_backups": 7
    },
    "alerts": {
        "warning_threshold": 80,
        "show_notifications": True,
        "show_on_startup": True
    },
    "display": {
        "theme": "default",
        "default_view": "dashboard",
        "page_size": 50
    },
    "data": {
        "auto_save": True,
        "duplicate_detection": True,
        "duplicate_days_threshold": 3
    }
}
```

### Technical Notes
- Atomic writes prevent corruption on crash
- Column validation adds missing columns gracefully
- Settings merge ensures new settings work with old config files

---

## Story 7.2: Auto-Save Functionality

**As a** user
**I want** my data saved automatically
**So that** I don't lose work

### Acceptance Criteria

- [ ] Auto-save after each operation:
  - Add expense
  - Edit expense
  - Delete expense
  - Budget change
  - Template change

- [ ] Auto-save behavior:
  - Immediate save after successful operation
  - No explicit "Save" button needed
  - Status bar shows "Saving..." during save
  - Status bar shows "All changes saved" or last save time

- [ ] Atomic save process:
  1. Write data to temp file
  2. Verify temp file is valid
  3. Rename temp to actual file (atomic operation)
  4. Delete temp file if rename fails

- [ ] Error handling:
  - If save fails, keep data in memory
  - Show warning notification
  - Retry option
  - Continue working without losing changes

- [ ] On application close:
  - Check for unsaved changes
  - Force save before exit
  - Warn if save fails

---

## Story 7.3: Backup System

**As a** user
**I want** to backup and restore my data
**So that** I can recover from problems

### Acceptance Criteria

- [ ] **Automatic Backup:**
  - Create backup daily (configurable)
  - Trigger: on application startup if last backup > 24 hours
  - Location: `data/backups/`
  - Naming: `backup_YYYYMMDD_HHMMSS.zip`
  - Keep last 7 daily backups (configurable)
  - Auto-delete older backups

- [ ] **Manual Backup:**
  - Menu: File > Create Backup
  - Option to name backup
  - Include all data: expenses, budgets, templates, settings
  - Show confirmation with file location

- [ ] **Restore from Backup:**
  - Menu: File > Restore from Backup
  - Show list of available backups
  - Preview backup contents before restore
  - Warning before restore
  - Create safety backup before restoring
  - Show restore progress and results

### Wireframe: Restore Backup Selection

```
+-------------------------------------------------------------+
|                   Restore from Backup                    [X] |
+-------------------------------------------------------------+
|                                                              |
|   Select a backup to restore:                                |
|                                                              |
|   +----------------------------------------------------------+
|   | Date & Time          | Size     | Expenses | Type        |
|   +----------------------+----------+----------+-------------+
|   | o 15/01/2024 10:30   | 245 KB   | 234      | Auto        |
|   | o 14/01/2024 18:45   | 242 KB   | 230      | Auto        |
|   | o 14/01/2024 10:30   | 238 KB   | 228      | Auto        |
|   | o 13/01/2024 15:22   | 235 KB   | 225      | Manual      |
|   +----------------------------------------------------------+
|                                                              |
|   Warning: Restoring will replace all current data.          |
|   A backup of current data will be created first.            |
|                                                              |
|   Or restore from file:                                      |
|   +-------------------------------------+ +----------------+ |
|   |                                     | | Browse...      | |
|   +-------------------------------------+ +----------------+ |
|                                                              |
|              [Restore Selected]         [Cancel]             |
|                                                              |
+-------------------------------------------------------------+
```

### Wireframe: Create Backup Dialog

```
+---------------------------------------------+
|              Create Backup               [X] |
+---------------------------------------------+
|                                              |
|   Create a manual backup of all data?        |
|                                              |
|   Data to backup:                            |
|   +----------------------------------------+ |
|   | - 234 expenses                         | |
|   | - 8 budgets                            | |
|   | - 12 templates                         | |
|   | - Application settings                 | |
|   +----------------------------------------+ |
|                                              |
|   Backup name (optional):                    |
|   +----------------------------------------+ |
|   | Before_Q1_Changes                      | |
|   +----------------------------------------+ |
|                                              |
|   Location: data/backups/                    |
|                                              |
|        [Create Backup]         [Cancel]      |
|                                              |
+---------------------------------------------+
```

---

## Story 7.4: Data Import

**As a** user
**I want** to import expenses from CSV
**So that** I can migrate existing data

### Acceptance Criteria

- [ ] Access: File > Import > Import from CSV

- [ ] **Step 1: File Selection**
  - File browser to select CSV file
  - Show file info (size, row count preview)
  - Detect encoding (UTF-8, Latin-1, etc.)

- [ ] **Step 2: Preview & Column Mapping**
  - Show preview of first 5-10 rows
  - Detect headers automatically
  - Column mapping interface:
    ```
    Our Field          Your CSV Column
    ─────────────────────────────────────
    Amount *           [dropdown: select column]
    Date *             [dropdown: select column]
    Category *         [dropdown: select column]
    Subcategory        [dropdown or "Not mapped"]
    Vendor *           [dropdown: select column]
    Payment Method     [dropdown or "Not mapped"]
    Description        [dropdown or "Not mapped"]
    Tags               [dropdown or "Not mapped"]
    ```

- [ ] **Step 3: Import Options**
  - [ ] Skip first row (header) - default checked
  - [ ] Date format: [dropdown: YYYY-MM-DD, DD/MM/YYYY, etc.]
  - [ ] Handle unknown categories: [Create new / Use "Administrative" / Skip]
  - [ ] Update existing (by matching ID) - for re-imports

- [ ] **Step 4: Import Execution**
  - Progress bar with percentage
  - Running count: "Imported: X, Skipped: Y"
  - Cancel button to abort

- [ ] **Step 5: Results Summary**
  - Total rows processed
  - Successfully imported count
  - Skipped count with reasons
  - [View Skipped Rows] button
  - [Export Skipped to CSV] button

### Wireframe: Import CSV Dialog

```
+----------------------------------------------------------------------+
|                         Import Expenses from CSV                  [X] |
+----------------------------------------------------------------------+
|                                                                       |
|  Step 1: Select File                                                  |
|  +-----------------------------------------------------+ +---------+ |
|  | C:\Users\...\expenses_export.csv                    | | Browse  | |
|  +-----------------------------------------------------+ +---------+ |
|                                                                       |
|  Step 2: Preview & Map Columns                                        |
|  +-------------------------------------------------------------------+|
|  | Preview (first 5 rows):                                           ||
|  | +----------+--------+----------+------------+---------+           ||
|  | | date     | amount | category | vendor     | notes   |           ||
|  | +----------+--------+----------+------------+---------+           ||
|  | | 2024-01-15| 5200  | Supplies | Hair Store | Monthly |           ||
|  | | 2024-01-14| 12000 | Utilities| KEK        | Electric|           ||
|  +-------------------------------------------------------------------+|
|                                                                       |
|  Column Mapping:                                                      |
|  +-------------------------+---------------------------------------+ |
|  | Our Field               | Your CSV Column                       | |
|  +-------------------------+---------------------------------------+ |
|  | Amount *                | [amount                            v] | |
|  | Date *                  | [date                              v] | |
|  | Category *              | [category                          v] | |
|  | Subcategory             | [-- Not mapped --                  v] | |
|  | Vendor *                | [vendor                            v] | |
|  | Payment Method          | [-- Not mapped --                  v] | |
|  | Description             | [notes                             v] | |
|  +-------------------------+---------------------------------------+ |
|                                                                       |
|  Options:                                                             |
|  +-------------------------------------------------------------------+|
|  | [x] Skip first row (header)                                       ||
|  | [ ] Update existing expenses with same ID                         ||
|  | Date format in file: [YYYY-MM-DD                              v]  ||
|  +-------------------------------------------------------------------+|
|                                                                       |
|                    [Import]          [Cancel]                         |
|                                                                       |
+----------------------------------------------------------------------+
```

### Wireframe: Import Results

```
+---------------------------------------------+
|              Import Results              [X] |
+---------------------------------------------+
|                                              |
|   Import completed!                          |
|                                              |
|   +----------------------------------------+ |
|   | Total rows processed:     150          | |
|   | Successfully imported:    142          | |
|   | Skipped (invalid):        8            | |
|   +----------------------------------------+ |
|                                              |
|   8 rows were skipped due to errors:         |
|   - Row 23: Invalid date format              |
|   - Row 45: Amount is negative               |
|   - Row 67: Unknown category "Misc"          |
|   - ...and 5 more                            |
|                                              |
|   [Export Skipped Rows]        [Close]       |
|                                              |
+---------------------------------------------+
```

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 7.1 | 1.1, 9.1 |
| 7.2 | 7.1 |
| 7.3 | 7.1 |
| 7.4 | 7.1, 9.2 |

---

## Testing Requirements

- [ ] Unit tests for DataManager (all methods)
- [ ] Unit tests for atomic write functionality
- [ ] Integration tests for backup/restore cycle
- [ ] Test corrupted file recovery
- [ ] Test import with various CSV formats
- [ ] Test disk space checking
- [ ] Performance test with large CSV files (10k+ rows)
