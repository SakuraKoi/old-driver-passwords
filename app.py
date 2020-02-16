from argparse import ArgumentParser
from pathlib import Path


def cli_main():
    pass


def cli_sort(dictionary: str = "resource/dictionary.txt"):
    """排序去重
    """
    print("start: sort")
    with open(dictionary, "rt", encoding="utf-8") as _in:
        content = [i.rstrip("\n").encode("utf-8")
                   for i in _in.readlines() if i != ""]
    listing = sorted(list(set(content)))
    with open(dictionary, "wb") as _out:
        _out.write(b"\n".join(listing))
    print("end: sort")


if __name__ == "__main__":
    cli_sort()
