"""
TemplatesView - Expense templates management.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ui.styles import COLORS, FONTS, PADDING
from models import ExpenseTemplate
from config import CATEGORIES, PAYMENT_METHODS, get_subcategories
from utils.formatters import format_currency


class TemplatesView(ttk.Frame):
    """
    Templates view for managing expense templates.
    """

    def __init__(self, parent, main_window):
        """
        Initialize TemplatesView.

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
        # Action bar
        action_frame = ttk.Frame(self)
        action_frame.pack(fill=tk.X, pady=(0, PADDING['medium']))

        add_btn = ttk.Button(
            action_frame,
            text="+ Add Template",
            command=self._show_add_dialog,
            style='Primary.TButton'
        )
        add_btn.pack(side=tk.LEFT)

        refresh_btn = ttk.Button(
            action_frame,
            text="Refresh",
            command=self.refresh
        )
        refresh_btn.pack(side=tk.RIGHT)

        # Main content
        content = ttk.Frame(self)
        content.pack(fill=tk.BOTH, expand=True)

        # Templates list
        self._create_template_list(content)

        # Details panel
        self._create_details_panel(content)

    def _create_template_list(self, parent):
        """Create template list."""
        list_frame = ttk.LabelFrame(parent, text="Templates")
        list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, PADDING['medium']))

        columns = ('name', 'category', 'vendor', 'amount', 'uses')
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show='headings',
            height=15
        )

        self.tree.heading('name', text='Name')
        self.tree.heading('category', text='Category')
        self.tree.heading('vendor', text='Vendor')
        self.tree.heading('amount', text='Typical Amount')
        self.tree.heading('uses', text='Uses')

        self.tree.column('name', width=150)
        self.tree.column('category', width=100)
        self.tree.column('vendor', width=120)
        self.tree.column('amount', width=100, anchor='e')
        self.tree.column('uses', width=60, anchor='center')

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bindings
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        self.tree.bind('<Double-1>', self._use_template)

        # Context menu
        self.context_menu = tk.Menu(self.tree, tearoff=0)
        self.context_menu.add_command(label="Use Template", command=self._use_template)
        self.context_menu.add_command(label="Edit", command=self._edit_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete", command=self._delete_selected)
        self.tree.bind('<Button-3>', self._show_context_menu)

    def _create_details_panel(self, parent):
        """Create template details panel."""
        details_frame = ttk.LabelFrame(parent, text="Template Details")
        details_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 0))

        self.details_content = ttk.Frame(details_frame, width=250)
        self.details_content.pack(fill=tk.BOTH, expand=True, padx=PADDING['medium'], pady=PADDING['medium'])
        self.details_content.pack_propagate(False)

        # Placeholder
        self.details_placeholder = ttk.Label(
            self.details_content,
            text="Select a template to view details",
            style='Muted.TLabel'
        )
        self.details_placeholder.pack(expand=True)

        # Action buttons
        btn_frame = ttk.Frame(details_frame)
        btn_frame.pack(fill=tk.X, padx=PADDING['small'], pady=PADDING['small'])

        self.use_btn = ttk.Button(
            btn_frame,
            text="Use Template",
            command=self._use_template,
            state='disabled',
            style='Primary.TButton'
        )
        self.use_btn.pack(fill=tk.X, pady=2)

        self.edit_btn = ttk.Button(
            btn_frame,
            text="Edit",
            command=self._edit_selected,
            state='disabled'
        )
        self.edit_btn.pack(fill=tk.X, pady=2)

        self.delete_btn = ttk.Button(
            btn_frame,
            text="Delete",
            command=self._delete_selected,
            state='disabled'
        )
        self.delete_btn.pack(fill=tk.X, pady=2)

    def refresh(self):
        """Refresh template list."""
        # Clear existing
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Get templates
        templates = self.main_window.template_manager.get_all_templates()

        for template in templates:
            self.tree.insert('', 'end', iid=template.template_id, values=(
                template.name,
                template.category,
                template.vendor,
                format_currency(template.typical_amount) if template.typical_amount else '-',
                template.use_count
            ))

    def _on_select(self, event):
        """Handle template selection."""
        selection = self.tree.selection()

        if selection:
            self._show_details(selection[0])
            self.use_btn.config(state='normal')
            self.edit_btn.config(state='normal')
            self.delete_btn.config(state='normal')
        else:
            self._clear_details()
            self.use_btn.config(state='disabled')
            self.edit_btn.config(state='disabled')
            self.delete_btn.config(state='disabled')

    def _show_details(self, template_id):
        """Show template details."""
        template = self.main_window.template_manager.get_template(template_id)
        if not template:
            return

        # Clear previous
        for widget in self.details_content.winfo_children():
            widget.destroy()

        # Template details
        details = [
            ("Name", template.name),
            ("Category", template.category),
            ("Subcategory", template.subcategory or '-'),
            ("Vendor", template.vendor),
            ("Typical Amount", format_currency(template.typical_amount) if template.typical_amount else '-'),
            ("Payment Method", template.payment_method),
            ("Description", template.description or '-'),
            ("Tags", ', '.join(template.tags) if template.tags else '-'),
            ("Times Used", str(template.use_count)),
            ("Last Used", template.last_used.strftime('%d/%m/%Y') if template.last_used else 'Never')
        ]

        for label, value in details:
            frame = ttk.Frame(self.details_content)
            frame.pack(fill=tk.X, pady=2)

            ttk.Label(
                frame,
                text=f"{label}:",
                style='Card.TLabel',
                font=FONTS['small_bold']
            ).pack(anchor='w')

            ttk.Label(
                frame,
                text=value,
                style='Card.TLabel',
                wraplength=200
            ).pack(anchor='w')

    def _clear_details(self):
        """Clear details panel."""
        for widget in self.details_content.winfo_children():
            widget.destroy()

        self.details_placeholder = ttk.Label(
            self.details_content,
            text="Select a template to view details",
            style='Muted.TLabel'
        )
        self.details_placeholder.pack(expand=True)

    def _show_context_menu(self, event):
        """Show context menu."""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _show_add_dialog(self):
        """Show add template dialog."""
        dialog = TemplateDialog(self, self.main_window, mode='add')

    def _edit_selected(self):
        """Edit selected template."""
        selection = self.tree.selection()
        if selection:
            dialog = TemplateDialog(self, self.main_window, mode='edit', template_id=selection[0])

    def _delete_selected(self):
        """Delete selected template."""
        selection = self.tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Confirm Delete", "Delete this template?"):
            template_id = selection[0]
            self.main_window.template_manager.delete_template(template_id)
            self.main_window.set_status("Template deleted")
            self.refresh()
            self._clear_details()

    def _use_template(self, event=None):
        """Use selected template to create expense."""
        selection = self.tree.selection()
        if not selection:
            return

        template_id = selection[0]
        template = self.main_window.template_manager.get_template(template_id)

        if template:
            # Navigate to expense form with template pre-filled
            self.main_window._show_add_expense()

            # Apply template to form
            if hasattr(self.main_window, 'current_view'):
                self.main_window.current_view._apply_template(template)


