from .categories import category_api_router
from .products import product_api_router
from .users import user_api_router
from .reviews import review_api_router
from .carts import carts_api_router
from .orders import orders_api_router 
from .payments import payments_api_router



__all__ = [
    'category_api_router', 
    'product_api_router', 
    'user_api_router', 
    'review_api_router', 
    'carts_api_router', 
    'orders_api_router',
    'payments_api_router']
