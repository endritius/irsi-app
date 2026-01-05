# Epic 2: Expense Management (CRUD Operations)

**Priority:** High
**Dependencies:** Epic 1 (Core Data Models), Epic 9 (Error Handling), Epic 7 (Data Persistence)
**Stories:** 10

---

## Story 2.1: ExpenseManager Class

**As a** developer
**I want** an ExpenseManager class to handle CRUD operations
**So that** expense operations are centralized

### Acceptance Criteria

- [ ] Create `managers/expense_manager.py`:

  **Methods:**
  ```python
  class ExpenseManager:
      """Manages all expense CRUD operations"""

      def __init__(self, data_manager: DataManager)
          """Initialize with DataManager, load expenses into memory cache"""

      def load_expenses(self) -> None
          """Load expenses from CSV into memory"""

      def save_expenses(self) -> None
          """Save all expenses to CSV"""

      def add_expense(self, expense: Expense) -> str
          """Add new expense. Validates, saves, returns expense_id"""

      def get_expense(self, expense_id: str) -> Optional[Expense]
          """Get single expense by ID"""

      def update_expense(self, expense_id: str, updates: Dict) -> bool
          """Update expense fields. Returns True on success"""

      def delete_expense(self, expense_id: str, permanent: bool = False) -> bool
          """Delete expense. Soft delete by default, permanent if specified"""

      def restore_expense(self, expense_id: str) -> bool
          """Restore a soft-deleted expense"""

      def bulk_delete(self, expense_ids: List[str], permanent: bool = False) -> int
          """Delete multiple expenses. Returns count deleted"""

      def get_all_expenses(self, include_deleted: bool = False) -> List[Expense]
          """Get all expenses (optionally including deleted)"""

      def get_deleted_expenses(self) -> List[Expense]
          """Get only soft-deleted expenses"""

      def get_expenses_dataframe(self, include_deleted: bool = False) -> pd.DataFrame
          """Get expenses as DataFrame for analysis"""

      def get_unique_vendors(self) -> List[str]
          """Get sorted list of unique vendors for autocomplete"""

      def get_unique_tags(self) -> Set[str]
          """Get set of all used tags"""

      def find_duplicates(self, expense: Expense, days_threshold: int = 3) -> List[Expense]
          """Find potential duplicate expenses (same vendor + amount within days)"""

      def get_recurring_expenses(self) -> List[Expense]
          """Get all recurring expense definitions"""

      def get_due_recurring_expenses(self) -> List[Expense]
          """Get recurring expenses that are due for generation/reminder"""
  ```

### Technical Notes
- In-memory cache for fast access
- Auto-save after each modification
- Maintains vendor and tag caches for autocomplete
- Supports both soft and permanent delete

---

## Story 2.2: Add Expense GUI Form

**As a** user
**I want** a form to add new expenses
**So that** I can record my salon expenses

### Acceptance Criteria

- [ ] Create `ui/expense_form.py` with Tkinter form containing:

  **Required Fields:**
  | Field | Widget | Notes |
  |-------|--------|-------|
  | Amount (L) | Entry | Numeric validation, max 2 decimals, formatted preview |
  | Date | DateEntry | Default today, calendar popup, no future dates |
  | Category | Combobox | From CategoryManager |
  | Subcategory | Combobox | Filtered by selected category |
  | Vendor | Entry | Autocomplete from existing vendors |
  | Payment Method | Combobox | Cash, Debit Card, Credit Card, Bank Transfer |

  **Optional Fields:**
  | Field | Widget | Notes |
  |-------|--------|-------|
  | Description | Text | Max 500 chars, character counter |
  | Tags | Entry | Comma-separated, autocomplete, display as chips |

  **Recurring Options** (collapsible):
  - Is Recurring: Checkbox
  - Type: Combobox (Weekly, Monthly, Yearly)
  - Action: Combobox (Auto-generate, Reminder only)

  **Buttons:** Save, Clear, Cancel

- [ ] Form validation:
  - Red border on invalid fields
  - Error message below field
  - Disable Save until all required fields valid

