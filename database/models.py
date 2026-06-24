from sqlalchemy import BigInteger, Boolean, Column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(unique=True)

    username: Mapped[str | None]

    age: Mapped[int | None]

    gender: Mapped[str | None]

    country: Mapped[str | None]

    bio: Mapped[str | None]

    coins: Mapped[int] = mapped_column(default=0)

    vip: Mapped[bool] = mapped_column(default=False)

    banned: Mapped[bool] = mapped_column(default=False)

    is_searching: Mapped[bool] = mapped_column(default=False)
    
    partner_id: Mapped[int | None] = mapped_column(BigInteger, nullable=True)