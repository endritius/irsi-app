# Epic 8: Export & Reporting Output - Implementation Tasks

**Phase:** 9 (Export)
**Priority:** Low
**Dependencies:** Epic 5 (Reporting), Epic 6 (Visualization)
**Estimated Tasks:** 25+

---

## Story 8.1: PDF Report Export

**Prerequisites:** Story 5.1 (ReportGenerator), Story 6.1 (Visualizer)

### Task 8.1.1: Create exports package
- [ ] Create `exports/__init__.py`:
```python
"""
Export functionality for Beauty Salon Expense Manager.
"""

from .pdf_exporter import PDFExporter, PDFReportConfig
from .excel_exporter import ExcelExporter, ExcelExportConfig
from .image_exporter import ImageExporter, ImageExportConfig, ImageFormat, ImageResolution

__all__ = [
    'PDFExporter',
    'PDFReportConfig',
    'ExcelExporter',
    'ExcelExportConfig',
    'ImageExporter',
    'ImageExportConfig',
    'ImageFormat',
    'ImageResolution'
]
```

### Task 8.1.2: Create PDFReportConfig dataclass
- [ ] Create `exports/pdf_exporter.py`:
```python
"""
PDFExporter - Exports expense reports to PDF format.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

import pandas as pd

from reports.report_generator import ReportGenerator


@dataclass
class PDFReportConfig:
    """Configuration for PDF report generation."""
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
    page_size: str = "A4"  # A4 or Letter
    orientation: str = "portrait"  # portrait or landscape
    include_page_numbers: bool = True
```

### Task 8.1.3: Create PDFExporter class
- [ ] Add PDFExporter class:
```python
class PDFExporter:
    """Exports expense reports to PDF format using ReportLab."""

    def __init__(self, report_generator: ReportGenerator):
        """Initialize with ReportGenerator."""
        self.report_generator = report_generator
        self._setup_styles()

    def _setup_styles(self):
        """Set up document styles."""
        self.styles = getSampleStyleSheet()

        # Title style
        self.styles.add(ParagraphStyle(
            name='ReportTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            alignment=TA_CENTER,
            spaceAfter=30
        ))

        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='ReportSubtitle',
            parent=self.styles['Normal'],
            fontSize=12,
            alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=20
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=colors.HexColor('#9C27B0')
        ))

        # Currency style
        self.styles.add(ParagraphStyle(
            name='Currency',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))

    def _get_page_size(self, config: PDFReportConfig):
        """Get page size from config."""
        base_size = A4 if config.page_size == "A4" else letter
        if config.orientation == "landscape":
            return (base_size[1], base_size[0])
        return base_size
```

### Task 8.1.4: Implement export_report method
- [ ] Add main export method:
```python
    def export_report(
        self,
        filepath: str,
        config: PDFReportConfig,
        expenses_df: pd.DataFrame = None
    ) -> str:
        """Export a complete expense report to PDF."""
        page_size = self._get_page_size(config)

        doc = SimpleDocTemplate(
            filepath,
            pagesize=page_size,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = []

        # Title
        elements.append(Paragraph(config.title, self.styles['ReportTitle']))

        # Salon info and date range
        if config.salon_name:
            elements.append(Paragraph(config.salon_name, self.styles['ReportSubtitle']))
        if config.salon_address:
            elements.append(Paragraph(config.salon_address, self.styles['Normal']))

        date_range = ""
        if config.date_from and config.date_to:
            date_range = f"{config.date_from.strftime('%d/%m/%Y')} - {config.date_to.strftime('%d/%m/%Y')}"
            elements.append(Paragraph(f"Period: {date_range}", self.styles['ReportSubtitle']))

        elements.append(Spacer(1, 20))

        # Summary section
        if config.include_summary:
            elements.extend(self._create_summary_section(expenses_df))

        # Category breakdown
        if config.include_category_breakdown:
            elements.extend(self._create_category_section(expenses_df))

        # Vendor analysis
        if config.include_vendor_analysis:
            elements.extend(self._create_vendor_section(expenses_df))

        # Charts
        if config.include_charts:
            elements.extend(self._create_chart_section(config))

        # Build document
        doc.build(elements, onFirstPage=self._add_page_number if config.include_page_numbers else None,
                 onLaterPages=self._add_page_number if config.include_page_numbers else None)

        return filepath

    def _add_page_number(self, canvas, doc):
        """Add page number to bottom of page."""
        canvas.saveState()
        canvas.setFont('Helvetica', 9)
        page_num = canvas.getPageNumber()
        text = f"Page {page_num}"
        canvas.drawCentredString(doc.pagesize[0]/2, 1*cm, text)
        canvas.restoreState()
```

