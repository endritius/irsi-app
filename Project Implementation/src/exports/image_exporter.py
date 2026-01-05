"""
ImageExporter - Exports charts and visualizations to image files.
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from io import BytesIO

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from PIL import Image

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from visualization.visualizer import Visualizer, get_visualizer


class ImageExporter:
    """
    Exports charts and visualizations to image formats.
    Supports PNG, JPG, SVG, and PDF formats.
    """

    def __init__(self, visualizer: Visualizer = None):
        """
        Initialize ImageExporter.

        Args:
            visualizer: Visualizer instance (uses global if None)
        """
        self.visualizer = visualizer or get_visualizer()
        self.default_dpi = 150
        self.default_format = 'png'

    def export_figure(
        self,
        fig: Figure,
        filepath: str,
        dpi: int = None,
        format: str = None,
        transparent: bool = False
    ) -> bool:
        """
        Export matplotlib figure to file.

        Args:
            fig: Matplotlib Figure
            filepath: Output file path
            dpi: Resolution (default 150)
            format: Output format (auto-detect if None)
            transparent: If True, transparent background

        Returns:
            True on success
        """
        try:
            dpi = dpi or self.default_dpi
            fig.savefig(
                filepath,
                dpi=dpi,
                format=format,
                bbox_inches='tight',
                facecolor='white' if not transparent else 'none',
                edgecolor='none',
                transparent=transparent
            )
            return True
        except Exception as e:
            print(f"Image export error: {e}")
            return False

    def figure_to_bytes(
        self,
        fig: Figure,
        format: str = 'png',
        dpi: int = None,
        transparent: bool = False
    ) -> bytes:
        """
        Convert figure to bytes.

        Args:
            fig: Matplotlib Figure
            format: Output format
            dpi: Resolution
            transparent: Transparent background

        Returns:
            Image bytes
        """
        dpi = dpi or self.default_dpi
        buf = BytesIO()
        fig.savefig(
            buf,
            format=format,
            dpi=dpi,
            bbox_inches='tight',
            facecolor='white' if not transparent else 'none',
            transparent=transparent
        )
        buf.seek(0)
        return buf.getvalue()

    # ===== CATEGORY CHARTS =====

    def export_category_pie_chart(
        self,
        category_data: List[Dict],
        filepath: str,
        title: str = "Expenses by Category",
        figsize: Tuple[int, int] = (8, 8),
        dpi: int = None
    ) -> bool:
        """
        Export category pie chart to file.

        Args:
            category_data: List of dicts with 'category' and 'amount'
            filepath: Output file path
            title: Chart title
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_category_pie_chart(
            category_data, figsize=figsize, title=title
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    def export_category_bar_chart(
        self,
        category_data: List[Dict],
        filepath: str,
        title: str = "Expenses by Category",
        horizontal: bool = True,
        figsize: Tuple[int, int] = (10, 6),
        dpi: int = None
    ) -> bool:
        """
        Export category bar chart to file.

        Args:
            category_data: List of dicts with 'category' and 'amount'
            filepath: Output file path
            title: Chart title
            horizontal: Horizontal bars if True
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_category_bar_chart(
            category_data, figsize=figsize, title=title, horizontal=horizontal
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    # ===== TREND CHARTS =====

    def export_monthly_trend_chart(
        self,
        monthly_data: List[Dict],
        filepath: str,
        title: str = "Monthly Expense Trend",
        figsize: Tuple[int, int] = (12, 6),
        dpi: int = None
    ) -> bool:
        """
        Export monthly trend line chart to file.

        Args:
            monthly_data: List of dicts with 'month' and 'amount'
            filepath: Output file path
            title: Chart title
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_monthly_trend_chart(
            monthly_data, figsize=figsize, title=title
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    def export_daily_trend_chart(
        self,
        daily_data: List[Dict],
        filepath: str,
        title: str = "Daily Expense Trend",
        figsize: Tuple[int, int] = (12, 6),
        dpi: int = None
    ) -> bool:
        """
        Export daily trend line chart to file.

        Args:
            daily_data: List of dicts with 'date' and 'amount'
            filepath: Output file path
            title: Chart title
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_daily_trend_chart(
            daily_data, figsize=figsize, title=title
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    # ===== BUDGET CHARTS =====

    def export_budget_comparison_chart(
        self,
        budget_data: List[Dict],
        filepath: str,
        title: str = "Budget vs Actual",
        figsize: Tuple[int, int] = (12, 6),
        dpi: int = None
    ) -> bool:
        """
        Export budget comparison bar chart to file.

        Args:
            budget_data: List of dicts with 'category', 'budget', 'actual'
            filepath: Output file path
            title: Chart title
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_budget_comparison_chart(
            budget_data, figsize=figsize, title=title
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    # ===== VENDOR CHARTS =====

    def export_vendor_bar_chart(
        self,
        vendor_data: List[Dict],
        filepath: str,
        title: str = "Top Vendors by Spending",
        figsize: Tuple[int, int] = (10, 6),
        dpi: int = None
    ) -> bool:
        """
        Export top vendors bar chart to file.

        Args:
            vendor_data: List of dicts with 'vendor' and 'amount'
            filepath: Output file path
            title: Chart title
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_vendor_bar_chart(
            vendor_data, figsize=figsize, title=title
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    # ===== DASHBOARD EXPORT =====

    def export_dashboard_summary(
        self,
        summary_data: Dict,
        filepath: str,
        figsize: Tuple[int, int] = (14, 10),
        dpi: int = None
    ) -> bool:
        """
        Export full dashboard summary to file.

        Args:
            summary_data: Dictionary with category_breakdown, monthly_trend,
                         budget_status, top_vendors
            filepath: Output file path
            figsize: Figure size
            dpi: Resolution

        Returns:
            True on success
        """
        fig = self.visualizer.create_dashboard_summary(
            summary_data, figsize=figsize
        )
        success = self.export_figure(fig, filepath, dpi=dpi)
        self.visualizer.close_figure(fig)
        return success

    # ===== BATCH EXPORT =====

    def export_all_charts(
        self,
        report_data: Dict,
        output_dir: str,
        prefix: str = "",
        format: str = 'png',
        dpi: int = None
    ) -> Dict[str, bool]:
        """
        Export all available charts from report data.

        Args:
            report_data: Report data dictionary
            output_dir: Output directory
            prefix: Filename prefix
            format: Output format
            dpi: Resolution

        Returns:
            Dictionary mapping filenames to success status
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        results = {}

        # Category pie chart
        if report_data.get('by_category'):
            filename = f"{prefix}category_pie.{format}"
            filepath = output_path / filename
            results[filename] = self.export_category_pie_chart(
                report_data['by_category'],
                str(filepath),
                dpi=dpi
            )

        # Category bar chart
        if report_data.get('by_category'):
            filename = f"{prefix}category_bar.{format}"
            filepath = output_path / filename
            results[filename] = self.export_category_bar_chart(
                report_data['by_category'],
                str(filepath),
                dpi=dpi
            )

        # Monthly trend
        if report_data.get('monthly_trend'):
            filename = f"{prefix}monthly_trend.{format}"
            filepath = output_path / filename
            results[filename] = self.export_monthly_trend_chart(
                report_data['monthly_trend'],
                str(filepath),
                dpi=dpi
            )

        # Daily trend
        if report_data.get('by_day'):
            filename = f"{prefix}daily_trend.{format}"
            filepath = output_path / filename
            results[filename] = self.export_daily_trend_chart(
                report_data['by_day'],
                str(filepath),
                dpi=dpi
            )

        # Budget comparison
        if report_data.get('budget_status'):
            filename = f"{prefix}budget_comparison.{format}"
            filepath = output_path / filename
            results[filename] = self.export_budget_comparison_chart(
                report_data['budget_status'],
                str(filepath),
                dpi=dpi
            )

        # Top vendors
        if report_data.get('by_vendor'):
            filename = f"{prefix}top_vendors.{format}"
            filepath = output_path / filename
            results[filename] = self.export_vendor_bar_chart(
                report_data['by_vendor'][:10],
                str(filepath),
                dpi=dpi
            )

        # Dashboard summary
        summary_data = {
            'category_breakdown': report_data.get('by_category', []),
            'monthly_trend': report_data.get('monthly_trend', []),
            'budget_status': report_data.get('budget_status', []),
            'top_vendors': report_data.get('by_vendor', [])[:5]
        }

        if any(summary_data.values()):
            filename = f"{prefix}dashboard.{format}"
            filepath = output_path / filename
            results[filename] = self.export_dashboard_summary(
                summary_data,
                str(filepath),
                dpi=dpi
            )

        return results

    # ===== UTILITIES =====

    def convert_format(
        self,
        input_path: str,
        output_path: str,
        output_format: str = None
    ) -> bool:
        """
        Convert image to different format.

        Args:
            input_path: Source file path
            output_path: Destination file path
            output_format: Target format (auto-detect if None)

        Returns:
            True on success
        """
        try:
            img = Image.open(input_path)

            # Convert RGBA to RGB for JPEG
            if output_format and output_format.lower() in ('jpg', 'jpeg'):
                if img.mode == 'RGBA':
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    background.paste(img, mask=img.split()[3])
                    img = background

            img.save(output_path, format=output_format)
            return True
        except Exception as e:
            print(f"Image conversion error: {e}")
            return False

    def resize_image(
        self,
        input_path: str,
        output_path: str,
        width: int = None,
        height: int = None,
        maintain_aspect: bool = True
    ) -> bool:
        """
        Resize an image.

        Args:
            input_path: Source file path
            output_path: Destination file path
            width: Target width
            height: Target height
            maintain_aspect: Maintain aspect ratio

        Returns:
            True on success
        """
        try:
            img = Image.open(input_path)

            if maintain_aspect:
                if width and height:
                    img.thumbnail((width, height), Image.Resampling.LANCZOS)
                elif width:
                    ratio = width / img.width
                    height = int(img.height * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
                elif height:
                    ratio = height / img.height
                    width = int(img.width * ratio)
                    img = img.resize((width, height), Image.Resampling.LANCZOS)
            else:
                if width and height:
                    img = img.resize((width, height), Image.Resampling.LANCZOS)

            img.save(output_path)
            return True
        except Exception as e:
            print(f"Image resize error: {e}")
            return False

    def create_thumbnail(
        self,
        input_path: str,
        output_path: str,
        size: Tuple[int, int] = (200, 200)
    ) -> bool:
        """
        Create thumbnail from image.

        Args:
            input_path: Source file path
            output_path: Destination file path
            size: Thumbnail size tuple

        Returns:
            True on success
        """
        try:
            img = Image.open(input_path)
            img.thumbnail(size, Image.Resampling.LANCZOS)
            img.save(output_path)
            return True
        except Exception as e:
            print(f"Thumbnail creation error: {e}")
            return False


# Singleton instance
_image_exporter: Optional[ImageExporter] = None


def get_image_exporter() -> ImageExporter:
    """Get or create global ImageExporter instance."""
    global _image_exporter
    if _image_exporter is None:
        _image_exporter = ImageExporter()
    return _image_exporter
