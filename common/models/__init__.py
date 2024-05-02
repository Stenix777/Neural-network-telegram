from ..settings import settings
from .base import Base, Database
from .generations import ImageQuery, TextGenerationRole, TextQuery, VideoQuery
from .payments import Invoice, Refund, Tariff
from .user import ReferalLink, User, UserAdmin
from .reports import Report

db = Database(async_url=settings.ASYNC_DB_URL, url=settings.DB_URL, echo=False)
