# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Status

This is a **Beauty Salon Expense Management** Python application currently in specification phase. The implementation has not yet been created.

## Documentation

| Document | Purpose |
|----------|---------|
| `Demo_Project_Python.pdf` | Original expense tracker requirements (reference) |
| `BEAUTY_SALON_PROJECT_OVERVIEW.md` | Adapted requirements with detailed Epics for beauty salon |

**Read `BEAUTY_SALON_PROJECT_OVERVIEW.md` before implementing any features.**

## Expected Commands

Once implemented:
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

## Required Dependencies

- numpy
- pandas
- matplotlib
- seaborn

## Architecture

OOP design with modular structure:

```
├── models/          # Data classes (Expense, Budget, Category)
├── managers/        # Business logic (ExpenseManager, BudgetManager, FilterManager)
├── reports/         # ReportGenerator for statistical analysis
├── visualization/   # Visualizer for charts and dashboards
├── persistence/     # DataManager for CSV file I/O
├── exports/         # PDF, Excel, image exporters
├── utils/           # Input validation utilities
├── data/            # CSV storage (expenses.csv, budgets.csv)
└── main.py          # Entry point
```

## Salon-Specific Expense Categories

- **Supplies**: Hair products, nail products, skincare, disposables, cleaning
- **Equipment**: Styling tools, furniture, technology, repairs
- **Facilities**: Rent, utilities, internet, insurance
- **Staff**: Salaries, commissions, training, uniforms
- **Marketing**: Advertising, social media, promotions
- **Administrative**: Software, accounting, licenses, bank fees

## Implementation Priority

1. Core Data Models (Epic 1)
2. CRUD Operations (Epic 2)
3. Data Persistence (Epic 7)
4. Filtering & Sorting (Epic 3)
5. Budget Tracking (Epic 4)
6. Reporting (Epic 5)
7. Visualizations (Epic 6)
8. Export (Epic 8)
