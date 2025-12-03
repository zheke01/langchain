"""
Модуль для создания и управления цепочками LLM
"""
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain_openai import OpenAI
from config import Config
import logging
from datetime import datetime
import os

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ContentGenerationChain:
    """Класс для управления цепочкой генерации контента"""
    
    def __init__(self, style="неформальный"):
        """
        Инициализация цепочки
        
        Args:
            style: Стиль написания контента (формальный, неформальный, юмористический)
        """
        Config.validate()
        self.style = style
        self.llm = self._initialize_llm()
        self.chain = self._create_chain()
    
    def _initialize_llm(self):
        """Инициализация языковой модели"""
        llm_type = Config.get_llm_type()
        logger.info(f"Инициализация LLM типа: {llm_type}")
        
        if llm_type == "ollama":
            from langchain.llms import Ollama
            return Ollama(
                model=Config.OLLAMA_MODEL,
                temperature=Config.TEMPERATURE
            )
        elif llm_type == "anthropic":
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model="claude-3-sonnet-20240229",
                temperature=Config.TEMPERATURE,
                api_key=Config.ANTHROPIC_API_KEY
            )
        else:
            return OpenAI(
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS,
                api_key=Config.OPENAI_API_KEY
            )
    
    def _create_chain(self):
        """Создание последовательной цепочки из трех шагов"""
        
        # Шаг 1: Генерация идеи для блог-поста
        idea_template = """Ты креативный контент-менеджер. 
        
Задача: Придумай интересную и актуальную тему для блог-поста в области: {topic}

Требования:
- Тема должна быть конкретной и привлекательной
- Должна вызывать интерес у целевой аудитории
- Должна быть релевантной современным трендам

Ответь только названием темы, без дополнительных объяснений.

Тема блог-поста:"""

        idea_prompt = PromptTemplate(
            input_variables=["topic"],
            template=idea_template
        )
        
        idea_chain = LLMChain(
            llm=self.llm,
            prompt=idea_prompt,
            output_key="blog_idea",
            verbose=True
        )
        
        # Шаг 2: Написание блог-поста
        post_template = """Ты опытный блогер и копирайтер.

Задача: Напиши короткий блог-пост на тему: {blog_idea}

Требования:
- Объем: 200-300 слов
- Стиль: {style}
- Структура: введение, основная часть, заключение
- Используй понятный язык
- Добавь практическую ценность для читателя

Блог-пост:"""

        post_prompt = PromptTemplate(
            input_variables=["blog_idea", "style"],
            template=post_template
        )
        
        post_chain = LLMChain(
            llm=self.llm,
            prompt=post_prompt,
            output_key="blog_post",
            verbose=True
        )
        
        # Шаг 3: Создание поста для социальных сетей
        social_template = """Ты SMM-специалист, эксперт по созданию вирусного контента.

Задача: Создай короткий пост для социальных сетей на основе этого блог-поста:

{blog_post}

Требования:
- Максимум 280 символов (включая хэштеги)
- Привлекательный и цепляющий текст
- 2-3 релевантных хэштега
- Призыв к действию или интригующий вопрос

Пост для соцсетей:"""

        social_prompt = PromptTemplate(
            input_variables=["blog_post"],
            template=social_template
        )
        
        social_chain = LLMChain(
            llm=self.llm,
            prompt=social_prompt,
            output_key="social_post",
            verbose=True
        )
        
        # Объединение всех цепочек в последовательную цепочку
        overall_chain = SequentialChain(
            chains=[idea_chain, post_chain, social_chain],
            input_variables=["topic", "style"],
            output_variables=["blog_idea", "blog_post", "social_post"],
            verbose=True
        )
        
        logger.info("Цепочка успешно создана")
        return overall_chain
    
    def generate_content(self, topic):
        """
        Генерация контента для заданной темы
        
        Args:
            topic: Область интересов для генерации контента
            
        Returns:
            dict: Словарь с результатами всех трех шагов
        """
        logger.info(f"Начало генерации контента для темы: {topic}")
        logger.info(f"Используемый стиль: {self.style}")
        
        try:
            # Выполнение цепочки
            result = self.chain({
                "topic": topic,
                "style": self.style
            })
            
            logger.info("Контент успешно сгенерирован")
            
            # Логирование промежуточных результатов
            self._log_intermediate_results(result)
            
            # Сохранение результатов в файл
            if Config.SAVE_TO_FILE:
                self._save_to_file(topic, result)
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при генерации контента: {str(e)}")
            raise
    
    def _log_intermediate_results(self, result):
        """Логирование промежуточных результатов каждого шага"""
        logger.info("=" * 80)
        logger.info("ПРОМЕЖУТОЧНЫЕ РЕЗУЛЬТАТЫ:")
        logger.info("=" * 80)
        
        logger.info("\n[ШАГ 1] Сгенерированная тема:")
        logger.info(result['blog_idea'])
        
        logger.info("\n[ШАГ 2] Блог-пост:")
        logger.info(result['blog_post'][:200] + "..." if len(result['blog_post']) > 200 else result['blog_post'])
        
        logger.info("\n[ШАГ 3] Пост для соцсетей:")
        logger.info(result['social_post'])
        
        logger.info("=" * 80)
    
    def _save_to_file(self, topic, result):
        """Сохранение результатов в текстовый файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{Config.OUTPUT_DIR}/content_{timestamp}.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"СГЕНЕРИРОВАННЫЙ КОНТЕНТ\n")
                f.write(f"Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Исходная тема: {topic}\n")
                f.write(f"Стиль: {self.style}\n")
                f.write("=" * 80 + "\n\n")
                
                f.write("ШАГ 1: ТЕМА БЛОГ-ПОСТА\n")
                f.write("-" * 80 + "\n")
                f.write(result['blog_idea'] + "\n\n")
                
                f.write("ШАГ 2: БЛОГ-ПОСТ\n")
                f.write("-" * 80 + "\n")
                f.write(result['blog_post'] + "\n\n")
                
                f.write("ШАГ 3: ПОСТ ДЛЯ СОЦИАЛЬНЫХ СЕТЕЙ\n")
                f.write("-" * 80 + "\n")
                f.write(result['social_post'] + "\n")
            
            logger.info(f"Результаты сохранены в файл: {filename}")
            
        except Exception as e:
            logger.error(f"Ошибка при сохранении в файл: {str(e)}")


def create_content_chain(style="неформальный"):
    """
    Фабричная функция для создания цепочки генерации контента
    
    Args:
        style: Стиль написания контента
        
    Returns:
        ContentGenerationChain: Экземпляр цепочки
    """
    return ContentGenerationChain(style=style)