import io
import os
import time
import datetime

import sys
from gooey import Gooey, GooeyParser
from os import walk

from routine import routine


@Gooey(monospace_display=True, program_name="Flscpcrper 1.0 - A Filesloop Scraper")
def main():
    parser = GooeyParser(description="Flscpcrper is a filesloop scraper, or.. atleast pretends to be one.")
    parser.add_argument(
        'savepath', metavar='Reports save location',
        default="./Reports",
        help='Click the browse button to locate the directory where reports will be saved.',
        widget="DirChooser")
    parser.add_argument(
        'clientspath', metavar='Clients folder location',
        default="./Clients",
        help='Click the browse button to locate the Clients folder which contains text files containing brand names.',
        widget="DirChooser")
    parser.add_argument('-workers', default=30, type=int, help='Number of threads.')
    parser.add_argument("-alluc", action="store_true", help="Enables alluc engine")
    parser.add_argument("-filesbug", action="store_true", help="Enables filesbug engine")
    parser.add_argument("-filespr", action="store_true", help="Enables filespr engine")
    parser.add_argument("-fourshared", action="store_true", help="Enables 4shared engine")
    parser.add_argument("-irfree", action="store_true", help="Enables irfree engine")
    parser.add_argument("-rapid4me", action="store_true", help="Enables rapid4me engine")
    parser.add_argument("-rapidsearchengine", action="store_true",
                        help="Enables rapidsearchengine engine")
    parser.add_argument("-sharedir", action="store_true", help="Enables sharedir engine")
    parser.add_argument("-softarchive", action="store_true", help="Enables softarchive engine")
    parser.add_argument("-twoddl", action="store_true", help="Enables twoddl engine")
    parser.add_argument("-sceper", action="store_true", help="Enables sceper engine")

    args = parser.parse_args()

    timestamp = datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d-%H-%M-%S')

    files = []
    for (dirpath, dirnames, filenames) in walk(args.clientspath):
        files.extend(filenames)
        break

    client_dict = {}
    for m_file in files:
        licensor = m_file[0:-4]
        with io.open(args.clientspath + "/" + m_file, "r", encoding="utf-8") as fo:
            for line in fo:
                string_list = []
                if line != "" and line not in string_list:
                    brand = line.strip("\t\r\n '\"")
                    client_dict[brand] = licensor

    routine(client_dict, timestamp, args)


if __name__ == '__main__':
    nonbuffered_stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)
    sys.stdout = nonbuffered_stdout
    main()
