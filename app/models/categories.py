from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class CategoryModel(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # самоссылка
    parent_id : Mapped[int | None] = mapped_column(ForeignKey('categories.id'), nullable=True)
    parent :  Mapped['CategoryModel | None'] = relationship('CategoryModel', back_populates='children', remote_side='CategoryModel.id') 
    children: Mapped[list["CategoryModel"]] = relationship("CategoryModel",
                                                      back_populates="parent")
    #отношения к другим таблицам
    products : Mapped[list["ProductModel"]] = relationship("ProductModel", back_populates='category')
    
    
