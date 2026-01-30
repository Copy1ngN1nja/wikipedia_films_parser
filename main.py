import subprocess
import sys
from pathlib import Path

def main():
    print("Запускаю парсер фильмов с Wikipedia...")
    
    # Абсолютный путь к проекту
    base_path = Path(__file__).parent.absolute()
    wiki_movies_path = base_path / "parse_films"
    
    try:
        print(f"Перехожу в: {wiki_movies_path}")
        print("Осуществляю парсинг...\n")
        result = subprocess.run(
            ["scrapy", "crawl", "wiki_spider"],
            cwd=wiki_movies_path,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        
        if result.stdout:
            print("\nВывод Scrapy:")
            print(result.stdout[-500:])
        
        if result.stderr:
            print("\nОшибки Scrapy:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\nScrapy завершился успешно!")
        else:
            print(f"\nScrapy завершился с кодом: {result.returncode}")
            
    except FileNotFoundError:
        print("Ошибка: Scrapy не найден!")
        print("Убедитесь, что Scrapy установлен в виртуальном окружении")
        print("Попробуйте: pip install scrapy")
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")

if __name__ == "__main__":
    main()