class TemplateDialog(tk.Toplevel):
    """Dialog for adding/editing templates."""

    def __init__(self, parent, main_window, mode='add', template_id=None):
        super().__init__(parent)
        self.main_window = main_window
        self.parent_view = parent
        self.mode = mode
        self.template_id = template_id

        self.title("Add Template" if mode == 'add' else "Edit Template")
        self.geometry("450x500")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self._create_widgets()

        if mode == 'edit' and template_id:
            self._load_template()

        self.wait_window()

    def _create_widgets(self):
        """Create dialog widgets."""
        main_frame = ttk.Frame(self, padding=PADDING['large'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Name
        ttk.Label(main_frame, text="Template Name *:").pack(anchor='w')
        self.name_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.name_var).pack(fill=tk.X, pady=(0, PADDING['small']))

        # Category
        ttk.Label(main_frame, text="Category *:").pack(anchor='w')
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(
            main_frame,
            textvariable=self.category_var,
            values=list(CATEGORIES.keys()),
            state='readonly'
        )
        self.category_combo.pack(fill=tk.X, pady=(0, PADDING['small']))
        self.category_combo.bind('<<ComboboxSelected>>', self._on_category_change)

        # Subcategory
        ttk.Label(main_frame, text="Subcategory:").pack(anchor='w')
        self.subcategory_var = tk.StringVar()
        self.subcategory_combo = ttk.Combobox(
            main_frame,
            textvariable=self.subcategory_var,
            state='readonly'
        )
        self.subcategory_combo.pack(fill=tk.X, pady=(0, PADDING['small']))

        # Vendor
        ttk.Label(main_frame, text="Vendor *:").pack(anchor='w')
        self.vendor_var = tk.StringVar()
        vendors = self.main_window.expense_manager.get_unique_vendors()
        vendor_combo = ttk.Combobox(main_frame, textvariable=self.vendor_var, values=vendors)
        vendor_combo.pack(fill=tk.X, pady=(0, PADDING['small']))

        # Typical Amount
        ttk.Label(main_frame, text="Typical Amount:").pack(anchor='w')
        self.amount_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.amount_var).pack(fill=tk.X, pady=(0, PADDING['small']))

        # Payment Method
        ttk.Label(main_frame, text="Payment Method:").pack(anchor='w')
        self.payment_var = tk.StringVar(value=PAYMENT_METHODS[0])
        ttk.Combobox(
            main_frame,
            textvariable=self.payment_var,
            values=PAYMENT_METHODS,
            state='readonly'
        ).pack(fill=tk.X, pady=(0, PADDING['small']))

        # Description
        ttk.Label(main_frame, text="Description:").pack(anchor='w')
        self.description_text = tk.Text(main_frame, height=3)
        self.description_text.pack(fill=tk.X, pady=(0, PADDING['small']))

        # Tags
        ttk.Label(main_frame, text="Tags (comma separated):").pack(anchor='w')
        self.tags_var = tk.StringVar()
        ttk.Entry(main_frame, textvariable=self.tags_var).pack(fill=tk.X, pady=(0, PADDING['medium']))

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

    def _on_category_change(self, event):
        """Handle category selection."""
        category = self.category_var.get()
        subcategories = get_subcategories(category)
        self.subcategory_combo['values'] = subcategories
        if subcategories:
            self.subcategory_combo.set(subcategories[0])

    def _load_template(self):
        """Load template for editing."""
        template = self.main_window.template_manager.get_template(self.template_id)
        if template:
            self.name_var.set(template.name)
            self.category_var.set(template.category)
            self._on_category_change(None)
            self.subcategory_var.set(template.subcategory or '')
            self.vendor_var.set(template.vendor)
            if template.typical_amount:
                self.amount_var.set(str(template.typical_amount))
            self.payment_var.set(template.payment_method)
            if template.description:
                self.description_text.insert('1.0', template.description)
            if template.tags:
                self.tags_var.set(', '.join(template.tags))

    def _save(self):
        """Save template."""
        # Validate
        name = self.name_var.get().strip()
        if not name:
            messagebox.showerror("Error", "Template name is required")
            return

        category = self.category_var.get()
        if not category:
            messagebox.showerror("Error", "Category is required")
            return

        vendor = self.vendor_var.get().strip()
        if not vendor:
            messagebox.showerror("Error", "Vendor is required")
            return

        # Parse amount
        amount = None
        if self.amount_var.get().strip():
            try:
                amount = float(self.amount_var.get().replace(',', ''))
            except ValueError:
                messagebox.showerror("Error", "Invalid amount")
                return

        description = self.description_text.get('1.0', tk.END).strip()
        tags_str = self.tags_var.get().strip()
        tags = [t.strip() for t in tags_str.split(',') if t.strip()] if tags_str else []

        try:
            if self.mode == 'add':
                template = ExpenseTemplate(
                    name=name,
                    category=category,
                    subcategory=self.subcategory_var.get(),
                    vendor=vendor,
                    typical_amount=amount,
                    payment_method=self.payment_var.get(),
                    description=description,
                    tags=tags
                )
                self.main_window.template_manager.add_template(template)
                self.main_window.set_status("Template added")
            else:
                self.main_window.template_manager.update_template(
                    self.template_id,
                    {
                        'name': name,
                        'category': category,
                        'subcategory': self.subcategory_var.get(),
                        'vendor': vendor,
                        'typical_amount': amount,
                        'payment_method': self.payment_var.get(),
                        'description': description,
                        'tags': tags
                    }
                )
                self.main_window.set_status("Template updated")

            self.parent_view.refresh()
            self.destroy()

        except Exception as e:
            messagebox.showerror("Error", str(e))
