BOT_NAME = "parse_films"

SPIDER_MODULES = ["parse_films.spiders"]
NEWSPIDER_MODULE = "parse_films.spiders"

ADDONS = {}

ROBOTSTXT_OBEY = False

# Concurrency and throttling settings
CONCURRENT_REQUESTS = 8
CONCURRENT_REQUESTS_PER_DOMAIN = 8
DOWNLOAD_DELAY = 1


FEED_EXPORT_ENCODING = "utf-8"
# Настройки для экспорта в CSV
FEED_FORMAT = 'csv'
FEED_URI = 'movies_data.csv'
FEED_EXPORT_ENCODING = 'utf-8'
FEED_EXPORT_FIELDS = ['Название', 'Режиссёр', 'Жанр', 'Страна', 'Год']