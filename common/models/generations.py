from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from common.models import Base
from common.services.neiro_api import GenerationStatus

from ..enums import (ImageAction, ImageModels, ServiceModels, TextModels,
                     VideoModels)

if TYPE_CHECKING:
    from .user import User


class TextSession(Base):
    __tablename__ = "sessions"

    user: Mapped["User"] = relationship(back_populates="text_session", single_parent=True, lazy="joined")
    text_queries: Mapped[list["TextQuery"]] = relationship(back_populates="session")

    def __str__(self):
        return f"<Session: {self.id}>"

    def __repr__(self):
        return self.__str__()


class TextQuery(Base):
    __tablename__ = "text_queries"

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    model: Mapped[TextModels] = mapped_column(String(20), default=TextModels.GPT_3_TURBO)
    session_id: Mapped[int | None] = mapped_column(ForeignKey("sessions.id", ondelete="SET NULL"))
    prompt: Mapped[str]
    result: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="text_queries")
    session: Mapped["TextSession"] = relationship(back_populates="text_queries")

    def __str__(self):
        return f"{self.id}({self.model})"

    def __repr__(self):
        return f"<TextQuery: {self.model} | {self.id}({self.session_id})"


class ImageQuery(Base):
    __tablename__ = "image_queries"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    model: Mapped[ImageModels] = mapped_column(String(20), default=ImageModels.STABLE_DIFFUSION)
    prompt: Mapped[str] = mapped_column(default="")
    result: Mapped[str] = mapped_column(default="")
    action: Mapped[ImageAction] = mapped_column(String(20), default=ImageAction.IMAGINE)
    index: Mapped[int | None] = mapped_column(default=None)
    status: Mapped[GenerationStatus | None] = mapped_column(String(), default=GenerationStatus.IN_QUEUE)

    user: Mapped["User"] = relationship(back_populates="image_queries")

    def __str__(self):
        return f"{self.id}({self.model})"

    def __repr__(self):
        return f"<ImageQuery | {self.model}: <{self.id}>"


class VideoQuery(Base):
    __tablename__ = "video_queries"

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    type: Mapped[VideoModels] = mapped_column(String(20))
    prompt: Mapped[str]
    result: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="video_queries")

    def __str__(self):
        return f"{self.id}({self.type})"

    def __repr__(self):
        return f"<VideoQuery | {self.type}: <{self.id}>"


class ServiceQuery(Base):
    __tablename__ = "service_queries"

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    type: Mapped[ServiceModels] = mapped_column(String(20))
    result: Mapped[str]

    user: Mapped["User"] = relationship(back_populates="services_queries")

    def __str__(self):
        return f"{self.id}({self.type})"

    def __repr__(self):
        return f"<ServiceQuery | {self.type}: <{self.id}>"


class TextGenerationRole(Base):
    __tablename__ = "text_generation_roles"

    title: Mapped[str] = mapped_column(unique=True)
    prompt: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(default=True)

    users: Mapped[list["User"]] = relationship(back_populates="txt_model_role")

    def __str__(self):
        return self.title

    def __repr__(self):
        return f"<TextRole | {self.title}>"
