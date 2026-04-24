"""
Customer Validator Module
Validation logic for customer data.
"""

import re
from typing import Optional, Dict, Any, List
from datetime import datetime, date


class CustomerValidationError(Exception):
    """Customer validation error."""

    def __init__(self, message: str, field: Optional[str] = None,
                 code: Optional[str] = None):
        self.message = message
        self.field = field
        self.code = code
        super().__init__(message)


class CustomerValidationResult:
    """Result of validation."""

    def __init__(self):
        self.errors: List[CustomerValidationError] = []
        self.is_valid: bool = True

    def add_error(self, message: str, field: Optional[str] = None,
                  code: Optional[str] = None):
        """Add an error to the result."""
        self.errors.append(CustomerValidationError(message, field, code))
        self.is_valid = False

    def get_errors_by_field(self) -> Dict[str, List[str]]:
        """Get errors grouped by field."""
        result = {}
        for error in self.errors:
            field = error.field or 'general'
            if field not in result:
                result[field] = []
            result[field].append(error.message)
        return result

    def raise_if_invalid(self):
        """Raise exception if validation failed."""
        if not self.is_valid:
            raise CustomerValidationError(
                f"Validation failed with {len(self.errors)} error(s)"
            )


class CustomerValidator:
    """Validator for customer data."""

    VALID_CUSTOMER_TYPES = ['individual', 'business']
    VALID_CUSTOMER_CLASSES = ['regular', 'potential', 'vip']
    VALID_GENDERS = ['Nam', 'Nữ', 'Khác']

    # Vietnamese phone patterns
    PHONE_PATTERNS = [
        r'^0[3|5|7|8|9][0-9]{8}$',  # Mobile
        r'^0[2|4|6|8][0-9]{8,9}$',  # Landline
    ]

    def validate_all(self, data: Dict[str, Any],
                     is_update: bool = False) -> CustomerValidationResult:
        """Validate all customer data.

        Args:
            data: Customer data to validate
            is_update: Whether this is an update operation

        Returns:
            ValidationResult with all errors
        """
        result = CustomerValidationResult()

        # Required fields
        if not is_update:
            self._validate_required(data, result)

        # Validate individual fields
        if 'full_name' in data:
            self._validate_full_name(data['full_name'], result)
        if 'phone' in data:
            self._validate_phone(data['phone'], result)
        if 'email' in data:
            self._validate_email(data['email'], result)
        if 'id_card' in data:
            self._validate_id_card(data['id_card'], result)
        if 'date_of_birth' in data:
            self._validate_date_of_birth(data['date_of_birth'], result)
        if 'customer_type' in data:
            self._validate_customer_type(data['customer_type'], result)
        if 'customer_class' in data:
            self._validate_customer_class(data['customer_class'], result)

        # Business-specific validation
        if data.get('customer_type') == 'business':
            self._validate_business_fields(data, result)

        return result

    def _validate_required(self, data: Dict[str, Any],
                          result: CustomerValidationResult):
        """Validate required fields."""
        required = ['full_name', 'phone']
        for field in required:
            if not data.get(field):
                result.add_error(
                    f"{self._field_name_vn(field)} không được để trống",
                    field, 'required'
                )

        # Business requires company_name
        if data.get('customer_type') == 'business' and not data.get('company_name'):
            result.add_error(
                "Tên công ty không được để trống với khách hàng doanh nghiệp",
                'company_name', 'required'
            )

    def _validate_full_name(self, name: str, result: CustomerValidationResult):
        """Validate full name."""
        if not name:
            return

        name = name.strip()
        if len(name) < 2:
            result.add_error("Họ tên quá ngắn", 'full_name', 'too_short')
        if len(name) > 100:
            result.add_error("Họ tên không được quá 100 ký tự", 'full_name', 'too_long')

    def _validate_phone(self, phone: str, result: CustomerValidationResult):
        """Validate Vietnamese phone number."""
        if not phone:
            return

        phone = phone.strip().replace(' ', '').replace('-', '').replace('.', '')

        if not any(re.match(p, phone) for p in self.PHONE_PATTERNS):
            result.add_error(
                "Số điện thoại không đúng định dạng Việt Nam",
                'phone', 'invalid_format'
            )

    def _validate_email(self, email: Optional[str], result: CustomerValidationResult):
        """Validate email."""
        if not email:
            return

        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            result.add_error("Email không đúng định dạng", 'email', 'invalid_format')

        if len(email) > 100:
            result.add_error("Email quá dài", 'email', 'too_long')

    def _validate_id_card(self, id_card: Optional[str],
                         result: CustomerValidationResult):
        """Validate ID card (CMND/CCCD)."""
        if not id_card:
            return

        id_card = id_card.strip().replace(' ', '')

        # CMND: 9 số, CCCD: 12 số
        if not re.match(r'^[0-9]{9}$|^[0-9]{12}$', id_card):
            result.add_error(
                "CMND phải có 9 số hoặc CCCD phải có 12 số",
                'id_card', 'invalid_format'
            )

    def _validate_date_of_birth(self, dob: Any, result: CustomerValidationResult):
        """Validate date of birth."""
        if not dob:
            return

        try:
            if isinstance(dob, str):
                dob = datetime.strptime(dob, '%Y-%m-%d').date()

            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

            if age < 18:
                result.add_error("Khách hàng phải từ 18 tuổi", 'date_of_birth', 'too_young')
            if age > 120:
                result.add_error("Ngày sinh không hợp lý", 'date_of_birth', 'invalid')
        except (ValueError, TypeError):
            result.add_error("Ngày sinh không đúng định dạng", 'date_of_birth', 'invalid_format')

    def _validate_customer_type(self, c_type: str, result: CustomerValidationResult):
        """Validate customer type."""
        if c_type not in self.VALID_CUSTOMER_TYPES:
            result.add_error(
                f"Loại khách hàng không hợp lệ",
                'customer_type', 'invalid_value'
            )

    def _validate_customer_class(self, c_class: str, result: CustomerValidationResult):
        """Validate customer class."""
        if c_class not in self.VALID_CUSTOMER_CLASSES:
            result.add_error(
                f"Phân loại khách hàng không hợp lệ",
                'customer_class', 'invalid_value'
            )

    def _validate_business_fields(self, data: Dict[str, Any],
                                 result: CustomerValidationResult):
        """Validate business-specific fields."""
        # Tax code validation (10 or 13 digits)
        if data.get('tax_code'):
            tax_code = data['tax_code'].strip().replace(' ', '').replace('-', '')
            if not re.match(r'^[0-9]{10}$|^[0-9]{13}$', tax_code):
                result.add_error(
                    "Mã số thuế phải có 10 hoặc 13 số",
                    'tax_code', 'invalid_format'
                )

    def _field_name_vn(self, field: str) -> str:
        """Get Vietnamese field name."""
        names = {
            'full_name': 'Họ tên',
            'phone': 'Số điện thoại',
            'email': 'Email',
            'id_card': 'CMND/CCCD',
            'date_of_birth': 'Ngày sinh',
            'customer_type': 'Loại khách hàng',
            'company_name': 'Tên công ty',
            'tax_code': 'Mã số thuế'
        }
        return names.get(field, field)

    # Backward compatibility - static methods that raise on first error
    @staticmethod
    def validate_phone(phone: str) -> None:
        """Validate phone (backward compatibility)."""
        result = CustomerValidationResult()
        CustomerValidator()._validate_phone(phone, result)
        result.raise_if_invalid()

    @staticmethod
    def validate_email(email: str) -> None:
        """Validate email (backward compatibility)."""
        result = CustomerValidationResult()
        CustomerValidator()._validate_email(email, result)
        result.raise_if_invalid()

    @staticmethod
    def validate_id_card(id_card: str) -> None:
        """Validate ID card (backward compatibility)."""
        result = CustomerValidationResult()
        CustomerValidator()._validate_id_card(id_card, result)
        result.raise_if_invalid()
