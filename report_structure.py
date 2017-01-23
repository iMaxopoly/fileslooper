import scrapy
from scrapy import Field


class FilesloopReportRow(scrapy.Item):
    search_term = Field()
    filesloop_link = Field()
    search_engine_link = Field()
    cyberlocker_pagetitle = Field()
    cyberlocker_link = Field()
