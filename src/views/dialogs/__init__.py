"""
Dialogs package for dialog forms.
"""

from .employee_dialog import EmployeeDialog
from .login_dialog import LoginDialog
from .role_permission_dialog import RolePermissionDialog
from .kpi_dashboard import KPIDashboardScreen
from .kpi_target_dialog import TargetSettingDialog

__all__ = [
    'EmployeeDialog', 'LoginDialog', 'RolePermissionDialog',
    'KPIDashboardScreen', 'TargetSettingDialog'
]
