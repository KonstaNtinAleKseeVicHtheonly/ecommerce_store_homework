from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.users import UserModel
from app.config import SECRET_KEY, ALGORITHM
from app.depends.db_depends import get_db_session
#repo
from app.repositories.user_rep import UserRepository
#custom depends
from app.depends.repository_depends import get_user_repository
from app.core.project_logging import project_logger



# Создаём контекст для хеширования с использованием bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


ACCESS_TOKEN_EXPIRE_MINUTES = 30 # время жизни jwt токена
REFRESH_TOKEN_EXPIRE_DAYS = 7         # New

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/token") # указываем url эндпоинта логина

def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    """
    project_logger.info("хэшируем пароль")
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    project_logger.info("Проверяем пароль на соответствие сохраненному хэшу")
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict): # прнимает инфу о юзере для payload в jwt
    """
    Создаёт JWT с payload (sub, role, id, exp).
    функия применяеься в post эндпионте после успешной аутентификации
    """
    project_logger.info(f"Начало создание jwt токена доступа юзера с данными {data}")
    to_encode = data.copy() #  Создаёт копию входного словаря data, чтобы избежать изменения оригинала
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # время жизни токена
    to_encode.update({"exp": expire,
                      'token_type' : 'access'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # кодируем данные от юзера

def create_refresh_token(data: dict): # прнимает инфу о юзере для payload в jwt
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    project_logger.info(f"Начало создание refresh токена доступа юзера с данными {data}")
    to_encode = data.copy() #  Создаёт копию входного словаря data, чтобы избежать изменения оригинала
    expire = datetime.now(timezone.utc) + timedelta(minutes=REFRESH_TOKEN_EXPIRE_DAYS) # время жизни токена
    to_encode.update({"exp": expire,
                      'token_type' : 'refresh'})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # кодируем данные от юзера




async def get_current_user(token: str = Depends(oauth2_scheme),
                           session: AsyncSession = Depends(get_db_session),
                           user_repo : UserRepository = Depends(get_user_repository)):
    """
    Проверяет JWT и возвращает пользователя из базы.Если таковой есть иначе ошибка
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email: str = payload.get("sub")
        project_logger.info(f"начало проверки данных от юзера {user_email} с jwt подписью ")
        if user_email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
    current_user = await user_repo.get_by_params(session, email=user_email, is_active=True)
    if current_user is None:
        project_logger('юзера с указанными данными не найден')
        raise credentials_exception
    project_logger.info("проверка завершена успешно")
    return current_user

async def get_current_seller(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'seller'.
    """
    if current_user.role != "seller":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sellers can perform this action")
    return current_user

async def get_current_buyer(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'buyer'.
    """
    if current_user.role != "buyer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only buyers can perform this action")
    return current_user


async def is_admin(current_user: UserModel = Depends(get_current_user)):
    if current_user.role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You're not an admin")
    return current_user