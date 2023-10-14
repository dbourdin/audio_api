"""Base CRUD implementation."""

from typing import Any, Generic, TypeVar

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy.orm import Session

from audio_api.db.models.base_db_model import SqlAlchemyModel

ModelType = TypeVar("ModelType", bound=SqlAlchemyModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Base CRUD class."""

    def __init__(self, model: type[ModelType]):
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        Args:
            model (Type[ModelType]): A SQLAlchemy model class
        """
        self.model = model

    def get(self, db: Session, id: Any) -> ModelType | None:
        """Get a single row by id.

        Args:
            db (Session): A database session
            id (Any): The id to retrieve

        Returns:
            Optional[ModelType]: The retrieved row
        """
        return db.query(self.model).filter(self.model.id == id).first()

    def get_by_uuid(self, db: Session, uuid: Any) -> ModelType | None:
        """Get a single row by uuid.

        Args:
            db (Session): A database session
            uuid (Any): The uuid to retrieve

        Returns:
            Optional[ModelType]: The retrieved row
        """
        return db.query(self.model).filter(self.model.uuid == uuid).first()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 1000,
    ) -> list[ModelType]:
        """Get many rows.

        Args:
            db (Session): A database session
            skip (int): How many rows to skip. Defaults to 0.
            limit (int): How many rows to return. Defaults to 1000.

        Returns:
            list[ModelType]: The retrieved rows
        """
        # Construct the actual query
        return db.query(self.model).offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """Create a new row.

        Args:
            db (Session): A database session
            obj_in: (CreateSchemaType) Object to create

        Returns:
            ModelType: The created object
        """
        obj_in_data = jsonable_encoder(obj_in, by_alias=False)
        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        """Update a row.

        Args:
            db (Session): A database session
            db_obj (ModelType): Old object in db
            obj_in (UpdateSchemaType): New values to apply

        Returns:
            ModelType: The updated row
        """
        obj_data = jsonable_encoder(db_obj, by_alias=False)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = jsonable_encoder(obj_in, exclude_unset=True, by_alias=False)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: int) -> ModelType:
        """Remove a row by id.

        Args:
            db (Session): A database session
            id (int): Id of resource to remove

        Returns:
            ModelType: The removed resource
        """
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        return obj
