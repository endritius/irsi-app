"""
UI Styles and Themes for Beauty Salon Expense Manager.
"""

import tkinter as tk
from tkinter import ttk


# Color Palette
COLORS = {
    'primary': '#3498db',
    'primary_dark': '#2980b9',
    'secondary': '#2ecc71',
    'secondary_dark': '#27ae60',
    'danger': '#e74c3c',
    'danger_dark': '#c0392b',
    'warning': '#f39c12',
    'warning_dark': '#d68910',
    'info': '#17a2b8',
    'light': '#f8f9fa',
    'dark': '#343a40',
    'white': '#ffffff',
    'gray': '#6c757d',
    'gray_light': '#dee2e6',
    'background': '#f5f6fa',
    'card': '#ffffff',
    'text': '#2c3e50',
    'text_muted': '#7f8c8d',
    'border': '#e1e8ed',
    'success': '#28a745',
    'over_budget': '#dc3545',
    'warning_budget': '#ffc107',
    'under_budget': '#28a745'
}

# Font configurations
FONTS = {
    'title': ('Segoe UI', 18, 'bold'),
    'heading': ('Segoe UI', 14, 'bold'),
    'subheading': ('Segoe UI', 12, 'bold'),
    'body': ('Segoe UI', 10),
    'body_bold': ('Segoe UI', 10, 'bold'),
    'small': ('Segoe UI', 9),
    'small_bold': ('Segoe UI', 9, 'bold'),
    'button': ('Segoe UI', 10),
    'input': ('Segoe UI', 10),
    'monospace': ('Consolas', 10),
    'large_number': ('Segoe UI', 24, 'bold')
}

# Padding and spacing
PADDING = {
    'small': 5,
    'medium': 10,
    'large': 15,
    'xl': 20,
    'section': 25
}

# Dimensions
DIMENSIONS = {
    'sidebar_width': 250,
    'input_height': 30,
    'button_height': 35,
    'row_height': 25,
    'card_width': 300,
    'card_height': 150,
    'dialog_width': 500,
    'dialog_height': 400
}


