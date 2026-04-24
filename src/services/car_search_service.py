"""
Car Search Service Module
Business logic for car search operations.
"""

from typing import List, Optional, Dict, Any, Tuple
from ..repositories.car_search_repository import CarSearchRepository, CarSearchFilter
from ..models.car import Car


class CarSearchService:
    """Service for car search operations."""

    def __init__(self, search_repository: CarSearchRepository):
        """Initialize search service.

        Args:
            search_repository: Search repository instance
        """
        self.search_repo = search_repository

    def quick_search(self, keyword: str,
                     page: int = 1,
                     per_page: int = 20) -> Tuple[List[Car], int]:
        """Quick search by keyword only.

        Args:
            keyword: Search keyword
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (cars, total count)
        """
        filter_criteria = CarSearchFilter(keyword=keyword)
        return self.search_repo.search(filter_criteria, page=page, per_page=per_page)

    def advanced_search(self,
                        keyword: Optional[str] = None,
                        brands: List[str] = None,
                        models: List[str] = None,
                        year_from: Optional[int] = None,
                        year_to: Optional[int] = None,
                        price_from: Optional[float] = None,
                        price_to: Optional[float] = None,
                        colors: List[str] = None,
                        statuses: List[str] = None,
                        transmissions: List[str] = None,
                        fuel_types: List[str] = None,
                        sort_by: str = 'created_at',
                        sort_order: str = 'DESC',
                        page: int = 1,
                        per_page: int = 20
                        ) -> Tuple[List[Car], int]:
        """Advanced search with multiple filters.

        Returns:
            Tuple of (cars, total count)
        """
        filter_criteria = CarSearchFilter(
            keyword=keyword,
            brands=brands or [],
            models=models or [],
            year_from=year_from,
            year_to=year_to,
            price_from=price_from,
            price_to=price_to,
            colors=colors or [],
            statuses=statuses or [],
            transmissions=transmissions or [],
            fuel_types=fuel_types or []
        )

        return self.search_repo.search(
            filter_criteria,
            sort_by=sort_by,
            sort_order=sort_order,
            page=page,
            per_page=per_page
        )

    def fts_search(self, keyword: str) -> List[Car]:
        """Full-text search.

        Args:
            keyword: Search keyword

        Returns:
            List of matching cars
        """
        return self.search_repo.fts_search(keyword)

    def get_filter_options(self) -> Dict[str, List]:
        """Get available filter options for UI."""
        return self.search_repo.get_filter_options()

    def get_price_range(self) -> Tuple[Optional[float], Optional[float]]:
        """Get min/max price for price slider."""
        return self.search_repo.get_price_range()

    def autocomplete(self, keyword: str, limit: int = 10) -> List[Car]:
        """Autocomplete search.

        Args:
            keyword: Partial keyword
            limit: Maximum results

        Returns:
            List of matching cars
        """
        return self.search_repo.quick_search(keyword, limit)

    def find_similar_cars(self, car_id: int, limit: int = 5) -> List[Car]:
        """Find cars similar to a given car.

        Args:
            car_id: Car ID to compare
            limit: Maximum results

        Returns:
            List of similar cars
        """
        # This would need to get the car first, then search
        # For now, return empty list
        return []

    def search_by_price_range(self, min_price: Optional[float],
                              max_price: Optional[float],
                              page: int = 1,
                              per_page: int = 20) -> Tuple[List[Car], int]:
        """Search by price range only.

        Args:
            min_price: Minimum price
            max_price: Maximum price
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (cars, total count)
        """
        filter_criteria = CarSearchFilter(
            price_from=min_price,
            price_to=max_price
        )
        return self.search_repo.search(
            filter_criteria,
            sort_by='selling_price',
            sort_order='ASC',
            page=page,
            per_page=per_page
        )

    def search_by_year_range(self, year_from: int, year_to: int,
                            page: int = 1,
                            per_page: int = 20) -> Tuple[List[Car], int]:
        """Search by year range.

        Args:
            year_from: Start year
            year_to: End year
            page: Page number
            per_page: Items per page

        Returns:
            Tuple of (cars, total count)
        """
        filter_criteria = CarSearchFilter(
            year_from=year_from,
            year_to=year_to
        )
        return self.search_repo.search(
            filter_criteria,
            sort_by='year',
            sort_order='DESC',
            page=page,
            per_page=per_page
        )
