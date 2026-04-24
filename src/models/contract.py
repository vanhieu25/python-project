"""
Contract Model Module
Data classes for Contract, ContractItem, and ContractPayment.
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List, Dict, Any


@dataclass
class Contract:
    """Contract model."""
    id: Optional[int] = None
    contract_code: Optional[str] = None

    # Customer info
    customer_id: int = 0
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_id_card: Optional[str] = None
    customer_address: Optional[str] = None

    # Car info
    car_id: int = 0
    car_vin: Optional[str] = None
    car_license_plate: Optional[str] = None
    car_brand: Optional[str] = None
    car_model: Optional[str] = None
    car_year: Optional[int] = None
    car_color: Optional[str] = None

    # Pricing
    car_price: float = 0.0
    discount_amount: float = 0.0
    discount_reason: Optional[str] = None
    total_amount: float = 0.0
    vat_amount: float = 0.0
    final_amount: float = 0.0

    # Payment
    payment_method: Optional[str] = None
    deposit_amount: float = 0.0
    paid_amount: float = 0.0
    remaining_amount: float = 0.0

    # Installment
    is_installment: bool = False
    installment_down_payment: Optional[float] = None
    installment_months: Optional[int] = None
    installment_monthly_amount: Optional[float] = None

    # Delivery
    delivery_date: Optional[date] = None
    actual_delivery_date: Optional[date] = None
    delivery_location: Optional[str] = None

    # Status
    status: str = 'draft'  # draft, pending, approved, signed, paid, delivered, cancelled
    approval_status: str = 'pending'

    # Approval
    created_by: Optional[int] = None
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    approval_notes: Optional[str] = None

    # Signing
    signed_at: Optional[datetime] = None
    signed_by_customer: bool = False
    signed_by_representative: bool = False

    # Metadata
    notes: Optional[str] = None
    contract_template_id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Related data (not in DB)
    items: List['ContractItem'] = field(default_factory=list)
    payments: List['ContractPayment'] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['Contract']:
        """Create Contract from dictionary."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            contract_code=data.get('contract_code'),
            customer_id=data.get('customer_id', 0),
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            customer_id_card=data.get('customer_id_card'),
            customer_address=data.get('customer_address'),
            car_id=data.get('car_id', 0),
            car_vin=data.get('car_vin'),
            car_license_plate=data.get('car_license_plate'),
            car_brand=data.get('car_brand'),
            car_model=data.get('car_model'),
            car_year=data.get('car_year'),
            car_color=data.get('car_color'),
            car_price=data.get('car_price', 0) or 0,
            discount_amount=data.get('discount_amount', 0) or 0,
            discount_reason=data.get('discount_reason'),
            total_amount=data.get('total_amount', 0) or 0,
            vat_amount=data.get('vat_amount', 0) or 0,
            final_amount=data.get('final_amount', 0) or 0,
            payment_method=data.get('payment_method'),
            deposit_amount=data.get('deposit_amount', 0) or 0,
            paid_amount=data.get('paid_amount', 0) or 0,
            remaining_amount=data.get('remaining_amount', 0) or 0,
            is_installment=bool(data.get('is_installment', 0)),
            installment_down_payment=data.get('installment_down_payment'),
            installment_months=data.get('installment_months'),
            installment_monthly_amount=data.get('installment_monthly_amount'),
            delivery_date=data.get('delivery_date'),
            actual_delivery_date=data.get('actual_delivery_date'),
            delivery_location=data.get('delivery_location'),
            status=data.get('status', 'draft'),
            approval_status=data.get('approval_status', 'pending'),
            created_by=data.get('created_by'),
            approved_by=data.get('approved_by'),
            approved_at=data.get('approved_at'),
            approval_notes=data.get('approval_notes'),
            signed_at=data.get('signed_at'),
            signed_by_customer=bool(data.get('signed_by_customer', 0)),
            signed_by_representative=bool(data.get('signed_by_representative', 0)),
            notes=data.get('notes'),
            contract_template_id=data.get('contract_template_id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert Contract to dictionary."""
        return {
            'id': self.id,
            'contract_code': self.contract_code,
            'customer_id': self.customer_id,
            'customer_name': self.customer_name,
            'customer_phone': self.customer_phone,
            'customer_id_card': self.customer_id_card,
            'customer_address': self.customer_address,
            'car_id': self.car_id,
            'car_vin': self.car_vin,
            'car_license_plate': self.car_license_plate,
            'car_brand': self.car_brand,
            'car_model': self.car_model,
            'car_year': self.car_year,
            'car_color': self.car_color,
            'car_price': self.car_price,
            'discount_amount': self.discount_amount,
            'discount_reason': self.discount_reason,
            'total_amount': self.total_amount,
            'vat_amount': self.vat_amount,
            'final_amount': self.final_amount,
            'payment_method': self.payment_method,
            'deposit_amount': self.deposit_amount,
            'paid_amount': self.paid_amount,
            'remaining_amount': self.remaining_amount,
            'is_installment': self.is_installment,
            'installment_down_payment': self.installment_down_payment,
            'installment_months': self.installment_months,
            'installment_monthly_amount': self.installment_monthly_amount,
            'delivery_date': self.delivery_date,
            'actual_delivery_date': self.actual_delivery_date,
            'delivery_location': self.delivery_location,
            'status': self.status,
            'approval_status': self.approval_status,
            'created_by': self.created_by,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at,
            'approval_notes': self.approval_notes,
            'signed_at': self.signed_at,
            'signed_by_customer': self.signed_by_customer,
            'signed_by_representative': self.signed_by_representative,
            'notes': self.notes,
            'contract_template_id': self.contract_template_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    @property
    def is_paid(self) -> bool:
        """Check if contract is fully paid."""
        return self.paid_amount >= self.final_amount

    @property
    def payment_progress(self) -> float:
        """Get payment progress percentage."""
        if self.final_amount == 0:
            return 0.0
        return (self.paid_amount / self.final_amount) * 100


@dataclass
class ContractItem:
    """Contract item (accessory, service, etc.)."""
    id: Optional[int] = None
    contract_id: int = 0
    item_type: str = ''  # accessory, service, insurance, registration
    item_name: str = ''
    item_description: Optional[str] = None
    quantity: int = 1
    unit_price: float = 0.0
    total_price: float = 0.0
    is_optional: bool = False
    is_selected: bool = True
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['ContractItem']:
        """Create ContractItem from dictionary."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            contract_id=data.get('contract_id', 0),
            item_type=data.get('item_type', ''),
            item_name=data.get('item_name', ''),
            item_description=data.get('item_description'),
            quantity=data.get('quantity', 1),
            unit_price=data.get('unit_price', 0) or 0,
            total_price=data.get('total_price', 0) or 0,
            is_optional=bool(data.get('is_optional', 0)),
            is_selected=bool(data.get('is_selected', 1)),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ContractItem to dictionary."""
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'item_type': self.item_type,
            'item_name': self.item_name,
            'item_description': self.item_description,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'total_price': self.total_price,
            'is_optional': self.is_optional,
            'is_selected': self.is_selected,
            'created_at': self.created_at
        }


@dataclass
class ContractPayment:
    """Contract payment record."""
    id: Optional[int] = None
    contract_id: int = 0
    payment_code: Optional[str] = None
    payment_type: Optional[str] = None  # deposit, installment, final
    amount: float = 0.0
    payment_method: Optional[str] = None
    payment_date: Optional[datetime] = None
    received_by: Optional[int] = None
    notes: Optional[str] = None
    receipt_printed: bool = False
    created_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['ContractPayment']:
        """Create ContractPayment from dictionary."""
        if not data:
            return None
        return cls(
            id=data.get('id'),
            contract_id=data.get('contract_id', 0),
            payment_code=data.get('payment_code'),
            payment_type=data.get('payment_type'),
            amount=data.get('amount', 0) or 0,
            payment_method=data.get('payment_method'),
            payment_date=data.get('payment_date'),
            received_by=data.get('received_by'),
            notes=data.get('notes'),
            receipt_printed=bool(data.get('receipt_printed', 0)),
            created_at=data.get('created_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ContractPayment to dictionary."""
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'payment_code': self.payment_code,
            'payment_type': self.payment_type,
            'amount': self.amount,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date,
            'received_by': self.received_by,
            'notes': self.notes,
            'receipt_printed': self.receipt_printed,
            'created_at': self.created_at
        }
