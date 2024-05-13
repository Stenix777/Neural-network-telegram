from datetime import datetime
from typing import TYPE_CHECKING

from flask_login import UserMixin
from sqlalchemy import (BigInteger, Boolean, Column, DateTime, ForeignKey,
                        Integer, String, Table)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql.functions import now
from werkzeug.security import check_password_hash, generate_password_hash

from ..enums import ImageModels, TextModels
from . import Base

if TYPE_CHECKING:
    from .generations import (ImageQuery, ServiceQuery, TextGenerationRole,
                              TextQuery, TextSession, VideoQuery)
    from .payments import Invoice, Refund, Tariff


user_referral_link_association = Table(
    "user_referral_link_association",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"),
           primary_key=True),
    Column("referral_link_id", Integer, ForeignKey("referral_links.id", ondelete="CASCADE"),
           primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=False)
    username: Mapped[str | None] = mapped_column(String(), default=None, server_default=None)
    first_name: Mapped[str | None] = mapped_column(String(), default=None, server_default=None)
    last_name: Mapped[str | None] = mapped_column(String(), default=None, server_default=None)
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False)

    chatgpt_daily_limit: Mapped[int | None] = mapped_column(default=0)
    gemini_daily_limit: Mapped[int] = mapped_column(default=0)
    kandinsky_daily_limit: Mapped[int] = mapped_column(default=0)
    sd_daily_limit: Mapped[int] = mapped_column(default=0)
    token_balance: Mapped[int] = mapped_column(default=0)

    txt_model: Mapped[TextModels] = mapped_column(String(), default=TextModels.GEMINI)
    txt_model_role_id: Mapped[int | None] = mapped_column(
        ForeignKey("text_generation_roles.id", ondelete="SET NULL"), default=None)
    img_model: Mapped[ImageModels] = mapped_column(String(), default=ImageModels.STABLE_DIFFUSION)
    tts_mode: Mapped[str] = mapped_column(default="")
    text_session_id: Mapped[int | None] = mapped_column(ForeignKey("sessions.id", ondelete="SET NULL"),
                                                        default=None, server_default=None)

    update_daily_limits_time: Mapped[datetime] = mapped_column(DateTime, default=now(), server_default=now())
    tariff_id: Mapped[int | None] = mapped_column(ForeignKey("tariffs.id", ondelete="SET NULL"), default=None)
    payment_time: Mapped[datetime | None] = mapped_column(DateTime, default=None)
    mother_invoice_id: Mapped[int | None] = mapped_column(default=None)
    payment_tries: Mapped[int] = mapped_column(default=0)
    recurring: Mapped[bool] = mapped_column(default=True)
    first_payment: Mapped[bool] = mapped_column(default=True)

    tariff: Mapped["Tariff"] = relationship(back_populates="users", lazy="joined")
    invoices: Mapped[list["Invoice"]] = relationship(back_populates="user")
    refunds: Mapped[list["Refund"]] = relationship(back_populates="user")
    text_session: Mapped["TextSession"] = relationship(back_populates="user", lazy="joined", single_parent=True)
    text_queries: Mapped[list["TextQuery"]] = relationship(back_populates="user")
    image_queries: Mapped[list["ImageQuery"]] = relationship(back_populates="user")
    video_queries: Mapped[list["VideoQuery"]] = relationship(back_populates="user")
    services_queries: Mapped[list["ServiceQuery"]] = relationship(back_populates="user")
    txt_model_role: Mapped["TextGenerationRole"] = relationship(back_populates="users", lazy="joined")
    referral_links: Mapped[list["ReferralLink"]] = relationship(secondary=user_referral_link_association,
                                                                back_populates="users")

    def __str__(self):
        return self.username if self.username else self.id

    def __repr__(self):
        return f"<User: {self.id}>"

    def sub_time_left(self) -> tuple:
        days_left = (self.payment_time - datetime.now()).days
        if days_left >= 2:
            return ("день", "дня", "дней"), days_left
        else:
            hours_left = int((self.payment_time - datetime.now()).total_seconds() // 3600)
            return ("час", "часа", "часов"), hours_left if hours_left > 1 else 1


class UserAdmin(Base, UserMixin):
    __tablename__ = 'users_admin'

    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    hash_password: Mapped[str] = mapped_column(String(256), nullable=False)

    def set_password(self, password):
        self.hash_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hash_password, password)


class ReferralLink(Base):
    __tablename__ = "referral_links"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True)
    name: Mapped[str]
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    clicks: Mapped[int] = mapped_column(default=0)
    buys_cnt: Mapped[int] = mapped_column(default=0)
    buys_sum: Mapped[int] = mapped_column(default=0)
    new_users: Mapped[int] = mapped_column(default=0)
    bot_link: Mapped[str] = mapped_column(unique=True, default="")
    site_link: Mapped[str] = mapped_column(unique=True, default="")

    users: Mapped[list["User"]] = relationship(secondary=user_referral_link_association,
                                               back_populates="referral_links")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<RefLink: {self.name}>"
