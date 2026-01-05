# Epic 8: Export & Reporting Output

**Priority:** Low
**Dependencies:** Epic 5 (Reporting), Epic 6 (Visualization)
**Stories:** 3

---

## Story 8.1: PDF Report Export

**As a** user
**I want** to export reports as PDF
**So that** I can share or archive them

### Acceptance Criteria

- [ ] Create `exports/pdf_exporter.py`:

  **PDFReportConfig Dataclass:**
  ```python
  @dataclass
  class PDFReportConfig:
      """Configuration for PDF report generation"""
      title: str = "Expense Report"
      salon_name: str = ""
      salon_address: str = ""
      date_from: Optional[datetime] = None
      date_to: Optional[datetime] = None
      include_summary: bool = True
      include_category_breakdown: bool = True
      include_vendor_analysis: bool = True
      include_trend_table: bool = True
      include_charts: bool = True
      category_chart_path: Optional[str] = None
      trend_chart_path: Optional[str] = None
      budget_chart_path: Optional[str] = None
  ```

  **PDFExporter Methods:**
  ```python
  class PDFExporter:
      """Exports expense reports to PDF format using ReportLab"""

      def __init__(self, report_generator: ReportGenerator)
          """Initialize with ReportGenerator, set up styles"""

      def export_report(self, filepath: str, config: PDFReportConfig,
                       expenses_df: pd.DataFrame = None) -> str
          """Export a complete expense report to PDF"""

      def export_expense_list(self, filepath: str, expenses_df: pd.DataFrame,
                             title: str = "Expense List", salon_name: str = "") -> str
          """Export a list of expenses to PDF"""
  ```

- [ ] **Menu Integration:**
  - Reports > Export as PDF
  - File > Export > PDF Report

### Wireframe: Export PDF Options

```
+---------------------------------------------+
|            Export Report as PDF          [X] |
+---------------------------------------------+
|                                              |
|  Include Sections:                           |
|  +----------------------------------------+  |
|  | [x] Header with salon name and date    |  |
|  | [x] Summary statistics                 |  |
|  | [x] Category breakdown table           |  |
|  | [x] Top expenses list                  |  |
|  | [x] Category pie chart                 |  |
|  | [x] Monthly trend chart                |  |
|  | [ ] Budget vs Actual chart             |  |
|  | [ ] Vendor analysis                    |  |
|  | [x] Page numbers in footer             |  |
|  +----------------------------------------+  |
|                                              |
|  Page Size:         Orientation:             |
|  +---------------+  +-----------------+      |
|  | A4          v |  | Portrait      v |      |
|  +---------------+  +-----------------+      |
|                                              |
|            [Export]         [Cancel]         |
|                                              |
+---------------------------------------------+
```

### Technical Notes
- Use ReportLab for PDF generation
- Generate chart images first, then embed
- A4 page format with page numbers
- Currency formatting with L symbol

---

## Story 8.2: Excel Export

**As a** user
**I want** to export data to Excel
**So that** I can do further analysis

### Acceptance Criteria

- [ ] Create `exports/excel_exporter.py`:

  **ExcelExportConfig Dataclass:**
  ```python
  @dataclass
  class ExcelExportConfig:
      """Configuration for Excel export"""
      filename: str = "expense_export.xlsx"
      include_summary: bool = True
      include_expenses: bool = True
      include_category_breakdown: bool = True
      include_monthly_trend: bool = True
      include_vendor_analysis: bool = True
      include_charts: bool = True
      auto_column_width: bool = True
      date_from: Optional[datetime] = None
      date_to: Optional[datetime] = None
  ```

  **ExcelExporter Methods:**
  ```python
  class ExcelExporter:
      """Exports expense data to Excel format using openpyxl"""

      def __init__(self, report_generator: ReportGenerator)
          """Initialize with ReportGenerator, create styles"""

      def export(self, filepath: str, config: ExcelExportConfig,
                expenses_df: pd.DataFrame = None) -> str
          """Export data to Excel workbook with multiple sheets"""

      def export_filtered_expenses(self, filepath: str,
                                   expenses_df: pd.DataFrame) -> str
          """Export just the filtered expense list to Excel"""
  ```

- [ ] **Menu Integration:**
  - File > Export > Export to Excel

### Wireframe: Export to Excel Options

```
+---------------------------------------------+
|            Export to Excel               [X] |
+---------------------------------------------+
|                                              |
|  Export Options:                             |
|  +----------------------------------------+  |
|  | o Current view (filtered data)         |  |
|  | o All expenses                         |  |
|  | o Selected date range                  |  |
|  +----------------------------------------+  |
|                                              |
|  Include Columns:                            |
|  +----------------------------------------+  |
|  | [x] Date          [x] Category         |  |
|  | [x] Subcategory   [x] Vendor           |  |
|  | [x] Amount        [x] Payment Method   |  |
|  | [x] Description   [ ] Tags             |  |
|  | [ ] ID            [ ] Created Date     |  |
|  +----------------------------------------+  |
|                                              |
|  Additional Sheets:                          |
|  +----------------------------------------+  |
|  | [x] Summary statistics                 |  |
|  | [ ] Category breakdown                 |  |
|  | [ ] Monthly totals                     |  |
|  +----------------------------------------+  |
|                                              |
|            [Export]         [Cancel]         |
|                                              |
+---------------------------------------------+
```

