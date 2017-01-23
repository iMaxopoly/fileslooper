import scrapy
import execjs
from scrapy import Request

import reader
import writer
from report_structure import FilesloopReportRow
from string_utils import find_between

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


class AllucCyberlockerSpider(scrapy.Spider):
    __domain = "www.alluc.ee"
    __protocol = "http"
    __baseURL = __protocol + "://" + __domain
    __read_path = "debug/{0}/alluc_url.txt"
    __write_dir = "debug"
    __write_filename = "alluc_cyberlocker.txt"
    __js_decrypt = execjs.compile(
        'function base64_decode(r){var e,t,o,n,a,i,d,h,'
        'c="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=",f=0,u=0,l="",s=[];if(!r)return '
        'r;r+="";do n=c.indexOf(r.charAt(f++)),a=c.indexOf(r.charAt(f++)),i=c.indexOf(r.charAt(f++)),d=c.indexOf('
        'r.charAt(f++)),h=n<<18|a<<12|i<<6|d,e=h>>16&255,t=h>>8&255,o=255&h,64==i?s[u++]=String.fromCharCode('
        'e):64==d?s[u++]=String.fromCharCode(e,t):s[u++]=String.fromCharCode(e,t,o);while(f<r.length);return '
        'l=s.join(""),l.replace(/\0+$/,"")}function ord(r){var e=r+"",t=e.charCodeAt(0);if(t>=55296&&56319>=t){var '
        'o=t;if(1===e.length)return t;var n=e.charCodeAt(1);return 1024*(o-55296)+(n-56320)+65536}return '
        't>=56320&&57343>=t?t:t}function decrypt(r,e){var t="";r=base64_decode(r);var o=0;for(o=0;o<r.length;o++){var '
        'n=r.substr(o,1),a=e.substr(o%e.length-1,1);n=Math.floor(ord(n)-ord(a)),n=String.fromCharCode(n),t+=n}return '
        't};')
    __timestamp = ""

    name = __domain
    allowed_domains = [__domain, "www.alluc.to"]
    start_urls = []

    custom_settings = {
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 503, 504, 400, 403, 408],
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 90,
            'scrapy_proxies.RandomProxy': 100,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },
        'PROXY_LIST': 'C:\Users\Eric\Desktop\\rotatingproxy.txt',
        'PROXY_MODE': 0,
        'CUSTOM_PROXY': "http://108.61.8.67:5008"
    }

    def __init__(self, search_term, licensor_name, time_stamp, **kwargs):
        self.__search_term = search_term
        self.__licensor_name = licensor_name
        self.__write_dir = self.__write_dir + "/" + time_stamp
        self.__timestamp = time_stamp
        super(AllucCyberlockerSpider, self).__init__(**kwargs)

    def start_requests(self):
        lines = reader.read(self.__read_path.format(self.__timestamp))
        for line in lines:
            obj = line.split("<<@>>")
            if len(obj) is not 4:
                continue
            item = FilesloopReportRow()
            item['filesloop_link'] = obj[2]
            item['search_engine_link'] = obj[3]
            yield Request(url=item['search_engine_link'], meta={'item': item}, callback=self.parse)

    def parse(self, response):
        check_valid_html = response.xpath("//span[@style='cursor:pointer;color:blue;']/text()").extract_first()
        if check_valid_html is None or "Add alluc to your browser" not in check_valid_html:
            print "invalid request", check_valid_html
            yield Request(url=response.url, dont_filter=True)

        iframe_src = response.xpath("//div[@id='actualPlayer']/iframe/@src").extract_first()
        if iframe_src is not None and iframe_src is not "":
            writer.write(self.__write_dir, self.__write_filename, iframe_src)

        script_list = response.xpath("//div[@id='linklistwrap']/div[@class='linktitleurl']/script/text()").extract()
        for script in script_list:
            script = script.strip()
            title = response.xpath("//title/text()").extract_first()
            code = find_between(script, "decrypt('", "', '")
            key = find_between(script, "', '", "' ));")
            print "@Alluc solving js key={0} and code={1}".format(key, code)
            try:
                cyberlocker_link = self.__js_decrypt.call("decrypt", code, key).strip()
            except RuntimeError:
                continue
            if cyberlocker_link is not None and cyberlocker_link is not "":
                writer.write(self.__write_dir, self.__write_dir + "/" + self.__write_filename,
                             self.__licensor_name +
                             "<<@>>" + self.__search_term +
                             "<<@>>" + title +
                             "<<@>>" + response.meta['item']['filesloop_link'] +
                             "<<@>>" + response.meta['item']['search_engine_link'] +
                             "<<@>>" + cyberlocker_link)
