from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, Integer, ForeignKey, Numeric, BigInteger, DateTime
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import Index, UniqueConstraint


class UserModel(Base):
        __tablename__ = "users"
        # индексы
        __table_args__ = (
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_role', 'role'))

        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        email: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
        hashed_password: Mapped[str] = mapped_column(String, nullable=False)
        is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
        role: Mapped[str] = mapped_column(String, default="buyer", index=True)  # "buyer" or "seller"
        # свзи с другими моделями
        products: Mapped[list["ProductModel"]] = relationship("ProductModel", back_populates="seller")
        user_reviews : Mapped['ReviewModel'] = relationship('ReviewModel', back_populates='user')        
