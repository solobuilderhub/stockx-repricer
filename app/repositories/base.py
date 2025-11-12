"""Base repository with common CRUD operations."""
from typing import Generic, TypeVar, Type, Optional, List, Any
from beanie import Document
from app.core.exceptions import DatabaseException
from app.core.logging import LoggerMixin

T = TypeVar("T", bound=Document)


class BaseRepository(Generic[T], LoggerMixin):
    """Base repository providing common CRUD operations for Beanie documents."""

    def __init__(self, model: Type[T]):
        """Initialize repository with a document model.

        Args:
            model: Beanie document model class
        """
        self.model = model

    async def create(self, data: dict) -> T:
        """Create a new document.

        Args:
            data: Dictionary of document data

        Returns:
            Created document instance

        Raises:
            DatabaseException: If creation fails
        """
        try:
            document = self.model(**data)
            await document.insert()
            self.logger.info(f"Created {self.model.__name__} with id: {document.id}")
            return document
        except Exception as e:
            self.logger.error(f"Failed to create {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to create document: {str(e)}")

    async def get_by_id(self, document_id: str) -> Optional[T]:
        """Get a document by its ID.

        Args:
            document_id: Document ID

        Returns:
            Document instance or None if not found
        """
        try:
            return await self.model.get(document_id)
        except Exception as e:
            self.logger.error(f"Error fetching {self.model.__name__} by id {document_id}: {str(e)}")
            return None

    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """Get a document by a specific field value.

        Args:
            field: Field name
            value: Field value

        Returns:
            Document instance or None if not found
        """
        try:
            return await self.model.find_one({field: value})
        except Exception as e:
            self.logger.error(f"Error fetching {self.model.__name__} by {field}: {str(e)}")
            return None

    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all documents with pagination.

        Args:
            skip: Number of documents to skip
            limit: Maximum number of documents to return

        Returns:
            List of documents
        """
        try:
            return await self.model.find_all().skip(skip).limit(limit).to_list()
        except Exception as e:
            self.logger.error(f"Error fetching all {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to fetch documents: {str(e)}")

    async def update(self, document_id: str, data: dict) -> Optional[T]:
        """Update a document by ID.

        Args:
            document_id: Document ID
            data: Dictionary of fields to update

        Returns:
            Updated document or None if not found

        Raises:
            DatabaseException: If update fails
        """
        try:
            document = await self.get_by_id(document_id)
            if not document:
                return None

            for key, value in data.items():
                setattr(document, key, value)

            await document.save()
            self.logger.info(f"Updated {self.model.__name__} with id: {document_id}")
            return document
        except Exception as e:
            self.logger.error(f"Failed to update {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to update document: {str(e)}")

    async def delete(self, document_id: str) -> bool:
        """Delete a document by ID.

        Args:
            document_id: Document ID

        Returns:
            True if deleted, False if not found

        Raises:
            DatabaseException: If deletion fails
        """
        try:
            document = await self.get_by_id(document_id)
            if not document:
                return False

            await document.delete()
            self.logger.info(f"Deleted {self.model.__name__} with id: {document_id}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to delete document: {str(e)}")

    async def count(self) -> int:
        """Count total documents.

        Returns:
            Total number of documents
        """
        try:
            return await self.model.count()
        except Exception as e:
            self.logger.error(f"Error counting {self.model.__name__}: {str(e)}")
            raise DatabaseException(f"Failed to count documents: {str(e)}")
