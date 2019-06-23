import scrapy
from scraper.items import GameItem
from scrapy.selector import Selector
from selenium import webdriver
import time

class ChampionsSpider(scrapy.Spider):
    name = "champions"

    def __init__(self):
        self.driver = webdriver.Firefox()

    def start_requests(self):
        seasons = [2009]
        for season in seasons:
            url = f"https://www.uefa.com/uefachampionsleague/history/season={season}/matches/"
            yield scrapy.Request(url=url, callback=self.parse_scroller, meta={"season": season})

    def parse_scroller(self, response):
        self.driver.get(response.url)
        content = Selector(text=self.driver.page_source.encode('utf-8'))

        for game in content.xpath("//a[@class='match-row_link']"):
            page_details = game.attrib['href']
            page_details = response.urljoin(page_details)
            item = GameItem()
            item["season"] = response.meta["season"]
            meta = {"item": item}
            yield scrapy.Request(page_details, callback=self.parse_details, meta=meta)

    def parse_details(self, response):
        #print("--------")

        item = response.meta["item"]
        #print(item["season"])

        game_information = response.xpath("//span[@class='round-name']/text()").getall()
        item["type"] = "".join(game_information)
        print(item["type"])

        zone_teams = response.xpath("//div[@class='team-name']")
        game_teams = [x.xpath(".//span[@class='fitty-fit']/text()").get().strip() for x in zone_teams]
        item["home_team"], item["away_team"] = tuple(game_teams)
        #print(item["home_team"], item["away_team"])

        item["home_score"] = response.xpath("//span[@class='js-team--home-score']/text()").get()
        item["away_score"] = response.xpath("//span[@class='js-team--away-score']/text()").get()
        #print(item["home_score"], item["away_score"])

        goals = response.xpath("//li[@class='scorer']/text()").getall()
        goals = [x.strip().split("   ") for x in goals]
        goals = [list(filter(lambda x: True if x!="" else False, x)) for x in goals]
        goals = [{"player": x[0], "time": x[1]} for x in goals]
        item["goals"] = goals
        #print(item["goals"])

        item["location"] = response.xpath("//div[@class='stadium-info']").css('h2::text').get()
        #print(item["location"])

        cards = {"yellow": [], "red": []}
        cards["yellow"].append(response.xpath("//div[@class='yellow-cards--value graph-bar--number-value graph-bar--number-value__home-team']/text()").get())
        cards["yellow"].append(response.xpath("//div[@class='yellow-cards--value graph-bar--number-value graph-bar--number-value__away-team']/text()").get())
        cards["red"].append(response.xpath("//div[@class='red-cards--value graph-bar--number-value graph-bar--number-value__home-team']/text()").get())
        cards["red"].append(response.xpath("//div[@class='red-cards--value graph-bar--number-value graph-bar--number-value__away-team']/text()").get())
        cards["yellow"] = ["0" if not x else x for x in cards["yellow"]]
        cards["red"] = ["0" if not x else x for x in cards["red"]]
        item["cards"] = cards

        details = response.xpath("//div[@class='js-match-status-rw match-status-rw']/text()").get()
        print("========", details)
        if not details:
            item["details"] = ""
        else:
            item["details"] = details
        print("/////////", item["details"])

        yield item

    def get_personal_details_driver(self, response):
        item = response.meta['item']
        name = response.xpath("//h1[@class='kirk-title my-l']/text()").get()
        age = response.xpath("//p[@class='kirk-text kirk-text-body']/text()").get()

        item["driver"]={"name": name, "age":age}

        yield item

    def get_personal_details_passenger(self, response):
        item = response.meta["item"]
        driver_url = response.meta["driver_url"]
        passenger_urls_generator = response.meta["passenger_urls_generator"]

        name = response.xpath("//h1[@class='kirk-title my-l']/text()").get()
        age = response.xpath("//p[@class='kirk-text kirk-text-body']/text()").get()

        item["passengers"].append({"name": name, "age":age})

        try:
            passenger_url = next(passenger_urls_generator)
            meta = {"item": item, "driver_url": driver_url,"passenger_urls_generator":passenger_urls_generator}
            yield scrapy.Request(passenger_url, callback=self.get_personal_details_passenger, meta=meta)
        except:
            meta = {"item": item}
            yield scrapy.Request(driver_url, callback=self.get_personal_details_driver, meta=meta)
