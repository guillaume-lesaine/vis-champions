# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import JsonLinesItemExporter
from scrapy.exceptions import DropItem

class CompetitionGamePipeline(object):

    def process_item(self, item, spider):
        acceptable_types = [
            "Group stage",
            "Round of 16, 1st leg",
            "Round of 16, 2nd leg",
            "Quarter-finals, 1st leg",
            "Quarter-finals, 2nd leg",
            "Semi-finals, 1st leg",
            "Semi-finals, 2nd leg",
            "Final"]
        if item.get('type') in acceptable_types:
            return item
        else:
            raise DropItem(f"{item}: Not a competition game")

class JsonLinesExportPipeline(object):

    def open_spider(self, spider):
        self.season_to_exporter = {}

    def close_spider(self, spider):
        for exporter in self.season_to_exporter.values():
            exporter.finish_exporting()
            exporter.file.close()

    def _exporter_for_item(self, item):
        season = item["season"]
        if season not in self.season_to_exporter:
            f = open(f'./outputs/champions_league_{season}.json', 'wb')
            exporter = JsonLinesItemExporter(f)
            exporter.start_exporting()
            self.season_to_exporter[season] = exporter
        return self.season_to_exporter[season]

    def process_item(self, item, spider):
        exporter = self._exporter_for_item(item)
        exporter.export_item(item)
        return item
