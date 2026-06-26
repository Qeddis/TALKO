from sqlalchemy import BigInteger, Boolean, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)

    username: Mapped[str | None]
    age: Mapped[int | None]
    gender: Mapped[str | None]
    search_gender: Mapped[str | None]
    country: Mapped[str | None]
    bio: Mapped[str | None]

    looking_for: Mapped[str | None]

    coins: Mapped[int] = mapped_column(default=0)
    vip: Mapped[bool] = mapped_column(default=False)
    banned: Mapped[bool] = mapped_column(default=False)
    reports: Mapped[int] = mapped_column(default=0)

    is_searching: Mapped[bool] = mapped_column(
        Boolean,
        default=False
    )

    partner_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True
    )


class BlockedUser(Base):
    __tablename__ = "blocked_users"
    __table_args__ = (UniqueConstraint("user_id", "blocked_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    blocked_id: Mapped[int] = mapped_column(BigInteger)


class Report(Base):
    __tablename__ = "reports"
    __table_args__ = (UniqueConstraint("reporter_id", "reported_id"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    reporter_id: Mapped[int] = mapped_column(BigInteger)
    reported_id: Mapped[int] = mapped_column(BigInteger)