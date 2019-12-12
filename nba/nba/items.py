# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NbaTeamItem(scrapy.Item):
    match_time = scrapy.Field()
    match_time_old_style = scrapy.Field()
    team_name = scrapy.Field()
    status = scrapy.Field()
    lineup_players = scrapy.Field()
    injure_players = scrapy.Field()
    rival = scrapy.Field()