### Task 8.1.5: Implement section builders
- [ ] Add section creation methods:
```python
    def _create_summary_section(self, df: pd.DataFrame) -> List:
        """Create summary statistics section."""
        elements = []
        elements.append(Paragraph("Summary Statistics", self.styles['SectionHeader']))

        summary = self.report_generator.get_statistical_summary(df)

        data = [
            ['Metric', 'Value'],
            ['Total Expenses', f'L {summary.total:,.2f}'],
            ['Transaction Count', str(summary.count)],
            ['Average', f'L {summary.average:,.2f}'],
            ['Median', f'L {summary.median:,.2f}'],
            ['Minimum', f'L {summary.minimum:,.2f}'],
            ['Maximum', f'L {summary.maximum:,.2f}'],
            ['Std. Deviation', f'L {summary.std_deviation:,.2f}'],
        ]

        table = Table(data, colWidths=[200, 150])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9C27B0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 1), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F5F5F5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_category_section(self, df: pd.DataFrame) -> List:
        """Create category breakdown section."""
        elements = []
        elements.append(Paragraph("Category Breakdown", self.styles['SectionHeader']))

        category_df = self.report_generator.get_category_summary(df)

        if category_df.empty:
            elements.append(Paragraph("No category data available.", self.styles['Normal']))
            return elements

        data = [['Category', 'Total', '%', 'Count', 'Average']]
        for _, row in category_df.iterrows():
            data.append([
                row['category'],
                f"L {row['total']:,.2f}",
                f"{row['percentage']:.1f}%",
                str(int(row['count'])),
                f"L {row['average']:,.2f}"
            ])

        table = Table(data, colWidths=[120, 100, 60, 60, 100])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9C27B0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_vendor_section(self, df: pd.DataFrame) -> List:
        """Create vendor analysis section."""
        elements = []
        elements.append(Paragraph("Top Vendors", self.styles['SectionHeader']))

        vendor_df = self.report_generator.get_vendor_analysis(top_n=10, df=df)

        if vendor_df.empty:
            elements.append(Paragraph("No vendor data available.", self.styles['Normal']))
            return elements

        data = [['Vendor', 'Total', 'Count', '%']]
        for _, row in vendor_df.iterrows():
            data.append([
                row['vendor'][:30],  # Truncate long names
                f"L {row['total']:,.2f}",
                str(int(row['count'])),
                f"{row['percentage']:.1f}%"
            ])

        table = Table(data, colWidths=[150, 100, 60, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9C27B0')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 20))

        return elements

    def _create_chart_section(self, config: PDFReportConfig) -> List:
        """Create charts section."""
        elements = []

        charts_added = False

        if config.category_chart_path and os.path.exists(config.category_chart_path):
            elements.append(Paragraph("Expense Distribution", self.styles['SectionHeader']))
            elements.append(Image(config.category_chart_path, width=400, height=300))
            elements.append(Spacer(1, 20))
            charts_added = True

        if config.trend_chart_path and os.path.exists(config.trend_chart_path):
            elements.append(Paragraph("Expense Trend", self.styles['SectionHeader']))
            elements.append(Image(config.trend_chart_path, width=400, height=250))
            elements.append(Spacer(1, 20))
            charts_added = True

        if config.budget_chart_path and os.path.exists(config.budget_chart_path):
            elements.append(Paragraph("Budget vs Actual", self.styles['SectionHeader']))
            elements.append(Image(config.budget_chart_path, width=400, height=250))
            charts_added = True

        return elements
```

