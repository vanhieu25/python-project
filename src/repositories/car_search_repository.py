"""
Car Search Repository Module
Advanced search and filtering for cars.
"""

from typing import List, Optional, Dict, Any, Tuple
from dataclasses import dataclass
from ..database.db_helper import DatabaseHelper
from ..models.car import Car


@dataclass
class CarSearchFilter:
    """Filter criteria for car search."""
    keyword: Optional[str] = None
    brands: List[str] = None
    models: List[str] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    price_from: Optional[float] = None
    price_to: Optional[float] = None
    colors: List[str] = None
    statuses: List[str] = None
    transmissions: List[str] = None
    fuel_types: List[str] = None

    def __post_init__(self):
        if self.brands is None:
            self.brands = []
        if self.models is None:
            self.models = []
        if self.colors is None:
            self.colors = []
        if self.statuses is None:
            self.statuses = []
        if self.transmissions is None:
            self.transmissions = []
        if self.fuel_types is None:
            self.fuel_types = []


class CarSearchRepository:
    """Repository for advanced car search."""

    def __init__(self, db: DatabaseHelper):
        self.db = db

    def search(self, filter_criteria: CarSearchFilter,
               sort_by: str = 'created_at',
               sort_order: str = 'DESC',
               page: int = 1,
               per_page: int = 20) -> Tuple[List[Car], int]:
        """Search cars with filters.

        Args:
            filter_criteria: Search filter criteria
            sort_by: Column to sort by
            sort_order: ASC or DESC
            page: Page number (1-based)
            per_page: Items per page

        Returns:
            Tuple of (list of cars, total count)
        """
        # Build WHERE clause
        conditions = ["is_deleted = 0"]
        params = []

        # Keyword search
        if filter_criteria.keyword:
            keyword = f"%{filter_criteria.keyword}%"
            conditions.append("""(
                vin LIKE ? OR
                license_plate LIKE ? OR
                brand LIKE ? OR
                model LIKE ?
            )""")
            params.extend([keyword, keyword, keyword, keyword])

        # Brand filter
        if filter_criteria.brands:
            placeholders = ','.join('?' * len(filter_criteria.brands))
            conditions.append(f"brand IN ({placeholders})")
            params.extend(filter_criteria.brands)

        # Model filter
        if filter_criteria.models:
            placeholders = ','.join('?' * len(filter_criteria.models))
            conditions.append(f"model IN ({placeholders})")
            params.extend(filter_criteria.models)

        # Year range
        if filter_criteria.year_from:
            conditions.append("year >= ?")
            params.append(filter_criteria.year_from)
        if filter_criteria.year_to:
            conditions.append("year <= ?")
            params.append(filter_criteria.year_to)

        # Price range
        if filter_criteria.price_from:
            conditions.append("selling_price >= ?")
            params.append(filter_criteria.price_from)
        if filter_criteria.price_to:
            conditions.append("selling_price <= ?")
            params.append(filter_criteria.price_to)

        # Color filter
        if filter_criteria.colors:
            placeholders = ','.join('?' * len(filter_criteria.colors))
            conditions.append(f"color IN ({placeholders})")
            params.extend(filter_criteria.colors)

        # Status filter
        if filter_criteria.statuses:
            placeholders = ','.join('?' * len(filter_criteria.statuses))
            conditions.append(f"status IN ({placeholders})")
            params.extend(filter_criteria.statuses)

        # Transmission filter
        if filter_criteria.transmissions:
            placeholders = ','.join('?' * len(filter_criteria.transmissions))
            conditions.append(f"transmission IN ({placeholders})")
            params.extend(filter_criteria.transmissions)

        # Fuel type filter
        if filter_criteria.fuel_types:
            placeholders = ','.join('?' * len(filter_criteria.fuel_types))
            conditions.append(f"fuel_type IN ({placeholders})")
            params.extend(filter_criteria.fuel_types)

        # Build query
        where_clause = " AND ".join(conditions)

        # Count query
        count_query = f"SELECT COUNT(*) as count FROM cars WHERE {where_clause}"
        count_result = self.db.fetch_one(count_query, tuple(params))
        total_count = count_result['count'] if count_result else 0

        # Main query
        allowed_sort = ['vin', 'license_plate', 'brand', 'model', 'year',
                       'selling_price', 'purchase_price', 'created_at', 'status']
        if sort_by not in allowed_sort:
            sort_by = 'created_at'

        sort_order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'

        query = f"""
            SELECT * FROM cars
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
        """
        offset = (page - 1) * per_page
        params.extend([per_page, offset])

        rows = self.db.fetch_all(query, tuple(params))
        cars = [Car.from_dict(row) for row in rows if row]

        return cars, total_count

    def fts_search(self, keyword: str) -> List[Car]:
        """Full-text search using FTS5.

        Args:
            keyword: Search keyword

        Returns:
            List of matching cars
        """
        query = """
            SELECT c.* FROM cars c
            JOIN cars_fts fts ON c.id = fts.rowid
            WHERE cars_fts MATCH ?
            AND c.is_deleted = 0
            ORDER BY rank
        """
        rows = self.db.fetch_all(query, (keyword,))
        return [Car.from_dict(row) for row in rows if row]

    def get_filter_options(self) -> Dict[str, List]:
        """Get available filter options.

        Returns:
            Dictionary of filter options
        """
        return {
            'brands': self._get_distinct_values('brand'),
            'models': self._get_distinct_values('model'),
            'colors': self._get_distinct_values('color'),
            'statuses': self._get_distinct_values('status'),
            'transmissions': self._get_distinct_values('transmission'),
            'fuel_types': self._get_distinct_values('fuel_type'),
            'years': self._get_numeric_values('year'),
        }

    def _get_distinct_values(self, column: str) -> List[str]:
        """Get distinct values for a column."""
        query = f"""
            SELECT DISTINCT {column} as value
            FROM cars
            WHERE {column} IS NOT NULL AND is_deleted = 0
            ORDER BY {column}
        """
        rows = self.db.fetch_all(query)
        return [row['value'] for row in rows if row['value']]

    def _get_numeric_values(self, column: str) -> List[int]:
        """Get distinct numeric values sorted."""
        query = f"""
            SELECT DISTINCT {column} as value
            FROM cars
            WHERE {column} IS NOT NULL AND is_deleted = 0
            ORDER BY {column} DESC
        """
        rows = self.db.fetch_all(query)
        return [row['value'] for row in rows if row['value'] is not None]

    def get_price_range(self) -> Tuple[Optional[float], Optional[float]]:
        """Get min and max selling prices."""
        query = """
            SELECT
                MIN(selling_price) as min_price,
                MAX(selling_price) as max_price
            FROM cars
            WHERE is_deleted = 0 AND selling_price IS NOT NULL
        """
        result = self.db.fetch_one(query)
        return (
            result['min_price'] if result else None,
            result['max_price'] if result else None
        )

    def quick_search(self, keyword: str, limit: int = 20) -> List[Car]:
        """Quick search for autocomplete.

        Args:
            keyword: Search keyword
            limit: Maximum results

        Returns:
            List of matching cars
        """
        search_term = f"%{keyword}%"
        query = """
            SELECT * FROM cars
            WHERE is_deleted = 0
            AND (vin LIKE ? OR license_plate LIKE ? OR brand LIKE ? OR model LIKE ?)
            ORDER BY brand, model
            LIMIT ?
        """
        rows = self.db.fetch_all(query, (search_term, search_term, search_term, search_term, limit))
        return [Car.from_dict(row) for row in rows if row]
