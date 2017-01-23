import json
import scrapy
from scrapy import Request
import writer
from report_structure import FilesloopReportRow
from settings import G_SETTINGS

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


class FoursharedRequestAndCyberlockerSpider(scrapy.Spider):
    __domain = "www.filesloop.com"
    __protocol = "https"
    __baseURL = __protocol + "://" + __domain
    __driver = "4shared"
    __write_dir = "debug"
    __write_filename = "4shared_cyberlocker.txt"
    __search_term = ""
    __licensor_name = ""

    __engine_request_url = "https://www.filesloop.com/fileslist/get/" + __driver
    __engine_request_content_type = {
        "Content-Type": "application/json",
        "Requested-With-AngularJS": "true"
    }
    __engine_request_method = "POST"
    __engine_request_page_number = 0

    name = __domain
    allowed_domains = [__domain]

    def __init__(self, search_term, licensor_name, time_stamp, **kwargs):
        self.__search_term = search_term
        self.__licensor_name = licensor_name
        self.__write_dir = self.__write_dir + "/" + time_stamp
        super(FoursharedRequestAndCyberlockerSpider, self).__init__(**kwargs)

    def start_requests(self):
        yield Request(
            url=self.__engine_request_url,
            method=self.__engine_request_method,
            body=json.dumps({
                "search": self.__search_term, "server": "all", "order": "relevance", "filesize": "all", "ext": "all",
                "page": self.__engine_request_page_number, "driver": self.__driver
            }),
            headers=self.__engine_request_content_type
        )

    def parse(self, response):
        json_response = json.loads(response.body_as_unicode())

        files = json_response["files"]
        if len(files) <= 0:
            return

        self.__engine_request_page_number += 1

        yield Request(
            url=self.__engine_request_url,
            method=self.__engine_request_method,
            body=json.dumps(
                {
                    "search": self.__search_term, "server": "all", "order": "relevance", "filesize": "all",
                    "ext": "all", "page": self.__engine_request_page_number, "driver": self.__driver
                }),
            headers=self.__engine_request_content_type,
            dont_filter=True,
            callback=self.parse
        )

        for f in files:
            serverclass = f["serverclass"]
            file_url = f["url"].strip()
            if serverclass != self.__driver or file_url is "":
                continue
            item = FilesloopReportRow()
            item['filesloop_link'] = response.urljoin(file_url)
            request = Request(response.urljoin(file_url), callback=self.parse_exit_filesloop_page, meta={'item': item})
            yield request

    def parse_exit_filesloop_page(self, response):
        searchserver_link = response.url
        searchserver_pagetitle = response.xpath("//title/text()").extract_first()
        filesloop_link = response.meta['item']['filesloop_link']
        cyberlocker_link = response.xpath("//div[@class='iframe']/iframe/@src").extract_first().strip()
        if cyberlocker_link is not None and cyberlocker_link is not "":
            writer.write(self.__write_dir, self.__write_dir + "/" + self.__write_filename,
                         self.__licensor_name +
                         "<<@>>" + self.__search_term +
                         "<<@>>" + searchserver_pagetitle +
                         "<<@>>" + filesloop_link +
                         "<<@>>" + searchserver_link +
                         "<<@>>" + cyberlocker_link)
