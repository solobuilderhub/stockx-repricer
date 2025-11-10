"""
API routes for product and variant management.
Handles creating products and variants from StockX data.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.product import (
    CreateProductRequest,
    CreateProductVariantRequest,
    CreateProductVariantResponse,
    ProductResponseSchema,
    VariantResponseSchema,
    AddVariantRequest,
    AddVariantResponse,
    CreateProductWithVariantsRequest,
    CreateProductWithVariantsResponse
)
from app.services.product import product_service
from app.core.exceptions import APIClientException, DatabaseException

router = APIRouter(prefix="/api/products", tags=["Products"])


def get_product_service():
    """Dependency for product service."""
    return product_service


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
        # Create product
        product = await service.create_product(request.product_id)

        # Convert to response schema
        product_response = ProductResponseSchema(
            id=str(product.id),
            product_id=product.product_id,
            title=product.title,
            brand=product.brand,
            product_type=product.product_type,
            style_id=product.style_id,
            url_key=product.url_key,
            retail_price=product.retail_price,
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
        # Add variant to existing product
        variant = await service.add_variant_to_product(
            request.product_id,
            request.variant_id
        )

        # Convert to response schema
        variant_response = VariantResponseSchema(
            id=str(variant.id),
            variant_id=variant.variant_id,
            product_id=variant.product_id,
            variant_name=variant.variant_name,
            variant_value=variant.variant_value,
            upc=variant.upc,
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
    1. Check if product already exists in database
    2. Check if any variants already exist
    3. Fetch product data from StockX API using the product_id
    4. Fetch all variants for the product from StockX API
    5. Filter and save only the requested variants
    6. Save product and all requested variants to the database

    Args:
        request: Request containing product_id and list of variant_ids

    Returns:
        Created product and variants data

    Raises:
        400: If product/variants already exist or variant IDs not found
        500: API error or database error
    """
    try:
        # Create product with multiple variants
        product, variants = await service.create_product_with_variants(
            request.product_id,
            request.variant_ids
        )

        # Convert to response schemas
        product_response = ProductResponseSchema(
            id=str(product.id),
            product_id=product.product_id,
            title=product.title,
            brand=product.brand,
            product_type=product.product_type,
            style_id=product.style_id,
            url_key=product.url_key,
            retail_price=product.retail_price,
            release_date=product.release_date,
            created_at=product.created_at,
            updated_at=product.updated_at
        )

        variant_responses = [
            VariantResponseSchema(
                id=str(variant.id),
                variant_id=variant.variant_id,
                product_id=variant.product_id,
                variant_name=variant.variant_name,
                variant_value=variant.variant_value,
                upc=variant.upc,
                created_at=variant.created_at,
                updated_at=variant.updated_at
            )
            for variant in variants
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
