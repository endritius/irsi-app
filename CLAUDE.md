# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Beauty Salon Expense Management** - A Python desktop application for tracking and analyzing salon business expenses.

## Configuration

| Setting | Value |
|---------|-------|
| Interface | GUI with Tkinter |
| Currency | ALL (Albanian Lek) - symbol: L |
| Date Format | DD/MM/YYYY |
| Budget Period | Calendar month |
| Payment Methods | Cash, Debit Card, Credit Card, Bank Transfer |
| Recurring | Auto-generate OR reminder (user choice per expense) |

## Documentation

| Document | Purpose |
|----------|---------|
| `BEAUTY_SALON_PROJECT_OVERVIEW.md` | Epics and high-level requirements |
| `IMPLEMENTATION_STORIES.md` | Detailed user stories with acceptance criteria |
| `Demo_Project_Python.pdf` | Original requirements reference |

## Commands

```bash
pip install -r requirements.txt    # Install dependencies
python main.py                     # Run application
python -m pytest tests/            # Run tests
```

## Dependencies

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
```

## Architecture

```
├── models/           # Data classes (Expense, Budget, Category)
├── managers/         # Business logic (ExpenseManager, BudgetManager, FilterManager)
├── reports/          # ReportGenerator for statistical analysis
├── visualization/    # Visualizer for Matplotlib/Seaborn charts
├── persistence/      # DataManager for CSV file I/O
├── exports/          # PDF (ReportLab), Excel (openpyxl), image exporters
├── ui/               # Tkinter GUI (main_window, forms, dialogs, dashboard)
├── utils/            # Validators, error handling, formatters, exceptions
├── data/             # CSV storage (expenses.csv, budgets.csv, settings.json)
├── logs/             # Error and activity logs
├── config.py         # Application constants
└── main.py           # Entry point
```

## Expense Categories

| Category | Subcategories |
|----------|---------------|
| Supplies | Hair products, Nail products, Skincare, Disposables, Cleaning |
| Equipment | Styling tools, Furniture, Technology, Maintenance |
| Facilities | Rent, Electricity, Water, Gas, Internet, Insurance |
| Staff | Salaries, Commissions, Training, Uniforms |
| Marketing | Advertising, Social media, Promotions, Loyalty programs |
| Administrative | Software, Accounting, Licenses, Bank fees |

## Implementation Priority

1. Core Data Models (Epic 1)
2. Error Handling & Validation (Epic 9)
3. CRUD Operations (Epic 2)
4. Data Persistence (Epic 7)
5. Filtering & Sorting (Epic 3)
6. Budget Tracking (Epic 4)
7. Reporting (Epic 5)
8. Visualizations (Epic 6)
9. Export (Epic 8)

## Key Implementation Notes

- Use `@dataclass` for Expense and Budget models
- Use UUID for expense_id generation
- Amounts: float with 2 decimal display, max 10,000,000
- Dates: stored as datetime, displayed as DD/MM/YYYY
- Tags: stored as comma-separated string in CSV
- Soft delete with `is_deleted` flag, permanent delete requires confirmation
- Auto-save after each CRUD operation
- Log errors to `logs/` with daily rotation
