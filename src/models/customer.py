"""
Customer Model Module
Data class representing a customer.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional


@dataclass
class Customer:
    """Model representing a customer."""

    # Primary fields
    id: Optional[int] = None
    customer_code: Optional[str] = None
    customer_type: str = "individual"  # individual/business

    # Personal info
    full_name: str = ""
    id_card: Optional[str] = None
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None  # Nam/Nữ/Khác

    # Business info
    company_name: Optional[str] = None
    tax_code: Optional[str] = None
    business_registration: Optional[str] = None

    # Contact info
    phone: Optional[str] = None
    phone2: Optional[str] = None
    email: Optional[str] = None

    # Address
    address: Optional[str] = None
    province: Optional[str] = None
    district: Optional[str] = None
    ward: Optional[str] = None

    # Classification
    customer_class: str = "regular"  # regular/potential/vip
    source: Optional[str] = None

    # Metadata
    notes: Optional[str] = None
    assigned_to: Optional[int] = None
    created_by: Optional[int] = None

    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    @property
    def is_business(self) -> bool:
        """Check if customer is a business."""
        return self.customer_type == 'business'

    @property
    def display_name(self) -> str:
        """Get display name for customer."""
        if self.is_business and self.company_name:
            return f"{self.company_name} ({self.full_name})"
        return self.full_name

    @property
    def is_vip(self) -> bool:
        """Check if customer is VIP."""
        return self.customer_class == 'vip'

    @classmethod
    def from_dict(cls, data: dict) -> Optional["Customer"]:
        """Create Customer from dictionary.

        Args:
            data: Dictionary containing customer data

        Returns:
            Customer instance or None if data is empty
        """
        if not data:
            return None

        # Convert string dates to date objects
        date_of_birth = data.get('date_of_birth')
        if isinstance(date_of_birth, str) and date_of_birth:
            try:
                date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
            except ValueError:
                date_of_birth = None

        # Convert string datetimes to datetime objects
        created_at = data.get('created_at')
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except ValueError:
                created_at = None

        updated_at = data.get('updated_at')
        if isinstance(updated_at, str):
            try:
                updated_at = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            except ValueError:
                updated_at = None

        deleted_at = data.get('deleted_at')
        if isinstance(deleted_at, str):
            try:
                deleted_at = datetime.fromisoformat(deleted_at.replace('Z', '+00:00'))
            except ValueError:
                deleted_at = None

        return cls(
            id=data.get('id'),
            customer_code=data.get('customer_code'),
            customer_type=data.get('customer_type', 'individual'),
            full_name=data.get('full_name', ''),
            id_card=data.get('id_card'),
            date_of_birth=date_of_birth,
            gender=data.get('gender'),
            company_name=data.get('company_name'),
            tax_code=data.get('tax_code'),
            business_registration=data.get('business_registration'),
            phone=data.get('phone'),
            phone2=data.get('phone2'),
            email=data.get('email'),
            address=data.get('address'),
            province=data.get('province'),
            district=data.get('district'),
            ward=data.get('ward'),
            customer_class=data.get('customer_class', 'regular'),
            source=data.get('source'),
            notes=data.get('notes'),
            assigned_to=data.get('assigned_to'),
            created_by=data.get('created_by'),
            created_at=created_at,
            updated_at=updated_at,
            is_deleted=bool(data.get('is_deleted', 0)),
            deleted_at=deleted_at,
            deleted_by=data.get('deleted_by')
        )

    def to_dict(self) -> dict:
        """Convert Customer instance to dictionary.

        Returns:
            Dictionary representation of the customer
        """
        result = {
            'id': self.id,
            'customer_code': self.customer_code,
            'customer_type': self.customer_type,
            'full_name': self.full_name,
            'id_card': self.id_card,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'gender': self.gender,
            'company_name': self.company_name,
            'tax_code': self.tax_code,
            'business_registration': self.business_registration,
            'phone': self.phone,
            'phone2': self.phone2,
            'email': self.email,
            'address': self.address,
            'province': self.province,
            'district': self.district,
            'ward': self.ward,
            'customer_class': self.customer_class,
            'source': self.source,
            'notes': self.notes,
            'assigned_to': self.assigned_to,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
            'deleted_by': self.deleted_by
        }

        # Remove None values for cleaner output
        return {k: v for k, v in result.items() if v is not None}

    def get_short_info(self) -> str:
        """Get short info string for display.

        Returns:
            Short description like "KH000001 - Nguyễn Văn An"
        """
        code = self.customer_code or "Chưa có mã"
        return f"{code} - {self.display_name}"

    def get_contact_info(self) -> str:
        """Get contact information string.

        Returns:
            Phone and email info
        """
        parts = []
        if self.phone:
            parts.append(f"📞 {self.phone}")
        if self.email:
            parts.append(f"✉️ {self.email}")
        return " | ".join(parts) if parts else "Chưa có thông tin liên hệ"

    def get_address_display(self) -> str:
        """Get formatted address.

        Returns:
            Full address string
        """
        if not self.address:
            return "Chưa có địa chỉ"

        parts = [self.address]
        if self.ward:
            parts.append(self.ward)
        if self.district:
            parts.append(self.district)
        if self.province:
            parts.append(self.province)

        return ", ".join(parts)

    def get_class_display(self) -> str:
        """Get customer class display with icon.

        Returns:
            Class with icon (e.g., "⭐ VIP")
        """
        icons = {
            'vip': '⭐',
            'regular': '●',
            'potential': '○'
        }
        names = {
            'vip': 'VIP',
            'regular': 'Regular',
            'potential': 'Potential'
        }
        icon = icons.get(self.customer_class, '○')
        name = names.get(self.customer_class, self.customer_class)
        return f"{icon} {name}"
