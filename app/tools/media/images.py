from fastapi import HTTPException, UploadFile, status
import uuid
from app.core.project_logging import project_logger

from pathlib import Path
import aiofiles







async def save_product_image(
    file: UploadFile, 
    media_root: Path,  # 👈 передаем как параметр
    allowed_types: set = None,
    max_size: int = 5 * 1024 * 1024
) -> str:
    """
    Сохраняет изображение товара и возвращает относительный URL.
    """
    project_logger.info(f"СОхранение фотки продукта с именем {file.filename}")
    if allowed_types is None:
        allowed_types = {'image/jpeg', 'image/png', 'image/webp'}
    
    if file.content_type not in allowed_types:
        project_logger.warning(f"формата фотки {file.filename} нет в допустимых {allowed_types}")
        raise HTTPException(400, "Only JPG, PNG or WebP images are allowed")

    content = await file.read()
    if len(content) > max_size:
        project_logger.warning(f"Рамер фотки {file.filename} больше допустимого {max_size} размера ")
        raise HTTPException(400, "Image is too large")

    extension = Path(file.filename or "").suffix.lower() or ".jpg"
    file_name = f"{uuid.uuid4()}{extension}"
    file_path = media_root / file_name  # 👈 используем переданный путь
    #асинхронная запись
    async with aiofiles.open(file_path, 'wb') as f:
        await f.write(content)
    project_logger.warning(f"Запись фотки  {file.filename} произведена успешно")
    return f"/media/products/{file_name}" # filepath не подходит т.к это абсолютный путь и юзеру он не нужен

def remove_product_image(media_root:Path, file_url: str | None) -> None:
    """
    Удаляет файл изображения, если он существует.
    """
    project_logger.info(f"начало удаления файла по пути  {file_url}")
    if not file_url:
        return

    file_name = Path(file_url).name 
    file_path = media_root / file_name

    
    if file_path.exists():
        file_path.unlink()# удаление файла из папки
        project_logger.info(f"фотка удалена успешно {file_url}")
    else:
        project_logger.warning(f"фотки по маршруту {file_path} не найдено")