### Task 8.1.6: Implement export_expense_list method
- [ ] Add expense list export:
```python
    def export_expense_list(
        self,
        filepath: str,
        expenses_df: pd.DataFrame,
        title: str = "Expense List",
        salon_name: str = ""
    ) -> str:
        """Export a list of expenses to PDF."""
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        elements = []

        # Title
        elements.append(Paragraph(title, self.styles['ReportTitle']))
        if salon_name:
            elements.append(Paragraph(salon_name, self.styles['ReportSubtitle']))

        elements.append(Spacer(1, 20))

        if expenses_df.empty:
            elements.append(Paragraph("No expenses to display.", self.styles['Normal']))
        else:
            # Create table
            data = [['Date', 'Category', 'Vendor', 'Amount', 'Payment']]

            for _, row in expenses_df.iterrows():
                date_str = pd.to_datetime(row['date']).strftime('%d/%m/%Y')
                data.append([
                    date_str,
                    row['category'],
                    str(row['vendor'])[:20],
                    f"L {row['amount']:,.2f}",
                    row['payment_method']
                ])

            table = Table(data, colWidths=[70, 90, 100, 80, 70])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#9C27B0')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E0E0E0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ]))

            elements.append(table)

            # Total
            total = expenses_df['amount'].sum()
            elements.append(Spacer(1, 10))
            elements.append(Paragraph(f"<b>Total: L {total:,.2f}</b>", self.styles['Normal']))

        doc.build(elements)
        return filepath
```

### Task 8.1.7: Create PDF export dialog
- [ ] Create `ui/dialogs/pdf_export_dialog.py`:
  - Section checkboxes
  - Page size and orientation
  - File location picker
  - Export and Cancel buttons

### Task 8.1.8: Create PDFExporter tests
- [ ] Create `tests/test_exports/__init__.py`
- [ ] Create `tests/test_exports/test_pdf_exporter.py`

---

## Story 8.2: Excel Export

**Prerequisites:** Story 5.1 (ReportGenerator)

### Task 8.2.1: Create ExcelExportConfig dataclass
- [ ] Create `exports/excel_exporter.py`:
```python
"""
ExcelExporter - Exports expense data to Excel format.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side, PatternFill
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.chart import PieChart, BarChart, Reference

import pandas as pd

from reports.report_generator import ReportGenerator


@dataclass
class ExcelExportConfig:
    """Configuration for Excel export."""
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

### Task 8.2.2: Create ExcelExporter class
- [ ] Add ExcelExporter class:
```python
class ExcelExporter:
    """Exports expense data to Excel format using openpyxl."""

    # Style constants
    HEADER_FILL = PatternFill(start_color="9C27B0", end_color="9C27B0", fill_type="solid")
    HEADER_FONT = Font(bold=True, color="FFFFFF")
    CURRENCY_FORMAT = '#,##0.00 "L"'
    DATE_FORMAT = 'DD/MM/YYYY'

    def __init__(self, report_generator: ReportGenerator):
        """Initialize with ReportGenerator."""
        self.report_generator = report_generator

    def _style_header_row(self, ws, row: int = 1):
        """Apply header styling to a row."""
        for cell in ws[row]:
            cell.fill = self.HEADER_FILL
            cell.font = self.HEADER_FONT
            cell.alignment = Alignment(horizontal='center')

    def _auto_adjust_columns(self, ws):
        """Auto-adjust column widths."""
        for column in ws.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            ws.column_dimensions[column_letter].width = adjusted_width
