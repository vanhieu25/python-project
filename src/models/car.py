"""
Car Model Module
Data class representing a car/vehicle.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Car:
    """Model representing a car/vehicle in the dealership."""

    # Primary fields
    id: Optional[int] = None
    vin: str = ""                              # Số VIN (17 ký tự)
    license_plate: Optional[str] = None        # Biển số xe
    brand: str = ""                            # Hãng xe
    model: str = ""                            # Model xe

    # Specifications
    year: Optional[int] = None                 # Năm sản xuất
    color: Optional[str] = None                # Màu sắc
    engine_number: Optional[str] = None        # Số máy
    transmission: Optional[str] = None         # Hộp số: auto/manual/cvt
    fuel_type: Optional[str] = None            # Nhiên liệu: gasoline/diesel/electric/hybrid
    mileage: int = 0                           # Số km đã đi

    # Pricing
    purchase_price: Optional[float] = None     # Giá nhập
    selling_price: Optional[float] = None      # Giá bán

    # Status
    status: str = "available"                  # available/sold/reserved/maintenance
    description: Optional[str] = None          # Mô tả chi tiết
    images: Optional[List[str]] = None         # Danh sách đường dẫn ảnh

    # Soft delete
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    deleted_by: Optional[int] = None

    # Metadata
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None

    @classmethod
    def from_dict(cls, data: dict) -> Optional["Car"]:
        """Create Car instance from dictionary.

        Args:
            data: Dictionary containing car data

        Returns:
            Car instance or None if data is empty
        """
        if not data:
            return None

        # Convert images JSON string to list if needed
        images = data.get('images')
        if isinstance(images, str):
            import json
            try:
                images = json.loads(images)
            except json.JSONDecodeError:
                images = None

        return cls(
            id=data.get('id'),
            vin=data.get('vin', ''),
            license_plate=data.get('license_plate'),
            brand=data.get('brand', ''),
            model=data.get('model', ''),
            year=data.get('year'),
            color=data.get('color'),
            engine_number=data.get('engine_number'),
            transmission=data.get('transmission'),
            fuel_type=data.get('fuel_type'),
            mileage=data.get('mileage', 0),
            purchase_price=data.get('purchase_price'),
            selling_price=data.get('selling_price'),
            status=data.get('status', 'available'),
            description=data.get('description'),
            images=images,
            is_deleted=bool(data.get('is_deleted', 0)),
            deleted_at=data.get('deleted_at'),
            deleted_by=data.get('deleted_by'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at'),
            created_by=data.get('created_by')
        )

    def to_dict(self) -> dict:
        """Convert Car instance to dictionary.

        Returns:
            Dictionary representation of the car
        """
        result = {
            'id': self.id,
            'vin': self.vin,
            'license_plate': self.license_plate,
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'color': self.color,
            'engine_number': self.engine_number,
            'transmission': self.transmission,
            'fuel_type': self.fuel_type,
            'mileage': self.mileage,
            'purchase_price': self.purchase_price,
            'selling_price': self.selling_price,
            'status': self.status,
            'description': self.description,
            'images': self.images,
            'is_deleted': self.is_deleted,
            'deleted_at': self.deleted_at,
            'deleted_by': self.deleted_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'created_by': self.created_by
        }

        # Remove None values for cleaner output
        return {k: v for k, v in result.items() if v is not None}

    def get_display_name(self) -> str:
        """Get display name for the car.

        Returns:
            Formatted display name (e.g., "2023 Honda Civic")
        """
        parts = []
        if self.year:
            parts.append(str(self.year))
        if self.brand:
            parts.append(self.brand)
        if self.model:
            parts.append(self.model)
        return " ".join(parts) if parts else "Xe chưa đặt tên"

    def get_price_display(self, price_type: str = 'selling') -> str:
        """Get formatted price display.

        Args:
            price_type: 'selling' or 'purchase'

        Returns:
            Formatted price string (e.g., "850.000.000 VNĐ")
        """
        price = self.selling_price if price_type == 'selling' else self.purchase_price
        if price is None:
            return "Chưa có giá"

        # Format: 850000000 -> 850.000.000
        return f"{price:,.0f} VNĐ".replace(',', '.')

    def get_short_vin(self) -> str:
        """Get shortened VIN for display.

        Returns:
            First 8 and last 4 characters of VIN
        """
        if len(self.vin) <= 12:
            return self.vin
        return f"{self.vin[:8]}...{self.vin[-4:]}"

    def is_available(self) -> bool:
        """Check if car is available for sale.

        Returns:
            True if status is 'available'
        """
        return self.status == 'available' and not self.is_deleted

    def calculate_profit(self) -> Optional[float]:
        """Calculate potential profit.

        Returns:
            Profit amount or None if prices not set
        """
        if self.selling_price is None or self.purchase_price is None:
            return None
        return self.selling_price - self.purchase_price

    def get_profit_margin(self) -> Optional[float]:
        """Calculate profit margin percentage.

        Returns:
            Profit margin as percentage or None
        """
        if self.purchase_price is None or self.purchase_price == 0:
            return None
        profit = self.calculate_profit()
        if profit is None:
            return None
        return (profit / self.purchase_price) * 100
