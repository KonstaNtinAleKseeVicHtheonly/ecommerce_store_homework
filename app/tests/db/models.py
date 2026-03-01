
from sqlalchemy.schema import CreateTable
from app.models.products import ProductModel
from app.models.categories import CategoryModel
from app.core.project_logging import project_logger
# импорты моих будущих моделей
# from app.models.db.cart import Cart
# from app.models.db.order import Order
# from app.models.db.user import User


def create_table(table_obj):
    try:
        return CreateTable(table_obj.__table__)
    except Exception as err:
        project_logger.error(f"Ошибка при тесте создания таблицы {table_obj.__name__} : {err}")
        return None

if __name__ == "__main__":
    # Output CREATE TABLE statements
    print(CreateTable(CategoryModel.__table__))
    print(CreateTable(ProductModel.__table__))
    
    #  принты таблиц будущих моделей
    # print(CreateTable(Cart.__table__))
    # print(CreateTable(Order.__table__))
    # print(CreateTable(User.__table__))