"""
BudgetView - Budget management view with CRUD and status tracking.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from models import Budget
from config import CATEGORIES
from utils.formatters import format_currency


class BudgetView(ttk.Frame):
    """
    Budget management view with status bars and CRUD operations.
    """

    def __init__(self, parent, main_window):
        """
        Initialize BudgetView.

        Args:
            parent: Parent widget
            main_window: Reference to MainWindow
        """
        super().__init__(parent)
        self.main_window = main_window
        self._create_widgets()
        self.refresh()

    def _create_widgets(self):
        """Create view widgets."""
        # Header with add button
        header = ttk.Frame(self)
        header.pack(fill=tk.X, pady=(0, PADDING['medium']))

        add_btn = ttk.Button(
            header,
            text="+ Add Budget",
            command=self._show_add_dialog,
            style='Primary.TButton'
        )
        add_btn.pack(side=tk.LEFT)

        refresh_btn = ttk.Button(
            header,
            text="Refresh",
            command=self.refresh
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Main content - split view
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True)

        # Left - Budget list
        left_frame = ttk.LabelFrame(content, text="Active Budgets")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['medium']))

        self._create_budget_list(left_frame)

        # Right - Budget details and status
        right_frame = ttk.Frame(content)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self._create_status_section(right_frame)
        self._create_alerts_section(right_frame)

    def _create_budget_list(self, parent):
        """Create budget list treeview."""
        columns = ('category', 'budget', 'spent', 'remaining', 'status')
        self.tree = ttk.Treeview(
            parent,
            columns=columns,
            show='headings',
            height=15
        )

        self.tree.heading('category', text='Category')
        self.tree.heading('budget', text='Budget')
        self.tree.heading('spent', text='Spent')
        self.tree.heading('remaining', text='Remaining')
        self.tree.heading('status', text='Status')

        self.tree.column('category', width=120)
        self.tree.column('budget', width=100, anchor='e')
        self.tree.column('spent', width=100, anchor='e')
        self.tree.column('remaining', width=100, anchor='e')
        self.tree.column('status', width=80, anchor='center')

        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bindings
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<<TreeviewSelect>>', self._on_select)

        # Context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Edit", command=self._edit_selected)
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
        self.tree.bind('<Button-3>', self._show_context_menu)

    def _create_status_section(self, parent):
        """Create budget status visualization."""
        status_frame = ttk.LabelFrame(parent, text="Budget Status")
        status_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        # Overall status
        self.overall_frame = tk.Frame(status_frame, bg=COLORS['card'])
        self.overall_frame.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

        # Status bars container
        self.bars_frame = ttk.Frame(status_frame)
        self.bars_frame.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

    def _create_alerts_section(self, parent):
        """Create budget alerts section."""
        alerts_frame = ttk.LabelFrame(parent, text="Budget Alerts")
        alerts_frame.pack(fill=tk.BOTH, expand=True)

        self.alerts_text = tk.Text(
            alerts_frame,
            height=10,
            font=FONTS['body'],
            wrap=tk.WORD,
            state='disabled'
        )
        self.alerts_text.pack(fill=tk.BOTH, expand=True, padx=PADDING['small'], pady=PADDING['small'])

        # Configure tags for coloring
        self.alerts_text.tag_configure('error', foreground=COLORS['danger'])
        self.alerts_text.tag_configure('warning', foreground=COLORS['warning'])
        self.alerts_text.tag_configure('info', foreground=COLORS['info'])

    def refresh(self):
        """Refresh budget data."""
        self._update_budget_list()
        self._update_status_bars()
        self._update_alerts()

    def _update_budget_list(self):
        """Update budget list treeview."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get budgets and update spent amounts
        budgets = self.main_window.budget_manager.get_active_budgets()
        expenses = self.main_window.expense_manager.get_all_expenses()
        self.main_window.budget_manager.update_all_budgets_spent(expenses)

        for budget in budgets:
            remaining = budget.get_remaining()
            pct = budget.get_used_percentage()

            if pct >= 100:
                status = "OVER"
            elif pct >= 80:
                status = "Warning"
            else:
                status = "OK"

            self.tree.insert('', 'end', iid=budget.budget_id, values=(
                budget.category,
                format_currency(budget.amount),
                format_currency(budget.spent),
                format_currency(remaining),
                status
            ))

    def _update_status_bars(self):
        """Update visual status bars."""
        # Clear existing
        for widget in self.overall_frame.winfo_children():
            widget.destroy()
        for widget in self.bars_frame.winfo_children():
            widget.destroy()

        budgets = self.main_window.budget_manager.get_active_budgets()

        if not budgets:
            tk.Label(
                self.overall_frame,
                text="No active budgets",
                font=FONTS['body'],
                fg=COLORS['text_muted'],
                bg=COLORS['card']
            ).pack(pady=PADDING['medium'])
            return

        # Overall summary
        total_budget = self.main_window.budget_manager.get_total_budgeted()
        total_spent = self.main_window.budget_manager.get_total_spent()
        overall_pct = (total_spent / total_budget * 100) if total_budget > 0 else 0

        tk.Label(
            self.overall_frame,
            text=f"Overall: {format_currency(total_spent)} / {format_currency(total_budget)} ({overall_pct:.1f}%)",
            font=FONTS['body_bold'],
            bg=COLORS['card']
        ).pack(pady=PADDING['small'])

        # Individual category bars
        for budget in budgets[:6]:  # Show top 6
            self._create_budget_bar(budget)

    def _create_budget_bar(self, budget):
        """Create a single budget progress bar."""
        bar_frame = tk.Frame(self.bars_frame, bg=COLORS['card'])
        bar_frame.pack(fill=tk.X, pady=2)

        # Label
        tk.Label(
            bar_frame,
            text=budget.category,
            font=FONTS['small'],
            bg=COLORS['card'],
            width=15,
            anchor='w'
        ).pack(side=tk.LEFT)

        # Progress bar container
        progress_container = tk.Frame(bar_frame, bg=COLORS['gray_light'], height=15, width=200)
        progress_container.pack(side=tk.LEFT, padx=5)
        progress_container.pack_propagate(False)

        # Progress bar
        pct = min(budget.get_used_percentage(), 100)
        if pct >= 100:
            color = COLORS['danger']
        elif pct >= 80:
            color = COLORS['warning']
        else:
            color = COLORS['success']

        progress = tk.Frame(progress_container, bg=color)
        progress.place(relwidth=pct/100, relheight=1)

        # Percentage label
        tk.Label(
            bar_frame,
            text=f"{pct:.0f}%",
            font=FONTS['small'],
            bg=COLORS['card'],
            width=6,
            anchor='e'
        ).pack(side=tk.LEFT)

    def _update_alerts(self):
        """Update alerts text."""
        self.alerts_text.config(state='normal')
        self.alerts_text.delete('1.0', tk.END)

        alerts = self.main_window.budget_manager.get_budget_alerts()

        if not alerts:
            self.alerts_text.insert('end', "No budget alerts. All budgets are within limits.", 'info')
        else:
            for alert in alerts:
                severity = alert.get('severity', 'info')
                message = alert.get('message', '')
                self.alerts_text.insert('end', f"• {message}\n", severity)

        self.alerts_text.config(state='disabled')

    def _show_add_dialog(self):
        """Show add budget dialog."""
        dialog = BudgetDialog(self, self.main_window, mode='add')

    def _on_double_click(self, event):
        """Handle double-click to edit."""
        self._edit_selected()

    def _on_select(self, event):
        """Handle selection change."""
        pass

    def _show_context_menu(self, event):
        """Show context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _edit_selected(self):
        """Edit selected budget."""
        selection = self.tree.selection()
        if selection:
            budget_id = selection[0]
            dialog = BudgetDialog(self, self.main_window, mode='edit', budget_id=budget_id)

    def _delete_selected(self):
        """Delete selected budget."""
        selection = self.tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Confirm Delete", "Delete this budget?"):
            budget_id = selection[0]
            self.main_window.budget_manager.delete_budget(budget_id)
            self.main_window.set_status("Budget deleted")
            self.refresh()


class BudgetDialog(tk.Toplevel):
    """Dialog for adding/editing budgets."""

    def __init__(self, parent, main_window, mode='add', budget_id=None):
        super().__init__(parent)
        self.main_window = main_window
        self.parent_view = parent
        self.mode = mode
        self.budget_id = budget_id

        self.title("Add Budget" if mode == 'add' else "Edit Budget")
        self.geometry("400x350")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        if mode == 'edit' and budget_id:
            self._load_budget()

        self.wait_window()

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=PADDING['large'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Category
        ttk.Label(main_frame, text="Category:").pack(anchor='w')
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=list(CATEGORIES.keys()),
            state='readonly' if self.mode == 'add' else 'disabled'
        )
        self.category_combo.pack(fill=tk.X, pady=(0, PADDING['medium']))

        # Amount
        ttk.Label(main_frame, text="Budget Amount:").pack(anchor='w')
        self.amount_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.amount_var).pack(fill=tk.X, pady=(0, PADDING['medium']))

        # Period
        ttk.Label(main_frame, text="Period:").pack(anchor='w')
        period_frame = ttk.Frame(main_frame)
        period_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        now = datetime.now()
        month_start = now.replace(day=1)

        self.start_var = tk.StringVar(value=month_start.strftime('%d/%m/%Y'))
        ttk.Label(period_frame, text="Start:").pack(side=tk.LEFT)
        ttk.Entry(period_frame, textvariable=self.start_var, width=12).pack(side=tk.LEFT, padx=5)

        # Calculate end of month
        if now.month == 12:
            month_end = now.replace(year=now.year+1, month=1, day=1)
        else:
            month_end = now.replace(month=now.month+1, day=1)
        from datetime import timedelta
        month_end = month_end - timedelta(days=1)

        self.end_var = tk.StringVar(value=month_end.strftime('%d/%m/%Y'))
        ttk.Label(period_frame, text="End:").pack(side=tk.LEFT, padx=(10, 0))
        ttk.Entry(period_frame, textvariable=self.end_var, width=12).pack(side=tk.LEFT, padx=5)

        # Notes
        ttk.Label(main_frame, text="Notes:").pack(anchor='w')
        self.notes_text = tk.Text(main_frame, height=3)
        self.notes_text.pack(fill=tk.X, pady=(0, PADDING['medium']))

        # Allow rollover
        self.rollover_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            main_frame,
            text="Allow rollover to next period",
            variable=self.rollover_var
        ).pack(anchor='w', pady=PADDING['small'])

        # Buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=PADDING['medium'])

        ttk.Button(btn_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT)
        ttk.Button(
            btn_frame,
            text="Save",
            command=self._save,
            style='Primary.TButton'
        ).pack(side=tk.RIGHT, padx=PADDING['small'])

    def _load_budget(self):
        """Load budget data for editing."""
        budget = self.main_window.budget_manager.get_budget(self.budget_id)
        if budget:
            self.category_var.set(budget.category)
            self.amount_var.set(str(budget.amount))
            self.start_var.set(budget.period_start.strftime('%d/%m/%Y'))
            self.end_var.set(budget.period_end.strftime('%d/%m/%Y'))
            if budget.notes:
                self.notes_text.insert('1.0', budget.notes)
            self.rollover_var.set(budget.rollover_enabled)

    def _save(self):
        """Save budget."""
        try:
            amount = float(self.amount_var.get().replace(',', ''))
            if amount <= 0:
                raise ValueError("Amount must be positive")

            start = datetime.strptime(self.start_var.get(), '%d/%m/%Y')
            end = datetime.strptime(self.end_var.get(), '%d/%m/%Y')

            if end <= start:
                raise ValueError("End date must be after start date")

            notes = self.notes_text.get('1.0', tk.END).strip()

            # Determine period_type from date range
            days_diff = (end - start).days
            if days_diff <= 35:
                period_type = 'monthly'
            elif days_diff <= 100:
                period_type = 'quarterly'
            else:
                period_type = 'yearly'

            if self.mode == 'add':
                budget = Budget(
                    category=self.category_var.get(),
                    amount=amount,
                    period_type=period_type,
                    period_start=start,
                    notes=notes,
                    rollover_enabled=self.rollover_var.get()
                )
                self.main_window.budget_manager.add_budget(budget)
                self.main_window.set_status("Budget added")
            else:
                self.main_window.budget_manager.update_budget(
                    self.budget_id,
                    {
                        'amount': amount,
                        'period_type': period_type,
                        'period_start': start,
                        'notes': notes,
                        'rollover_enabled': self.rollover_var.get()
                    }
                )
                self.main_window.set_status("Budget updated")

            self.parent_view.refresh()
            self.destroy()

        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", str(e))
