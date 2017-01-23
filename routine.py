import os
import io
import logging
import validators
import xlsxwriter
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from settings import G_SETTINGS
from submodules.alluc.alluc_cyberlocker import AllucCyberlockerSpider
from submodules.alluc.alluc_request import AllucRequestSpider
from submodules.filesbug.filesbug_cyberlocker import FilesbugCyberlockerSpider
from submodules.filesbug.filesbug_request import FilesbugRequestSpider
from submodules.filespr.filespr_request_and_cyberlocker import FilesprRequestAndCyberlockerSpider
from submodules.fourshared.fourshared_request_and_cyberlocker import FoursharedRequestAndCyberlockerSpider
from submodules.irfree.irfree_request import IrfreeRequestSpider
from submodules.rapid4me.rapid4me_cyberlocker import Rapid4meCyberlockerSpider
from submodules.rapid4me.rapid4me_request import Rapid4meRequestSpider
from submodules.rapidsearchengine.rapidsearchengine_cyberlocker import RapidsearchengineCyberlockerSpider
from submodules.rapidsearchengine.rapidsearchengine_request import RapidsearchengineRequestSpider
from submodules.sceper.sceper_cyberlocker import SceperCyberlockerSpider
from submodules.sceper.sceper_request import SceperRequestSpider
from submodules.sharedir.sharedir_cyberlocker import SharedirCyberlockerSpider
from submodules.sharedir.sharedir_request import SharedirRequestSpider
from submodules.softarchive.softarchive_request import SoftarchiveRequestSpider
from submodules.twoddl.twoddl_cyberlocker import TwoddlCyberlockerSpider
from submodules.twoddl.twoddl_request import TwoddlRequestSpider


def remove_file(filename):
    try:
        os.remove(filename)
    except OSError:
        pass


def join_files(timestamp, filenames):
    with open('./debug/' + timestamp + "/all.txt", 'a+') as outfile:
        for fname in filenames:
            if "cyberlocker" not in fname:
                continue
            with open('./debug/' + timestamp + "/" + fname) as infile:
                for line in infile:
                    outfile.write(line)


def prepare_report(savepath, timestamp):
    cyberlocker_link_files = []
    for (dirpath, dirnames, filenames) in os.walk("./debug/" + timestamp):
        cyberlocker_link_files.extend(filenames)
        break

    join_files(timestamp, cyberlocker_link_files)

    workbook = xlsxwriter.Workbook(savepath + "/" + timestamp + ".xlsx")
    worksheet = workbook.add_worksheet("filesloop_removeyourmedia")

    row = 0
    col = 0

    title_format = workbook.add_format()
    title_format.set_bold()
    title_format.set_bottom()
    title_format.set_align("center")
    title_format.set_font_name('Times New Roman')
    title_format.set_font_size(12)

    data_format = workbook.add_format()
    data_format.set_font_name('Verdana')
    data_format.set_font_size(9)
    data_format.set_text_v_align(3)

    cyberlocker_format = workbook.add_format()
    cyberlocker_format.set_font_name('Verdana')
    cyberlocker_format.set_font_size(9)
    cyberlocker_format.set_font_color('blue')

    worksheet.set_column(0, 0, 30)
    worksheet.set_column(1, 1, 30)
    worksheet.set_column(2, 2, 70)
    worksheet.set_column(3, 3, 70)
    worksheet.set_column(4, 4, 70)
    worksheet.set_column(5, 5, 70)

    worksheet.write_string(row, col, "Licensor", title_format)
    worksheet.write_string(row, col + 1, "Search_Term", title_format)
    worksheet.write_string(row, col + 2, "Cyberlocker_Pagetitle", title_format)
    worksheet.write_string(row, col + 3, "Filesloop_link", title_format)
    worksheet.write_string(row, col + 4, "Search_Engine_link", title_format)
    worksheet.write_string(row, col + 5, "Cyberlocker_link", title_format)
    row += 1

    with io.open('./debug/' + timestamp + "/all.txt", "r", encoding="utf-8") as f:
        for line in f:
            obj = line.split("<<@>>")
            if line == "" \
                    or len(obj) != 6 \
                    or not validators.url(obj[3], public=True) \
                    or not validators.url(obj[4], public=True) \
                    or not validators.url(obj[5], public=True):
                continue
            worksheet.write_string(row, col, obj[0], data_format)
            worksheet.write_string(row, col + 1, obj[1], data_format)
            worksheet.write_string(row, col + 2, obj[2], data_format)
            worksheet.write_string(row, col + 3, obj[3], data_format)
            worksheet.write_string(row, col + 4, obj[4], data_format)
            worksheet.write_string(row, col + 5, obj[5], cyberlocker_format)
            row += 1

    workbook.close()


@defer.inlineCallbacks
def crawl(client_dict, timestamp, args, runner):
    for search, licensor in client_dict.iteritems():
        if args.fourshared:
            yield runner.crawl(FoursharedRequestAndCyberlockerSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
        if args.filesbug:
            yield runner.crawl(FilesbugRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/filesbug_url.txt"):
                yield runner.crawl(FilesbugCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/filesbug_url.txt")
        if args.filespr:
            yield runner.crawl(FilesprRequestAndCyberlockerSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
        if args.irfree:
            yield runner.crawl(IrfreeRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
        if args.rapid4me:
            yield runner.crawl(Rapid4meRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/rapid4me_url.txt"):
                yield runner.crawl(Rapid4meCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/rapid4me_url.txt")
        if args.rapidsearchengine:
            yield runner.crawl(RapidsearchengineRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/rapidsearchengine_url.txt"):
                yield runner.crawl(RapidsearchengineCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/rapidsearchengine_url.txt")
        if args.sharedir:
            yield runner.crawl(SharedirRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/sharedir_url.txt"):
                yield runner.crawl(SharedirCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/sharedir_url.txt")
        if args.softarchive:
            yield runner.crawl(SoftarchiveRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
        if args.twoddl:
            yield runner.crawl(TwoddlRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/twoddl_url.txt"):
                yield runner.crawl(TwoddlCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/twoddl_url.txt")
        if args.alluc:
            yield runner.crawl(AllucRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/alluc_url.txt"):
                yield runner.crawl(AllucCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/alluc_url.txt")
        if args.sceper:
            print "Running sceper with", search, licensor
            yield runner.crawl(SceperRequestSpider, search_term=search, licensor_name=licensor,
                               time_stamp=timestamp)
            if os.path.isfile("./debug/" + timestamp + "/sceper_url.txt"):
                yield runner.crawl(SceperCyberlockerSpider, search_term=search, licensor_name=licensor,
                                   time_stamp=timestamp)
                os.remove("./debug/" + timestamp + "/sceper_url.txt")
    reactor.stop()


def routine(client_dict, timestamp, args):
    configure_logging(install_root_handler=False)
    logging.basicConfig(
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    runner = CrawlerRunner({
        "CONCURRENT_REQUESTS": 300,
        "CONCURRENT_REQUESTS_PER_DOMAIN": args.workers,
        "USER_AGENT": G_SETTINGS["G_USER_AGENT"],
    })

    print "Running arguments:", client_dict, args
    crawl(client_dict, timestamp, args, runner)
    reactor.run()
    prepare_report(args.savepath, timestamp)
    print "Done"
