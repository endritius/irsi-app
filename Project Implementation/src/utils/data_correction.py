"""
DataCorrection - Utilities for automatic data correction and validation.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import csv

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import CATEGORIES, PAYMENT_METHODS, LOGS_DIR


@dataclass
class DataCorrection:
    """
    Record of a data correction applied.

    Attributes:
        timestamp: When correction was made
        record_type: Type of record (expense, budget, template)
        record_id: ID of the record
        field: Field that was corrected
        original_value: Original (invalid) value
        corrected_value: New (corrected) value
        rule: Correction rule applied
    """
    timestamp: datetime
    record_type: str
    record_id: str
    field: str
    original_value: Any
    corrected_value: Any
    rule: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary for CSV storage."""
        return {
            'timestamp': self.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'record_type': self.record_type,
            'record_id': self.record_id,
            'field': self.field,
            'original_value': str(self.original_value),
            'corrected_value': str(self.corrected_value),
            'rule': self.rule
        }


class DataCorrectionService:
    """
    Service for applying and tracking data corrections.
    """

    def __init__(self, log_dir: Path = None):
        """
        Initialize data correction service.

        Args:
            log_dir: Directory for correction logs
        """
        self.log_dir = log_dir or LOGS_DIR
        self.log_dir = Path(self.log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.corrections: List[DataCorrection] = []

    def correct_expense(self, expense_data: Dict[str, Any], expense_id: str) -> Dict[str, Any]:
        """
        Apply corrections to expense data.

        Args:
            expense_data: Expense data dictionary
            expense_id: Expense ID for logging

        Returns:
            Corrected expense data
        """
        corrected = expense_data.copy()

        # Correct invalid date
        if 'date' in corrected:
            corrected_date = self._correct_date(
                corrected.get('date'),
                corrected.get('created_at'),
                'expense',
                expense_id
            )
            if corrected_date:
                corrected['date'] = corrected_date

        # Correct invalid category
        if 'category' in corrected:
            category = corrected.get('category', '')
            if category not in CATEGORIES:
                self._record_correction(
                    'expense', expense_id, 'category',
                    category, 'Administrative',
                    'unknown_category'
                )
                corrected['category'] = 'Administrative'
                # Clear subcategory since category changed
                if corrected.get('subcategory'):
                    self._record_correction(
                        'expense', expense_id, 'subcategory',
                        corrected['subcategory'], '',
                        'category_changed'
                    )
                    corrected['subcategory'] = ''

        # Correct invalid subcategory
        if 'subcategory' in corrected and corrected.get('subcategory'):
            category = corrected.get('category', '')
            subcategory = corrected.get('subcategory', '')
            if category in CATEGORIES:
                valid_subcats = CATEGORIES[category]['subcategories']
                if subcategory not in valid_subcats:
                    self._record_correction(
                        'expense', expense_id, 'subcategory',
                        subcategory, '',
                        'invalid_subcategory'
                    )
                    corrected['subcategory'] = ''

        # Correct negative amount
        if 'amount' in corrected:
            try:
                amount = float(corrected['amount'])
                if amount < 0:
                    self._record_correction(
                        'expense', expense_id, 'amount',
                        amount, abs(amount),
                        'negative_amount'
                    )
                    corrected['amount'] = abs(amount)
            except (ValueError, TypeError):
                self._record_correction(
                    'expense', expense_id, 'amount',
                    corrected['amount'], 0.0,
                    'invalid_amount'
                )
                corrected['amount'] = 0.0

        # Correct missing payment method
        if 'payment_method' in corrected:
            method = corrected.get('payment_method', '')
            if not method or method not in PAYMENT_METHODS:
                self._record_correction(
                    'expense', expense_id, 'payment_method',
                    method, 'Cash',
                    'missing_payment_method'
                )
                corrected['payment_method'] = 'Cash'

        # Correct future date
        if 'date' in corrected:
            try:
                date_val = corrected['date']
                if isinstance(date_val, str):
                    date_val = datetime.strptime(date_val, '%Y-%m-%d')
                if date_val > datetime.now():
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    self._record_correction(
                        'expense', expense_id, 'date',
                        corrected['date'], today_str,
                        'future_date'
                    )
                    corrected['date'] = today_str
            except (ValueError, TypeError):
                pass

        return corrected

    def correct_budget(self, budget_data: Dict[str, Any], budget_id: str) -> Dict[str, Any]:
        """
        Apply corrections to budget data.

        Args:
            budget_data: Budget data dictionary
            budget_id: Budget ID for logging

        Returns:
            Corrected budget data
        """
        corrected = budget_data.copy()

        # Correct negative amount
        if 'amount' in corrected:
            try:
                amount = float(corrected['amount'])
                if amount < 0:
                    self._record_correction(
                        'budget', budget_id, 'amount',
                        amount, abs(amount),
                        'negative_amount'
                    )
                    corrected['amount'] = abs(amount)
            except (ValueError, TypeError):
                self._record_correction(
                    'budget', budget_id, 'amount',
                    corrected['amount'], 0.0,
                    'invalid_amount'
                )
                corrected['amount'] = 0.0

        # Correct invalid thresholds
        if 'warning_threshold' in corrected:
            try:
                threshold = float(corrected['warning_threshold'])
                if threshold < 0:
                    corrected['warning_threshold'] = 0
                elif threshold > 100:
                    corrected['warning_threshold'] = 100
            except (ValueError, TypeError):
                corrected['warning_threshold'] = 80.0

        if 'critical_threshold' in corrected:
            try:
                threshold = float(corrected['critical_threshold'])
                if threshold < 0:
                    corrected['critical_threshold'] = 0
                elif threshold > 100:
                    corrected['critical_threshold'] = 100
            except (ValueError, TypeError):
                corrected['critical_threshold'] = 95.0

        # Correct invalid category
        if 'category' in corrected:
            category = corrected.get('category', '')
            if category and category not in CATEGORIES:
                self._record_correction(
                    'budget', budget_id, 'category',
                    category, 'Administrative',
                    'unknown_category'
                )
                corrected['category'] = 'Administrative'

        return corrected

    def _correct_date(
        self,
        date_value: Any,
        fallback_date: Any,
        record_type: str,
        record_id: str
    ) -> Optional[str]:
        """
        Correct invalid date value.

        Args:
            date_value: Date to validate
            fallback_date: Fallback date if invalid
            record_type: Type of record
            record_id: Record ID

        Returns:
            Corrected date string or None if no correction needed
        """
        if not date_value:
            return None

        # Try to parse the date
        date_formats = ['%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y']
        parsed_date = None

        if isinstance(date_value, datetime):
            parsed_date = date_value
        else:
            for fmt in date_formats:
                try:
                    parsed_date = datetime.strptime(str(date_value), fmt)
                    break
                except ValueError:
                    continue

        if parsed_date is None:
            # Use fallback date
            fallback = datetime.now()
            if fallback_date:
                try:
                    if isinstance(fallback_date, datetime):
                        fallback = fallback_date
                    else:
                        fallback = datetime.strptime(str(fallback_date), '%Y-%m-%d %H:%M:%S')
                except (ValueError, TypeError):
                    pass

            corrected_value = fallback.strftime('%Y-%m-%d')
            self._record_correction(
                record_type, record_id, 'date',
                date_value, corrected_value,
                'invalid_date_format'
            )
            return corrected_value

        return None

    def _record_correction(
        self,
        record_type: str,
        record_id: str,
        field: str,
        original_value: Any,
        corrected_value: Any,
        rule: str
    ) -> None:
        """
        Record a data correction.

        Args:
            record_type: Type of record
            record_id: Record ID
            field: Field corrected
            original_value: Original value
            corrected_value: New value
            rule: Correction rule applied
        """
        correction = DataCorrection(
            timestamp=datetime.now(),
            record_type=record_type,
            record_id=record_id,
            field=field,
            original_value=original_value,
            corrected_value=corrected_value,
            rule=rule
        )
        self.corrections.append(correction)

    def save_corrections_log(self) -> str:
        """
        Save corrections to log file.

        Returns:
            Path to log file
        """
        if not self.corrections:
            return ""

        log_file = self.log_dir / f"data_corrections_{datetime.now().strftime('%Y%m%d')}.csv"
        file_exists = log_file.exists()

        with open(log_file, 'a', newline='', encoding='utf-8') as f:
            fieldnames = ['timestamp', 'record_type', 'record_id', 'field',
                         'original_value', 'corrected_value', 'rule']
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not file_exists:
                writer.writeheader()

            for correction in self.corrections:
                writer.writerow(correction.to_dict())

        return str(log_file)

    def get_correction_summary(self) -> Dict[str, Any]:
        """
        Get summary of corrections made.

        Returns:
            Summary dictionary
        """
        by_type = {}
        by_field = {}
        by_rule = {}

        for c in self.corrections:
            by_type[c.record_type] = by_type.get(c.record_type, 0) + 1
            by_field[c.field] = by_field.get(c.field, 0) + 1
            by_rule[c.rule] = by_rule.get(c.rule, 0) + 1

        return {
            'total_corrections': len(self.corrections),
            'by_type': by_type,
            'by_field': by_field,
            'by_rule': by_rule,
            'corrections': [c.to_dict() for c in self.corrections]
        }

    def clear_corrections(self) -> None:
        """Clear recorded corrections."""
        self.corrections = []

    def check_duplicates(self, records: List[Dict], id_field: str) -> List[Tuple[str, List[int]]]:
        """
        Check for duplicate IDs in records.

        Args:
            records: List of record dictionaries
            id_field: Field name containing ID

        Returns:
            List of (id, [indices]) for duplicates
        """
        id_indices = {}
        for idx, record in enumerate(records):
            record_id = record.get(id_field, '')
            if record_id:
                if record_id not in id_indices:
                    id_indices[record_id] = []
                id_indices[record_id].append(idx)

        # Return only duplicates
        return [(id_val, indices) for id_val, indices in id_indices.items()
                if len(indices) > 1]


def validate_and_correct_expenses(
    expenses: List[Dict],
    correction_service: DataCorrectionService = None
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Validate and correct a list of expense records.

    Args:
        expenses: List of expense dictionaries
        correction_service: Optional correction service

    Returns:
        Tuple of (corrected_expenses, summary)
    """
    if correction_service is None:
        correction_service = DataCorrectionService()

    corrected = []
    for expense in expenses:
        expense_id = expense.get('expense_id', 'unknown')
        corrected.append(correction_service.correct_expense(expense, expense_id))

    summary = correction_service.get_correction_summary()
    correction_service.save_corrections_log()

    return corrected, summary


def validate_and_correct_budgets(
    budgets: List[Dict],
    correction_service: DataCorrectionService = None
) -> Tuple[List[Dict], Dict[str, Any]]:
    """
    Validate and correct a list of budget records.

    Args:
        budgets: List of budget dictionaries
        correction_service: Optional correction service

    Returns:
        Tuple of (corrected_budgets, summary)
    """
    if correction_service is None:
        correction_service = DataCorrectionService()

    corrected = []
    for budget in budgets:
        budget_id = budget.get('budget_id', 'unknown')
        corrected.append(correction_service.correct_budget(budget, budget_id))

    summary = correction_service.get_correction_summary()
    correction_service.save_corrections_log()

    return corrected, summary
