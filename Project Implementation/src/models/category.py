"""
CategoryManager - Manages expense categories and subcategories.
"""

from typing import List, Dict, Optional
from config import CATEGORIES


class CategoryManager:
    """
    Static manager for expense categories.
    Provides access to predefined categories, subcategories, and colors.
    """

    @staticmethod
    def get_categories() -> List[str]:
        """Get list of all category names."""
        return list(CATEGORIES.keys())

    @staticmethod
    def get_subcategories(category: str) -> List[str]:
        """
        Get subcategories for a given category.

        Args:
            category: Category name

        Returns:
            List of subcategory names, empty if category not found
        """
        if category in CATEGORIES:
            return CATEGORIES[category]["subcategories"].copy()
        return []

    @staticmethod
    def get_all_subcategories() -> Dict[str, List[str]]:
        """
        Get all categories with their subcategories.

        Returns:
            Dictionary mapping category names to subcategory lists
        """
        return {
            cat: data["subcategories"].copy()
            for cat, data in CATEGORIES.items()
        }

    @staticmethod
    def get_category_color(category: str) -> str:
        """
        Get color for a category.

        Args:
            category: Category name

        Returns:
            Hex color string, default gray if not found
        """
        if category in CATEGORIES:
            return CATEGORIES[category]["color"]
        return "#808080"

    @staticmethod
    def get_all_colors() -> Dict[str, str]:
        """
        Get all category colors.

        Returns:
            Dictionary mapping category names to hex colors
        """
        return {
            cat: data["color"]
            for cat, data in CATEGORIES.items()
        }

    @staticmethod
    def is_valid_category(category: str) -> bool:
        """
        Check if category exists.

        Args:
            category: Category name to check

        Returns:
            True if category exists
        """
        return category in CATEGORIES

    @staticmethod
    def is_valid_subcategory(category: str, subcategory: str) -> bool:
        """
        Check if subcategory exists under category.

        Args:
            category: Parent category name
            subcategory: Subcategory name to check

        Returns:
            True if subcategory exists under category
        """
        if category in CATEGORIES:
            return subcategory in CATEGORIES[category]["subcategories"]
        return False

    @staticmethod
    def get_category_for_subcategory(subcategory: str) -> Optional[str]:
        """
        Find which category a subcategory belongs to.

        Args:
            subcategory: Subcategory name

        Returns:
            Category name or None if not found
        """
        for cat, data in CATEGORIES.items():
            if subcategory in data["subcategories"]:
                return cat
        return None

    @staticmethod
    def get_category_count() -> int:
        """Get total number of categories."""
        return len(CATEGORIES)

    @staticmethod
    def get_subcategory_count() -> int:
        """Get total number of subcategories across all categories."""
        return sum(len(data["subcategories"]) for data in CATEGORIES.values())
