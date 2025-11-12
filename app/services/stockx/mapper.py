"""
StockX API response mapper.
Transforms raw API responses into domain models.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.exceptions import APIClientException
from app.domain import (
    Product,
    Variant,
    Listing,
    MarketData,
    ProductFactory,
    VariantFactory,
    ListingFactory,
    MarketDataFactory,
)


class StockXMapper:
    """Maps StockX API responses to domain models."""

    @staticmethod
    def to_product(api_response: Dict[str, Any]) -> Product:
        """
        Transform StockX product API response to Product domain model.

        Args:
            api_response: Raw API response containing products array

        Returns:
            Product domain model instance

        Raises:
            APIClientException: If required fields are missing or response is invalid
        """
        try:
            # Extract products array
            products = api_response.get("products", [])
            if not products:
                raise APIClientException("No products found in API response")

            # Get first product from paginated response
            product_data = products[0]

            # Extract product attributes
            product_attrs = product_data.get("productAttributes", {})

            # Prepare data dictionary for factory
            factory_data = {
                "product_id": product_data["productId"],
                "title": product_data["title"],
                "brand": product_data["brand"],
                "product_type": product_data.get("productType"),
                "style_id": product_data["styleId"],
                "url_key": product_data.get("urlKey"),
                "retail_price": product_attrs.get("retailPrice"),
                "release_date": product_attrs.get("releaseDate"),
            }

            # Use factory to create domain model
            product = ProductFactory.from_stockx_api(factory_data)
            return product

        except KeyError as e:
            raise APIClientException(f"Missing required field in product API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming product data: {e}")

    @staticmethod
    def to_product_from_single_response(api_response: Dict[str, Any]) -> Product:
        """
        Transform single product API response to Product domain model.

        This method handles the response from /v2/catalog/products/{productId} endpoint,
        which returns a single product object directly (not in a products array).

        Args:
            api_response: Raw API response for a single product

        Returns:
            Product domain model instance

        Raises:
            APIClientException: If required fields are missing or response is invalid
        """
        try:
            # Extract product attributes
            product_attrs = api_response.get("productAttributes", {})

            # Prepare data dictionary for factory
            factory_data = {
                "product_id": api_response["productId"],
                "title": api_response["title"],
                "brand": api_response["brand"],
                "product_type": api_response.get("productType"),
                "style_id": api_response["styleId"],
                "url_key": api_response.get("urlKey"),
                "retail_price": product_attrs.get("retailPrice"),
                "release_date": product_attrs.get("releaseDate"),
            }

            # Use factory to create domain model
            product = ProductFactory.from_stockx_api(factory_data)
            return product

        except KeyError as e:
            raise APIClientException(f"Missing required field in product API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming product data: {e}")

    @staticmethod
    def to_variant(variant_data: Dict[str, Any]) -> Variant:
        """
        Transform StockX variant API response to Variant domain model.

        Args:
            variant_data: Raw variant data from API

        Returns:
            Variant domain model instance

        Raises:
            APIClientException: If required fields are missing
        """
        try:
            # Extract UPC from gtins array (find where type="UPC")
            upc = None
            gtins = variant_data.get("gtins", [])
            for gtin in gtins:
                if gtin.get("type") == "UPC":
                    upc = gtin.get("identifier")
                    break

            # Prepare data dictionary for factory
            factory_data = {
                "variant_id": variant_data["variantId"],
                "product_id": variant_data["productId"],
                "variant_name": variant_data["variantName"],
                "variant_value": variant_data["variantValue"],
                "upc": upc,
            }

            # Use factory to create domain model
            variant = VariantFactory.from_stockx_api(factory_data)
            return variant

        except KeyError as e:
            raise APIClientException(f"Missing required field in variant API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming variant data: {e}")

    @staticmethod
    def to_market_data(market_data_response: Dict[str, Any]) -> MarketData:
        """
        Transform StockX market data API response to MarketData domain model.

        Args:
            market_data_response: Raw market data from API

        Returns:
            MarketData domain model instance (immutable value object)

        Raises:
            APIClientException: If response is invalid
        """
        try:
            # Use factory to create domain model
            market_data = MarketDataFactory.from_stockx_api(market_data_response)
            return market_data

        except Exception as e:
            raise APIClientException(f"Error transforming market data: {e}")

    @staticmethod
    def to_listing(listing_data: Dict[str, Any]) -> Listing:
        """
        Transform a single StockX listing to Listing domain model.

        Args:
            listing_data: Raw listing data from API

        Returns:
            Listing domain model instance

        Raises:
            APIClientException: If required fields are missing
        """
        try:
            # Helper to parse datetime strings
            def to_datetime(value):
                if value is None:
                    return None
                try:
                    return datetime.fromisoformat(value.replace('Z', '+00:00'))
                except (ValueError, TypeError, AttributeError):
                    return None

            ask = listing_data.get("ask", {})
            product = listing_data.get("product", {})
            variant = listing_data.get("variant", {})
            batch = listing_data.get("batch", {})

            # Prepare data dictionary for factory
            factory_data = {
                "listing_id": listing_data.get("listingId"),
                "amount": listing_data.get("amount"),
                "currency_code": listing_data.get("currencyCode", "USD"),
                "status": listing_data.get("status"),
                "inventory_type": listing_data.get("inventoryType"),
                "created_at": to_datetime(listing_data.get("createdAt")),
                "updated_at": to_datetime(listing_data.get("updatedAt")),

                # Ask details
                "ask_id": ask.get("askId"),
                "ask_created_at": to_datetime(ask.get("askCreatedAt")),
                "ask_updated_at": to_datetime(ask.get("askUpdatedAt")),
                "ask_expires_at": to_datetime(ask.get("askExpiresAt")),

                # Product details
                "product_id": product.get("productId"),
                "product_name": product.get("productName"),
                "style_id": product.get("styleId"),

                # Variant details
                "variant_id": variant.get("variantId"),
                "variant_name": variant.get("variantName"),
                "variant_value": variant.get("variantValue"),

                # Batch details
                "batch_id": batch.get("batchId"),
                "task_id": batch.get("taskId"),
            }

            # Use factory to create domain model
            listing = ListingFactory.from_stockx_api(factory_data)
            return listing

        except Exception as e:
            raise APIClientException(f"Error transforming listing data: {e}")

    @staticmethod
    def extract_upc(gtins: list) -> Optional[str]:
        """
        Extract UPC identifier from gtins array.

        Args:
            gtins: List of GTIN objects from API response

        Returns:
            UPC identifier string or None if not found
        """
        for gtin in gtins:
            if gtin.get("type") == "UPC":
                return gtin.get("identifier")
        return None

    @staticmethod
    def to_create_batch_listings_response(api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform StockX create batch listings API response to structured dictionary.

        Args:
            api_response: Raw API response containing create batch listings data

        Returns:
            Dictionary with create batch listings data
        """
        try:
            return {
                "batch_id": api_response.get("batchId"),
                "status": api_response.get("status"),
                "total_items": api_response.get("totalItems")
            }
        except Exception as e:
            raise APIClientException(f"Error transforming create batch listings data: {e}")