```

### Task 8.2.3: Implement export method
- [ ] Add main export method:
```python
    def export(
        self,
        filepath: str,
        config: ExcelExportConfig,
        expenses_df: pd.DataFrame = None
    ) -> str:
        """Export data to Excel workbook with multiple sheets."""
        wb = Workbook()

        # Remove default sheet
        default_sheet = wb.active
        wb.remove(default_sheet)

        # Summary sheet
        if config.include_summary:
            self._create_summary_sheet(wb, expenses_df)

        # Expenses sheet
        if config.include_expenses and expenses_df is not None:
            self._create_expenses_sheet(wb, expenses_df)

        # Category breakdown sheet
        if config.include_category_breakdown:
            self._create_category_sheet(wb, expenses_df, config.include_charts)

        # Monthly trend sheet
        if config.include_monthly_trend:
            self._create_trend_sheet(wb, config.include_charts)

        # Vendor analysis sheet
        if config.include_vendor_analysis:
            self._create_vendor_sheet(wb, expenses_df)

        wb.save(filepath)
        return filepath
```

### Task 8.2.4: Implement sheet creation methods
- [ ] Add sheet creation methods:
```python
    def _create_summary_sheet(self, wb: Workbook, df: pd.DataFrame):
        """Create summary statistics sheet."""
        ws = wb.create_sheet("Summary")

        summary = self.report_generator.get_statistical_summary(df)

        ws['A1'] = "Expense Summary Report"
        ws['A1'].font = Font(bold=True, size=14)

        ws['A3'] = "Metric"
        ws['B3'] = "Value"
        self._style_header_row(ws, 3)

        metrics = [
            ('Total Expenses', summary.total, self.CURRENCY_FORMAT),
            ('Transaction Count', summary.count, None),
            ('Average', summary.average, self.CURRENCY_FORMAT),
            ('Median', summary.median, self.CURRENCY_FORMAT),
            ('Minimum', summary.minimum, self.CURRENCY_FORMAT),
            ('Maximum', summary.maximum, self.CURRENCY_FORMAT),
            ('Std. Deviation', summary.std_deviation, self.CURRENCY_FORMAT),
        ]

        for i, (label, value, fmt) in enumerate(metrics, start=4):
            ws[f'A{i}'] = label
            ws[f'B{i}'] = value
            if fmt:
                ws[f'B{i}'].number_format = fmt

        self._auto_adjust_columns(ws)

    def _create_expenses_sheet(self, wb: Workbook, df: pd.DataFrame):
        """Create expenses list sheet."""
        ws = wb.create_sheet("Expenses")

        if df.empty:
            ws['A1'] = "No expenses to display"
            return

        # Select and order columns
        columns = ['date', 'category', 'subcategory', 'vendor', 'amount',
                  'payment_method', 'description']
        export_df = df[columns].copy()

        # Write headers
        headers = ['Date', 'Category', 'Subcategory', 'Vendor', 'Amount',
                  'Payment Method', 'Description']
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws)

        # Write data
        for row_idx, row in enumerate(export_df.itertuples(), start=2):
            ws.cell(row=row_idx, column=1, value=row.date).number_format = self.DATE_FORMAT
            ws.cell(row=row_idx, column=2, value=row.category)
            ws.cell(row=row_idx, column=3, value=row.subcategory)
            ws.cell(row=row_idx, column=4, value=row.vendor)
            ws.cell(row=row_idx, column=5, value=row.amount).number_format = self.CURRENCY_FORMAT
            ws.cell(row=row_idx, column=6, value=row.payment_method)
            ws.cell(row=row_idx, column=7, value=row.description)

        # Add auto-filter
        ws.auto_filter.ref = ws.dimensions

        self._auto_adjust_columns(ws)

    def _create_category_sheet(self, wb: Workbook, df: pd.DataFrame, include_chart: bool):
        """Create category breakdown sheet."""
        ws = wb.create_sheet("Categories")

        category_df = self.report_generator.get_category_summary(df)

        if category_df.empty:
            ws['A1'] = "No category data available"
            return

        # Headers
        headers = ['Category', 'Total', 'Percentage', 'Count', 'Average']
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws)

        # Data
        for row_idx, row in enumerate(category_df.itertuples(), start=2):
            ws.cell(row=row_idx, column=1, value=row.category)
            ws.cell(row=row_idx, column=2, value=row.total).number_format = self.CURRENCY_FORMAT
            ws.cell(row=row_idx, column=3, value=row.percentage / 100).number_format = '0.0%'
            ws.cell(row=row_idx, column=4, value=row.count)
            ws.cell(row=row_idx, column=5, value=row.average).number_format = self.CURRENCY_FORMAT

        self._auto_adjust_columns(ws)

        # Add chart
        if include_chart and len(category_df) > 0:
            chart = PieChart()
            labels = Reference(ws, min_col=1, min_row=2, max_row=len(category_df)+1)
            data = Reference(ws, min_col=2, min_row=1, max_row=len(category_df)+1)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(labels)
            chart.title = "Expenses by Category"
            ws.add_chart(chart, "G2")

    def _create_trend_sheet(self, wb: Workbook, include_chart: bool):
        """Create monthly trend sheet."""
        ws = wb.create_sheet("Monthly Trend")

        trend_df = self.report_generator.get_monthly_trend()

        if trend_df.empty:
            ws['A1'] = "No trend data available"
            return

        # Headers
        headers = ['Month', 'Total', 'Count', 'Average']
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws)

        # Data
        for row_idx, row in enumerate(trend_df.itertuples(), start=2):
            ws.cell(row=row_idx, column=1, value=row.year_month)
            ws.cell(row=row_idx, column=2, value=row.total).number_format = self.CURRENCY_FORMAT
            ws.cell(row=row_idx, column=3, value=row.count)
            ws.cell(row=row_idx, column=4, value=row.average).number_format = self.CURRENCY_FORMAT

        self._auto_adjust_columns(ws)

        # Add chart
        if include_chart and len(trend_df) > 0:
            chart = BarChart()
            data = Reference(ws, min_col=2, min_row=1, max_row=len(trend_df)+1)
            categories = Reference(ws, min_col=1, min_row=2, max_row=len(trend_df)+1)
            chart.add_data(data, titles_from_data=True)
            chart.set_categories(categories)
            chart.title = "Monthly Expense Trend"
            chart.type = "col"
            ws.add_chart(chart, "F2")

    def _create_vendor_sheet(self, wb: Workbook, df: pd.DataFrame):
        """Create vendor analysis sheet."""
        ws = wb.create_sheet("Vendors")

        vendor_df = self.report_generator.get_vendor_analysis(top_n=20, df=df)

        if vendor_df.empty:
            ws['A1'] = "No vendor data available"
            return

        # Headers
        headers = ['Vendor', 'Total', 'Count', 'Average', 'Percentage']
        for col, header in enumerate(headers, start=1):
            ws.cell(row=1, column=col, value=header)
        self._style_header_row(ws)

        # Data
        for row_idx, row in enumerate(vendor_df.itertuples(), start=2):
            ws.cell(row=row_idx, column=1, value=row.vendor)
            ws.cell(row=row_idx, column=2, value=row.total).number_format = self.CURRENCY_FORMAT
            ws.cell(row=row_idx, column=3, value=row.count)
            ws.cell(row=row_idx, column=4, value=row.average).number_format = self.CURRENCY_FORMAT
            ws.cell(row=row_idx, column=5, value=row.percentage / 100).number_format = '0.0%'

        self._auto_adjust_columns(ws)
