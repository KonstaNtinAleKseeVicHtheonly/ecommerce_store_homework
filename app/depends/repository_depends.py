from typing import TypeVar, Type
from app.repositories import CategoryRepository, ProductRepository, UserRepository, ReviewRepository
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.depends.db_depends import get_db_session




def get_category_repository():
    return CategoryRepository()

def get_product_repository():
    return ProductRepository()

def get_user_repository():
    return UserRepository()

def get_review_repository():
    return ReviewRepository()