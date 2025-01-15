from datetime import datetime

from sqlalchemy import String, DateTime, Boolean, Integer, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase): ...


class Ad(Base):
    __tablename__ = "ads"
    id: Mapped[int] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(String, nullable=False)
    publication_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    title: Mapped[str] = mapped_column(String(70), nullable=False)
    price: Mapped[int | None] = mapped_column(nullable=True, default=None)
    location: Mapped[str] = mapped_column(String, nullable=False)
    username: Mapped[str] = mapped_column(String(100), nullable=False)
    user_registration: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    last_seen: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    business: Mapped[Boolean] = mapped_column(Boolean, nullable=False)
    olx_delivery: Mapped[Boolean] = mapped_column(Boolean, nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    user_rating: Mapped[float] = mapped_column(Float, nullable=False)
    _image_urls: Mapped[str] = mapped_column(String, nullable=False)
    _params: Mapped[str] = mapped_column(String, nullable=False)

    @property
    def image_urls(self):
        return [url for url in self._image_urls.split("|")[:-1]]

    @image_urls.setter
    def image_urls(self, value):
        self._image_urls = value

    @property
    def params(self):
        return [param for param in self._params.split("|")[:-1]]

    @params.setter
    def params(self, value):
        self._params = value