### Technical Notes
- Use openpyxl for Excel generation
- Currency format: `#,##0.00 "L"`
- Date format: DD/MM/YYYY
- Include charts in appropriate sheets
- Auto-filter on data sheets

---

## Story 8.3: Chart Image Export

**As a** user
**I want** to save charts as images
**So that** I can use them in presentations

### Acceptance Criteria

- [ ] Create `exports/image_exporter.py`:

  **ImageFormat Enum:**
  ```python
  class ImageFormat(Enum):
      """Supported image export formats"""
      PNG = "png"
      JPG = "jpg"
      SVG = "svg"
      PDF = "pdf"
  ```

  **ImageResolution Enum:**
  ```python
  class ImageResolution(Enum):
      """Predefined resolution options"""
      SCREEN = 72       # For screen display
      STANDARD = 150    # Good quality
      PRINT = 300       # High quality print
  ```

  **ImageExportConfig Dataclass:**
  ```python
  @dataclass
  class ImageExportConfig:
      """Configuration for image export"""
      format: ImageFormat = ImageFormat.PNG
      resolution: ImageResolution = ImageResolution.STANDARD
      width: Optional[float] = None
      height: Optional[float] = None
      transparent_background: bool = False
  ```

  **ImageExporter Methods:**
  ```python
  class ImageExporter:
      """Exports matplotlib charts as image files"""

      def export_chart(self, figure: Figure, filepath: str,
                      config: ImageExportConfig = None) -> str
          """Export a single chart to an image file"""

      def export_multiple_charts(self, figures: List[Figure], output_dir: str,
                                base_name: str, config: ImageExportConfig = None) -> List[str]
          """Export multiple charts to image files"""

      def export_dashboard_charts(self, charts: dict, output_dir: str,
                                  config: ImageExportConfig = None) -> dict
          """Export all dashboard charts with meaningful names"""

      def get_file_filter(self, format: ImageFormat) -> str
          """Get file dialog filter string for format"""
  ```

- [ ] **Context Menu Integration:**
  - Right-click on any chart > "Save as Image..."
  - Right-click on any chart > "Copy to Clipboard"

### Wireframe: Save Chart Dialog

```
+---------------------------------------------+
|              Save Chart as Image         [X] |
+---------------------------------------------+
|                                              |
|  File Name                                   |
|  +----------------------------------------+  |
|  | category_pie_chart_jan2024             |  |
|  +----------------------------------------+  |
|                                              |
|  Format:        Resolution:                  |
|  +----------+   +----------------------+     |
|  | PNG    v |   | 150 dpi (Standard) v |     |
|  +----------+   +----------------------+     |
|                                              |
|  Save to:                                    |
|  +----------------------------+ +---------+  |
|  | C:\Users\...\Charts\       | | Browse  |  |
|  +----------------------------+ +---------+  |
|                                              |
|            [Save]           [Cancel]         |
|                                              |
+---------------------------------------------+
```

### Wireframe: Batch Export All Charts

```
+-------------------------------------------------------------+
|              Export All Dashboard Charts                 [X] |
+-------------------------------------------------------------+
|                                                              |
|  Charts to Export:                                           |
|  [x] Category Distribution (category_distribution.png)       |
|  [x] Monthly Trend (monthly_trend.png)                       |
|  [x] Budget vs Actual (budget_vs_actual.png)                 |
|  [x] Top Vendors (top_vendors.png)                           |
|                                                              |
|  Export Settings:                                            |
|  Format: [PNG v]    Resolution: [Standard (150 DPI) v]       |
|                                                              |
|  Output Folder:                                              |
|  +--------------------------------------+ +----------------+ |
|  | C:\Users\...\Charts\January_2024\   | | Browse...      | |
|  +--------------------------------------+ +----------------+ |
|                                                              |
|                              [Export All]     [Cancel]       |
|                                                              |
+-------------------------------------------------------------+
```

### Technical Notes
- Use Matplotlib savefig() method
- Support multiple formats (PNG, JPG, SVG, PDF)
- Support multiple resolutions (72, 150, 300 DPI)
- Transparent background option for PNG/SVG

---

## Dependencies

| Story | Depends On |
|-------|------------|
| 8.1 | 5.1 (ReportGenerator), 6.1 (Visualizer) |
| 8.2 | 5.1 (ReportGenerator) |
| 8.3 | 6.1 (Visualizer) |

---

## Testing Requirements

- [ ] Unit tests for PDFExporter (all section generators)
- [ ] Unit tests for ExcelExporter (all sheet generators)
- [ ] Unit tests for ImageExporter (all formats)
- [ ] Tests with empty data
- [ ] Tests with large data sets
- [ ] File validation tests (open exported files)
- [ ] Format-specific tests (PDF structure, Excel formulas)