- [ ] Vendor autocomplete:
  - Show dropdown with matching vendors as user types (min 2 chars)
  - Display "Recent:" section below field with 5 most recently used vendors
  - Vendors ordered by last_used date (most recent first)
  - Source: ExpenseManager.get_unique_vendors() method

- [ ] After successful save:
  - Show success toast notification
  - Option to add another or close form

### Wireframe

```
+-------------------------------------------------------------+
|                      Add New Expense                     [X] |
+-------------------------------------------------------------+
|                                                              |
|  Amount (L) *                                                |
|  +---------------------------------------------------------+ |
|  | 5,200.00                                                | |
|  +---------------------------------------------------------+ |
|                                                              |
|  Date *                                                      |
|  +-----------------------------------------------+ +---+    |
|  | 15/01/2024                                    | | C |    |
|  +-----------------------------------------------+ +---+    |
|                                                              |
|  Category *                        Subcategory *             |
|  +-------------------------+       +-------------------------+|
|  | Supplies              v |       | Hair products         v ||
|  +-------------------------+       +-------------------------+|
|                                                              |
|  Vendor *                                                    |
|  +---------------------------------------------------------+ |
|  | Hair Store                                            v | |
|  +---------------------------------------------------------+ |
|  Recent: Hair Store, Beauty Supply, Nail World               |
|                                                              |
|  Payment Method *                                            |
|  +---------------------------------------------------------+ |
|  | Cash                                                  v | |
|  +---------------------------------------------------------+ |
|                                                              |
|  Description                                                 |
|  +---------------------------------------------------------+ |
|  | Monthly order of shampoos and conditioners              | |
|  +---------------------------------------------------------+ |
|                                                              |
|  Tags (comma separated)                                      |
|  +---------------------------------------------------------+ |
|  | hair care, monthly order                                | |
|  +---------------------------------------------------------+ |
|                                                              |
|  +---------------------------------------------------------+ |
|  | [ ] This is a recurring expense                         | |
|  |                                                         | |
|  |    Frequency:  [Monthly              v]                 | |
|  |    Action:     [Auto-generate        v]                 | |
|  |    Next occurrence: 15/02/2024                          | |
|  +---------------------------------------------------------+ |
|                                                              |
|  +---------------------------------------------------------+ |
|  | Warning: Similar expense found: Hair Store, L 5,200     | |
|  | [View Existing]  or continue to save new expense        | |
|  +---------------------------------------------------------+ |
|                                                              |
|            [Save]          [Clear]          [Cancel]         |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Use `ttk.Combobox` for dropdowns with autocomplete
- Use `tkcalendar.DateEntry` for date picker
- Real-time validation as user types
- Tab order should follow logical flow

---

## Story 2.3: View Expenses List

**As a** user
**I want** to see all my expenses in a list
**So that** I can review my spending

### Acceptance Criteria

- [ ] Create `ui/expense_list.py` with:

  **Summary Bar:**
  - Total: L X,XXX.XX (sum of displayed expenses)
  - Count: XX expenses
  - Average: L X,XXX.XX

  **Search Box:**
  - Quick search (vendor, description, tags)
  - Real-time filtering
  - Clear button (X)

  **Treeview Table Columns:**
  | Column | Sortable | Notes |
  |--------|----------|-------|
  | Date | Yes | DD/MM/YYYY format |
  | Category | Yes | |
  | Subcategory | No | |
  | Vendor | Yes | |
  | Description | No | Truncated to 30 chars |
  | Amount | Yes | Right-aligned, L X,XXX.XX |
  | Payment Method | No | |

  **Row Features:**
  - Alternating row colors
  - Hover/selection highlight
  - Multi-select (Ctrl+Click, Shift+Click)
  - Recurring expense indicator icon

  **Row Actions:**
  - Double-click: Edit expense
  - Right-click: Context menu (View, Edit, Delete, Copy, Save as Template)

  **Pagination:** 50 per page, navigation controls

  **Toolbar:** [+ Add New] [Edit] [Delete] [Refresh]

### Wireframe

```
+-------------------------------------------------------------------------------------+
|                                    Expenses                                          |
+-------------------------------------------------------------------------------------+
|  [Search expenses...____________________] [X]     [+ New Expense]  [Filters v]      |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Total: L 296,500.00    |    Count: 100 expenses    |    Average: L 2,965.00        |
|                                                                                      |
+-------------------------------------------------------------------------------------+
| # | Date v      | Category    | Subcategory    | Vendor       | Amount      | Pay   |
+---+-------------+-------------+----------------+--------------+-------------+-------+
| o | 15/01/2024  | Supplies    | Hair products  | Hair Store   | L 5,200.00  | Cash  |
| o | 14/01/2024  | Facilities  | Electricity    | KEK          | L 12,000.00 | Bank  |
| o | 13/01/2024  | Staff       | Salaries       | Ana Koci     | L 45,000.00 | Bank  |
| o | 12/01/2024  | Supplies    | Nail products  | Nail World   | L 8,500.00  | Card  |
| o | 11/01/2024  | Equipment   | Styling tools  | Pro Tools    | L 15,000.00 | Card  |
|   |             |             |                |              |             |       |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  [Delete Selected]                     [First] [< Prev]  Page 1 of 10  [Next >] [Last]|
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Right-Click Context Menu
```
+---------------------+
| Edit                |
| View Details        |
|---------------------|
| Delete              |
| Permanent Delete    |
|---------------------|
| Copy                |
| Save as Template    |
+---------------------+
```

