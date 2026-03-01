import logging
import sys
from pathlib import Path




# Логи в папке "logs"
log_dir = Path(__file__).parent.parent / "project_logger" # создаем файл если его нет в app/core
log_file = log_dir / "app.log"


# Создаем папку, если нет ее
log_dir.mkdir(parents=True, exist_ok=True)

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.StreamHandler(sys.stdout),# вывод логов в консоль
        logging.FileHandler(log_file, encoding='utf-8')  #  Используем log_file для записи логов
    ]
)

# Создаем основной логгер для всего проекта
project_logger = logging.getLogger("ecommerce_project")
