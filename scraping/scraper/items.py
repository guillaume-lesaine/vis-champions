# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class GameItem(scrapy.Item):
    season = scrapy.Field()
    type = scrapy.Field()
    home_team = scrapy.Field()
    away_team = scrapy.Field()
    home_score = scrapy.Field()
    away_score = scrapy.Field()
    goals = scrapy.Field()
    location = scrapy.Field()
    cards = scrapy.Field()
    details = scrapy.Field()
