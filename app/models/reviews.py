from app.core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import CheckConstraint, String, Boolean, Text, Integer, ForeignKey, Numeric, BigInteger, DateTime
from decimal import Decimal
from datetime import datetime, date
from sqlalchemy import Index, UniqueConstraint





class  ReviewModel(Base):
    '''модель отвечающая за отзывы юзеров(User) на товары(Product)'''
    __tablename__ = 'reviews'
    
    __table_args__ = (
        CheckConstraint('grade >= 1 AND grade <= 5', name='valid_rating'),
    )
    
    id: Mapped[int] = mapped_column(primary_key=True)
    # внешние ключи
    product_id : Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    user_id : Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    #инфа об отзыве
    comment : Mapped[str|None]  = mapped_column(Text,nullable= True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    grade : Mapped[int]  = mapped_column(Integer,nullable= False)
    is_active : Mapped[bool] = mapped_column(Boolean, default=True)
    
    # связи 
    product : Mapped['ProductModel'] = relationship("ProductModel", back_populates='product_reviews')
    user : Mapped['UserModel'] = relationship("UserModel", back_populates='user_reviews')
    