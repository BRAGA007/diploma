import logging
import math
from collections.abc import Awaitable, Callable, Sequence
from typing import Any, Generic, List, Optional, Type

from fastapi.encoders import jsonable_encoder
from fastapi_filter.contrib.sqlalchemy import Filter
from sqlalchemy import ColumnExpressionArgument, Select, and_, func, literal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import InstrumentedAttribute
from sqlalchemy.sql.base import ExecutableOption

from app.exceptions.model import ModelNotFoundError
from app.schemas import ErrorModel
from app.schemas.pagination import Page, PaginationParams
from app.schemas.typing import CreateType, ModelType, UpdateType


logger = logging.getLogger(__name__)


# базовый класс в дальнейшем используется как родитель, для классов взаимодействующих с базой данных
class CRUDBase(Generic[ModelType, CreateType, UpdateType]):
    def __init__(self, table: Type[ModelType]):
        """Инициализация класса с определением таблицы"""
        self._table = table

    async def create(self, db: AsyncSession, obj_in: CreateType) -> ModelType:
        """Метод создания объекта"""
        obj_in_data = obj_in.model_dump()  # формирование данных для создания объекта
        db_obj = self._table(**obj_in_data)  # cоздание объекта
        db.add(db_obj)   # добавление объекта
        await db.commit()  # commit в базу данных
        await db.refresh(db_obj)  # обновление базы данных
        logger.debug(f"{self._table.__name__} successfully created")  # логирование действия создания объекта
        return db_obj  # возвращение озданного объекта

    async def get(self, db: AsyncSession, obj_id: int, **kwargs) -> ModelType:
        """Метод получения объекта по id"""
        result = await db.get(self._table, obj_id, **kwargs)  # получение объекта по id

        if not result:  # если нет результата выводим сообщение об ошибке
            logger.error(f"{self._table.__name__} id={obj_id} not found")
            error = ErrorModel(class_name=self._table.__name__, value=obj_id)
            raise ModelNotFoundError(error)

        logger.debug(f"{self._table.__name__} id={obj_id} found")  # логирование действия
        return result  # возвращение найденного объекта в базе данных

    async def update(self, db: AsyncSession, obj_in: UpdateType, obj_id: int) -> ModelType:
        """Метод обновления объекта по id"""
        db_obj: ModelType = await self.get(db, obj_id)  # получаем исходный объект для обновления

        update_data = obj_in.model_dump(exclude_unset=True)  # формирование данных для обновления объекта
        for field in jsonable_encoder(db_obj):  # проход по всем полям объекта
            if field in update_data:  # если поле есть в данных для обновления
                setattr(db_obj, field, update_data[field])  # меняем значения поля на обновленное

        db.add(db_obj)  # добавление объекта
        await db.commit()  # commit в базу данных
        await db.refresh(db_obj)  # обновление базы данных

        logger.debug(f"{self._table.__name__} id={obj_id} successfully updated")  # логирование действия
        return db_obj  # возвращение обновленного объекта

    async def delete(self, db: AsyncSession, obj_id: int) -> None:
        """Метод для удаления объекта из базы данных по id"""
        db_obj = await self.get(db, obj_id)  # получаем объект для удаления
        await db.delete(db_obj)  # удаление объекта
        await db.commit()  # commit в базу данных
        logger.debug(f"{self._table.__name__} successfully deleted")  # логирование действия

    async def list(
        self,
        db: AsyncSession,
        clauses: Optional[List[Any]] = None,
        base_query: Optional[Select] = None,
        joins: Optional[List[Any]] = None,
        model_filter: Optional[Filter] = None,
        options: Optional[List[ExecutableOption]] = None,
        offset: Optional[int] = 0,
        limit: Optional[int] = 100,
    ) -> Sequence[ModelType]:
        query = select(self._table) if base_query is None else base_query
        if joins:
            for target in joins:
                query = query.join(target)
        if options:
            query = query.options(*options)
        if clauses:
            query = query.where(*clauses)
        if model_filter:
            query = model_filter.filter(query)
        if limit:
            query = query.offset(offset).limit(limit)
        results = await db.execute(query)

        logger.debug(f"List all {self._table.__name__} successful")
        return results.scalars().all()

    async def paginate(
        self,
        db: AsyncSession,
        pagination_params: PaginationParams,
        *,
        clauses: Optional[List[ColumnExpressionArgument]] = None,
        base_query: Optional[Select] = None,
        model_filter: Optional[Filter] = None,
        transformer: Optional[Callable[[Sequence], Awaitable[List]]] = None,
        joins: Optional[List[Type | InstrumentedAttribute]] = None,
        options: Optional[List[ExecutableOption]] = None,
        scalars: bool = True,
    ) -> Page:
        query = select(self._table) if base_query is None else base_query
        if joins:
            for target in joins:
                query = query.join(target)
        if options:
            query = query.options(*options)
        if clauses:
            query = query.where(*clauses)
        if model_filter:
            query = model_filter.filter(query)

        # Считаем количество строк, удовлетворяющих условиям
        count_query = query.with_only_columns(
            func.count(literal(1)),
            maintain_column_froms=True,
        )
        total = (await db.execute(count_query)).scalar_one()

        # Результаты должны быть отсортированы, иначе данные на странице в пагинации будут всегда разными
        if model_filter:
            query = model_filter.sort(query)
        else:
            query = query.order_by(self._table.__table__.primary_key.columns)

        page = pagination_params.page
        size = pagination_params.size

        query = query.limit(size).offset(size * (page - 1))  # Номера страницы начинаются с 1
        result = await db.execute(query)
        sequence = result.scalars().all() if scalars else result.all()
        items = (await transformer(sequence)) if transformer else sequence

        return Page(
            items=items,
            total=total,
            page=page,
            size=size,
            pages=math.ceil(total / size),
        )

    async def count(self, db: AsyncSession, clauses: Optional[List[Any]] = None) -> int:
        if clauses is None:
            clauses = []
        results = await db.execute(select(func.count(self._table.id)).where(and_(True, *clauses)))
        (result,) = results.one()
        return result



    async def get_one_or_none(
        self,
        db: AsyncSession,
        model_key: InstrumentedAttribute,
        value: Any,
    ) -> Optional[ModelType]:
        """Получение объекта с нужным значением поля"""
        statement = select(self._table).where(model_key == value)
        result = await db.execute(statement)
        return result.scalars().one_or_none()


    @property
    def table(self) -> Type[ModelType]:
        return self._table
