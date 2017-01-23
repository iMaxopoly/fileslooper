import scrapy
from scrapy import Request

import reader
import writer
from report_structure import FilesloopReportRow

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


class TwoddlCyberlockerSpider(scrapy.Spider):
    __domain = "twoddl.tv"
    __protocol = "https"
    __baseURL = __protocol + "://" + __domain
    __write_dir = "debug"
    __write_filename = "twoddl_cyberlocker_url.txt"
    __read_filename = "debug/{0}/twoddl_url.txt"
    __timestamp = ""

    name = __domain
    allowed_domains = [__domain]
    start_urls = []

    def __init__(self, search_term, licensor_name, time_stamp, **kwargs):
        self.__timestamp = time_stamp
        self.__search_term = search_term
        self.__licensor_name = licensor_name
        self.__write_dir = self.__write_dir + "/" + time_stamp
        super(TwoddlCyberlockerSpider, self).__init__(**kwargs)

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
        cyberlocker_links = response.xpath("//div[@id='posts']//a/@href").extract()
        title = response.xpath("//title/text()").extract_first()
        for cyberlocker_link in cyberlocker_links:
            if "http://ul.to" in cyberlocker_link or \
                            "http://nitroflare.com/view/" in cyberlocker_link or \
                            "http://www.nitroflare.com/view/" in cyberlocker_link or \
                            "http://rapidgator.net/file/" in cyberlocker_link or \
                            "http://go4up.com/dl" in cyberlocker_link or \
                            "http://sh.st/" in cyberlocker_link or \
                            "https://uplod.ws" in cyberlocker_link or \
                            "http://uploaded.net/file" in cyberlocker_link or \
                            "http://www.filefactory.com/file/" in cyberlocker_link or \
                            "http://ouo.io/" in cyberlocker_link or \
                            "http://k2s.cc/file/" in cyberlocker_link:
                writer.write(self.__write_dir, self.__write_dir + "/" + self.__write_filename,
                             self.__licensor_name +
                             "<<@>>" + self.__search_term +
                             "<<@>>" + title +
                             "<<@>>" + response.meta['item']['filesloop_link'] +
                             "<<@>>" + response.meta['item']['search_engine_link'] +
                             "<<@>>" + cyberlocker_link)
