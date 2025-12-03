"""
Конфигурационный модуль для управления настройками приложения
"""
import os
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


class Config:
    """Класс конфигурации приложения"""
    
    # API ключи
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    
    # Настройки модели
    USE_OLLAMA = os.getenv("USE_OLLAMA", "false").lower() == "true"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama2")
    USE_ANTHROPIC = os.getenv("USE_ANTHROPIC", "false").lower() == "true"
    
    # Параметры генерации
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    
    # Настройки вывода
    OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
    SAVE_TO_FILE = os.getenv("SAVE_TO_FILE", "true").lower() == "true"
    
    # Стили написания
    AVAILABLE_STYLES = ["формальный", "неформальный", "юмористический", "профессиональный"]
    
    @classmethod
    def validate(cls):
        """Проверка наличия необходимых настроек"""
        if not cls.USE_OLLAMA and not cls.OPENAI_API_KEY and not cls.ANTHROPIC_API_KEY:
            raise ValueError(
                "Необходимо установить OPENAI_API_KEY, ANTHROPIC_API_KEY или USE_OLLAMA=true в .env файле"
            )
        
        # Создание директории для вывода если она не существует
        if cls.SAVE_TO_FILE and not os.path.exists(cls.OUTPUT_DIR):
            os.makedirs(cls.OUTPUT_DIR)
    
    @classmethod
    def get_llm_type(cls):
        """Определение типа используемой LLM"""
        if cls.USE_OLLAMA:
            return "ollama"
        elif cls.USE_ANTHROPIC:
            return "anthropic"
        else:
            return "openai"