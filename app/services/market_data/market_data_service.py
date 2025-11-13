"""Market data service for fetching and storing sales and pricing data."""
from typing import List, Tuple, Optional, Any
from datetime import datetime, timedelta, timezone
from app.services.external_stockx.service import external_stockx_service
from app.repositories.variant.variant_repository import variant_repository
from app.repositories.sale.sale_repository import sale_repository
from app.repositories.historical_pricing.historical_pricing_repository import historical_pricing_repository
from app.core.exceptions import DatabaseException, APIClientException
from app.core.logging import LoggerMixin
from app.domain.external_market_data.sale import Sale as SaleDomain
from app.domain.external_market_data.historical_sale import HistoricalSale


class MarketDataService(LoggerMixin):
    """Service for managing market data (sales and historical pricing)."""

    def __init__(self):
        super().__init__()
        self.external_stockx_service = external_stockx_service
        self.variant_repo = variant_repository
        self.sale_repo = sale_repository
        self.historical_pricing_repo = historical_pricing_repository

    async def _determine_date_range(self, variant_db_id: str) -> Tuple[Optional[str], str]:
        """
        Determine automatic date range based on existing data.

        Finds the latest date from existing sales and pricing data,
        then sets start_date to one day after the latest date and
        end_date to today.

        Args:
            variant_db_id: MongoDB ID of the variant

        Returns:
            Tuple of (start_date ISO string or None, end_date ISO string)

        Raises:
            DatabaseException: If database query fails
        """
        self.logger.info("Determining automatic date range...")

        # Get latest sale date
        existing_sales = await self.sale_repo.get_by_variant_db_id(variant_db_id)
        latest_sale_date = None
        if existing_sales:
            latest_sale_date = max(sale.sale_date for sale in existing_sales)
            self.logger.info(f"Latest sale date found: {latest_sale_date}")

        # Get latest pricing date
        existing_pricing = await self.historical_pricing_repo.get_by_variant_db_id(variant_db_id)
        latest_pricing_date = None
        if existing_pricing:
            latest_pricing_date = max(pricing.date for pricing in existing_pricing)
            self.logger.info(f"Latest pricing date found: {latest_pricing_date}")

        # Determine the latest date between sales and pricing
        latest_date = None
        if latest_sale_date and latest_pricing_date:
            latest_date = max(latest_sale_date, latest_pricing_date)
        elif latest_sale_date:
            latest_date = latest_sale_date
        elif latest_pricing_date:
            latest_date = latest_pricing_date

        # Set start_date to one day after the latest date (date only, no time)
        if latest_date:
            start_date_dt = latest_date + timedelta(days=1)
            start_date = start_date_dt.date().isoformat()  # Extract date only (YYYY-MM-DD)
            self.logger.info(f"Auto-determined start_date: {start_date} (one day after latest data)")
        else:
            # No existing data, set start_date to None to fetch all available data
            start_date = None
            self.logger.info("No existing data found, start_date set to None (fetch all available data)")

        # Set end_date to today (date only, no time)
        end_date_dt = datetime.now(timezone.utc)
        end_date = end_date_dt.date().isoformat()  # Extract date only (YYYY-MM-DD)
        self.logger.info(f"Auto-determined end_date: {end_date} (today)")

        return start_date, end_date

    async def fetch_and_store_variant_market_data(
        self,
        variant_db_id: str,
        intervals: int = 400,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[SaleDomain], List[HistoricalSale], int, int]:
        """
        Fetch sales and historical pricing from StockX API and store in MongoDB.

        Args:
            variant_db_id: MongoDB ID of the variant
            intervals: Number of data points for historical pricing
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            Tuple of (sales list, pricing list, new sales count, new pricing count)

        Raises:
            ValueError: If variant not found
            APIClientException: If external API fails
            DatabaseException: If database operation fails
        """
        self.logger.info(f"Fetching market data for variant {variant_db_id}")

        # 1. Look up variant by MongoDB ID
        variant = await self.variant_repo.get_by_id(variant_db_id)
        if not variant:
            raise ValueError(f"Variant with ID {variant_db_id} not found")

        variant_id = variant.variant_id
        product_id = variant.product_id
        self.logger.info(f"Found variant: {variant_id}")

        # 2. Auto-determine date range if not provided
        if start_date is None and end_date is None:
            start_date, end_date = await self._determine_date_range(variant_db_id)

        try:
            # 3. Fetch sales from StockX API
            self.logger.info(f"Fetching sales for variant {variant_id}")
            sales_domain = await self.external_stockx_service.get_sales(
                product_id=variant_id,
                is_variant=True
            )
            self.logger.info(f"Fetched {len(sales_domain)} sales from API")

            # 4. Fetch historical pricing from StockX API
            self.logger.info(f"Fetching historical pricing for variant {variant_id}")
            pricing_domain = await self.external_stockx_service.get_historical_sales(
                product_id=variant_id,
                is_variant=True,
                intervals=intervals,
                start_date=start_date,
                end_date=end_date
            )
            self.logger.info(f"Fetched {len(pricing_domain)} pricing records from API")

            # 5. Filter out existing sales
            new_sales_data = []
            filtered_sales_domain = []
            for sale in sales_domain:
                exists = await self.sale_repo.sale_exists(
                    variant_db_id=variant_db_id,
                    sale_date=sale.created_at,
                    amount=float(sale.amount.amount)
                )
                if not exists:
                    new_sales_data.append({
                        "variant_db_id": variant_db_id,
                        "variant_id": variant_id,
                        "product_id": product_id,
                        "sale_date": sale.created_at,
                        "amount": float(sale.amount.amount),
                        "currency_code": sale.amount.currency_code,
                        "size": sale.size,
                        "order_type": sale.order_type,
                        "is_variant": sale.is_variant
                    })
                    filtered_sales_domain.append(sale)

            # 6. Filter out existing historical pricing
            new_pricing_data = []
            filtered_pricing_domain = []
            for pricing in pricing_domain:
                exists = await self.historical_pricing_repo.pricing_exists(
                    variant_db_id=variant_db_id,
                    date=pricing.date
                )
                if not exists:
                    new_pricing_data.append({
                        "variant_db_id": variant_db_id,
                        "variant_id": variant_id,
                        "product_id": product_id,
                        "date": pricing.date,
                        "price": pricing.price,
                        "is_variant": pricing.is_variant
                    })
                    filtered_pricing_domain.append(pricing)

            # 7. Bulk insert new records
            self.logger.info(f"Inserting {len(new_sales_data)} new sales")
            await self.sale_repo.bulk_create(new_sales_data)

            self.logger.info(f"Inserting {len(new_pricing_data)} new pricing records")
            await self.historical_pricing_repo.bulk_create(new_pricing_data)

            self.logger.info(
                f"Successfully stored {len(new_sales_data)} sales and "
                f"{len(new_pricing_data)} pricing records for variant {variant_id}"
            )

            # 8. Return domain models (only newly stored ones)
            return (
                filtered_sales_domain,
                filtered_pricing_domain,
                len(new_sales_data),
                len(new_pricing_data)
            )

        except APIClientException as e:
            self.logger.error(f"Failed to fetch data from StockX API: {e}")
            raise
        except DatabaseException as e:
            self.logger.error(f"Database operation failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise DatabaseException(f"Failed to fetch and store market data: {e}")

    async def get_sales_by_variant(
        self,
        variant_db_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[Any], Any, Any]:
        """
        Get sales data for a variant from the database.

        Args:
            variant_db_id: MongoDB ID of the variant
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            Tuple of (List of Sale DB models, Variant model, Product model)

        Raises:
            ValueError: If variant or product not found
            DatabaseException: If database operation fails
        """
        self.logger.info(f"Fetching sales for variant {variant_db_id}")

        # Look up variant by MongoDB ID
        variant = await self.variant_repo.get_by_id(variant_db_id)
        if not variant:
            raise ValueError(f"Variant with ID {variant_db_id} not found")

        # Fetch the linked product
        await variant.fetch_link(variant.__class__.product)
        product = variant.product
        if not product:
            raise ValueError(f"Product not found for variant {variant_db_id}")

        try:
            # Parse dates if provided
            start_date_dt = None
            end_date_dt = None
            if start_date:
                start_date_dt = datetime.fromisoformat(start_date)
            if end_date:
                end_date_dt = datetime.fromisoformat(end_date)

            # Fetch sales from database
            sales = await self.sale_repo.get_by_variant_db_id(
                variant_db_id=variant_db_id,
                start_date=start_date_dt,
                end_date=end_date_dt
            )

            self.logger.info(f"Found {len(sales)} sales for variant {variant.variant_id}")
            return sales, variant, product

        except DatabaseException as e:
            self.logger.error(f"Database operation failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise DatabaseException(f"Failed to fetch sales: {e}")

    async def get_historical_pricing_by_variant(
        self,
        variant_db_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[List[Any], Any, Any]:
        """
        Get historical pricing data for a variant from the database.

        Args:
            variant_db_id: MongoDB ID of the variant
            start_date: Optional start date filter (ISO format)
            end_date: Optional end date filter (ISO format)

        Returns:
            Tuple of (List of HistoricalPricing DB models, Variant model, Product model)

        Raises:
            ValueError: If variant or product not found
            DatabaseException: If database operation fails
        """
        self.logger.info(f"Fetching historical pricing for variant {variant_db_id}")

        # Look up variant by MongoDB ID
        variant = await self.variant_repo.get_by_id(variant_db_id)
        if not variant:
            raise ValueError(f"Variant with ID {variant_db_id} not found")

        # Fetch the linked product
        await variant.fetch_link(variant.__class__.product)
        product = variant.product
        if not product:
            raise ValueError(f"Product not found for variant {variant_db_id}")

        try:
            # Parse dates if provided
            start_date_dt = None
            end_date_dt = None
            if start_date:
                start_date_dt = datetime.fromisoformat(start_date)
            if end_date:
                end_date_dt = datetime.fromisoformat(end_date)

            # Fetch historical pricing from database
            pricing = await self.historical_pricing_repo.get_by_variant_db_id(
                variant_db_id=variant_db_id,
                start_date=start_date_dt,
                end_date=end_date_dt
            )

            self.logger.info(f"Found {len(pricing)} pricing records for variant {variant.variant_id}")
            return pricing, variant, product

        except DatabaseException as e:
            self.logger.error(f"Database operation failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error: {e}")
            raise DatabaseException(f"Failed to fetch historical pricing: {e}")


# Singleton instance
market_data_service = MarketDataService()
