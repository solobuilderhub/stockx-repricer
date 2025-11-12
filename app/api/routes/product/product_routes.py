"""
API routes for product and variant management.
Handles creating products and variants from StockX data.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.product import (
    CreateProductRequest,
    ProductResponseSchema,
    VariantResponseSchema,
    AddVariantRequest,
    AddVariantResponse,
    CreateProductWithVariantsRequest,
    CreateProductWithVariantsResponse,
    ProductWithVariantsResponse,
    GetAllProductsResponse
)
from app.services.product import product_service
from app.core.exceptions import APIClientException, DatabaseException

router = APIRouter(prefix="/api/products", tags=["Products"])


def get_product_service():
    """Dependency for product service."""
    return product_service


@router.get("/", response_model=GetAllProductsResponse, status_code=status.HTTP_200_OK)
async def get_all_products(
    skip: int = 0,
    limit: int = 100,
    service = Depends(get_product_service)
):
    """
    Get all products with their variants from database.

    Supports pagination through skip and limit query parameters.

    Args:
        skip: Number of products to skip (default: 0)
        limit: Maximum number of products to return (default: 100)

    Returns:
        List of products with their associated variants and pagination info

    Raises:
        500: Database error
    """
    try:
        # Get all products with variants (returns DB models)
        products_with_variants = await service.get_all_products_with_variants(skip=skip, limit=limit)

        # Convert database models to response schemas
        response_products = []
        for product_db, variants_db in products_with_variants:
            product_response = ProductResponseSchema(
                id=str(product_db.id),  # MongoDB ID
                product_id=product_db.product_id,
                title=product_db.title,
                brand=product_db.brand,
                product_type=product_db.product_type,
                style_id=product_db.style_id,
                url_key=product_db.url_key,
                retail_price=product_db.retail_price,
                release_date=product_db.release_date,
                created_at=product_db.created_at,
                updated_at=product_db.updated_at
            )

            variant_responses = [
                VariantResponseSchema(
                    id=str(variant_db.id),  # MongoDB ID
                    variant_id=variant_db.variant_id,
                    product_id=variant_db.product_id,
                    variant_name=variant_db.variant_name,
                    variant_value=variant_db.variant_value,
                    upc=variant_db.upc,
                    created_at=variant_db.created_at,
                    updated_at=variant_db.updated_at
                )
                for variant_db in variants_db
            ]

            response_products.append(
                ProductWithVariantsResponse(
                    product=product_response,
                    variants=variant_responses
                )
            )

        return GetAllProductsResponse(
            products=response_products,
            total=len(response_products),
            skip=skip,
            limit=limit
        )

    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/", response_model=ProductResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_product(
    request: CreateProductRequest,
    service = Depends(get_product_service)
):
    """
    Create a product by fetching data from StockX API.

    This endpoint will:
    1. Check if product already exists in database
    2. Fetch product data from StockX API using the product_id
    3. Save product to the database

    Args:
        request: Request containing product_id

    Returns:
        Created product data

    Raises:
        400: If product already exists or invalid data
        500: API error or database error
    """
    try:
        # Create product (returns domain model and MongoDB ID)
        product, product_db_id = await service.create_product(request.product_id)

        # Convert domain model to response schema
        product_response = ProductResponseSchema(
            id=product_db_id,  # MongoDB ID
            product_id=product.product_id.value,
            title=product.title,
            brand=product.brand,
            product_type=product.product_type,
            style_id=product.style_id.value,
            url_key=product.url_key,
            retail_price=float(product.retail_price.amount) if product.retail_price else None,
            release_date=product.release_date,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        return product_response

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data from StockX API: {str(e)}"
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )


@router.post("/variants", response_model=AddVariantResponse, status_code=status.HTTP_201_CREATED)
async def add_variant_to_product(
    request: AddVariantRequest,
    service = Depends(get_product_service)
):
    """
    Add a new variant to an existing product.

    This endpoint will:
    1. Check if product exists in database
    2. Check if variant already exists
    3. Fetch variant data from StockX API using the variant_id
    4. Save variant to the database with link to existing product

    Args:
        request: Request containing product_id and variant_id

    Returns:
        Created variant data

    Raises:
        400: If product doesn't exist or variant already exists
        500: API error or database error
    """
    try:
        # Add variant to existing product (returns domain model and MongoDB ID)
        variant, variant_db_id = await service.add_variant_to_product(
            request.product_id,
            request.variant_id
        )

        # Convert domain model to response schema
        variant_response = VariantResponseSchema(
            id=variant_db_id,  # MongoDB ID
            variant_id=variant.variant_id.value,
            product_id=variant.product_id.value,
            variant_name=variant.variant_name,
            variant_value=variant.variant_value,
            upc=variant.upc.value if variant.upc else None,
            created_at=variant.created_at,
            updated_at=variant.updated_at
        )

        return AddVariantResponse(variant=variant_response)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data from StockX API: {str(e)}"
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )

@router.post("/bulk", response_model=CreateProductWithVariantsResponse, status_code=status.HTTP_201_CREATED)
async def create_product_with_variants(
    request: CreateProductWithVariantsRequest,
    service = Depends(get_product_service)
):
    """
    Create a product with multiple variants by fetching data from StockX API.

    This endpoint will:
    1. Check if product already exists in database (if yes, use existing product)
    2. Check which variants already exist in database
    3. Fetch product data from StockX API (only if product doesn't exist)
    4. Fetch all variants for the product from StockX API
    5. Filter and save only the NEW variants that don't exist yet
    6. Return the product and list of newly created variants

    Args:
        request: Request containing product_id and list of variant_ids

    Returns:
        Product data and list of newly created variants

    Raises:
        400: If variant IDs not found in StockX
        500: API error or database error
    """
    try:
        # Create product with multiple variants (returns domain models and MongoDB IDs)
        product, variants, product_db_id, variant_db_ids = await service.create_product_with_variants(
            request.product_id,
            request.variant_ids
        )

        # Convert domain models to response schemas
        product_response = ProductResponseSchema(
            id=product_db_id,  # MongoDB ID
            product_id=product.product_id.value,
            title=product.title,
            brand=product.brand,
            product_type=product.product_type,
            style_id=product.style_id.value,
            url_key=product.url_key,
            retail_price=float(product.retail_price.amount) if product.retail_price else None,
            release_date=product.release_date,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        variant_responses = [
            VariantResponseSchema(
                id=variant_db_ids[idx],  # MongoDB ID
                variant_id=variant.variant_id.value,
                product_id=variant.product_id.value,
                variant_name=variant.variant_name,
                variant_value=variant.variant_value,
                upc=variant.upc.value if variant.upc else None,
                created_at=variant.created_at,
                updated_at=variant.updated_at
            )
            for idx, variant in enumerate(variants)
        ]

        return CreateProductWithVariantsResponse(
            product=product_response,
            variants=variant_responses
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except APIClientException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch data from StockX API: {str(e)}"
        )
    except DatabaseException as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
