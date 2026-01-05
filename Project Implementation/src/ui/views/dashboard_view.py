"""
DashboardView - Main dashboard with summary cards and recent activity.
"""

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from utils.formatters import format_currency, format_date
from config import CURRENCY_SYMBOL


class DashboardView(ttk.Frame):
    """
    Dashboard view with summary cards, charts, and recent expenses.
    """

    def __init__(self, parent, main_window):
        """
        Initialize DashboardView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """Create dashboard widgets."""
        # Summary cards row
        self.cards_frame = ttk.Frame(self)
        self.cards_frame.pack(fill=tk.X, pady=(0, PADDING['large']))

        # Create summary cards
        self._create_summary_cards()

        # Main content area - split into two columns
        self.content_frame = ttk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True)

        # Left column - Recent expenses
        self.left_column = ttk.Frame(self.content_frame)
        self.left_column.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['medium']))

        self._create_recent_expenses()

        # Right column - Budget status and quick actions
        self.right_column = ttk.Frame(self.content_frame)
        self.right_column.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_budget_status()
        self._create_quick_actions()

    def _create_summary_cards(self):
        """Create summary stat cards."""
        cards_data = [
            ("Total This Month", "month_total", COLORS['primary']),
            ("Today's Expenses", "today_total", COLORS['secondary']),
            ("Average Expense", "average", COLORS['info']),
            ("Expenses Count", "count", COLORS['warning'])
        ]

        self.card_values = {}

        for i, (title, key, color) in enumerate(cards_data):
            card = self._create_card(self.cards_frame, title, "0", color)
            card.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0 if i == 0 else PADDING['small'], 0))
            self.card_values[key] = card

    def _create_card(self, parent, title, value, color):
        """Create a summary card widget."""
        card = tk.Frame(parent, bg=COLORS['card'], relief='flat', bd=1)
        card.config(highlightbackground=COLORS['border'], highlightthickness=1)

        # Top colored bar
        top_bar = tk.Frame(card, bg=color, height=4)
        top_bar.pack(fill=tk.X)

        # Content
        content = tk.Frame(card, bg=COLORS['card'], padx=15, pady=15)
        content.pack(fill=tk.BOTH, expand=True)

        title_label = tk.Label(
            content,
            text=title,
            font=FONTS['small'],
            fg=COLORS['text_muted'],
            bg=COLORS['card']
        )
        title_label.pack(anchor='w')

        value_label = tk.Label(
            content,
            text=value,
            font=FONTS['large_number'],
            fg=color,
            bg=COLORS['card']
        )
        value_label.pack(anchor='w')

        card.value_label = value_label
        return card

    def _create_recent_expenses(self):
        """Create recent expenses section."""
        # Section header
        header_frame = ttk.Frame(self.left_column)
        header_frame.pack(fill=tk.X, pady=(0, PADDING['small']))

        ttk.Label(
            header_frame,
            text="Recent Expenses",
            style='Subheading.TLabel'
        ).pack(side=tk.LEFT)

        view_all_btn = ttk.Button(
            header_frame,
            text="View All",
            command=self.main_window._show_expenses,
            style='Outline.TButton'
        )
        view_all_btn.pack(side=tk.RIGHT)

        # Expenses list
        list_frame = ttk.Frame(self.left_column)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Treeview for expenses
        columns = ('date', 'vendor', 'category', 'amount')
        self.expenses_tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=10
        )

        self.expenses_tree.heading('date', text='Date')
        self.expenses_tree.heading('vendor', text='Vendor')
        self.expenses_tree.heading('category', text='Category')
        self.expenses_tree.heading('amount', text='Amount')

        self.expenses_tree.column('date', width=80)
        self.expenses_tree.column('vendor', width=150)
        self.expenses_tree.column('category', width=100)
        self.expenses_tree.column('amount', width=100, anchor='e')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.expenses_tree.yview)
        self.expenses_tree.configure(yscrollcommand=scrollbar.set)

        self.expenses_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Double-click to edit
        self.expenses_tree.bind('<Double-1>', self._on_expense_double_click)

    def _create_budget_status(self):
        """Create budget status section."""
        # Section header
        header_frame = ttk.Frame(self.right_column)
        header_frame.pack(fill=tk.X, pady=(0, PADDING['small']))

        ttk.Label(
            header_frame,
            text="Budget Status",
            style='Subheading.TLabel'
        ).pack(side=tk.LEFT)

        # Budget bars container
        self.budget_frame = ttk.LabelFrame(self.right_column, text="")
        self.budget_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        self.budget_bars = []

    def _create_quick_actions(self):
        """Create quick actions section."""
        actions_frame = ttk.LabelFrame(self.right_column, text="Quick Actions")
        actions_frame.pack(fill=tk.X, pady=PADDING['small'])

        actions = [
            ("Add Expense", self.main_window._show_add_expense, 'primary'),
            ("View Reports", self.main_window._show_reports, 'secondary'),
            ("Manage Budgets", self.main_window._show_budgets, 'outline')
        ]

        for text, command, style in actions:
            btn = ttk.Button(
                actions_frame,
                text=text,
                command=command,
                style=f'{style.capitalize()}.TButton' if style != 'outline' else 'TButton'
            )
            btn.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

    def refresh(self):
        """Refresh dashboard data."""
        self._update_summary_cards()
        self._update_recent_expenses()
        self._update_budget_status()

    def _update_summary_cards(self):
        """Update summary card values."""
        expenses = self.main_window.expense_manager.get_all_expenses()

        # This month total
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_expenses = [e for e in expenses if e.date >= month_start]
        month_total = sum(e.amount for e in month_expenses)
        self.card_values['month_total'].value_label.config(
            text=format_currency(month_total)
        )

        # Today's total
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_expenses = [e for e in expenses if e.date >= today_start]
        today_total = sum(e.amount for e in today_expenses)
        self.card_values['today_total'].value_label.config(
            text=format_currency(today_total)
        )

        # Average
        if expenses:
            avg = sum(e.amount for e in expenses) / len(expenses)
        else:
            avg = 0
        self.card_values['average'].value_label.config(
            text=format_currency(avg)
        )

        # Count
        self.card_values['count'].value_label.config(
            text=str(len(expenses))
        )

    def _update_recent_expenses(self):
        """Update recent expenses list."""
        # Clear current items
        for item in self.expenses_tree.get_children():
            self.expenses_tree.delete(item)

        # Get recent expenses
        expenses = self.main_window.expense_manager.get_all_expenses()
        expenses.sort(key=lambda e: e.date, reverse=True)

        for expense in expenses[:10]:
            self.expenses_tree.insert('', 'end', iid=expense.expense_id, values=(
                expense.date.strftime('%d/%m/%Y'),
                expense.vendor,
                expense.category,
                format_currency(expense.amount)
            ))

    def _update_budget_status(self):
        """Update budget status bars."""
        # Clear existing
        for widget in self.budget_frame.winfo_children():
            widget.destroy()

        budgets = self.main_window.budget_manager.get_active_budgets()
        expenses = self.main_window.expense_manager.get_all_expenses()

        if not budgets:
            ttk.Label(
                self.budget_frame,
                text="No active budgets",
                style='Muted.TLabel'
            ).pack(pady=PADDING['medium'])
            return

        # Update spent amounts
        self.main_window.budget_manager.update_all_budgets_spent(expenses)

        for budget in budgets[:5]:  # Show top 5
            self._create_budget_bar(budget)

    def _create_budget_bar(self, budget):
        """Create a budget progress bar."""
        bar_frame = tk.Frame(self.budget_frame, bg=COLORS['card'])
        bar_frame.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

        # Category label
        tk.Label(
            bar_frame,
            text=budget.category,
            font=FONTS['small_bold'],
            bg=COLORS['card'],
            fg=COLORS['text']
        ).pack(anchor='w')

        # Progress bar container
        progress_container = tk.Frame(bar_frame, bg=COLORS['gray_light'], height=15)
        progress_container.pack(fill=tk.X, pady=2)
        progress_container.pack_propagate(False)

        # Progress bar
        percentage = min(budget.get_used_percentage(), 100)
        if percentage >= 100:
            color = COLORS['danger']
        elif percentage >= 80:
            color = COLORS['warning']
        else:
            color = COLORS['success']

        progress = tk.Frame(progress_container, bg=color)
        progress.place(relwidth=percentage/100, relheight=1)

        # Stats label
        stats = f"{format_currency(budget.spent)} / {format_currency(budget.amount)} ({percentage:.0f}%)"
        tk.Label(
            bar_frame,
            text=stats,
            font=FONTS['small'],
            bg=COLORS['card'],
            fg=COLORS['text_muted']
        ).pack(anchor='e')

    def _on_expense_double_click(self, event):
        """Handle double-click on expense row."""
        selection = self.expenses_tree.selection()
        if selection:
            expense_id = selection[0]
            self.main_window._show_edit_expense(expense_id)
