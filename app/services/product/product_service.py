"""
Product Service.
Handles business logic for creating and managing products and variants.
"""
from typing import Tuple, List
from app.repositories.product import product_repository
from app.repositories.variant import variant_repository
from app.services.stockx import stockx_service
from app.core.logging import LoggerMixin
from app.core.exceptions import APIClientException, DatabaseException
from app.models.product import Product
from app.models.variant import Variant
from app.domain.product import Product as ProductDomain
from app.domain.variant import Variant as VariantDomain


class ProductService(LoggerMixin):
    """
    Service for product and variant management.

    Fetches data from StockX API and persists to database.
    """

    def __init__(self):
        """Initialize product service."""
        self.product_repo = product_repository
        self.variant_repo = variant_repository
        self.stockx_service = stockx_service

    async def create_product(
        self,
        product_id: str
    ) -> Tuple[ProductDomain, str]:
        """
        Create a product by fetching data from StockX API.

        This method will:
        1. Check if product already exists
        2. Fetch product data from StockX API
        3. Save product to database

        Args:
            product_id: StockX product UUID

        Returns:
            Tuple of (Product domain model, MongoDB ID)

        Raises:
            APIClientException: If StockX API call fails
            DatabaseException: If database operation fails
            ValueError: If product already exists
        """
        self.logger.info(f"Creating product {product_id}")

        # Check if product already exists
        existing_product = await self.product_repo.get_by_product_id(product_id)
        if existing_product:
            self.logger.warning(f"Product {product_id} already exists")
            raise ValueError(f"Product with ID {product_id} already exists")

        try:
            # Fetch product data from StockX API
            self.logger.info(f"Fetching product data for {product_id} from StockX API")
            product_domain = await self.stockx_service.get_product_by_id(product_id)

            # Prepare product data for repository
            product_data = {
                "product_id": product_domain.product_id.value,
                "title": product_domain.title,
                "brand": product_domain.brand,
                "product_type": product_domain.product_type,
                "style_id": product_domain.style_id.value,
                "url_key": product_domain.url_key,
                "retail_price": float(product_domain.retail_price.amount) if product_domain.retail_price else None,
                "release_date": product_domain.release_date
            }

            # Save product to database using repository
            self.logger.info(f"Saving product {product_id} to database")
            product_doc = await self.product_repo.create(product_data)

            # Convert database model to domain model
            from app.domain.factories import ProductFactory
            product_domain_result = ProductFactory.from_database(product_doc.dict())

            self.logger.info(f"Successfully created product {product_id}")

            # Return domain model and MongoDB ID
            return product_domain_result, str(product_doc.id)

        except APIClientException as e:
            self.logger.error(f"Failed to fetch data from StockX API: {e}")
            raise
        except DatabaseException as e:
            self.logger.error(f"Failed to save to database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating product: {e}")
            raise DatabaseException(f"Failed to create product: {e}")

    async def create_product_and_variant(
        self,
        product_id: str,
        variant_id: str
    ) -> Tuple[ProductDomain, VariantDomain]:
        """
        Create a product and variant by fetching data from StockX API.

        This method will:
        1. Check if product/variant already exist
        2. Fetch product data from StockX API
        3. Fetch variant data from StockX API
        4. Save product to database
        5. Save variant to database with link to product

        Args:
            product_id: StockX product UUID
            variant_id: StockX variant UUID

        Returns:
            Tuple of (Product, Variant) documents

        Raises:
            APIClientException: If StockX API call fails
            DatabaseException: If database operation fails
            ValueError: If product/variant already exists or data is invalid
        """
        self.logger.info(f"Creating product {product_id} and variant {variant_id}")

        # Check if product already exists
        existing_product = await self.product_repo.get_by_product_id(product_id)
        if existing_product:
            self.logger.warning(f"Product {product_id} already exists")
            raise ValueError(f"Product with ID {product_id} already exists")

        # Check if variant already exists
        existing_variant = await self.variant_repo.get_by_variant_id(variant_id)
        if existing_variant:
            self.logger.warning(f"Variant {variant_id} already exists")
            raise ValueError(f"Variant with ID {variant_id} already exists")

        try:
            # Fetch product data from StockX API
            self.logger.info(f"Fetching product data for {product_id} from StockX API")
            product_domain = await self.stockx_service.get_product_by_id(product_id)

            # Fetch variant data from StockX API (returns Variant domain model)
            self.logger.info(f"Fetching variant data for {variant_id} from StockX API")
            variant_domain = await self.stockx_service.get_variant(variant_id, product_id)

            # Prepare product data for repository
            product_data = {
                "product_id": product_domain.product_id.value,
                "title": product_domain.title,
                "brand": product_domain.brand,
                "product_type": product_domain.product_type,
                "style_id": product_domain.style_id.value,
                "url_key": product_domain.url_key,
                "retail_price": float(product_domain.retail_price.amount) if product_domain.retail_price else None,
                "release_date": product_domain.release_date
            }

            # Save product to database using repository
            self.logger.info(f"Saving product {product_id} to database")
            product_doc = await self.product_repo.create(product_data)

            # Prepare variant data for repository
            variant_data = {
                "variant_id": variant_domain.variant_id.value,
                "product_id": variant_domain.product_id.value,
                "product": product_doc,  # Beanie Link
                "variant_name": variant_domain.variant_name,
                "variant_value": variant_domain.variant_value,
                "upc": variant_domain.upc.value if variant_domain.upc else None
            }

            # Save variant to database using repository
            self.logger.info(f"Saving variant {variant_id} to database")
            variant_doc = await self.variant_repo.create(variant_data)

            # Convert database models to domain models
            from app.domain.factories import ProductFactory, VariantFactory
            product_domain_result = ProductFactory.from_database(product_doc.dict())
            variant_domain_result = VariantFactory.from_database(variant_doc.dict())

            self.logger.info(
                f"Successfully created product {product_id} and variant {variant_id}"
            )

            return product_domain_result, variant_domain_result

        except APIClientException as e:
            self.logger.error(f"Failed to fetch data from StockX API: {e}")
            raise
        except DatabaseException as e:
            self.logger.error(f"Failed to save to database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating product and variant: {e}")
            raise DatabaseException(f"Failed to create product and variant: {e}")

    async def add_variant_to_product(
        self,
        product_id: str,
        variant_id: str
    ) -> Tuple[VariantDomain, str]:
        """
        Add a new variant to an existing product.

        This method will:
        1. Check if product exists in database
        2. Check if variant already exists
        3. Fetch variant data from StockX API
        4. Save variant to database with link to existing product

        Args:
            product_id: StockX product UUID
            variant_id: StockX variant UUID

        Returns:
            Tuple of (Variant domain model, MongoDB ID)

        Raises:
            APIClientException: If StockX API call fails
            DatabaseException: If database operation fails
            ValueError: If product doesn't exist or variant already exists
        """
        self.logger.info(f"Adding variant {variant_id} to product {product_id}")

        # Check if product exists
        existing_product = await self.product_repo.get_by_product_id(product_id)
        if not existing_product:
            self.logger.warning(f"Product {product_id} not found")
            raise ValueError(f"Product with ID {product_id} does not exist")

        # Check if variant already exists
        existing_variant = await self.variant_repo.get_by_variant_id(variant_id)
        if existing_variant:
            self.logger.warning(f"Variant {variant_id} already exists")
            raise ValueError(f"Variant with ID {variant_id} already exists")

        try:
            # Fetch variant data from StockX API (returns Variant domain model)
            self.logger.info(f"Fetching variant data for {variant_id} from StockX API")
            variant_domain = await self.stockx_service.get_variant(variant_id, product_id)

            # Prepare variant data for repository
            variant_data = {
                "variant_id": variant_domain.variant_id.value,
                "product_id": variant_domain.product_id.value,
                "product": existing_product,  # Beanie Link to existing product
                "variant_name": variant_domain.variant_name,
                "variant_value": variant_domain.variant_value,
                "upc": variant_domain.upc.value if variant_domain.upc else None
            }

            # Save variant to database using repository
            self.logger.info(f"Saving variant {variant_id} to database")
            variant_doc = await self.variant_repo.create(variant_data)

            # Convert database model to domain model
            from app.domain.factories import VariantFactory
            variant_domain_result = VariantFactory.from_database(variant_doc.dict())

            self.logger.info(
                f"Successfully added variant {variant_id} to product {product_id}"
            )

            # Return domain model and MongoDB ID
            return variant_domain_result, str(variant_doc.id)

        except APIClientException as e:
            self.logger.error(f"Failed to fetch variant data from StockX API: {e}")
            raise
        except DatabaseException as e:
            self.logger.error(f"Failed to save variant to database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error adding variant to product: {e}")
            raise DatabaseException(f"Failed to add variant to product: {e}")

    async def create_product_with_variants(
        self,
        product_id: str,
        variant_ids: List[str]
    ) -> Tuple[ProductDomain, List[VariantDomain], str, List[str]]:
        """
        Create a product with multiple variants by fetching data from StockX API.

        This method will:
        1. Check if product already exists, if so use existing product
        2. Filter out variants that already exist in database
        3. Fetch product data from StockX API (if product doesn't exist)
        4. Fetch all variants for the product from StockX API
        5. Filter variants by provided variant IDs and exclude existing ones
        6. Save product to database (if it doesn't exist)
        7. Save only new variants to database with link to product

        Args:
            product_id: StockX product UUID
            variant_ids: List of StockX variant UUIDs to create

        Returns:
            Tuple of (Product domain model, list of Variant domain models, product MongoDB ID, list of variant MongoDB IDs)

        Raises:
            APIClientException: If StockX API call fails
            DatabaseException: If database operation fails
            ValueError: If requested variant IDs not found in StockX
        """
        self.logger.info(
            f"Creating product {product_id} with {len(variant_ids)} variants"
        )

        # Check if product already exists
        existing_product = await self.product_repo.get_by_product_id(product_id)
        product_exists = existing_product is not None

        if product_exists:
            self.logger.info(f"Product {product_id} already exists, will only add new variants")

        # Check which variants already exist
        existing_variant_ids = set()
        for variant_id in variant_ids:
            existing_variant = await self.variant_repo.get_by_variant_id(variant_id)
            if existing_variant:
                existing_variant_ids.add(variant_id)
                self.logger.info(f"Variant {variant_id} already exists, skipping")

        # Filter to only new variant IDs
        new_variant_ids = [vid for vid in variant_ids if vid not in existing_variant_ids]

        # Import factories at the beginning
        from app.domain.factories import ProductFactory, VariantFactory

        if not new_variant_ids and product_exists:
            self.logger.info("All variants already exist, nothing to create")
            # Return existing product and existing variants
            product_domain = ProductFactory.from_database(existing_product.dict())
            product_db_id = str(existing_product.id)

            # Get all existing variants for this product
            existing_variants_db = await self.variant_repo.get_by_product_id(product_id)
            # Filter to only the variants that were requested
            requested_variant_id_set = set(variant_ids)
            filtered_existing_variants = [
                v for v in existing_variants_db
                if v.variant_id in requested_variant_id_set
            ]

            # Convert to domain models and collect MongoDB IDs
            existing_variants_domain = [
                VariantFactory.from_database(v.dict()) for v in filtered_existing_variants
            ]
            variant_db_ids = [str(v.id) for v in filtered_existing_variants]

            return product_domain, existing_variants_domain, product_db_id, variant_db_ids

        try:

            # Fetch all variants for the product from StockX API
            self.logger.info(f"Fetching all variants for product {product_id} from StockX API")
            all_variants = await self.stockx_service.get_variants(product_id)

            # Filter variants by NEW variant IDs only (excluding existing ones)
            new_variant_id_set = set(new_variant_ids)
            filtered_variants = [
                v for v in all_variants
                if v.variant_id.value in new_variant_id_set
            ]

            # Check if all requested new variants were found
            found_variant_ids = {v.variant_id.value for v in filtered_variants}
            missing_ids = new_variant_id_set - found_variant_ids
            if missing_ids:
                raise ValueError(
                    f"The following variant IDs were not found for product {product_id}: {missing_ids}"
                )

            self.logger.info(
                f"Found {len(filtered_variants)} new variants to create out of {len(all_variants)} total variants"
            )

            # Create or use existing product
            if not product_exists:
                # Fetch product data from StockX API
                self.logger.info(f"Fetching product data for {product_id} from StockX API")
                product_domain = await self.stockx_service.get_product_by_id(product_id)

                # Prepare product data for repository
                product_data = {
                    "product_id": product_domain.product_id.value,
                    "title": product_domain.title,
                    "brand": product_domain.brand,
                    "product_type": product_domain.product_type,
                    "style_id": product_domain.style_id.value,
                    "url_key": product_domain.url_key,
                    "retail_price": float(product_domain.retail_price.amount) if product_domain.retail_price else None,
                    "release_date": product_domain.release_date
                }

                # Save product to database using repository
                self.logger.info(f"Saving product {product_id} to database")
                product_doc = await self.product_repo.create(product_data)
            else:
                product_doc = existing_product

            # Save all new filtered variants
            variant_docs = []
            for idx, variant_domain in enumerate(filtered_variants, 1):
                self.logger.info(
                    f"Saving variant {variant_domain.variant_id.value} ({idx}/{len(filtered_variants)}) to database"
                )

                # Prepare variant data for repository
                variant_data = {
                    "variant_id": variant_domain.variant_id.value,
                    "product_id": variant_domain.product_id.value,
                    "product": product_doc,  # Beanie Link
                    "variant_name": variant_domain.variant_name,
                    "variant_value": variant_domain.variant_value,
                    "upc": variant_domain.upc.value if variant_domain.upc else None
                }

                # Save variant to database using repository
                variant_doc = await self.variant_repo.create(variant_data)
                variant_docs.append(variant_doc)

            # Convert database models to domain models and collect MongoDB IDs
            product_domain_result = ProductFactory.from_database(product_doc.dict())
            product_db_id = str(product_doc.id)

            variant_domain_results = [
                VariantFactory.from_database(v.dict()) for v in variant_docs
            ]
            variant_db_ids = [str(v.id) for v in variant_docs]

            self.logger.info(
                f"Successfully created product {product_id} with {len(variant_domain_results)} variants"
            )

            return product_domain_result, variant_domain_results, product_db_id, variant_db_ids

        except APIClientException as e:
            self.logger.error(f"Failed to fetch data from StockX API: {e}")
            raise
        except DatabaseException as e:
            self.logger.error(f"Failed to save to database: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error creating product with variants: {e}")
            raise DatabaseException(f"Failed to create product with variants: {e}")

    async def get_all_products_with_variants(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[Tuple[Product, List[Variant]]]:
        """
        Get all products with their associated variants from database.

        Args:
            skip: Number of products to skip (for pagination)
            limit: Maximum number of products to return (for pagination)

        Returns:
            List of tuples containing (Product DB model, List of Variant DB models)

        Raises:
            DatabaseException: If database operation fails
        """
        self.logger.info(f"Fetching all products with variants (skip={skip}, limit={limit})")

        try:
            # Fetch all products with pagination
            products_db = await self.product_repo.get_all(skip=skip, limit=limit)

            products_with_variants = []
            for product_db in products_db:
                # Get all variants for this product
                variants_db = await self.variant_repo.get_by_product_id(product_db.product_id)

                # Return database models directly for read operations
                products_with_variants.append((product_db, variants_db))

            self.logger.info(
                f"Successfully fetched {len(products_with_variants)} products with their variants"
            )

            return products_with_variants

        except DatabaseException as e:
            self.logger.error(f"Failed to fetch products with variants: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error fetching products with variants: {e}")
            raise DatabaseException(f"Failed to fetch products with variants: {e}")


# Singleton instance
product_service = ProductService()
