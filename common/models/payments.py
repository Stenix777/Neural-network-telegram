from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class Tariff(Base):
    __tablename__ = "tariffs"

    name: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(50), unique=True)
    description: Mapped[str]
    chatgpt_daily_limit: Mapped[int | None] = mapped_column(default=0)
    gemini_daily_limit: Mapped[int] = mapped_column(default=0)
    kandinsky_daily_limit: Mapped[int] = mapped_column(default=0)
    sd_daily_limit: Mapped[int] = mapped_column(default=0)
    token_balance: Mapped[int]
    days: Mapped[int]
    price: Mapped[int]
    main_tariff_id: Mapped[int | None] = mapped_column(default=None, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_extra: Mapped[bool] = mapped_column(default=False)
    is_trial: Mapped[bool] = mapped_column(default=False)

    users: Mapped[list["User"]] = relationship(back_populates="tariff")
    invoices: Mapped["Invoice"] = relationship(back_populates="tariff")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Tariff: {self.name}>"


class Invoice(Base):
    __tablename__ = "invoices"

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    is_paid: Mapped[bool] = mapped_column(default=False)
    mother_invoice_id: Mapped[int | None] = mapped_column(default=None)
    tariff_id: Mapped[int | None] = mapped_column(ForeignKey("tariffs.id", ondelete="SET NULL"))
    sum: Mapped[int] = mapped_column(default=0)

    user: Mapped["User"] = relationship(back_populates="invoices", lazy="joined")
    tariff: Mapped["Tariff"] = relationship(back_populates="invoices", lazy="joined")

    def __str__(self):
        return str(self.id)

    def __repr__(self):
        return f"<Invoice: {self.id} | User: {self.user_id}>"


class Refund(Base):
    __tablename__ = "refunds"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    sum: Mapped[int]
    attention: Mapped[bool]
    is_done: Mapped[bool] = mapped_column(default=False)

    user: Mapped["User"] = relationship(back_populates="refunds")

    def __str__(self):
        return self.user.username if self.user.username else self.user.id

    def __repr__(self):
        return f"<Invoice: {self.id} | User: {self.user_id}>"
