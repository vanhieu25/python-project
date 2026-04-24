"""
Template Repository Module
Data access for contract templates.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime

from database.db_helper import DatabaseHelper
from models.contract_template import ContractTemplate


class TemplateRepository:
    """Repository for contract template data access."""

    def __init__(self, db: DatabaseHelper):
        """Initialize repository.

        Args:
            db: DatabaseHelper instance
        """
        self.db = db

    def create(self, template_data: Dict[str, Any]) -> int:
        """Create new template.

        Args:
            template_data: Template data dictionary

        Returns:
            ID of created template
        """
        query = """
            INSERT INTO contract_templates (
                template_code, template_name, template_content,
                description, is_default, is_active, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        params = (
            template_data.get('template_code'),
            template_data.get('template_name'),
            template_data.get('template_content', ''),
            template_data.get('description'),
            1 if template_data.get('is_default') else 0,
            1 if template_data.get('is_active', True) else 0,
            template_data.get('created_by')
        )

        return self.db.execute(query, params)

    def get_by_id(self, template_id: int) -> Optional[ContractTemplate]:
        """Get template by ID.

        Args:
            template_id: Template ID

        Returns:
            ContractTemplate instance or None
        """
        query = "SELECT * FROM contract_templates WHERE id = ?"
        row = self.db.fetch_one(query, (template_id,))
        return ContractTemplate.from_dict(row)

    def get_by_code(self, template_code: str) -> Optional[ContractTemplate]:
        """Get template by code.

        Args:
            template_code: Template code (e.g., 'CONTRACT_DEFAULT')

        Returns:
            ContractTemplate instance or None
        """
        query = "SELECT * FROM contract_templates WHERE template_code = ?"
        row = self.db.fetch_one(query, (template_code,))
        return ContractTemplate.from_dict(row)

    def get_default(self) -> Optional[ContractTemplate]:
        """Get default template.

        Returns:
            Default ContractTemplate or None
        """
        query = """
            SELECT * FROM contract_templates
            WHERE is_default = 1 AND is_active = 1
            ORDER BY id LIMIT 1
        """
        row = self.db.fetch_one(query)
        return ContractTemplate.from_dict(row)

    def get_all(
        self,
        active_only: bool = True,
        category: str = None
    ) -> List[ContractTemplate]:
        """Get all templates.

        Args:
            active_only: Only return active templates
            category: Optional filter by category

        Returns:
            List of ContractTemplate instances
        """
        query = "SELECT * FROM contract_templates WHERE 1=1"
        params = []

        if active_only:
            query += " AND is_active = 1"

        query += " ORDER BY is_default DESC, template_name"

        rows = self.db.fetch_all(query, tuple(params))
        return [ContractTemplate.from_dict(row) for row in rows if row]

    def update(self, template_id: int, data: Dict[str, Any]) -> bool:
        """Update template.

        Args:
            template_id: Template ID
            data: Updated data dictionary

        Returns:
            True if successful
        """
        allowed_fields = [
            'template_code', 'template_name', 'template_content',
            'description', 'is_default', 'is_active'
        ]

        fields = []
        params = []

        for field in allowed_fields:
            if field in data:
                fields.append(f"{field} = ?")
                params.append(data[field])

        if not fields:
            return False

        # Add updated_at
        fields.append("updated_at = ?")
        params.append(datetime.now())

        query = f"UPDATE contract_templates SET {', '.join(fields)} WHERE id = ?"
        params.append(template_id)

        try:
            self.db.execute(query, tuple(params))
            return True
        except Exception:
            return False

    def delete(self, template_id: int, soft: bool = True) -> bool:
        """Delete template.

        Args:
            template_id: Template ID
            soft: Soft delete (set inactive) or hard delete

        Returns:
            True if successful
        """
        if soft:
            return self.update(template_id, {'is_active': False})
        else:
            query = "DELETE FROM contract_templates WHERE id = ?"
            try:
                self.db.execute(query, (template_id,))
                return True
            except Exception:
                return False

    def set_default(self, template_id: int) -> bool:
        """Set template as default.

        Args:
            template_id: Template ID to set as default

        Returns:
            True if successful
        """
        try:
            # Clear existing default
            self.db.execute(
                "UPDATE contract_templates SET is_default = 0 WHERE is_default = 1"
            )

            # Set new default
            self.db.execute(
                "UPDATE contract_templates SET is_default = 1 WHERE id = ?",
                (template_id,)
            )
            return True
        except Exception:
            return False

    def clone(self, template_id: int, new_code: str, created_by: int = None) -> Optional[int]:
        """Clone existing template.

        Args:
            template_id: Source template ID
            new_code: New template code
            created_by: User creating the clone

        Returns:
            ID of new template or None
        """
        source = self.get_by_id(template_id)
        if not source:
            return None

        clone_data = {
            'template_code': new_code,
            'template_name': f"{source.template_name} (Copy)",
            'template_content': source.template_content,
            'description': source.description,
            'is_default': False,
            'is_active': True,
            'created_by': created_by
        }

        return self.create(clone_data)

    def exists(self, template_code: str) -> bool:
        """Check if template code exists.

        Args:
            template_code: Template code to check

        Returns:
            True if exists
        """
        query = "SELECT 1 FROM contract_templates WHERE template_code = ? LIMIT 1"
        result = self.db.fetch_one(query, (template_code,))
        return result is not None
