import scrapy
import re


class WikiSpiderSpider(scrapy.Spider):
    name = "wiki_spider"
    allowed_domains = ["ru.wikipedia.org"]
    start_urls = ["https://ru.wikipedia.org/wiki/%D0%9A%D0%B0%D1%82%D0%B5%D0%B3%D0%BE%D1%80%D0%B8%D1%8F:%D0%A4%D0%B8%D0%BB%D1%8C%D0%BC%D1%8B_%D0%BF%D0%BE_%D0%B0%D0%BB%D1%84%D0%B0%D0%B2%D0%B8%D1%82%D1%83"]

    custom_settings = {
        'FEEDS': {
            'movies_data.csv': {
                'format': 'csv',
                'encoding': 'utf8',
                'overwrite': True,
            }
        },
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'DOWNLOAD_DELAY': 1, 
        'CONCURRENT_REQUESTS': 8,
    }

    def parse(self, response):
        """
        Находит ссылку на страницу фильма и переходит по ней
        """
        # итерируемся по всем категориям ьмов
        for group in response.css("div.mw-category-group"):
            
            # получаем список ссылок на страницы
            cur_group_film_links = group.css("ul li a::attr(href)").getall()

            # переходим по каждой ссылке
            for film_link in cur_group_film_links:
                yield response.follow(film_link, callback=self.parse_film_items)
                
        # находим ссылку на следующую страницу
        next_page_link = None
        all_hrefs = response.css("div#mw-pages a")
        for link in all_hrefs:
            link_text = link.css("::text").get()
            if link_text == "Следующая страница":
                next_page_link = link.css("::attr(href)").get()
                break
        
        # переход на следующую страницу
        if next_page_link:
            yield response.follow(next_page_link, callback=self.parse)


    def parse_film_items(self, response):
        """Выделяет основную информацию о фильме с его страницы"""
    
        film_items = {
            'Название': self.parse_title(response), 
            'Режиссёр': self.parse_director(response), 
            'Жанр': self.parse_genre(response), 
            'Страна': self.parse_countries(response), 
            'Год': self.parse_year(response)
        }

        if None in film_items.values():
            film_items_2 = self.extract_film_data(response)
            for key in film_items_2.keys():
                if film_items[key] is None:
                    film_items[key] = film_items_2[key]
        
        yield film_items
       
    def extract_film_data(self, response) -> dict:
        """
        Итерируется по таблице фильма, забирает основную информацию.
        Нужна для страниц, на которых некоторая информация является только текстом (не ссылкой)
        """
        data = {}
        
        for row in response.css('table.infobox tr'):
            header = row.css('th ::text').get()
            value_cell = row.css('td')
            
            if header and value_cell:
                header = header.strip().lower()
                value = ' '.join(value_cell.css('::text').getall()).strip()
        
                if header.find("год") + header.find("дат") != -2:
                    data['Год'] = self.check_year(value)
                elif header.find("стран"):
                    data['Страна'] = self.clean_str(value)
                elif header.find("жанр") != -1: 
                    data['Жанр'] = self.clean_str(value)
                elif header.find("режисс") != -1:
                    data['Режиссёр'] = self.clean_str(value)
        
        return data


    def parse_title(self, response) -> str:
        """
        Забирает название фильма
        """
        title = (
            response.css("h1.firstHeading span::text").get() or
            response.css("div.mw-content-ltr div.mw-parser-output p b::text").get() or
            response.css("table tbody th.infobox-above::text").get()
        )

        return title
    

    def parse_element_text(self, element) -> str|None:
        """
        Пытается забрать ифнормацию, всеми способами, пока не найдет ее
        или варианты не закончатся
        """
        text = (
            element.css("a::text").getall() or
            element.css("a span::text").getall() or
            element.css("span::text").getall() or
            element.css("a span::text").getall() or
            element.css("::text").getall() or 
            element.css("a::attr(title)").getall()
        )

        if text:
            text = ', '.join(text)
            if text.strip():
                return text
        
        return None
    

    def parse_genre(self, response) -> str|None:
        """
        Забирает жанр фильма
        """
        genre_data = response.css('[data-wikidata-property-id="P136"]')
        if genre_data:
            genre = self.parse_element_text(genre_data)
            return self.clean_str(genre)
        
        return None


    def parse_countries(self, response) -> str|None:
        """
        Забирает страны, в которых снимался фильм
        """
        countries_data = response.css('[data-wikidata-property-id="P495"]')
        if countries_data:
            countries = self.parse_element_text(countries_data)
            return self.clean_str(countries)
        
        return None


    def parse_director(self, response) -> str|None:
        """
        Находит имена режиссера/режиссеров
        """
        directors_data = response.css('[data-wikidata-property-id="P57"]')
        if directors_data:
            directors = self.parse_element_text(directors_data)
            return self.clean_str(directors)
        
        return None

        
    def parse_year(self, response) -> str|None:
        """
        Находит год выпуска фильма/год начала выхода сериала
        """
        if response.css('[data-wikidata-property-id="P577"]'):
            year_data = response.css('[data-wikidata-property-id="P577"]')
            year = self.parse_element_text(year_data)
        
        elif response.css('[data-wikidata-property-id="P580"]'):
            year_data = response.css('[data-wikidata-property-id="P580"]')
            year = self.parse_element_text(year_data)
        
        else:
            year = response.css('span.dtstart::text').getall()
            year = ' '.join(year)

        return self.check_year(year)


    def check_year(self, year) -> str|None:
        """
        Проверяет, есть ли год в строке.
        Возрващает год, в случае успеха, None иначе
        """
        if not year:
            return None
    
        matches = re.findall(r'\d{4}', str(year))
    
        for match in matches:
            if 1900 <= int(match) <= 2026:
                return match
    
        return None
    

    def clean_str(self, string) -> str|None:
        """
        Очищает строку, оставляя только алфавитные символы, символы пробела и запятой
        """
        if not string:
            return None
        
        cleaned_string = []
        for ch in string:
            if ch.isalpha() or ch == "," or ch == " ":
                cleaned_string.append(ch)
        
        return ''.join(cleaned_string).strip().strip(',')