```

### Task 8.2.5: Implement filtered expenses export
- [ ] Add simple export method:
```python
    def export_filtered_expenses(
        self,
        filepath: str,
        expenses_df: pd.DataFrame
    ) -> str:
        """Export just the filtered expense list to Excel."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Expenses"

        if expenses_df.empty:
            ws['A1'] = "No expenses to display"
            wb.save(filepath)
            return filepath

        # Select columns
        columns = ['date', 'category', 'subcategory', 'vendor', 'amount',
                  'payment_method', 'description', 'tags']
        export_df = expenses_df[[c for c in columns if c in expenses_df.columns]].copy()

        # Write headers
        for col, header in enumerate(export_df.columns, start=1):
            ws.cell(row=1, column=col, value=header.replace('_', ' ').title())
        self._style_header_row(ws)

        # Write data
        for row_idx, (_, row) in enumerate(export_df.iterrows(), start=2):
            for col_idx, value in enumerate(row, start=1):
                cell = ws.cell(row=row_idx, column=col_idx, value=value)
                if 'amount' in export_df.columns[col_idx-1]:
                    cell.number_format = self.CURRENCY_FORMAT
                elif 'date' in export_df.columns[col_idx-1]:
                    cell.number_format = self.DATE_FORMAT

        ws.auto_filter.ref = ws.dimensions
        self._auto_adjust_columns(ws)

        # Add total row
        total_row = len(export_df) + 2
        ws[f'A{total_row}'] = "TOTAL"
        ws[f'A{total_row}'].font = Font(bold=True)

        if 'amount' in export_df.columns:
            amount_col_idx = list(export_df.columns).index('amount') + 1
            col_letter = ws.cell(row=1, column=amount_col_idx).column_letter
            ws[f'{col_letter}{total_row}'] = expenses_df['amount'].sum()
            ws[f'{col_letter}{total_row}'].number_format = self.CURRENCY_FORMAT
            ws[f'{col_letter}{total_row}'].font = Font(bold=True)

        wb.save(filepath)
        return filepath
```

### Task 8.2.6: Create Excel export dialog
- [ ] Create `ui/dialogs/excel_export_dialog.py`:
  - Export options (current view, all, date range)
  - Column selection checkboxes
  - Additional sheets checkboxes
  - File location picker

### Task 8.2.7: Create ExcelExporter tests
- [ ] Create `tests/test_exports/test_excel_exporter.py`

---

## Story 8.3: Chart Image Export

**Prerequisites:** Story 6.1 (Visualizer)

### Task 8.3.1: Create ImageExporter class
- [ ] Create `exports/image_exporter.py`:
```python
"""
ImageExporter - Exports matplotlib charts as image files.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple

