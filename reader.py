import io
import validators

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


def read(filename):
    with io.open(filename, "r", encoding="utf-8") as f:
        string_list = []
        for line in f:
            line = line.strip("\t\r\n '\"")
            obj = line.split("<<@>>")
            if line is "" \
                    or len(obj) is not 4 \
                    or not validators.url(obj[2], public=True) \
                    or not validators.url(obj[3], public=True) or line in string_list:
                continue

            string_list.append(line)
        return string_list