### Technical Notes
- Use `ttk.Treeview` for the table
- Store expense_id in hidden column
- Format amounts with thousand separators
- Load data in batches for large datasets

---

## Story 2.4: Edit Expense

**As a** user
**I want** to edit existing expenses
**So that** I can correct mistakes

### Acceptance Criteria

- [ ] Reuse expense form from Story 2.2 in "edit mode"
- [ ] Pre-populate all fields with existing values
- [ ] Show read-only information:
  - Expense ID (for reference)
  - Created: DD/MM/YYYY HH:MM
  - Last Updated: DD/MM/YYYY HH:MM
- [ ] Visual indication of "Edit Mode" (title, color accent)
- [ ] Track changes:
  - Highlight modified fields
  - Show original value on hover
- [ ] Significant change warning:
  - If amount changes by more than 50%, show confirmation
- [ ] On save:
  - Update `updated_at` timestamp
  - Log changes for audit trail

### Wireframe (Edit Mode Header)

```
+-------------------------------------------------------------+
|                       Edit Expense                       [X] |
+-------------------------------------------------------------+
|                                                              |
|  ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890                   |
|  Created: 15/01/2024 10:30    Modified: 15/01/2024 14:22    |
|                                                              |
|  ... (same fields as Add form) ...                          |
|                                                              |
|            [Save Changes]     [Delete]     [Cancel]          |
|                                                              |
+-------------------------------------------------------------+
```

---

## Story 2.5: Delete Expense

**As a** user
**I want** to delete expenses
**So that** I can remove incorrect entries

### Acceptance Criteria

- [ ] **Soft Delete** (default):
  - Marks `is_deleted = True`, sets `deleted_at`
  - Removes from main list
  - Can be restored from Deleted Items

- [ ] **Permanent Delete**:
  - Only from Deleted Items view
  - Additional confirmation required
  - Completely removes from database

- [ ] **Bulk Delete**:
  - Multi-select with Ctrl+Click
  - Confirmation shows count and list
  - Progress indicator for large batches

- [ ] **Keyboard Support**:
  - Delete key: Soft delete
  - Shift+Delete: Permanent delete (with confirmation)

### Wireframe: Soft Delete Confirmation

```
+---------------------------------------------+
|              Delete Expense              [X] |
+---------------------------------------------+
|                                              |
|   Are you sure you want to delete            |
|   this expense?                              |
|                                              |
|     L 5,200.00 - Hair Store                  |
|     15/01/2024                               |
|                                              |
|   The item will be moved to trash.           |
|                                              |
|        [Delete]           [Cancel]           |
|                                              |
+---------------------------------------------+
```

