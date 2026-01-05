# Beauty Salon Expense Manager - Project Implementation

## Installation Guide (Windows)

### Prerequisites
- Python 3.10 or higher installed ([Download Python](https://www.python.org/downloads/))
- During Python installation, check "Add Python to PATH"

### Step-by-Step Installation

1. **Open Command Prompt**
   ```
   Press Win + R, type "cmd", press Enter
   ```

2. **Navigate to the project folder**
   ```cmd
   cd path\to\Project Implementation
   ```

3. **Create a virtual environment**
   ```cmd
   python -m venv venv
   ```

4. **Activate the virtual environment**
   ```cmd
   venv\Scripts\activate
   ```
   You should see `(venv)` appear at the beginning of your command line.

5. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

6. **Run the application**
   ```cmd
   python main.py
   ```

### Deactivating the Virtual Environment

When you're done using the application:
```cmd
deactivate
```

### Running the App Again

After initial setup, you only need to:
```cmd
cd path\to\Project Implementation
venv\Scripts\activate
python main.py
```

### Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not recognized | Reinstall Python with "Add to PATH" checked |
| `pip` not found | Run `python -m pip install -r requirements.txt` |
| Tkinter import error | Reinstall Python with tcl/tk option selected |
| Permission denied | Run Command Prompt as Administrator |

---

## Quick Reference

| Setting | Value |
|---------|-------|
| Framework | Python 3.10+ with Tkinter |
| Currency | Albanian Lek (L) |
| Date Format | DD/MM/YYYY |
| Window Size | 1024 x 768 (minimum), 1280 x 800 (default) |

---

## Epic Index

| # | Epic | File | Stories | Priority |
|---|------|------|---------|----------|
| 1 | Core Data Models | [EPIC_01_CORE_DATA_MODELS.md](EPIC_01_CORE_DATA_MODELS.md) | 1.1-1.7 | High |
| 2 | Expense Management | [EPIC_02_EXPENSE_MANAGEMENT.md](EPIC_02_EXPENSE_MANAGEMENT.md) | 2.1-2.10 | High |
| 3 | Filtering & Sorting | [EPIC_03_FILTERING_AND_SORTING.md](EPIC_03_FILTERING_AND_SORTING.md) | 3.1-3.3 | Medium |
| 4 | Budget Management | [EPIC_04_BUDGET_MANAGEMENT.md](EPIC_04_BUDGET_MANAGEMENT.md) | 4.1-4.5 | Medium |
| 5 | Reporting & Analytics | [EPIC_05_REPORTING_AND_ANALYTICS.md](EPIC_05_REPORTING_AND_ANALYTICS.md) | 5.1-5.7 | Medium |
| 6 | Visualization & Dashboards | [EPIC_06_VISUALIZATION_AND_DASHBOARDS.md](EPIC_06_VISUALIZATION_AND_DASHBOARDS.md) | 6.1-6.5 | Medium-Low |
| 7 | Data Persistence | [EPIC_07_DATA_PERSISTENCE.md](EPIC_07_DATA_PERSISTENCE.md) | 7.1-7.4 | High |
| 8 | Export Functionality | [EPIC_08_EXPORT_FUNCTIONALITY.md](EPIC_08_EXPORT_FUNCTIONALITY.md) | 8.1-8.3 | Low |
| 9 | Error Handling | [EPIC_09_ERROR_HANDLING.md](EPIC_09_ERROR_HANDLING.md) | 9.1-9.5 | High |
| 10 | Main Application | [EPIC_10_MAIN_APPLICATION.md](EPIC_10_MAIN_APPLICATION.md) | 10.1-10.5 | High |
| 11 | Enhancements | [EPIC_11_ENHANCEMENTS.md](EPIC_11_ENHANCEMENTS.md) | 11.1-11.6 | Low (Future) |

---

## Implementation Order

1. **Foundation** - Epic 1 (Data Models), Epic 9 (Error Handling)
2. **Core CRUD** - Epic 7 (Persistence), Epic 2 (Expense Management)
3. **Filtering** - Epic 3 (Filtering & Sorting)
4. **Budgets** - Epic 4 (Budget Management)
5. **Reporting** - Epic 5 (Reporting & Analytics)
6. **Visualization** - Epic 6 (Dashboards & Charts)
7. **Export** - Epic 8 (PDF, Excel, Images)
8. **Integration** - Epic 10 (Main Application)
9. **Polish** - Epic 11 (Enhancements)

---

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
pytest>=7.0.0
```
