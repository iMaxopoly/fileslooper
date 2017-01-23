import scrapy
from scrapy import Request

import reader
import writer
from report_structure import FilesloopReportRow

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


class Rapid4meCyberlockerSpider(scrapy.Spider):
    __domain = "rapid4me.com"
    __protocol = "https"
    __baseURL = __protocol + "://" + __domain
    __write_dir = "debug"
    __write_filename = "rapid4me_cyberlocker_url.txt"
    __read_filename = "./debug/{0}/rapid4me_url.txt"
    __timestamp = ""

    name = __domain
    allowed_domains = [__domain]
    start_urls = []

    def __init__(self, search_term, licensor_name, time_stamp, **kwargs):
        self.__search_term = search_term
        self.__licensor_name = licensor_name
        self.__write_dir = self.__write_dir + "/" + time_stamp
        self.__timestamp = time_stamp
        super(Rapid4meCyberlockerSpider, self).__init__(**kwargs)

    def start_requests(self):
        lines = reader.read(self.__read_filename.format(self.__timestamp))
        for line in lines:
            obj = line.split("<<@>>")
            if len(obj) is not 4:
                continue
            item = FilesloopReportRow()
            item['filesloop_link'] = obj[2]
            item['search_engine_link'] = obj[3]
            yield Request(url=item['search_engine_link'], meta={'item': item}, callback=self.parse)

    def parse(self, response):
        title = response.xpath("//title/text()").extract_first()
        cyberlocker_link = response.xpath(
            "//a[contains(@class, 'main-btn') and contains(@class, 'font90') and contains(@class, "
            "'adddwnl')]/@href").extract_first()
        if cyberlocker_link is not None and cyberlocker_link is not "":
            writer.write(self.__write_dir, self.__write_dir + "/" + self.__write_filename,
                         self.__licensor_name +
                         "<<@>>" + self.__search_term +
                         "<<@>>" + title +
                         "<<@>>" + response.meta['item']['filesloop_link'] +
                         "<<@>>" + response.meta['item']['search_engine_link'] +
                         "<<@>>" + cyberlocker_link)