### Wireframe: Permanent Delete Confirmation

```
+---------------------------------------------+
|          Permanent Delete                [X] |
+---------------------------------------------+
|                                              |
|   This action cannot be undone!              |
|                                              |
|   Are you sure you want to permanently       |
|   delete this expense?                       |
|                                              |
|     L 5,200.00 - Hair Store                  |
|     15/01/2024                               |
|                                              |
|   [Permanently Delete]        [Cancel]       |
|                                              |
+---------------------------------------------+
```

### Wireframe: Bulk Delete Confirmation

```
+-------------------------------------------------+
|          Delete Multiple Expenses            [X] |
+-------------------------------------------------+
|                                                  |
|   Are you sure you want to delete                |
|   5 selected expenses?                           |
|                                                  |
|   +------------------------------------------+   |
|   | - L 5,200.00 - Hair Store (15/01)        |   |
|   | - L 12,000.00 - KEK (14/01)              |   |
|   | - L 8,500.00 - Nail World (12/01)        |   |
|   | - L 3,000.00 - FB Ads (10/01)            |   |
|   | - L 2,100.00 - CleanPro (06/01)          |   |
|   +------------------------------------------+   |
|                                                  |
|   Total: L 30,800.00                             |
|                                                  |
|      [Delete All]           [Cancel]             |
|                                                  |
+-------------------------------------------------+
```

---

## Story 2.6: Expense Details Dialog

**As a** user
**I want** to view full expense details
**So that** I can see all information

### Acceptance Criteria

- [ ] Modal dialog showing:

  **Header:**
  - Category icon/color
  - Vendor name (large)
  - Amount (prominent)

  **Details Grid:**
  - Date, Category, Subcategory
  - Payment Method
  - Description (full, scrollable)

  **Tags Section:** Colored chips/badges

  **Recurring Info** (if applicable):
  - Type, Action, Next Due Date

  **Metadata:**
  - Expense ID (copyable)
  - Created/Modified timestamps

  **Action Buttons:** [Edit] [Delete] [Copy] [Close]

### Wireframe

```
+-------------------------------------------------------------+
|                      Expense Details                     [X] |
+-------------------------------------------------------------+
|                                                              |
|  +---------------------------------------------------------+ |
|  |                      L 5,200.00                         | |
|  |                    -------------                        | |
|  |                      Hair Store                         | |
|  |                    15/01/2024                           | |
|  +---------------------------------------------------------+ |
|                                                              |
|  +----------------------+----------------------------------+ |
|  | Category             | Supplies                         | |
|  +----------------------+----------------------------------+ |
|  | Subcategory          | Hair products                    | |
|  +----------------------+----------------------------------+ |
|  | Payment Method       | Cash                             | |
|  +----------------------+----------------------------------+ |
|  | Description          | Monthly order of shampoos and    | |
|  |                      | conditioners for the salon       | |
|  +----------------------+----------------------------------+ |
|  | Tags                 | [hair care] [monthly order]      | |
|  +----------------------+----------------------------------+ |
|  | Recurring            | Yes - Monthly (Auto-generate)    | |
|  |                      | Next: 15/02/2024                 | |
|  +----------------------+----------------------------------+ |
|                                                              |
|  +---------------------------------------------------------+ |
|  | Created:  15/01/2024 10:30:45                           | |
|  | Modified: 15/01/2024 14:22:18                           | |
|  | ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890               | |
|  +---------------------------------------------------------+ |
|                                                              |
|            [Edit]           [Delete]          [Close]        |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Modal dialog (blocks parent window)
- Keyboard: Escape to close

---

## Story 2.7: Deleted Items View

**As a** user
**I want** to view and restore deleted expenses
**So that** I can recover accidentally deleted items

### Acceptance Criteria

- [ ] Access via: View > Deleted Items (menu)
- [ ] Show list of soft-deleted expenses:
  - Date, Category, Vendor, Amount
  - Deleted On, Days Until Auto-Delete

- [ ] Actions per row:
  - [Restore] - Return to active expenses
  - [Permanent Delete] - Delete forever

- [ ] Bulk actions:
  - [Restore Selected]
  - [Permanently Delete Selected]
  - [Empty Trash] - Delete all (strong confirmation)

- [ ] Empty state message when no deleted items

- [ ] Auto-cleanup option (settings):
  - Auto-delete after X days (default: 30)

### Wireframe

```
+-------------------------------------------------------------------------------------+
|                                  Deleted Items                                       |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  Items in trash: 5                              [Restore Selected]  [Empty Trash]    |
|                                                                                      |
+-------------------------------------------------------------------------------------+
| # | Deleted On   | Date       | Category   | Vendor      | Amount     | Actions     |
+---+--------------+------------+------------+-------------+------------+-------------+
| o | 14/01 15:30  | 10/01/2024 | Supplies   | Test Vendor | L 100.00   | [R] [X]     |
| o | 13/01 10:22  | 05/01/2024 | Equipment  | Wrong Entry | L 5,000.00 | [R] [X]     |
| o | 12/01 09:15  | 01/01/2024 | Marketing  | Duplicate   | L 500.00   | [R] [X]     |
+-------------------------------------------------------------------------------------+
|                                                                                      |
|  [R] = Restore    [X] = Permanently Delete                                           |
|                                                                                      |
|  Items in trash will be permanently deleted after 30 days                            |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Technical Notes
- Filter by `is_deleted = True`
- Sort by `deleted_at` descending

