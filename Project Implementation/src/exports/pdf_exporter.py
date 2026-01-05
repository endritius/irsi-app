"""
PDFExporter - Generates PDF reports using ReportLab.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import APP_NAME, CURRENCY_SYMBOL, DATE_DISPLAY_FORMAT
from utils.formatters import format_currency, format_date


class PDFExporter:
    """
    Generates PDF reports using ReportLab.
    Supports expense lists, summaries, and analytics reports.
    """

    def __init__(self, pagesize=A4):
        """
        Initialize PDFExporter.

        Args:
            pagesize: Page size (default A4)
        """
        self.pagesize = pagesize
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Setup custom paragraph styles."""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#2c3e50')
        ))

        self.styles.add(ParagraphStyle(
            name='SectionTitle',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#34495e')
        ))

        self.styles.add(ParagraphStyle(
            name='TableHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.white,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        ))

        self.styles.add(ParagraphStyle(
            name='RightAlign',
            parent=self.styles['Normal'],
            alignment=TA_RIGHT
        ))

    def _create_header(self, title: str) -> List:
        """Create report header elements."""
        elements = []

        # Title
        elements.append(Paragraph(title, self.styles['CustomTitle']))

        # Date
        date_str = datetime.now().strftime('%d/%m/%Y %H:%M')
        elements.append(Paragraph(
            f"Generated: {date_str}",
            self.styles['Normal']
        ))
        elements.append(Spacer(1, 20))

        return elements

    def _create_footer(self, canvas, doc):
        """Add footer to page."""
        canvas.saveState()
        footer_text = f"{APP_NAME} - Page {doc.page}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(
            self.pagesize[0] / 2,
            0.5 * inch,
            footer_text
        )
        canvas.restoreState()

    def _create_table(
        self,
        data: List[List],
        col_widths: List[float] = None,
        header_bg: str = '#3498db'
    ) -> Table:
        """
        Create styled table.

        Args:
            data: Table data (first row is header)
            col_widths: Column widths
            header_bg: Header background color

        Returns:
            Styled Table object
        """
        table = Table(data, colWidths=col_widths)

        style = TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(header_bg)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            ('TOPPADDING', (0, 1), (-1, -1), 8),

            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),

            # Alternate row colors
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ])

        table.setStyle(style)
        return table

    # ===== EXPENSE LIST EXPORT =====

    def export_expense_list(
        self,
        expenses: List[Dict],
        filepath: str,
        title: str = "Expense List"
    ) -> bool:
        """
        Export list of expenses to PDF.

        Args:
            expenses: List of expense dictionaries
            filepath: Output file path
            title: Report title

        Returns:
            True on success
        """
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=self.pagesize,
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )

            elements = self._create_header(title)

            if not expenses:
                elements.append(Paragraph(
                    "No expenses found.",
                    self.styles['Normal']
                ))
            else:
                # Summary
                total = sum(e.get('amount', 0) for e in expenses)
                elements.append(Paragraph(
                    f"<b>Total:</b> {format_currency(total)} ({len(expenses)} expenses)",
                    self.styles['Normal']
                ))
                elements.append(Spacer(1, 15))

                # Table
                table_data = [['Date', 'Vendor', 'Category', 'Description', 'Amount']]

                for expense in expenses:
                    date_str = format_date(expense.get('date', ''))
                    table_data.append([
                        date_str,
                        expense.get('vendor', '')[:20],
                        expense.get('category', ''),
                        expense.get('description', '')[:30] or '-',
                        format_currency(expense.get('amount', 0))
                    ])

                col_widths = [1.5*cm, 3.5*cm, 3*cm, 5*cm, 2.5*cm]
                table = self._create_table(table_data, col_widths)
                elements.append(table)

            doc.build(elements, onFirstPage=self._create_footer,
                     onLaterPages=self._create_footer)
            return True

        except Exception as e:
            print(f"PDF export error: {e}")
            return False

    # ===== MONTHLY REPORT EXPORT =====

    def export_monthly_report(
        self,
        report_data: Dict,
        filepath: str
    ) -> bool:
        """
        Export monthly report to PDF.

        Args:
            report_data: Monthly report data dictionary
            filepath: Output file path

        Returns:
            True on success
        """
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=self.pagesize,
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )

            period = report_data.get('period', {})
            title = f"Monthly Report - {period.get('month', 'Unknown')}"
            elements = self._create_header(title)

            # Summary section
            elements.append(Paragraph("Summary", self.styles['SectionTitle']))
            summary = report_data.get('summary', {})

            summary_data = [
                ['Metric', 'Value'],
                ['Total Expenses', format_currency(summary.get('total_amount', 0))],
                ['Number of Transactions', str(summary.get('expense_count', 0))],
                ['Average Expense', format_currency(summary.get('average_amount', 0))],
                ['Highest Expense', format_currency(summary.get('max_amount', 0))],
                ['Lowest Expense', format_currency(summary.get('min_amount', 0))]
            ]

            table = self._create_table(summary_data, [6*cm, 5*cm])
            elements.append(table)
            elements.append(Spacer(1, 20))

            # Category breakdown
            elements.append(Paragraph("Expenses by Category", self.styles['SectionTitle']))
            categories = report_data.get('by_category', [])

            if categories:
                cat_data = [['Category', 'Amount', 'Count', '%']]
                for cat in categories:
                    cat_data.append([
                        cat.get('category', ''),
                        format_currency(cat.get('amount', 0)),
                        str(cat.get('count', 0)),
                        f"{cat.get('percentage', 0):.1f}%"
                    ])

                table = self._create_table(cat_data, [4*cm, 4*cm, 2*cm, 2*cm])
                elements.append(table)
            else:
                elements.append(Paragraph("No category data.", self.styles['Normal']))

            elements.append(Spacer(1, 20))

            # Top vendors
            elements.append(Paragraph("Top Vendors", self.styles['SectionTitle']))
            vendors = report_data.get('by_vendor', [])[:10]

            if vendors:
                vendor_data = [['Vendor', 'Amount', 'Transactions']]
                for v in vendors:
                    vendor_data.append([
                        v.get('vendor', '')[:25],
                        format_currency(v.get('amount', 0)),
                        str(v.get('count', 0))
                    ])

                table = self._create_table(vendor_data, [6*cm, 4*cm, 3*cm])
                elements.append(table)
            else:
                elements.append(Paragraph("No vendor data.", self.styles['Normal']))

            elements.append(Spacer(1, 20))

            # Budget status
            budget_status = report_data.get('budget_status', [])
            if budget_status:
                elements.append(Paragraph("Budget Status", self.styles['SectionTitle']))

                budget_data = [['Category', 'Budget', 'Spent', 'Remaining', 'Used %']]
                for b in budget_status:
                    remaining = b.get('variance', 0)
                    budget_data.append([
                        b.get('category', ''),
                        format_currency(b.get('budget', 0)),
                        format_currency(b.get('actual', 0)),
                        format_currency(remaining),
                        f"{b.get('used_percentage', 0):.1f}%"
                    ])

                table = self._create_table(budget_data, [3*cm, 3*cm, 3*cm, 3*cm, 2*cm])
                elements.append(table)

            doc.build(elements, onFirstPage=self._create_footer,
                     onLaterPages=self._create_footer)
            return True

        except Exception as e:
            print(f"PDF export error: {e}")
            return False

    # ===== ANNUAL REPORT EXPORT =====

    def export_annual_report(
        self,
        report_data: Dict,
        filepath: str
    ) -> bool:
        """
        Export annual report to PDF.

        Args:
            report_data: Annual report data dictionary
            filepath: Output file path

        Returns:
            True on success
        """
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=self.pagesize,
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )

            period = report_data.get('period', {})
            title = f"Annual Report - {period.get('year', 'Unknown')}"
            elements = self._create_header(title)

            # Executive Summary
            elements.append(Paragraph("Executive Summary", self.styles['SectionTitle']))
            summary = report_data.get('summary', {})

            summary_text = f"""
            <b>Total Expenses:</b> {format_currency(summary.get('total_amount', 0))}<br/>
            <b>Number of Transactions:</b> {summary.get('expense_count', 0)}<br/>
            <b>Average Expense:</b> {format_currency(summary.get('average_amount', 0))}<br/>
            <b>Estimated Monthly Recurring:</b> {format_currency(report_data.get('estimated_monthly_recurring', 0))}
            """
            elements.append(Paragraph(summary_text, self.styles['Normal']))
            elements.append(Spacer(1, 20))

            # Monthly trend
            elements.append(Paragraph("Monthly Trend", self.styles['SectionTitle']))
            monthly = report_data.get('monthly_trend', [])

            if monthly:
                monthly_data = [['Month', 'Amount', 'Transactions']]
                for m in monthly:
                    monthly_data.append([
                        m.get('month_name', m.get('month', '')),
                        format_currency(m.get('amount', 0)),
                        str(m.get('count', 0))
                    ])

                table = self._create_table(monthly_data, [5*cm, 4*cm, 3*cm])
                elements.append(table)

            elements.append(PageBreak())

            # Category breakdown
            elements.append(Paragraph("Expenses by Category", self.styles['SectionTitle']))
            categories = report_data.get('by_category', [])

            if categories:
                cat_data = [['Category', 'Amount', 'Count', '%']]
                for cat in categories:
                    cat_data.append([
                        cat.get('category', ''),
                        format_currency(cat.get('amount', 0)),
                        str(cat.get('count', 0)),
                        f"{cat.get('percentage', 0):.1f}%"
                    ])

                table = self._create_table(cat_data, [4*cm, 4*cm, 2*cm, 2*cm])
                elements.append(table)

            elements.append(Spacer(1, 20))

            # Subcategory breakdown
            elements.append(Paragraph("Expenses by Subcategory", self.styles['SectionTitle']))
            subcategories = report_data.get('by_subcategory', [])[:15]

            if subcategories:
                sub_data = [['Category', 'Subcategory', 'Amount']]
                for sub in subcategories:
                    sub_data.append([
                        sub.get('category', ''),
                        sub.get('subcategory', ''),
                        format_currency(sub.get('amount', 0))
                    ])

                table = self._create_table(sub_data, [4*cm, 4*cm, 4*cm])
                elements.append(table)

            elements.append(Spacer(1, 20))

            # Top 20 vendors
            elements.append(Paragraph("Top Vendors", self.styles['SectionTitle']))
            vendors = report_data.get('by_vendor', [])[:20]

            if vendors:
                vendor_data = [['Vendor', 'Amount', 'Count', '%']]
                for v in vendors:
                    vendor_data.append([
                        v.get('vendor', '')[:25],
                        format_currency(v.get('amount', 0)),
                        str(v.get('count', 0)),
                        f"{v.get('percentage', 0):.1f}%"
                    ])

                table = self._create_table(vendor_data, [5*cm, 3.5*cm, 2*cm, 2*cm])
                elements.append(table)

            doc.build(elements, onFirstPage=self._create_footer,
                     onLaterPages=self._create_footer)
            return True

        except Exception as e:
            print(f"PDF export error: {e}")
            return False

    # ===== BUDGET REPORT EXPORT =====

    def export_budget_report(
        self,
        budget_data: List[Dict],
        filepath: str,
        title: str = "Budget Report"
    ) -> bool:
        """
        Export budget status report to PDF.

        Args:
            budget_data: List of budget status dictionaries
            filepath: Output file path
            title: Report title

        Returns:
            True on success
        """
        try:
            doc = SimpleDocTemplate(
                filepath,
                pagesize=self.pagesize,
                rightMargin=1*cm,
                leftMargin=1*cm,
                topMargin=1.5*cm,
                bottomMargin=1.5*cm
            )

            elements = self._create_header(title)

            if not budget_data:
                elements.append(Paragraph(
                    "No budget data available.",
                    self.styles['Normal']
                ))
            else:
                # Overall summary
                total_budget = sum(b.get('budget', b.get('amount', 0)) for b in budget_data)
                total_spent = sum(b.get('actual', b.get('spent', 0)) for b in budget_data)
                overall_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0

                summary_text = f"""
                <b>Total Budgeted:</b> {format_currency(total_budget)}<br/>
                <b>Total Spent:</b> {format_currency(total_spent)}<br/>
                <b>Overall Usage:</b> {overall_pct:.1f}%
                """
                elements.append(Paragraph(summary_text, self.styles['Normal']))
                elements.append(Spacer(1, 20))

                # Detailed table
                table_data = [['Category', 'Budget', 'Spent', 'Remaining', 'Used %', 'Status']]

                for b in budget_data:
                    budget_amt = b.get('budget', b.get('amount', 0))
                    spent = b.get('actual', b.get('spent', 0))
                    remaining = budget_amt - spent
                    pct = b.get('used_percentage', (spent / budget_amt * 100) if budget_amt > 0 else 0)

                    if pct >= 100:
                        status = 'OVER'
                    elif pct >= 80:
                        status = 'Warning'
                    else:
                        status = 'OK'

                    table_data.append([
                        b.get('category', ''),
                        format_currency(budget_amt),
                        format_currency(spent),
                        format_currency(remaining),
                        f"{pct:.1f}%",
                        status
                    ])

                col_widths = [3*cm, 2.5*cm, 2.5*cm, 2.5*cm, 1.8*cm, 1.5*cm]
                table = self._create_table(table_data, col_widths)
                elements.append(table)

            doc.build(elements, onFirstPage=self._create_footer,
                     onLaterPages=self._create_footer)
            return True

        except Exception as e:
            print(f"PDF export error: {e}")
            return False

    def export_to_bytes(
        self,
        expenses: List[Dict],
        title: str = "Expense Report"
    ) -> bytes:
        """
        Export to PDF bytes (for streaming/download).

        Args:
            expenses: List of expense dictionaries
            title: Report title

        Returns:
            PDF as bytes
        """
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.pagesize,
            rightMargin=1*cm,
            leftMargin=1*cm,
            topMargin=1.5*cm,
            bottomMargin=1.5*cm
        )

        elements = self._create_header(title)

        if expenses:
            total = sum(e.get('amount', 0) for e in expenses)
            elements.append(Paragraph(
                f"<b>Total:</b> {format_currency(total)} ({len(expenses)} expenses)",
                self.styles['Normal']
            ))
            elements.append(Spacer(1, 15))

            table_data = [['Date', 'Vendor', 'Category', 'Amount']]
            for expense in expenses:
                table_data.append([
                    format_date(expense.get('date', '')),
                    expense.get('vendor', '')[:20],
                    expense.get('category', ''),
                    format_currency(expense.get('amount', 0))
                ])

            table = self._create_table(table_data, [2.5*cm, 4*cm, 4*cm, 3*cm])
            elements.append(table)

        doc.build(elements)
        return buffer.getvalue()


# Singleton instance
_pdf_exporter: Optional[PDFExporter] = None


def get_pdf_exporter() -> PDFExporter:
    """Get or create global PDFExporter instance."""
    global _pdf_exporter
    if _pdf_exporter is None:
        _pdf_exporter = PDFExporter()
    return _pdf_exporter
