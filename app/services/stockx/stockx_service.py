"""
StockX Service Wrapper.
Orchestrates API calls and transforms responses into structured data.
"""
from typing import List, Tuple, Dict, Any, Optional
from app.services.stockx.api_client import api_client
from app.services.stockx.mapper import StockXMapper
from app.core.logging import LoggerMixin
from app.core.exceptions import APIClientException


class StockXService(LoggerMixin):
    """
    Wrapper service that transforms StockX API responses into structured data.

    This service acts as a facade between the raw API client and your application,
    providing a clean interface that returns structured dictionaries that can be used
    to create domain models or API responses.
    """

    def __init__(self):
        """Initialize the StockX service."""
        self.api_client = api_client
        self.mapper = StockXMapper()

    async def get_product(self, search_param: str) -> Dict[str, Any]:
        """
        Fetch product data from StockX API and transform to structured data.

        Args:
            search_param: Style ID or UPC to search for

        Returns:
            Dictionary with product data

        Raises:
            APIClientException: If API call fails or no products found
        """
        self.logger.info(f"Fetching product data for: {search_param}")

        try:
            # Fetch raw data from API
            api_response = await self.api_client.fetch_product_data(search_param)

            # Transform to structured data
            product = self.mapper.to_product(api_response)

            self.logger.info(
                f"Successfully fetched and transformed product: {product['product_id']} - {product['title']}"
            )

            return product

        except APIClientException as e:
            self.logger.error(f"Failed to fetch product for {search_param}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching product {search_param}: {e}")
            raise APIClientException(f"Failed to fetch product: {e}")

    async def get_variants(self, product_id: str) -> List[Dict[str, Any]]:
        """
        Fetch variant data from StockX API and transform to structured data.

        Args:
            product_id: The StockX product ID

        Returns:
            List of variant dictionaries

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

            # Transform each variant to structured data
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

    async def get_product_with_variants(self, search_param: str) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Fetch both product and its variants in one operation.

        This is a convenience method that fetches the product first,
        then uses the product_id to fetch all variants.

        Args:
            search_param: Style ID or UPC to search for

        Returns:
            Tuple of (product_dict, list of variant_dicts)

        Raises:
            APIClientException: If either API call fails
        """
        self.logger.info(f"Fetching product with variants for: {search_param}")

        try:
            # Fetch product first
            product = await self.get_product(search_param)

            # Fetch variants using product_id
            variants = await self.get_variants(product['product_id'])

            self.logger.info(
                f"Successfully fetched product {product['product_id']} with {len(variants)} variants"
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
    ) -> Dict[str, Any]:
        """
        Fetch market data for a specific product variant.

        Args:
            product_id: StockX product UUID
            variant_id: StockX variant UUID
            currency_code: Currency code for pricing (default: USD)

        Returns:
            Dictionary with market data including bids, asks, and different market types

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

            # Transform to structured data
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
    ) -> List[Dict[str, Any]]:
        """
        Fetch listings from StockX selling API with automatic pagination.

        Args:
            product_id: StockX Product identifier (optional if variant_id provided)
            variant_id: StockX Variant identifier (optional if product_id provided)
            from_date: Filter listings from this date (format: YYYY-MM-DD)
            listing_status: Filter by listing status (default: ACTIVE)
            fetch_all_pages: If True, automatically fetches all pages (default: True)

        Returns:
            List of listing dictionaries

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

                # Transform each listing
                listings = api_response.get("listings", [])
                for listing_data in listings:
                    listing_dict = self.mapper.to_listing(listing_data)
                    all_listings.append(listing_dict)

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


# Singleton instance
stockx_service = StockXService()
