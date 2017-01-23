import os
import io

if __name__ == "__main__":
    print("file is meant for import.")
    exit()


def write(directory, filename, content):
    if not os.path.exists(directory):
        os.makedirs(directory)
    with io.open(filename, "a+", encoding="utf-8") as f:
        f.write(unicode(content))
        f.write(u"\n")
