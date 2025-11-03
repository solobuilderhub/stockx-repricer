"""
StockX API response mapper.
Transforms raw API responses into structured dictionaries.
"""
from datetime import datetime
from typing import Dict, Any, Optional
from app.core.exceptions import APIClientException


class StockXMapper:
    """Maps StockX API responses to structured dictionaries."""

    @staticmethod
    def to_product(api_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform StockX product API response to structured product dictionary.

        Args:
            api_response: Raw API response containing products array

        Returns:
            Dictionary with product data

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

            # Parse release date if present
            release_date = None
            if product_attrs.get("releaseDate"):
                try:
                    release_date = datetime.fromisoformat(product_attrs["releaseDate"])
                except (ValueError, TypeError):
                    # If date parsing fails, leave as None
                    pass

            # Get retail price
            retail_price = product_attrs.get("retailPrice")
            if retail_price is not None:
                retail_price = float(retail_price)

            # Create product dictionary
            now = datetime.utcnow()
            product = {
                "product_id": product_data["productId"],
                "title": product_data["title"],
                "brand": product_data["brand"],
                "product_type": product_data.get("productType"),
                "style_id": product_data["styleId"],
                "url_key": product_data.get("urlKey"),
                "retail_price": retail_price,
                "release_date": release_date,
                "created_at": now,
                "updated_at": now
            }

            return product

        except KeyError as e:
            raise APIClientException(f"Missing required field in product API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming product data: {e}")

    @staticmethod
    def to_variant(variant_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform StockX variant API response to structured variant dictionary.

        Args:
            variant_data: Raw variant data from API

        Returns:
            Dictionary with variant data

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

            # Create variant dictionary
            now = datetime.utcnow()
            variant = {
                "variant_id": variant_data["variantId"],
                "product_id": variant_data["productId"],
                "variant_name": variant_data["variantName"],
                "variant_value": variant_data["variantValue"],
                "upc": upc,
                "created_at": now,
                "updated_at": now
            }

            return variant

        except KeyError as e:
            raise APIClientException(f"Missing required field in variant API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming variant data: {e}")

    @staticmethod
    def to_market_data(market_data_response: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform StockX market data API response to structured dictionary.

        Args:
            market_data_response: Raw market data from API

        Returns:
            Dictionary with market data including standard, flex, and direct market data

        Raises:
            APIClientException: If response is invalid
        """
        try:
            now = datetime.utcnow()

            # Extract nested market data objects
            standard_market_data = market_data_response.get("standardMarketData", {})
            flex_market_data = market_data_response.get("flexMarketData", {})
            direct_market_data = market_data_response.get("directMarketData", {})

            # Helper to convert string prices to float
            def to_float(value):
                if value is None:
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None

            market_data = {
                "product_id": market_data_response.get("productId"),
                "variant_id": market_data_response.get("variantId"),
                "currency_code": market_data_response.get("currencyCode"),
                "highest_bid_amount": to_float(market_data_response.get("highestBidAmount")),
                "lowest_ask_amount": to_float(market_data_response.get("lowestAskAmount")),
                "flex_lowest_ask_amount": to_float(market_data_response.get("flexLowestAskAmount")),
                "earn_more_amount": to_float(market_data_response.get("earnMoreAmount")),
                "sell_faster_amount": to_float(market_data_response.get("sellFasterAmount")),

                # Standard market data
                "standard_lowest_ask": to_float(standard_market_data.get("lowestAsk")),
                "standard_highest_bid": to_float(standard_market_data.get("highestBidAmount")),
                "standard_sell_faster": to_float(standard_market_data.get("sellFaster")),
                "standard_earn_more": to_float(standard_market_data.get("earnMore")),
                "standard_beat_us": to_float(standard_market_data.get("beatUS")),

                # Flex market data
                "flex_lowest_ask": to_float(flex_market_data.get("lowestAsk")),
                "flex_highest_bid": to_float(flex_market_data.get("highestBidAmount")),
                "flex_sell_faster": to_float(flex_market_data.get("sellFaster")),
                "flex_earn_more": to_float(flex_market_data.get("earnMore")),
                "flex_beat_us": to_float(flex_market_data.get("beatUS")),

                # Direct market data
                "direct_lowest_ask": to_float(direct_market_data.get("lowestAsk")),
                "direct_highest_bid": to_float(direct_market_data.get("highestBidAmount")),
                "direct_sell_faster": to_float(direct_market_data.get("sellFaster")),
                "direct_earn_more": to_float(direct_market_data.get("earnMore")),
                "direct_beat_us": to_float(direct_market_data.get("beatUS")),

                "created_at": now,
                "updated_at": now
            }

            return market_data

        except Exception as e:
            raise APIClientException(f"Error transforming market data: {e}")

    @staticmethod
    def to_listing(listing_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform a single StockX listing to structured dictionary.

        Args:
            listing_data: Raw listing data from API

        Returns:
            Dictionary with listing data

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

            # Helper to convert string prices to float
            def to_float(value):
                if value is None:
                    return None
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None

            ask = listing_data.get("ask", {})
            product = listing_data.get("product", {})
            variant = listing_data.get("variant", {})
            batch = listing_data.get("batch", {})

            listing_dict = {
                "listing_id": listing_data.get("listingId"),
                "amount": to_float(listing_data.get("amount")),
                "currency_code": listing_data.get("currencyCode"),
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

            return listing_dict

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
