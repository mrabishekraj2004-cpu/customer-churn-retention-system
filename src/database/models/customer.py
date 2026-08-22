from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database.session import Base

if TYPE_CHECKING:
    from src.database.models.prediction import Prediction


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False,
    )

    gender: Mapped[str] = mapped_column(String(20))
    senior_citizen: Mapped[int] = mapped_column(Integer)
    partner: Mapped[str] = mapped_column(String(10))
    dependents: Mapped[str] = mapped_column(String(10))

    tenure: Mapped[int] = mapped_column(Integer)

    phone_service: Mapped[str] = mapped_column(String(30))
    multiple_lines: Mapped[str] = mapped_column(String(30))

    internet_service: Mapped[str] = mapped_column(String(30))
    online_security: Mapped[str] = mapped_column(String(30))
    online_backup: Mapped[str] = mapped_column(String(30))
    device_protection: Mapped[str] = mapped_column(String(30))
    tech_support: Mapped[str] = mapped_column(String(30))
    streaming_tv: Mapped[str] = mapped_column(String(30))
    streaming_movies: Mapped[str] = mapped_column(String(30))

    contract: Mapped[str] = mapped_column(String(30))
    paperless_billing: Mapped[str] = mapped_column(String(10))
    payment_method: Mapped[str] = mapped_column(String(50))

    monthly_charges: Mapped[float] = mapped_column(Float)
    total_charges: Mapped[float] = mapped_column(Float)

    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
    )

    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    predictions: Mapped[list[Prediction]] = relationship(
        back_populates="customer",
        cascade="all, delete-orphan",
    )