---

## Story 2.8: Empty State Handling

**As a** user
**I want** helpful guidance when there's no data
**So that** I know how to get started

### Acceptance Criteria

- [ ] **Expense List Empty State:**
  - Icon, message, [+ Add First Expense] button
  - Quick tips for getting started

- [ ] **Filtered Results Empty State:**
  - "No expenses match your filters"
  - [Clear Filters] button

- [ ] **Search Results Empty State:**
  - "No results for [search term]"
  - [Clear Search] button

- [ ] **Dashboard Empty State:**
  - Placeholder charts with "No data"
  - Getting started checklist

- [ ] **Budget Empty State:**
  - "No budgets set for this month"
  - [Set Up Budget] button

### Wireframe: No Expenses

```
+-------------------------------------------------------------------------------------+
|                                                                                      |
|                                                                                      |
|                                   [icon]                                             |
|                                                                                      |
|                        No expenses recorded yet                                      |
|                                                                                      |
|              Start tracking your salon expenses by adding                            |
|                       your first expense record.                                     |
|                                                                                      |
|                         [+ Add First Expense]                                        |
|                                                                                      |
|         Quick tips:                                                                  |
|         - Record your daily purchases and bills                                      |
|         - Categorize expenses for better tracking                                    |
|         - Set up budgets to control spending                                         |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

### Wireframe: No Search Results

```
+-------------------------------------------------------------------------------------+
|                                                                                      |
|                                   [icon]                                             |
|                                                                                      |
|                        No expenses match your filters                                |
|                                                                                      |
|            Try adjusting your search criteria or clear filters                       |
|                                                                                      |
|                            [Clear All Filters]                                       |
|                                                                                      |
+-------------------------------------------------------------------------------------+
```

---

## Story 2.9: Duplicate Expense Detection

**As a** user
**I want** warning about potential duplicate entries
**So that** I don't accidentally record the same expense twice

### Acceptance Criteria

- [ ] On save, check for similar expenses:
  - **Exact duplicate**: Same vendor + amount + date
  - **Likely duplicate**: Same vendor + amount + date within 3 days

- [ ] Show warning dialog with:
  - Existing expense summary
  - New expense summary
  - Options: [View Existing] [Save Anyway] [Cancel]

- [ ] Configuration in settings:
  - Enable/disable duplicate detection
  - Days threshold (default: 3)

### Wireframe

```
+---------------------------------------------+
|        Possible Duplicate Found          [X] |
+---------------------------------------------+
|                                              |
|   A similar expense already exists:          |
|                                              |
|   +--------------------------------------+   |
|   | 13/01/2024 - Hair Store              |   |
|   | L 5,200.00 - Supplies                |   |
|   +--------------------------------------+   |
|                                              |
|   Your new expense:                          |
|   +--------------------------------------+   |
|   | 15/01/2024 - Hair Store              |   |
|   | L 5,200.00 - Supplies                |   |
|   +--------------------------------------+   |
|                                              |
|   [View Existing]  [Save Anyway]  [Cancel]   |
|                                              |
+---------------------------------------------+
```

---

## Story 2.10: Quick Add Templates

**As a** user
**I want** to quickly add common expenses
**So that** I save time on repetitive entries

### Acceptance Criteria

- [ ] Create `models/template.py` with dataclass:

  **ExpenseTemplate Fields:**
  | Field | Type | Description |
  |-------|------|-------------|
  | template_id | str | UUID, auto-generated |
  | name | str | Template display name |
  | category | str | Expense category |
  | subcategory | str | Expense subcategory |
  | vendor | str | Default vendor name |
  | typical_amount | float | Default amount |
  | payment_method | str | Default payment method |
  | description | str | Default description |
  | tags | List[str] | Optional tags (stored as comma-separated in CSV) |
  | use_count | int | Number of times used |
  | last_used | datetime | Last usage timestamp |
  | created_at | datetime | Creation timestamp |

  **Methods:**
  ```python
  @dataclass
  class ExpenseTemplate:
      """Template for quickly creating common expenses"""

      def to_dict(self) -> dict
          """Convert to dictionary for CSV serialization"""

      @classmethod
      def from_dict(cls, data: dict) -> 'ExpenseTemplate'
          """Create ExpenseTemplate from dictionary"""

      def to_expense(self, date: datetime, amount: float = None) -> 'Expense'
          """Create an Expense from this template"""

      def increment_usage(self) -> None
          """Increment use_count and update last_used"""
  ```

- [ ] Create `managers/template_manager.py`:

  **TemplateManager Methods:**
  ```python
  class TemplateManager:
      """Manages expense template operations"""

      def __init__(self, data_manager: DataManager)
          """Initialize with DataManager, load templates"""

      def load_templates(self) -> None
          """Load templates from CSV"""

      def save_templates(self) -> None
          """Save templates to CSV"""

      def add_template(self, template: ExpenseTemplate) -> str
          """Add new template, return template_id"""

      def get_template(self, template_id: str) -> Optional[ExpenseTemplate]
          """Get template by ID"""

      def update_template(self, template_id: str, updates: Dict) -> bool
          """Update template fields"""

      def delete_template(self, template_id: str) -> bool
          """Delete template"""

      def get_all_templates(self) -> List[ExpenseTemplate]
          """Get all templates sorted by use_count (most used first)"""

      def get_top_templates(self, n: int = 5) -> List[ExpenseTemplate]
          """Get top N most used templates"""

      def create_from_expense(self, expense: Expense, name: str) -> ExpenseTemplate
          """Create a template from an existing expense"""

      def search_templates(self, query: str) -> List[ExpenseTemplate]
          """Search templates by name"""
  ```

- [ ] **Quick Add Button/Menu:**
  - Shows list of saved templates
  - Most used first
  - Search by name

- [ ] **Use Template:**
  - Opens expense form pre-filled
  - User adjusts amount/date
  - One-click save

- [ ] **Create Template:**
  - From existing expense: Right-click > "Save as Template"
  - From scratch: Templates > Create New
  - Stores: Name, Category, Subcategory, Vendor, Typical Amount, Payment Method, Description, Tags

- [ ] **Template Manager:**
  - View, edit, delete templates
  - Reorder (drag/drop or up/down)
  - Track usage count and last used

- [ ] **Storage:** `data/templates.csv`

### Wireframe: Quick Add

```
+-------------------------------------------------------------+
|                      Quick Add Expense                   [X] |
+-------------------------------------------------------------+
|                                                              |
|  Select a template or create new:                            |
|                                                              |
|  +---------------------------------------------------------+ |
|  | * Monthly Rent          | Facilities | L 80,000   [Use] | |
|  +---------------------------------------------------------+ |
|  | * Hair Products Order   | Supplies   | L 5,000    [Use] | |
|  +---------------------------------------------------------+ |
|  | * Electricity Bill      | Facilities | L 12,000   [Use] | |
|  +---------------------------------------------------------+ |
|  | * Staff Salary          | Staff      | L 45,000   [Use] | |
|  +---------------------------------------------------------+ |
|                                                              |
|  [+ Create New Template]           [Manage Templates]        |
|                                                              |
|                              [Cancel]                        |
|                                                              |
+-------------------------------------------------------------+
```

### Wireframe: Template Manager

```
+-------------------------------------------------------------+
|                    Manage Templates                      [X] |
+-------------------------------------------------------------+
|                                                              |
|  Expense Templates                         [+ New Template]  |
|                                                              |
|  +-----------------------------------------------------------+
|  | Name                | Category   | Vendor      | Amount   |
|  +---------------------+------------+-------------+----------+
|  | Monthly Rent        | Facilities | Landlord    | L 80,000 |
|  | Hair Products Order | Supplies   | Hair Store  | L 5,000  |
|  | Electricity Bill    | Facilities | KEK         | L 12,000 |
|  | Staff Salary - Ana  | Staff      | Ana Koci    | L 45,000 |
|  +-----------------------------------------------------------+
|                                                              |
|  Selected: Monthly Rent                                      |
|                                                              |
|        [Use Template]    [Edit]    [Delete]    [Close]       |
|                                                              |
+-------------------------------------------------------------+
```

### Wireframe: Create/Edit Template

```
+-------------------------------------------------+
|              Create Template                 [X] |
+-------------------------------------------------+
|                                                  |
|  Template Name *                                 |
|  +-------------------------------------------+  |
|  | Monthly Rent                              |  |
|  +-------------------------------------------+  |
|                                                  |
|  Category *           Subcategory                |
|  +-----------------+  +---------------------+    |
|  | Facilities    v |  | Rent              v |    |
|  +-----------------+  +---------------------+    |
|                                                  |
|  Default Vendor                                  |
|  +-------------------------------------------+  |
|  | Landlord                                  |  |
|  +-------------------------------------------+  |
|                                                  |
|  Default Amount (L)                              |
|  +-------------------------------------------+  |
|  | 80,000.00                                 |  |
|  +-------------------------------------------+  |
|                                                  |
|  Payment Method                                  |
|  +-------------------------------------------+  |
|  | Bank Transfer                           v |  |
|  +-------------------------------------------+  |
|                                                  |
|  Default Description                             |
|  +-------------------------------------------+  |
|  | Monthly rent payment                      |  |
|  +-------------------------------------------+  |
|                                                  |
|           [Save]              [Cancel]           |
|                                                  |
+-------------------------------------------------+
```

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 2.1 | 7.1 (DataManager), 9.1, 9.2 |
| 2.2 | 2.1, 1.2, 1.3 |
| 2.3 | 2.1 |
| 2.4 | 2.2 |
| 2.5 | 2.1 |
| 2.6 | 2.1 |
| 2.7 | 2.1, 2.5 |
| 2.8 | 2.3 |
| 2.9 | 2.1, 2.2 |
| 2.10 | 2.2, 7.1 (DataManager) |

---

## Testing Requirements

- [ ] Unit tests for ExpenseManager (all CRUD operations)
- [ ] Unit tests for duplicate detection
- [ ] Unit tests for TemplateManager (CRUD, search, usage tracking)
- [ ] Unit tests for ExpenseTemplate dataclass (to_dict, from_dict, to_expense)
- [ ] Integration tests for form validation
- [ ] UI tests for expense form
- [ ] Test bulk operations with large datasets
- [ ] Test template create/use cycle
- [ ] Test template creation from existing expense