from matplotlib.figure import Figure


class ImageFormat(Enum):
    """Supported image export formats."""
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"
    PDF = "pdf"


class ImageResolution(Enum):
    """Predefined resolution options."""
    SCREEN = 72       # For screen display
    STANDARD = 150    # Good quality
    PRINT = 300       # High quality print


@dataclass
class ImageExportConfig:
    """Configuration for image export."""
    format: ImageFormat = ImageFormat.PNG
    resolution: ImageResolution = ImageResolution.STANDARD
    width: Optional[float] = None
    height: Optional[float] = None
    transparent_background: bool = False


class ImageExporter:
    """Exports matplotlib charts as image files."""

    FORMAT_EXTENSIONS = {
        ImageFormat.PNG: '.png',
        ImageFormat.JPG: '.jpg',
        ImageFormat.SVG: '.svg',
        ImageFormat.PDF: '.pdf',
    }

    FORMAT_FILTERS = {
        ImageFormat.PNG: "PNG Image (*.png)",
        ImageFormat.JPG: "JPEG Image (*.jpg)",
        ImageFormat.SVG: "SVG Vector (*.svg)",
        ImageFormat.PDF: "PDF Document (*.pdf)",
    }

    def __init__(self):
        """Initialize exporter."""
        pass
```

### Task 8.3.2: Implement export methods
- [ ] Add export functionality:
```python
    def export_chart(
        self,
        figure: Figure,
        filepath: str,
        config: ImageExportConfig = None
    ) -> str:
        """Export a single chart to an image file."""
        if config is None:
            config = ImageExportConfig()

        # Set figure size if specified
        if config.width and config.height:
            figure.set_size_inches(config.width, config.height)

        # Export options
        save_kwargs = {
            'dpi': config.resolution.value,
            'bbox_inches': 'tight',
        }

        # Transparent background for PNG and SVG
        if config.transparent_background and config.format in (ImageFormat.PNG, ImageFormat.SVG):
            save_kwargs['transparent'] = True

        # Save
        figure.savefig(filepath, format=config.format.value, **save_kwargs)

        return filepath

    def export_multiple_charts(
        self,
        figures: List[Figure],
        output_dir: str,
        base_name: str,
        config: ImageExportConfig = None
    ) -> List[str]:
        """Export multiple charts to image files."""
        if config is None:
            config = ImageExportConfig()

        exported = []
        ext = self.FORMAT_EXTENSIONS[config.format]

        for i, fig in enumerate(figures, start=1):
            filepath = f"{output_dir}/{base_name}_{i}{ext}"
            self.export_chart(fig, filepath, config)
            exported.append(filepath)

        return exported

    def export_dashboard_charts(
        self,
        charts: Dict[str, Figure],
        output_dir: str,
        config: ImageExportConfig = None
    ) -> Dict[str, str]:
        """Export all dashboard charts with meaningful names."""
        if config is None:
            config = ImageExportConfig()

        exported = {}
        ext = self.FORMAT_EXTENSIONS[config.format]

        for name, figure in charts.items():
            filepath = f"{output_dir}/{name}{ext}"
            self.export_chart(figure, filepath, config)
            exported[name] = filepath

        return exported

    def get_file_filter(self, format: ImageFormat) -> str:
        """Get file dialog filter string for format."""
        return self.FORMAT_FILTERS.get(format, "All Files (*.*)")

    def get_all_file_filters(self) -> str:
        """Get combined file filter string for all formats."""
        filters = list(self.FORMAT_FILTERS.values())
        return ";;".join(filters)
