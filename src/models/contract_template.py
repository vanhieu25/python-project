"""
Contract Template Model Module
Data classes for contract templates.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List
import re


@dataclass
class ContractTemplate:
    """Contract template model."""
    id: Optional[int] = None
    template_code: Optional[str] = None
    template_name: Optional[str] = None
    description: Optional[str] = None

    # Template content with placeholders
    template_content: str = ''
    header_content: Optional[str] = None
    footer_content: Optional[str] = None
    css_styles: Optional[str] = None

    # Metadata
    is_default: bool = False
    is_active: bool = True
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Optional['ContractTemplate']:
        """Create ContractTemplate from dictionary.

        Args:
            data: Dictionary data from database

        Returns:
            ContractTemplate instance or None
        """
        if not data:
            return None

        return cls(
            id=data.get('id'),
            template_code=data.get('template_code'),
            template_name=data.get('template_name'),
            description=data.get('description'),
            template_content=data.get('template_content', ''),
            header_content=data.get('header_content'),  # May not exist in DB
            footer_content=data.get('footer_content'),  # May not exist in DB
            css_styles=data.get('css_styles'),  # May not exist in DB
            is_default=bool(data.get('is_default', 0)),
            is_active=bool(data.get('is_active', 1)),
            created_by=data.get('created_by'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert ContractTemplate to dictionary.

        Returns:
            Dictionary representation
        """
        return {
            'id': self.id,
            'template_code': self.template_code,
            'template_name': self.template_name,
            'description': self.description,
            'template_content': self.template_content,
            'header_content': self.header_content,
            'footer_content': self.footer_content,
            'css_styles': self.css_styles,
            'is_default': 1 if self.is_default else 0,
            'is_active': 1 if self.is_active else 0,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def get_variables(self) -> List[str]:
        """Extract all template variables from content.

        Returns:
            List of variable names (e.g., ['customer_name', 'car_price'])
        """
        pattern = r'\{\{(\w+)\}\}'
        content = self.template_content or ''
        if self.header_content:
            content += self.header_content
        if self.footer_content:
            content += self.footer_content

        variables = set(re.findall(pattern, content))
        return sorted(list(variables))

    def validate(self) -> tuple[bool, Optional[str]]:
        """Validate template content.

        Returns:
            (is_valid, error_message)
        """
        if not self.template_name or not self.template_name.strip():
            return False, "Tên mẫu không được để trống"

        if not self.template_code or not self.template_code.strip():
            return False, "Mã mẫu không được để trống"

        if not self.template_content or not self.template_content.strip():
            return False, "Nội dung mẫu không được để trống"

        # Check for balanced braces
        open_count = self.template_content.count('{{')
        close_count = self.template_content.count('}}')

        if open_count != close_count:
            return False, f"Lỗi cú pháp: Có {open_count} dấu '{{{{' và {close_count} dấu '}}'"

        return True, None

    def render(self, data: Dict[str, Any]) -> str:
        """Render template with provided data.

        Args:
            data: Dictionary of variable values

        Returns:
            Rendered HTML string
        """
        content = self.template_content or ''

        # Add header
        if self.header_content:
            content = self.header_content + '\n' + content

        # Add footer
        if self.footer_content:
            content = content + '\n' + self.footer_content

        # Add CSS styles
        if self.css_styles:
            content = f"<style>{self.css_styles}</style>\n{content}"

        # Replace variables
        for key, value in data.items():
            placeholder = f'{{{{{key}}}}}'
            content = content.replace(placeholder, str(value) if value is not None else '')

        return content


@dataclass
class TemplateVariable:
    """Definition of a template variable."""
    name: str
    description: str
    category: str  # 'customer', 'car', 'contract', 'pricing', 'company'
    example: str

    @classmethod
    def get_all_variables(cls) -> List['TemplateVariable']:
        """Get all available template variables.

        Returns:
            List of TemplateVariable definitions
        """
        return [
            # Customer variables
            cls('customer_name', 'Tên khách hàng', 'customer', 'Nguyễn Văn A'),
            cls('customer_phone', 'Số điện thoại KH', 'customer', '0909123456'),
            cls('customer_id_card', 'CMND/CCCD', 'customer', '123456789012'),
            cls('customer_address', 'Địa chỉ KH', 'customer', '123 ABC, Quận 1, TP.HCM'),
            cls('customer_email', 'Email KH', 'customer', 'customer@example.com'),

            # Car variables
            cls('car_brand', 'Hãng xe', 'car', 'Toyota'),
            cls('car_model', 'Model xe', 'car', 'Camry'),
            cls('car_year', 'Năm sản xuất', 'car', '2024'),
            cls('car_color', 'Màu xe', 'car', 'Đen'),
            cls('car_vin', 'Số khung (VIN)', 'car', 'ABC123456789'),
            cls('car_license_plate', 'Biển số', 'car', '51A-12345'),
            cls('car_price', 'Giá xe (số)', 'car', '1000000000'),

            # Pricing variables (formatted)
            cls('car_price_formatted', 'Giá xe (VNĐ)', 'pricing', '1.000.000.000 VNĐ'),
            cls('discount_amount_formatted', 'Giảm giá', 'pricing', '50.000.000 VNĐ'),
            cls('total_amount_formatted', 'Tổng tiền', 'pricing', '950.000.000 VNĐ'),
            cls('vat_amount_formatted', 'Thuế VAT', 'pricing', '95.000.000 VNĐ'),
            cls('final_amount_formatted', 'Tổng thanh toán', 'pricing', '1.045.000.000 VNĐ'),
            cls('deposit_amount_formatted', 'Tiền đặt cọc', 'pricing', '100.000.000 VNĐ'),
            cls('paid_amount_formatted', 'Đã thanh toán', 'pricing', '1.045.000.000 VNĐ'),
            cls('remaining_amount_formatted', 'Còn lại', 'pricing', '0 VNĐ'),

            # Contract variables
            cls('contract_code', 'Mã hợp đồng', 'contract', 'HD000001'),
            cls('contract_date', 'Ngày tạo (YYYY-MM-DD)', 'contract', '2024-01-15'),
            cls('contract_date_vn', 'Ngày tạo (DD/MM/YYYY)', 'contract', '15/01/2024'),
            cls('created_by_name', 'Người tạo', 'contract', 'Nguyễn Văn B'),
            cls('approved_by_name', 'Người phê duyệt', 'contract', 'Trần Văn C'),
            cls('delivery_date', 'Ngày giao dự kiến', 'contract', '20/01/2024'),
            cls('delivery_location', 'Địa điểm giao xe', 'contract', 'Showroom ABC'),

            # Company variables
            cls('company_name', 'Tên công ty', 'company', 'CÔNG TY TNHH Ô TÔ ABC'),
            cls('company_address', 'Địa chỉ công ty', 'company', '123 XYZ, Quận 1, TP.HCM'),
            cls('company_phone', 'Điện thoại công ty', 'company', '028-12345678'),
            cls('company_tax_code', 'Mã số thuế', 'company', '0123456789'),
        ]

    @classmethod
    def get_by_category(cls, category: str) -> List['TemplateVariable']:
        """Get variables by category.

        Args:
            category: Category name

        Returns:
            List of TemplateVariable in category
        """
        return [v for v in cls.get_all_variables() if v.category == category]
