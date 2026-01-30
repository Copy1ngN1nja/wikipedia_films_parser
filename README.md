# Парсер фильмов с Wikipedia

Парсер для сбора информации о фильмах с русскоязычной Википедии.

## Возможности

- Сбор данных о 37,000+ фильмах
- Извлечение названия, года, страны, жанра, режиссера
- Сохранение в CSV формате

## Установка

1. Установите [uv](https://github.com/astral-sh/uv)
2. Клонируйте репозиторий:
```bash
git clone https://github.com/Copy1ngN1nja/wikipedia_films_parser.git
cd wikipedia_films_parser
```
3. Создайте виртуальное окружение и установите зависимости:
```bash
uv sync
```
4. Запуск **Scrapy**:
```bash 
cd parse_films
cd parse_films
scrapy crawl wiki_spider
```
или
```bash
python3 main.py
```