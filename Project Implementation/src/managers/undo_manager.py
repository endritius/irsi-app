"""
UndoManager - Manages undo/redo operations for reversible actions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.error_handler import log_info, log_warning


class ActionType(Enum):
    """Types of undoable actions."""
    ADD_EXPENSE = "add_expense"
    UPDATE_EXPENSE = "update_expense"
    DELETE_EXPENSE = "delete_expense"
    RESTORE_EXPENSE = "restore_expense"
    ADD_BUDGET = "add_budget"
    UPDATE_BUDGET = "update_budget"
    DELETE_BUDGET = "delete_budget"
    ADD_TEMPLATE = "add_template"
    UPDATE_TEMPLATE = "update_template"
    DELETE_TEMPLATE = "delete_template"
    BULK_DELETE = "bulk_delete"
    BULK_RESTORE = "bulk_restore"


@dataclass
class UndoAction:
    """
    Represents an undoable action.

    Attributes:
        action_type: Type of action
        timestamp: When action was performed
        description: Human-readable description
        undo_data: Data needed to undo the action
        redo_data: Data needed to redo the action
    """
    action_type: ActionType
    timestamp: datetime
    description: str
    undo_data: Dict[str, Any]
    redo_data: Dict[str, Any] = field(default_factory=dict)


class UndoManager:
    """
    Manages undo/redo stack for reversible operations.
    """

    def __init__(self, max_history: int = 50):
        """
        Initialize UndoManager.

        Args:
            max_history: Maximum number of actions to keep
        """
        self.max_history = max_history
        self._undo_stack: List[UndoAction] = []
        self._redo_stack: List[UndoAction] = []
        self._callbacks: Dict[ActionType, Callable] = {}

    def register_handler(
        self,
        action_type: ActionType,
        handler: Callable[[Dict[str, Any]], bool]
    ) -> None:
        """
        Register a handler for undoing a specific action type.

        Args:
            action_type: Type of action to handle
            handler: Function that performs the undo, returns success
        """
        self._callbacks[action_type] = handler

    def record_action(
        self,
        action_type: ActionType,
        description: str,
        undo_data: Dict[str, Any],
        redo_data: Dict[str, Any] = None
    ) -> None:
        """
        Record an action for potential undo.

        Args:
            action_type: Type of action
            description: Human-readable description
            undo_data: Data needed to undo
            redo_data: Data needed to redo
        """
        action = UndoAction(
            action_type=action_type,
            timestamp=datetime.now(),
            description=description,
            undo_data=undo_data,
            redo_data=redo_data or {}
        )

        self._undo_stack.append(action)

        # Clear redo stack when new action is recorded
        self._redo_stack.clear()

        # Limit history size
        while len(self._undo_stack) > self.max_history:
            self._undo_stack.pop(0)

        log_info(f"Recorded action: {description}")

    def undo(self) -> bool:
        """
        Undo the last action.

        Returns:
            True if undo was successful
        """
        if not self._undo_stack:
            log_warning("Nothing to undo")
            return False

        action = self._undo_stack.pop()

        # Get handler for action type
        handler = self._callbacks.get(action.action_type)
        if not handler:
            log_warning(f"No handler for action type: {action.action_type}")
            self._undo_stack.append(action)  # Put it back
            return False

        # Execute undo
        try:
            success = handler(action.undo_data)
            if success:
                self._redo_stack.append(action)
                log_info(f"Undone: {action.description}")
                return True
            else:
                self._undo_stack.append(action)
                return False
        except Exception as e:
            log_warning(f"Undo failed: {e}")
            self._undo_stack.append(action)
            return False

    def redo(self) -> bool:
        """
        Redo the last undone action.

        Returns:
            True if redo was successful
        """
        if not self._redo_stack:
            log_warning("Nothing to redo")
            return False

        action = self._redo_stack.pop()

        # Get handler for action type
        handler = self._callbacks.get(action.action_type)
        if not handler:
            log_warning(f"No handler for action type: {action.action_type}")
            self._redo_stack.append(action)
            return False

        # Execute redo
        try:
            success = handler(action.redo_data)
            if success:
                self._undo_stack.append(action)
                log_info(f"Redone: {action.description}")
                return True
            else:
                self._redo_stack.append(action)
                return False
        except Exception as e:
            log_warning(f"Redo failed: {e}")
            self._redo_stack.append(action)
            return False

    def can_undo(self) -> bool:
        """Check if undo is available."""
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        """Check if redo is available."""
        return len(self._redo_stack) > 0

    def get_undo_description(self) -> Optional[str]:
        """Get description of next undo action."""
        if self._undo_stack:
            return self._undo_stack[-1].description
        return None

    def get_redo_description(self) -> Optional[str]:
        """Get description of next redo action."""
        if self._redo_stack:
            return self._redo_stack[-1].description
        return None

    def get_undo_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent undo history.

        Args:
            limit: Maximum number of items

        Returns:
            List of action summaries
        """
        history = []
        for action in reversed(self._undo_stack[-limit:]):
            history.append({
                'description': action.description,
                'type': action.action_type.value,
                'timestamp': action.timestamp.strftime('%H:%M:%S')
            })
        return history

    def clear(self) -> None:
        """Clear all undo/redo history."""
        self._undo_stack.clear()
        self._redo_stack.clear()
        log_info("Undo history cleared")

    @property
    def undo_count(self) -> int:
        """Number of available undo actions."""
        return len(self._undo_stack)

    @property
    def redo_count(self) -> int:
        """Number of available redo actions."""
        return len(self._redo_stack)


# Singleton instance
_undo_manager: Optional[UndoManager] = None


def get_undo_manager() -> UndoManager:
    """Get or create global UndoManager instance."""
    global _undo_manager
    if _undo_manager is None:
        _undo_manager = UndoManager()
    return _undo_manager
