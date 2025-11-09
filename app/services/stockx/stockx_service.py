"""
StockX Service Wrapper.
Orchestrates API calls and transforms responses into domain models.
"""
from typing import List, Tuple, Dict, Any, Optional
from app.services.stockx.api_client import api_client
from app.services.stockx.mapper import StockXMapper
from app.core.logging import LoggerMixin
from app.core.exceptions import APIClientException
from app.schemas.stockx import CreateBatchListingsRequest
from app.schemas.stockx import UpdateBatchListingsRequest
from app.domain import Product, Variant, Listing, MarketData

class StockXService(LoggerMixin):
    """
    Wrapper service that transforms StockX API responses into domain models.

    This service acts as a facade between the raw API client and your application,
    providing a clean interface that returns domain models for use throughout
    the application.
    """

    def __init__(self):
        """Initialize the StockX service."""
        self.api_client = api_client
        self.mapper = StockXMapper()

    async def get_product(self, search_param: str) -> Product:
        """
        Fetch product data from StockX API and transform to Product domain model.

        Args:
            search_param: Style ID or UPC to search for

        Returns:
            Product domain model instance

        Raises:
            APIClientException: If API call fails or no products found
        """
        self.logger.info(f"Fetching product data for: {search_param}")

        try:
            # Fetch raw data from API
            api_response = await self.api_client.fetch_product_data(search_param)

            # Transform to domain model
            product = self.mapper.to_product(api_response)

            self.logger.info(
                f"Successfully fetched and transformed product: {product.product_id.value} - {product.title}"
            )

            return product

        except APIClientException as e:
            self.logger.error(f"Failed to fetch product for {search_param}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching product {search_param}: {e}")
            raise APIClientException(f"Failed to fetch product: {e}")

    async def get_variants(self, product_id: str) -> List[Variant]:
        """
        Fetch variant data from StockX API and transform to Variant domain models.

        Args:
            product_id: The StockX product ID

        Returns:
            List of Variant domain model instances

        Raises:
            APIClientException: If API call fails
        """
        self.logger.info(f"Fetching variants for product: {product_id}")

        try:
            # Fetch raw data from API
            api_response = await self.api_client.fetch_variant_data(product_id)

            # API returns array of variants directly
            if not isinstance(api_response, list):
                raise APIClientException("Expected variant API response to be a list")

            # Transform each variant to domain model
            variants = [self.mapper.to_variant(variant_data) for variant_data in api_response]

            self.logger.info(
                f"Successfully fetched and transformed {len(variants)} variants for product {product_id}"
            )

            return variants

        except APIClientException as e:
            self.logger.error(f"Failed to fetch variants for product {product_id}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching variants for {product_id}: {e}")
            raise APIClientException(f"Failed to fetch variants: {e}")

    async def get_product_with_variants(self, search_param: str) -> Tuple[Product, List[Variant]]:
        """
        Fetch both product and its variants in one operation.

        This is a convenience method that fetches the product first,
        then uses the product_id to fetch all variants.

        Args:
            search_param: Style ID or UPC to search for

        Returns:
            Tuple of (Product domain model, list of Variant domain models)

        Raises:
            APIClientException: If either API call fails
        """
        self.logger.info(f"Fetching product with variants for: {search_param}")

        try:
            # Fetch product first
            product = await self.get_product(search_param)

            # Fetch variants using product_id
            variants = await self.get_variants(product.product_id.value)

            self.logger.info(
                f"Successfully fetched product {product.product_id.value} with {len(variants)} variants"
            )

            return product, variants

        except APIClientException as e:
            self.logger.error(f"Failed to fetch product with variants for {search_param}: {e}")
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error fetching product with variants for {search_param}: {e}"
            )
            raise APIClientException(f"Failed to fetch product with variants: {e}")

    async def get_market_data(
        self,
        product_id: str,
        variant_id: str,
        currency_code: str = "USD"
    ) -> MarketData:
        """
        Fetch market data for a specific product variant.

        Args:
            product_id: StockX product UUID
            variant_id: StockX variant UUID
            currency_code: Currency code for pricing (default: USD)

        Returns:
            MarketData domain model instance (immutable value object)

        Raises:
            APIClientException: If API call fails
        """
        self.logger.info(
            f"Fetching market data for product {product_id}, variant {variant_id}"
        )

        try:
            # Fetch raw data from API
            api_response = await self.api_client.fetch_market_data(
                product_id, variant_id, currency_code
            )

            # Transform to domain model
            market_data = self.mapper.to_market_data(api_response)

            self.logger.info(
                f"Successfully fetched market data for variant {variant_id}"
            )

            return market_data

        except APIClientException as e:
            self.logger.error(
                f"Failed to fetch market data for product {product_id}, variant {variant_id}: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error fetching market data for {product_id}/{variant_id}: {e}"
            )
            raise APIClientException(f"Failed to fetch market data: {e}")

    async def get_listings(
        self,
        product_id: Optional[str] = None,
        variant_id: Optional[str] = None,
        from_date: Optional[str] = None,
        listing_status: str = "ACTIVE",
        fetch_all_pages: bool = True
    ) -> List[Listing]:
        """
        Fetch listings from StockX selling API with automatic pagination.

        Args:
            product_id: StockX Product identifier (optional if variant_id provided)
            variant_id: StockX Variant identifier (optional if product_id provided)
            from_date: Filter listings from this date (format: YYYY-MM-DD)
            listing_status: Filter by listing status (default: ACTIVE)
            fetch_all_pages: If True, automatically fetches all pages (default: True)

        Returns:
            List of Listing domain model instances

        Raises:
            APIClientException: If API call fails
            ValueError: If neither product_id nor variant_id is provided
        """
        if not product_id and not variant_id:
            raise ValueError("Either product_id or variant_id must be provided")

        self.logger.info(
            f"Fetching listings for product={product_id}, variant={variant_id}, "
            f"fetch_all={fetch_all_pages}"
        )

        all_listings = []
        page_number = 1
        has_next_page = True

        try:
            while has_next_page:
                # Fetch current page
                api_response = await self.api_client.fetch_listings(
                    product_id=product_id,
                    variant_id=variant_id,
                    page_number=page_number,
                    page_size=100,
                    from_date=from_date,
                    listing_status=listing_status
                )

                # Transform each listing to domain model
                listings = api_response.get("listings", [])
                for listing_data in listings:
                    listing = self.mapper.to_listing(listing_data)
                    all_listings.append(listing)

                self.logger.info(
                    f"Fetched page {page_number}: {len(listings)} listings "
                    f"(total so far: {len(all_listings)})"
                )

                # Check if we should continue to next page
                has_next_page = api_response.get("hasNextPage", False) and fetch_all_pages

                if has_next_page:
                    page_number += 1
                else:
                    break

            self.logger.info(
                f"Successfully fetched {len(all_listings)} total listings across {page_number} page(s)"
            )

            return all_listings

        except APIClientException as e:
            self.logger.error(
                f"Failed to fetch listings for product={product_id}, variant={variant_id}: {e}"
            )
            raise
        except Exception as e:
            self.logger.error(
                f"Unexpected error fetching listings for product={product_id}, variant={variant_id}: {e}"
            )
            raise APIClientException(f"Failed to fetch listings: {e}")

    async def create_batch_listings(self, items: CreateBatchListingsRequest) -> Dict[str, Any]:
        """Create batch listings in StockX selling API.

        Args:
            items: List of listings to create

        Returns:
            Batch listings data dictionary
        """
        try:
            api_response = await self.api_client.create_batch_listings(items)
            return self.mapper.to_create_batch_listings_response(api_response)
        except APIClientException as e:
            self.logger.error(f"Failed to create batch listings: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating batch listings: {e}")
            raise APIClientException(f"Failed to create batch listings: {e}")

    async def update_batch_listings(self, items: UpdateBatchListingsRequest) -> Dict[str, Any]:
        """Update batch listings in StockX selling API.

        Args:
            items: List of listings to update

        Returns:
            Batch listings data dictionary
        """
        try:
            api_response = await self.api_client.update_batch_listings(items)
            return self.mapper.to_create_batch_listings_response(api_response)
        except APIClientException as e:
            self.logger.error(f"Failed to update batch listings: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error updating batch listings: {e}")
            raise APIClientException(f"Failed to update batch listings: {e}")

# Singleton instance
stockx_service = StockXService()
