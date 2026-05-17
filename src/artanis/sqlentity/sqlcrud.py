#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2026 Busana Apparel Group. All rights reserved.
#
# This product and it's source code is protected by patents, copyright laws and
# international copyright treaties, as well as other intellectual property
# laws and treaties. The product is licensed, not sold.
#
# The source code and sample programs in this package or parts hereof
# as well as the documentation shall not be copied, modified or redistributed
# without permission, explicit or implied, of the author.
#
# This module is part of Artanis Enterprise Platform and is released under
# the Apache-2.0 License: https://www.apache.org/licenses/LICENSE-2.0

from typing import TypeVar, Type, Optional, List, Any, Generic

from sqlalchemy.sql.elements import BinaryExpression
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
# Workaround for SQLAlchemy Warning
from sqlmodel.sql.expression import Select, SelectOfScalar

from artanis.config import Configuration
from artanis.sqlentity import Entity

SelectOfScalar.inherit_cache = True  # type: ignore
Select.inherit_cache = True  # type: ignore

ModelClass = TypeVar('ModelClass', bound=Entity)


class EntityCRUD(Generic[ModelClass]):
    """Simple class providing base CRUD operations on given Model"""
    db: AsyncSession
    model: Type[ModelClass]

    def __init__(self, model: Type[ModelClass]):
        """
        Class constructor
        Args:
            model: The model onto perform operations
            db: Database engine Session
        """
        self.config = Configuration.get_default_instance(create_instance=False)
        self.model = model
        session = self.config.container.scoped_session
        self.db = session()

    async def create(self, instance: Entity) -> Optional[Entity]:
        """
        Persists an item into the Database
        Args:
            instance: model to persist

        Returns:
            Optional[SQLModel]: the created instance itself

        """
        self.db.add(instance)
        await self.db.commit()
        await self.db.refresh(instance)
        return instance

    async def get(self, *args: BinaryExpression, **kwargs: Any) -> Optional[ModelClass]:
        """
        Gets a single record from the database
        Args:
            *args: filter args
            **kwargs: filter args

        Returns:
            Optional[ModelClass]: the retrieved instance or None

        """
        statement = select(self.model).filter(*args).filter_by(**kwargs)
        return (await self.db.exec(statement)).first()

    async def filter(self,
                     offset: Optional[int] = 0,
                     limit: Optional[int] = 100,
                     *args: BinaryExpression,
                     **kwargs: Any) -> List[Any]:
        """
        Gets one or more instances from the database, filtering them by one or more column
        Args:
            offset: specifies the point from where to start returning data
            limit: parameter that limits the number of results
            *args: filter args
            **kwargs: filter args

        Returns:
            List: List of retrieved items from the database

        """
        result = await self.db.execute(select(self.model).filter(*args).filter_by(**kwargs).offset(offset).limit(limit))
        return result.scalars().all()

    async def get_all(self) -> Optional[List[ModelClass]]:
        """
        Gets all instances of given module from the Database
        Returns:
            List: List of all instances of that model in the database.
        """
        statement = select(self.model)
        return (await self.db.exec(statement)).all()

    async def update(self, instance: SQLModel) -> Optional[SQLModel]:
        """
        Updates a record into database. It is equal to create data process, so it will call that method
        Args:
            instance: the instance to update

        Returns:
            Optional[SQLModel]: the updated instance
        """
        updated_instance = await self.create(instance)
        return updated_instance

    async def delete(self, instance: Type[ModelClass]) -> Type[ModelClass]:
        """
        Removes an instance from the database
        Args:
            instance: the instance to remove

        Returns:
            Type[ModelClass]: the instance removed
        """
        await self.db.delete(instance)
        await self.db.commit()
        return instance

    async def bulk_create(self, instances: List[ModelClass]) -> List[ModelClass]:
        """
        Insert multiple instances in the database
        Args:
            instances: List of instances to be added into the Database

        Returns:
            List[ModelClass]: the inserted instances
        """
        self.db.add_all(instances)
        await self.db.commit()
        return instances
