from pydantic import BaseModel, Field, ConfigDict, field_validator
from decimal import Decimal
from app.models import ProductModel, CartItemModel
from app.schemas.products_schemas import ProductSchema


# вообще нужая для масштабирования но хер с ней
# class CartItemSchemaBase(BaseModel):
#     """
#     Используется как основа для других схем к CartItem с общими полями

#     """
#     product_id: int = Field(..., description="id товара при добавлении в корзину")
#     quantity : int  = Field(..., description="количество товара")


class CartItemCreateSchema(BaseModel):
    """
    Модель для создания и обновления категории.
    Используется в POST
    """
    product_id: int = Field(..., description="id товара при добавлении в корзину")
    quantity : int  = Field(..., ge=1, description="количество товара")


class CartItemUpdateSchema(BaseModel):
    """Модель для обновления количества товара в корзине.
    без product_id что бы не бло подмены id продукта"""
    
    quantity : int  = Field(..., description="Новое количество товара")





class CartItemSchema(BaseModel):
    """ Выходная модель отображающая опред позицию товара в корзине юзера"""
    id: int = Field(..., description="ID позиции корзины")
    quantity: int = Field(..., ge=0, description="Количество товара")
    product: ProductSchema = Field(..., description="Информация о товаре") # вложенная модель с полной информацией о товаре (название, цена, фото и т.д.).

    model_config = ConfigDict(from_attributes=True)

class TotalCartSchema(BaseModel):
    '''Выходная модель выводящая всю корзину юзера со всеми товарами'''
    user_id: int = Field(..., description="ID пользователя")
    items: list[CartItemSchema] = Field(default_factory=list, description="Содержимое корзины") # список вложенных моделей CartItem.Создаем новый список при каждом новом объекте TotalCart
    total_quantity: int = Field(..., ge=0, description="Общее количество товаров")
    total_price: Decimal = Field(..., ge=0, description="Общая стоимость товаров")

    model_config = ConfigDict(from_attributes=True)