```

### Task 8.3.3: Create chart save dialog
- [ ] Create `ui/dialogs/chart_save_dialog.py`:
  - File name field
  - Format dropdown (PNG, JPG, SVG, PDF)
  - Resolution dropdown
  - Save location picker

### Task 8.3.4: Create batch export dialog
- [ ] Create `ui/dialogs/batch_export_dialog.py`:
  - Chart selection checkboxes
  - Export settings
  - Output folder picker

### Task 8.3.5: Implement context menu integration
- [ ] Add to chart context menus:
  - "Save as Image..." action
  - "Copy to Clipboard" action (if supported)

### Task 8.3.6: Create ImageExporter tests
- [ ] Create `tests/test_exports/test_image_exporter.py`

---

## Completion Checklist

### Story 8.1: PDF Export
- [ ] PDFReportConfig created
- [ ] PDFExporter class created
- [ ] Report export working
- [ ] Expense list export working
- [ ] Charts embedded
- [ ] Export dialog created
- [ ] Tests passing

### Story 8.2: Excel Export
- [ ] ExcelExportConfig created
- [ ] ExcelExporter class created
- [ ] Multi-sheet export working
- [ ] Charts in Excel working
- [ ] Currency formatting correct
- [ ] Export dialog created
- [ ] Tests passing

### Story 8.3: Image Export
- [ ] ImageExporter created
- [ ] All formats working (PNG, JPG, SVG, PDF)
- [ ] Resolution options working
- [ ] Batch export working
- [ ] Context menu integration done
- [ ] Tests passing

---

## Next Steps

After completing Epic 8, proceed to:
- **Epic 10: Main Application** - Integrates all components
