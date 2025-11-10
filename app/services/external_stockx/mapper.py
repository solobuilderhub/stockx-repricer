"""
External StockX API response mapper.
Transforms raw API responses into domain models.
"""
from typing import Dict, Any, List
from app.core.exceptions import APIClientException
from app.domain.external_market_data import Sale, Bid, Ask, HistoricalSale, SaleFactory, BidFactory, AskFactory, HistoricalSaleFactory


class ExternalStockXMapper:
    """Maps external StockX API responses to domain models."""

    @staticmethod
    def to_sales(api_response: Dict[str, Any], product_id: str, is_variant: bool) -> List[Sale]:
        """
        Transform external API sales response to list of Sale domain models.

        Args:
            api_response: Raw API response from external service
            product_id: The product or variant ID
            is_variant: Whether product_id is a variant ID

        Returns:
            List of Sale domain model instances

        Raises:
            APIClientException: If response is invalid or missing required fields
        """
        try:
            # Navigate through the nested response structure
            data = api_response.get('data', {})
            inner_data = data.get('data', {})
            variant = inner_data.get('variant', {})
            market = variant.get('market', {})
            sales_data = market.get('sales', {})
            edges = sales_data.get('edges', [])

            if not isinstance(edges, list):
                raise APIClientException("Expected 'edges' to be a list in sales response")

            # Transform each edge node to Sale entity
            sales = []
            for edge in edges:
                node = edge.get('node')
                if not node:
                    continue

                try:
                    sale = SaleFactory.from_external_api(node, product_id, is_variant)
                    sales.append(sale)
                except Exception as e:
                    # Log and skip invalid sales, don't fail the entire request
                    print(f"Skipping invalid sale: {e}")
                    continue

            return sales

        except KeyError as e:
            raise APIClientException(f"Missing required field in sales API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming sales data: {e}")

    @staticmethod
    def to_bids(api_response: Dict[str, Any], product_id: str, is_variant: bool) -> List[Bid]:
        """
        Transform external API bids response to list of Bid domain models.

        Args:
            api_response: Raw API response from external service
            product_id: The product or variant ID
            is_variant: Whether product_id is a variant ID

        Returns:
            List of Bid domain model instances

        Raises:
            APIClientException: If response is invalid or missing required fields
        """
        try:
            # Navigate through the nested response structure
            data = api_response.get('data', {})
            inner_data = data.get('data', {})
            variant = inner_data.get('variant', {})
            market = variant.get('market', {})
            price_levels = market.get('priceLevels', {})
            edges = price_levels.get('edges', [])

            if not isinstance(edges, list):
                raise APIClientException("Expected 'edges' to be a list in bids response")

            # Transform each edge node to Bid entity
            bids = []
            for edge in edges:
                node = edge.get('node')
                if not node:
                    continue

                try:
                    bid = BidFactory.from_external_api(node, product_id, is_variant)
                    bids.append(bid)
                except Exception as e:
                    # Log and skip invalid bids, don't fail the entire request
                    print(f"Skipping invalid bid: {e}")
                    continue

            return bids

        except KeyError as e:
            raise APIClientException(f"Missing required field in bids API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming bids data: {e}")

    @staticmethod
    def to_asks(api_response: Dict[str, Any], product_id: str, is_variant: bool) -> List[Ask]:
        """
        Transform external API asks response to list of Ask domain models.

        Args:
            api_response: Raw API response from external service
            product_id: The product or variant ID
            is_variant: Whether product_id is a variant ID

        Returns:
            List of Ask domain model instances

        Raises:
            APIClientException: If response is invalid or missing required fields
        """
        try:
            # Navigate through the nested response structure
            data = api_response.get('data', {})
            inner_data = data.get('data', {})
            variant = inner_data.get('variant', {})
            market = variant.get('market', {})
            price_levels = market.get('priceLevels', {})
            edges = price_levels.get('edges', [])

            if not isinstance(edges, list):
                raise APIClientException("Expected 'edges' to be a list in asks response")

            # Transform each edge node to Ask entity
            asks = []
            for edge in edges:
                node = edge.get('node')
                if not node:
                    continue

                try:
                    ask = AskFactory.from_external_api(node, product_id, is_variant)
                    asks.append(ask)
                except Exception as e:
                    # Log and skip invalid asks, don't fail the entire request
                    print(f"Skipping invalid ask: {e}")
                    continue

            return asks

        except KeyError as e:
            raise APIClientException(f"Missing required field in asks API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming asks data: {e}")

    @staticmethod
    def to_historical_sales(api_response: Dict[str, Any], product_id: str, is_variant: bool) -> List[HistoricalSale]:
        """
        Transform external API historical sales response to list of HistoricalSale domain models.

        Args:
            api_response: Raw API response from external service
            product_id: The product or variant ID
            is_variant: Whether product_id is a variant ID

        Returns:
            List of HistoricalSale domain model instances

        Raises:
            APIClientException: If response is invalid or missing required fields
        """
        try:
            # Navigate through the nested response structure
            data = api_response.get('data', {})
            inner_data = data.get('data', {})
            variant = inner_data.get('variant', {})
            sales_chart = variant.get('salesChart', {})
            series = sales_chart.get('series', [])

            if not isinstance(series, list):
                raise APIClientException("Expected 'series' to be a list in historical sales response")

            # Transform each series data point to HistoricalSale entity
            historical_sales = []
            for data_point in series:
                if not data_point:
                    continue

                try:
                    historical_sale = HistoricalSaleFactory.from_external_api(data_point, product_id, is_variant)
                    historical_sales.append(historical_sale)
                except Exception as e:
                    # Log and skip invalid data points, don't fail the entire request
                    print(f"Skipping invalid historical sale data point: {e}")
                    continue

            return historical_sales

        except KeyError as e:
            raise APIClientException(f"Missing required field in historical sales API response: {e}")
        except Exception as e:
            raise APIClientException(f"Error transforming historical sales data: {e}")
