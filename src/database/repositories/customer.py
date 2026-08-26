from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.database.models import Customer


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(
        self,
        customer_db_id: int,
    ) -> Customer | None:
        return self.db.get(Customer, customer_db_id)

    def get_by_customer_id(
        self,
        customer_id: str,
    ) -> Customer | None:
        statement = select(Customer).where(Customer.customer_id == customer_id)

        return self.db.scalar(statement)

    def get_all(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Customer]:
        statement = (
            select(Customer)
            .order_by(Customer.created_at.desc())
            .offset(offset)
            .limit(limit)
        )

        return list(self.db.scalars(statement).all())

    def create(
        self,
        customer_id: str,
        customer_data: dict[str, Any],
    ) -> Customer:
        customer = Customer(
            customer_id=customer_id,
            **customer_data,
        )

        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)

        return customer

    def update(
        self,
        customer: Customer,
        customer_data: dict[str, Any],
    ) -> Customer:
        for field, value in customer_data.items():
            setattr(customer, field, value)

        self.db.commit()
        self.db.refresh(customer)

        return customer
