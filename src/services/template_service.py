"""
Template Service Module
Business logic for contract templates.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime

from models.contract_template import ContractTemplate, TemplateVariable
from models.contract import Contract
from repositories.template_repository import TemplateRepository
from repositories.contract_repository import ContractRepository


class TemplateResult:
    """Result wrapper for template operations."""

    def __init__(self, success: bool, message: str = None, data: Any = None):
        self.success = success
        self.message = message
        self.data = data

    @classmethod
    def ok(cls, message: str = None, data: Any = None) -> 'TemplateResult':
        return cls(success=True, message=message, data=data)

    @classmethod
    def fail(cls, message: str, data: Any = None) -> 'TemplateResult':
        return cls(success=False, message=message, data=data)


class TemplateService:
    """Service for contract template operations."""

    def __init__(
        self,
        template_repo: TemplateRepository,
        contract_repo: ContractRepository = None,
        user_repo=None
    ):
        """Initialize service.

        Args:
            template_repo: Template repository
            contract_repo: Optional contract repository
            user_repo: Optional user repository
        """
        self.template_repo = template_repo
        self.contract_repo = contract_repo
        self.user_repo = user_repo

    def _get_contract_data(self, contract: Contract) -> Dict[str, Any]:
        """Extract template variables from contract.

        Args:
            contract: Contract instance

        Returns:
            Dictionary of template variables
        """
        data = {}

        # Customer data
        data['customer_name'] = contract.customer_name or ''
        data['customer_phone'] = contract.customer_phone or ''
        data['customer_id_card'] = contract.customer_id_card or ''
        data['customer_address'] = contract.customer_address or ''
        data['customer_email'] = ''  # Not in contract model yet

        # Car data
        data['car_brand'] = contract.car_brand or ''
        data['car_model'] = contract.car_model or ''
        data['car_year'] = str(contract.car_year) if contract.car_year else ''
        data['car_color'] = contract.car_color or ''
        data['car_vin'] = contract.car_vin or ''
        data['car_license_plate'] = contract.car_license_plate or ''
        data['car_price'] = str(int(contract.car_price))

        # Pricing - formatted
        data['car_price_formatted'] = f"{contract.car_price:,.0f}"
        data['discount_amount_formatted'] = f"{contract.discount_amount:,.0f}"
        data['total_amount_formatted'] = f"{contract.total_amount:,.0f}"
        data['vat_amount_formatted'] = f"{contract.vat_amount:,.0f}"
        data['final_amount_formatted'] = f"{contract.final_amount:,.0f}"
        data['deposit_amount_formatted'] = f"{contract.deposit_amount:,.0f}"
        data['paid_amount_formatted'] = f"{contract.paid_amount:,.0f}"
        data['remaining_amount_formatted'] = f"{contract.remaining_amount:,.0f}"

        # Contract data
        data['contract_code'] = contract.contract_code or ''

        if contract.created_at:
            if isinstance(contract.created_at, str):
                # SQLite returns string
                data['contract_date'] = contract.created_at[:10]
                # Convert to DD/MM/YYYY
                try:
                    parts = contract.created_at[:10].split('-')
                    data['contract_date_vn'] = f"{parts[2]}/{parts[1]}/{parts[0]}"
                except:
                    data['contract_date_vn'] = contract.created_at[:10]
            else:
                data['contract_date'] = contract.created_at.strftime('%Y-%m-%d')
                data['contract_date_vn'] = contract.created_at.strftime('%d/%m/%Y')
        else:
            data['contract_date'] = datetime.now().strftime('%Y-%m-%d')
            data['contract_date_vn'] = datetime.now().strftime('%d/%m/%Y')

        # Creator name
        if self.user_repo and contract.created_by:
            creator = self.user_repo.get_by_id(contract.created_by)
            data['created_by_name'] = getattr(creator, 'full_name', 'N/A') if creator else 'N/A'
        else:
            data['created_by_name'] = 'N/A'

        # Approver name
        if self.user_repo and contract.approved_by:
            approver = self.user_repo.get_by_id(contract.approved_by)
            data['approved_by_name'] = getattr(approver, 'full_name', 'N/A') if approver else 'N/A'
        else:
            data['approved_by_name'] = 'N/A'

        # Delivery
        if contract.delivery_date:
            if isinstance(contract.delivery_date, str):
                # SQLite returns string
                if len(contract.delivery_date) >= 10:
                    data['delivery_date'] = contract.delivery_date[:10]
                else:
                    data['delivery_date'] = contract.delivery_date
            else:
                data['delivery_date'] = contract.delivery_date.strftime('%d/%m/%Y')
        else:
            data['delivery_date'] = ''
        data['delivery_location'] = contract.delivery_location or ''

        # Company (default values)
        data['company_name'] = 'CÔNG TY TNHH SHOWROOM Ô TÔ'
        data['company_address'] = '123 Đường ABC, Quận 1, TP.HCM'
        data['company_phone'] = '028-12345678'
        data['company_tax_code'] = '0123456789'

        return data

    def render_contract(
        self,
        contract_id: int,
        template_id: int = None
    ) -> TemplateResult:
        """Render contract with template.

        Args:
            contract_id: Contract ID
            template_id: Template ID (None = use default)

        Returns:
            TemplateResult with rendered HTML
        """
        if not self.contract_repo:
            return TemplateResult.fail("Contract repository not available")

        # Get contract
        contract = self.contract_repo.get_by_id(contract_id)
        if not contract:
            return TemplateResult.fail("Hợp đồng không tồn tại")

        # Get template
        if template_id:
            template = self.template_repo.get_by_id(template_id)
        else:
            template = self.template_repo.get_default()

        if not template:
            return TemplateResult.fail("Không tìm thấy mẫu hợp đồng")

        # Get contract data
        data = self._get_contract_data(contract)

        # Render
        try:
            html = template.render(data)
            return TemplateResult.ok("Render thành công", {
                'html': html,
                'template_name': template.template_name
            })
        except Exception as e:
            return TemplateResult.fail(f"Lỗi render: {str(e)}")

    def preview_template(
        self,
        template_id: int,
        sample_data: Dict[str, Any] = None
    ) -> TemplateResult:
        """Preview template with sample data.

        Args:
            template_id: Template ID
            sample_data: Optional sample data (uses defaults if None)

        Returns:
            TemplateResult with rendered HTML
        """
        template = self.template_repo.get_by_id(template_id)
        if not template:
            return TemplateResult.fail("Mẫu không tồn tại")

        # Use sample data or defaults
        if sample_data is None:
            sample_data = self._get_sample_data()

        try:
            html = template.render(sample_data)
            return TemplateResult.ok("Preview thành công", {'html': html})
        except Exception as e:
            return TemplateResult.fail(f"Lỗi preview: {str(e)}")

    def _get_sample_data(self) -> Dict[str, Any]:
        """Get sample data for preview.

        Returns:
            Dictionary of sample values
        """
        return {
            'customer_name': 'Nguyễn Văn A',
            'customer_phone': '0909123456',
            'customer_id_card': '123456789012',
            'customer_address': '123 Đường ABC, Quận 1, TP.HCM',
            'customer_email': 'khachhang@example.com',
            'car_brand': 'Toyota',
            'car_model': 'Camry',
            'car_year': '2024',
            'car_color': 'Đen',
            'car_vin': 'ABC123456789XYZ',
            'car_license_plate': '51A-12345',
            'car_price': '1000000000',
            'car_price_formatted': '1.000.000.000',
            'discount_amount_formatted': '50.000.000',
            'total_amount_formatted': '950.000.000',
            'vat_amount_formatted': '95.000.000',
            'final_amount_formatted': '1.045.000.000',
            'deposit_amount_formatted': '100.000.000',
            'paid_amount_formatted': '1.045.000.000',
            'remaining_amount_formatted': '0',
            'contract_code': 'HD000001',
            'contract_date': '2024-01-15',
            'contract_date_vn': '15/01/2024',
            'created_by_name': 'Nhân viên bán hàng',
            'approved_by_name': 'Quản lý',
            'delivery_date': '20/01/2024',
            'delivery_location': 'Showroom ABC',
            'company_name': 'CÔNG TY TNHH SHOWROOM Ô TÔ',
            'company_address': '123 Đường ABC, Quận 1, TP.HCM',
            'company_phone': '028-12345678',
            'company_tax_code': '0123456789',
        }

    def validate_template(self, template_content: str) -> TemplateResult:
        """Validate template content.

        Args:
            template_content: HTML template content

        Returns:
            TemplateResult with validation info
        """
        errors = []
        warnings = []

        # Check for balanced braces
        open_count = template_content.count('{{')
        close_count = template_content.count('}}')

        if open_count != close_count:
            errors.append(f"Lỗi cú pháp: Có {open_count} '{{{{' và {close_count} '}}'")

        # Extract variables
        import re
        pattern = r'\{\{(\w+)\}\}'
        variables = set(re.findall(pattern, template_content))

        # Check for unknown variables
        valid_vars = {v.name for v in TemplateVariable.get_all_variables()}
        unknown = variables - valid_vars

        if unknown:
            warnings.append(f"Biến không xác định: {', '.join(unknown)}")

        # Check for recommended variables
        recommended = ['customer_name', 'car_brand', 'final_amount_formatted']
        missing = [v for v in recommended if v not in variables]

        if missing:
            warnings.append(f"Nên thêm các biến: {', '.join(missing)}")

        if errors:
            return TemplateResult.fail("; ".join(errors), {
                'errors': errors,
                'warnings': warnings,
                'variables': list(variables)
            })

        return TemplateResult.ok("Template hợp lệ", {
            'errors': errors,
            'warnings': warnings,
            'variables': list(variables)
        })

    def get_available_variables(self) -> List[TemplateVariable]:
        """Get all available template variables.

        Returns:
            List of TemplateVariable
        """
        return TemplateVariable.get_all_variables()

    def create_template(
        self,
        data: Dict[str, Any],
        created_by: int = None
    ) -> TemplateResult:
        """Create new template.

        Args:
            data: Template data
            created_by: Creator user ID

        Returns:
            TemplateResult with new template ID
        """
        # Validate
        template = ContractTemplate.from_dict(data)
        is_valid, error = template.validate()

        if not is_valid:
            return TemplateResult.fail(error)

        # Check code unique
        if self.template_repo.exists(template.template_code):
            return TemplateResult.fail(f"Mã mẫu '{template.template_code}' đã tồn tại")

        # Validate content
        validation = self.validate_template(template.template_content)
        if not validation.success:
            return validation

        # Create
        data['created_by'] = created_by
        try:
            template_id = self.template_repo.create(data)

            # Set as default if first template
            if template.is_default or not self.template_repo.get_default():
                self.template_repo.set_default(template_id)

            return TemplateResult.ok("Tạo mẫu thành công", {'template_id': template_id})
        except Exception as e:
            return TemplateResult.fail(f"Lỗi tạo mẫu: {str(e)}")

    def update_template(
        self,
        template_id: int,
        data: Dict[str, Any]
    ) -> TemplateResult:
        """Update template.

        Args:
            template_id: Template ID
            data: Updated data

        Returns:
            TemplateResult
        """
        template = self.template_repo.get_by_id(template_id)
        if not template:
            return TemplateResult.fail("Mẫu không tồn tại")

        # Validate content if provided
        if 'template_content' in data:
            validation = self.validate_template(data['template_content'])
            if not validation.success:
                return validation

        # Update
        try:
            success = self.template_repo.update(template_id, data)

            if success and data.get('is_default'):
                self.template_repo.set_default(template_id)

            return TemplateResult.ok("Cập nhật thành công") if success else TemplateResult.fail("Cập nhật thất bại")
        except Exception as e:
            return TemplateResult.fail(f"Lỗi cập nhật: {str(e)}")

    def clone_template(
        self,
        template_id: int,
        new_code: str,
        created_by: int = None
    ) -> TemplateResult:
        """Clone template.

        Args:
            template_id: Source template ID
            new_code: New template code
            created_by: Creator user ID

        Returns:
            TemplateResult with new template ID
        """
        if self.template_repo.exists(new_code):
            return TemplateResult.fail(f"Mã mẫu '{new_code}' đã tồn tại")

        new_id = self.template_repo.clone(template_id, new_code, created_by)

        if new_id:
            return TemplateResult.ok("Nhân bản thành công", {'template_id': new_id})
        else:
            return TemplateResult.fail("Nhân bản thất bại")

    def delete_template(self, template_id: int, hard: bool = False) -> TemplateResult:
        """Delete template.

        Args:
            template_id: Template ID
            hard: Hard delete if True, soft delete otherwise

        Returns:
            TemplateResult
        """
        template = self.template_repo.get_by_id(template_id)
        if not template:
            return TemplateResult.fail("Mẫu không tồn tại")

        # Prevent deleting default template
        if template.is_default and not hard:
            return TemplateResult.fail("Không thể xóa mẫu mặc định. Vui lòng đặt mẫu khác làm mặc định trước.")

        try:
            success = self.template_repo.delete(template_id, soft=not hard)
            return TemplateResult.ok("Xóa thành công") if success else TemplateResult.fail("Xóa thất bại")
        except Exception as e:
            return TemplateResult.fail(f"Lỗi xóa: {str(e)}")

    def list_templates(self, active_only: bool = True) -> List[ContractTemplate]:
        """List all templates.

        Args:
            active_only: Only active templates

        Returns:
            List of ContractTemplate
        """
        return self.template_repo.get_all(active_only=active_only)
