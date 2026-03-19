
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
    
# # создания кучи товаров по категории смартфоны
# INSERT INTO products (name, description, price, image_url, stock, is_active, category_id, seller_id) VALUES 
# ('iPhone 15 Pro Max', 'Flagship smartphone with A17 Pro chip and titanium design', 105000, 'string', 5, true, 13, 5),
# ('iPhone 15 Pro', 'Powerful smartphone with advanced camera system', 95000, 'string', 8, true, 13, 5),
# ('iPhone 15', 'Standard model with Dynamic Island and USB-C', 75000, 'string', 12, true, 13, 5),
# ('iPhone 15 Plus', 'Larger display with all-day battery life', 85000, 'string', 10, true, 13, 5),
# ('iPhone 14 Pro', 'Pro model with A16 Bionic and Always-On display', 80000, 'string', 6, true, 13, 5),
# ('iPhone 14', 'Reliable smartphone with dual camera system', 65000, 'string', 15, true, 13, 5),
# ('iPhone 14 Plus', 'Big screen with great battery performance', 75000, 'string', 7, true, 13, 5),
# ('iPhone 13 Pro', 'Pro-grade camera and A15 Bionic chip', 70000, 'string', 4, true, 13, 5),
# ('iPhone 13', 'Balanced performance with vibrant display', 60000, 'string', 20, true, 13, 5),
# ('iPhone 13 Mini', 'Compact design with powerful performance', 55000, 'string', 10, true, 13, 5),
# ('iPhone 12 Pro Max', 'Large display with pro camera features', 65000, 'string', 3, true, 13, 5),
# ('iPhone 12', 'Sleek design with 5G support', 50000, 'string', 18, true, 13, 5),
# ('iPhone 12 Mini', 'Smallest iPhone with 5G and A14 chip', 45000, 'string', 12, true, 13, 5),
# ('iPhone SE (3rd Gen)', 'Affordable iPhone with A15 Bionic', 40000, 'string', 25, true, 13, 5),
# ('iPhone 11', 'Dual cameras and long battery life', 45000, 'string', 15, true, 13, 5),
# ('iPhone 11 Pro', 'Triple camera system with Night mode', 55000, 'string', 5, true, 13, 5),
# ('iPhone XR', 'Colorful design with Liquid Retina display', 35000, 'string', 20, true, 13, 5),
# ('iPhone XS Max', 'Large OLED display with A12 Bionic', 40000, 'string', 8, true, 13, 5),
# ('iPhone XS', 'Premium iPhone with dual cameras', 38000, 'string', 10, true, 13, 5),
# ('iPhone 8 Plus', 'Classic design with wireless charging', 30000, 'string', 15, true,13, 5);