def apply_theme(root: tk.Tk):
    """
    Apply custom theme to the application.

    Args:
        root: Root Tkinter window
    """
    style = ttk.Style(root)

    # Use clam as base theme
    style.theme_use('clam')

    # Configure frame
    style.configure('TFrame', background=COLORS['background'])
    style.configure('Card.TFrame', background=COLORS['card'])

    # Configure labels
    style.configure('TLabel',
                   background=COLORS['background'],
                   foreground=COLORS['text'],
                   font=FONTS['body'])

    style.configure('Title.TLabel',
                   font=FONTS['title'],
                   foreground=COLORS['text'])

    style.configure('Heading.TLabel',
                   font=FONTS['heading'],
                   foreground=COLORS['text'])

    style.configure('Subheading.TLabel',
                   font=FONTS['subheading'],
                   foreground=COLORS['text'])

    style.configure('Muted.TLabel',
                   foreground=COLORS['text_muted'])

    style.configure('Card.TLabel',
                   background=COLORS['card'])

    style.configure('LargeNumber.TLabel',
                   font=FONTS['large_number'],
                   foreground=COLORS['primary'])

    # Configure buttons
    style.configure('TButton',
                   font=FONTS['button'],
                   padding=(15, 8))

    style.configure('Primary.TButton',
                   background=COLORS['primary'],
                   foreground=COLORS['white'])

    style.map('Primary.TButton',
             background=[('active', COLORS['primary_dark']),
                        ('pressed', COLORS['primary_dark'])])

    style.configure('Secondary.TButton',
                   background=COLORS['secondary'],
                   foreground=COLORS['white'])

    style.map('Secondary.TButton',
             background=[('active', COLORS['secondary_dark']),
                        ('pressed', COLORS['secondary_dark'])])

    style.configure('Danger.TButton',
                   background=COLORS['danger'],
                   foreground=COLORS['white'])

    style.map('Danger.TButton',
             background=[('active', COLORS['danger_dark']),
                        ('pressed', COLORS['danger_dark'])])

    style.configure('Outline.TButton',
                   background=COLORS['white'],
                   foreground=COLORS['primary'])

    # Configure entry
    style.configure('TEntry',
                   font=FONTS['input'],
                   padding=5)

    # Configure combobox
    style.configure('TCombobox',
                   font=FONTS['input'],
                   padding=5)

    # Configure treeview
    style.configure('Treeview',
                   background=COLORS['white'],
                   foreground=COLORS['text'],
                   fieldbackground=COLORS['white'],
                   font=FONTS['body'],
                   rowheight=DIMENSIONS['row_height'])

    style.configure('Treeview.Heading',
                   font=FONTS['body_bold'],
                   background=COLORS['primary'],
                   foreground=COLORS['white'])

    style.map('Treeview',
             background=[('selected', COLORS['primary'])],
             foreground=[('selected', COLORS['white'])])

    # Configure notebook (tabs)
    style.configure('TNotebook',
                   background=COLORS['background'])

    style.configure('TNotebook.Tab',
                   font=FONTS['body'],
                   padding=(15, 8))

    style.map('TNotebook.Tab',
             background=[('selected', COLORS['card'])],
             expand=[('selected', [1, 1, 1, 0])])

    # Configure labelframe
    style.configure('TLabelframe',
                   background=COLORS['card'])

    style.configure('TLabelframe.Label',
                   font=FONTS['subheading'],
                   foreground=COLORS['text'],
                   background=COLORS['card'])

    # Configure scrollbar
    style.configure('TScrollbar',
                   background=COLORS['gray_light'],
                   troughcolor=COLORS['light'])

    # Configure progressbar
    style.configure('TProgressbar',
                   background=COLORS['primary'],
                   troughcolor=COLORS['gray_light'])

    style.configure('Success.TProgressbar',
                   background=COLORS['success'])

    style.configure('Warning.TProgressbar',
                   background=COLORS['warning'])

    style.configure('Danger.TProgressbar',
                   background=COLORS['danger'])

    # Configure separator
    style.configure('TSeparator',
                   background=COLORS['border'])

    # Configure checkbutton
    style.configure('TCheckbutton',
                   background=COLORS['background'],
                   font=FONTS['body'])

    # Configure radiobutton
    style.configure('TRadiobutton',
                   background=COLORS['background'],
                   font=FONTS['body'])


def create_rounded_button(parent, text, command=None, style='primary', width=None):
    """
    Create a styled button.

    Args:
        parent: Parent widget
        text: Button text
        command: Click handler
        style: 'primary', 'secondary', 'danger', 'outline'
        width: Button width

    Returns:
        Button widget
    """
    style_map = {
        'primary': 'Primary.TButton',
        'secondary': 'Secondary.TButton',
        'danger': 'Danger.TButton',
        'outline': 'Outline.TButton'
    }

    btn = ttk.Button(
        parent,
        text=text,
        command=command,
        style=style_map.get(style, 'TButton'),
        width=width
    )
    return btn


def create_card_frame(parent, title=None):
    """
    Create a card-style frame with optional title.

    Args:
        parent: Parent widget
        title: Optional card title

    Returns:
        Frame widget (or LabelFrame if title provided)
    """
    if title:
        frame = ttk.LabelFrame(parent, text=title, style='TLabelframe')
    else:
        frame = ttk.Frame(parent, style='Card.TFrame')

    return frame


def create_separator(parent, orient='horizontal'):
    """
    Create a separator line.

    Args:
        parent: Parent widget
        orient: 'horizontal' or 'vertical'

    Returns:
        Separator widget
    """
    return ttk.Separator(parent, orient=orient)


def get_status_color(percentage):
    """
    Get color based on budget percentage.

    Args:
        percentage: Usage percentage

    Returns:
        Color hex code
    """
    if percentage >= 100:
        return COLORS['over_budget']
    elif percentage >= 80:
        return COLORS['warning_budget']
    else:
        return COLORS['under_budget']
