"""
Интерфейс командной строки для приложения генерации контента.
"""
import argparse
import sys
from colorama import init, Fore, Style
from chains import create_content_chain
from config import Config

# Инициализация colorama для цветного вывода
init(autoreset=True)


def print_header():
    """Вывод заголовка приложения"""
    print(Fore.CYAN + Style.BRIGHT + "=" * 80)
    print(Fore.CYAN + Style.BRIGHT + "  ГЕНЕРАТОР КОНТЕНТА С ИСПОЛЬЗОВАНИЕМ LLM ЦЕПОЧЕК")
    print(Fore.CYAN + Style.BRIGHT + "=" * 80)
    print()


def print_result(result):
    """
    Красивый вывод результатов генерации
    
    Args:
        result: Словарь с результатами генерации
    """
    print()
    print(Fore.GREEN + Style.BRIGHT + "✓ ГЕНЕРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
    print()
    
    # Шаг 1: Тема
    print(Fore.YELLOW + Style.BRIGHT + "━" * 80)
    print(Fore.YELLOW + Style.BRIGHT + "ШАГ 1: СГЕНЕРИРОВАННАЯ ТЕМА БЛОГ-ПОСТА")
    print(Fore.YELLOW + Style.BRIGHT + "━" * 80)
    print(Fore.WHITE + result['blog_idea'].strip())
    print()
    
    # Шаг 2: Блог-пост
    print(Fore.MAGENTA + Style.BRIGHT + "━" * 80)
    print(Fore.MAGENTA + Style.BRIGHT + "ШАГ 2: БЛОГ-ПОСТ (200-300 СЛОВ)")
    print(Fore.MAGENTA + Style.BRIGHT + "━" * 80)
    print(Fore.WHITE + result['blog_post'].strip())
    print()
    
    # Шаг 3: Пост для соцсетей
    print(Fore.BLUE + Style.BRIGHT + "━" * 80)
    print(Fore.BLUE + Style.BRIGHT + "ШАГ 3: ПОСТ ДЛЯ СОЦИАЛЬНЫХ СЕТЕЙ (до 280 символов)")
    print(Fore.BLUE + Style.BRIGHT + "━" * 80)
    print(Fore.WHITE + result['social_post'].strip())
    print()
    
    # Статистика
    print(Fore.CYAN + "━" * 80)
    print(Fore.CYAN + "СТАТИСТИКА:")
    print(Fore.CYAN + f"  Длина блог-поста: {len(result['blog_post'].split())} слов")
    print(Fore.CYAN + f"  Длина поста для соцсетей: {len(result['social_post'])} символов")
    print(Fore.CYAN + "━" * 80)
    print()


def interactive_mode():
    """Интерактивный режим работы приложения"""
    print_header()
    print(Fore.WHITE + "Добро пожаловать в интерактивный режим!")
    print()
    
    # Ввод темы
    print(Fore.YELLOW + "Введите область интересов для генерации контента:")
    print(Fore.WHITE + "Примеры: 'искусственный интеллект', 'здоровое питание', 'путешествия'")
    topic = input(Fore.GREEN + "➜ Тема: " + Fore.WHITE).strip()
    
    if not topic:
        print(Fore.RED + "✗ Ошибка: тема не может быть пустой")
        sys.exit(1)
    
    # Выбор стиля
    print()
    print(Fore.YELLOW + "Выберите стиль написания:")
    for i, style in enumerate(Config.AVAILABLE_STYLES, 1):
        print(Fore.WHITE + f"  {i}. {style}")
    
    try:
        style_choice = input(Fore.GREEN + "➜ Ваш выбор (1-4, по умолчанию 2): " + Fore.WHITE).strip()
        if not style_choice:
            style_choice = "2"
        style_index = int(style_choice) - 1
        if 0 <= style_index < len(Config.AVAILABLE_STYLES):
            style = Config.AVAILABLE_STYLES[style_index]
        else:
            print(Fore.YELLOW + "⚠ Используется стиль по умолчанию: неформальный")
            style = "неформальный"
    except ValueError:
        print(Fore.YELLOW + "⚠ Используется стиль по умолчанию: неформальный")
        style = "неформальный"
    
    # Генерация контента
    print()
    print(Fore.CYAN + "⏳ Генерация контента... Это может занять некоторое время.")
    print()
    
    try:
        chain = create_content_chain(style=style)
        result = chain.generate_content(topic)
        print_result(result)
        
        if Config.SAVE_TO_FILE:
            print(Fore.GREEN + f"✓ Результаты также сохранены в директории: {Config.OUTPUT_DIR}/")
        
    except Exception as e:
        print(Fore.RED + f"✗ Ошибка при генерации контента: {str(e)}")
        sys.exit(1)


def batch_mode(topic, style):
    """
    Пакетный режим для использования в скриптах
    
    Args:
        topic: Тема для генерации контента
        style: Стиль написания
    """
    try:
        chain = create_content_chain(style=style)
        result = chain.generate_content(topic)
        print_result(result)
        
    except Exception as e:
        print(Fore.RED + f"✗ Ошибка: {str(e)}")
        sys.exit(1)


def main():
    """Главная функция приложения"""
    parser = argparse.ArgumentParser(
        description="Генератор контента с использованием цепочек LLM",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Примеры использования:

  Интерактивный режим:
    python cli.py

  Пакетный режим:
    python cli.py --topic "искусственный интеллект" --style формальный
    python cli.py -t "здоровое питание" -s юмористический

  Доступные стили:
    формальный, неформальный, юмористический, профессиональный
        """
    )
    
    parser.add_argument(
        '-t', '--topic',
        type=str,
        help='Область интересов для генерации контента'
    )
    
    parser.add_argument(
        '-s', '--style',
        type=str,
        choices=Config.AVAILABLE_STYLES,
        default='неформальный',
        help='Стиль написания контента (по умолчанию: неформальный)'
    )
    
    parser.add_argument(
        '-i', '--interactive',
        action='store_true',
        help='Запуск в интерактивном режиме'
    )
    
    args = parser.parse_args()
    
    # Проверка аргументов
    if args.interactive or (not args.topic):
        interactive_mode()
    else:
        print_header()
        batch_mode(args.topic, args.style)


if __name__ == "__main__":
    main()