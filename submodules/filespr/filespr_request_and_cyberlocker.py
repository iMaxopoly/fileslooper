import json
import scrapy
from scrapy import Request
import writer
from report_structure import FilesloopReportRow

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


class FilesprRequestAndCyberlockerSpider(scrapy.Spider):
    __domain = "www.filesloop.com"
    __protocol = "https"
    __baseURL = __protocol + "://" + __domain
    __driver = "filespr"
    __write_dir = "debug"
    __write_filename = "filespr_cyberlocker_url.txt"
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
    allowed_domains = [__domain, "www.fileps.net"]

    def __init__(self, search_term, licensor_name, time_stamp, **kwargs):
        self.__search_term = search_term
        self.__licensor_name = licensor_name
        self.__write_dir = self.__write_dir + "/" + time_stamp
        super(FilesprRequestAndCyberlockerSpider, self).__init__(**kwargs)

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
        searchserver_pagetitle = response.xpath("//title/text()").extract_first()
        cyberlocker_links = response.xpath("//textarea/text()").extract_first()
        filesloop_link = response.meta['item']['filesloop_link']
        searchserver_link = response.url
        link_list = cyberlocker_links.split()
        for cyberlocker_link in link_list:
            writer.write(self.__write_dir, self.__write_dir + "/" + self.__write_filename,
                         self.__licensor_name +
                         "<<@>>" + self.__search_term +
                         "<<@>>" + searchserver_pagetitle +
                         "<<@>>" + filesloop_link +
                         "<<@>>" + searchserver_link +
                         "<<@>>" + cyberlocker_link)
