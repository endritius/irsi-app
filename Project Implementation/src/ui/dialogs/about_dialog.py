"""
AboutDialog - Application information dialog.
"""

import tkinter as tk
from tkinter import ttk
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from config import APP_NAME, APP_VERSION
from ui.styles import COLORS, FONTS, PADDING


class AboutDialog(tk.Toplevel):
    """
    About dialog showing application information.
    """

    def __init__(self, parent):
        """
        Initialize AboutDialog.

        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.title("About")
        self.geometry("400x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        # Center on parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - self.winfo_width()) // 2
        y = parent.winfo_y() + (parent.winfo_height() - self.winfo_height()) // 2
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=PADDING['large'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # App name
        title_label = ttk.Label(
            main_frame,
            text=APP_NAME,
            font=('Segoe UI', 18, 'bold'),
            foreground=COLORS['primary']
        )
        title_label.pack(pady=(PADDING['large'], PADDING['small']))

        # Version
        version_label = ttk.Label(
            main_frame,
            text=f"Version {APP_VERSION}",
            font=FONTS['body']
        )
        version_label.pack()

        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(
            fill=tk.X,
            pady=PADDING['medium']
        )

        # Description
        desc_text = """A comprehensive expense management solution designed
specifically for beauty salons and similar businesses.

Features:
- Track expenses across salon-specific categories
- Set and monitor budgets with alerts
- Generate detailed reports and visualizations
- Export data to PDF, Excel, and CSV
- Backup and restore functionality"""

        desc_label = ttk.Label(
            main_frame,
            text=desc_text,
            font=FONTS['body'],
            justify='left',
            wraplength=350
        )
        desc_label.pack(pady=PADDING['small'])

        # Separator
        ttk.Separator(main_frame, orient='horizontal').pack(
            fill=tk.X,
            pady=PADDING['medium']
        )

        # Credits
        credits_label = ttk.Label(
            main_frame,
            text="IRSI Project",
            font=FONTS['small'],
            foreground=COLORS['text_muted']
        )
        credits_label.pack()

        # Copyright
        copyright_label = ttk.Label(
            main_frame,
            text="2024 - All Rights Reserved",
            font=FONTS['small'],
            foreground=COLORS['text_muted']
        )
        copyright_label.pack()

        # Close button
        close_btn = ttk.Button(
            main_frame,
            text="Close",
            command=self.destroy,
            style='Primary.TButton'
        )
        close_btn.pack(pady=PADDING['large'])

        # Focus close button
        close_btn.focus()

        # Bind escape to close
        self.bind('<Escape>', lambda e: self.destroy())
