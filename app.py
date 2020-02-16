from argparse import ArgumentParser
from pathlib import Path
from subprocess import PIPE
from subprocess import DEVNULL
from subprocess import run
from sys import exit


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


def cli_test(compressed: str, dictionary: str = "resource/dictionary.txt"):
    """测试解压密码"""
    # 测试 7z 是否存在
    try:
        exe7z = run(["7z", "-version"], stdout=PIPE,
                    stderr=PIPE, encoding="utf-8")
    except FileNotFoundError:
        print("7z 不存在，请安装： https://www.7-zip.org/")
        exit(-1)

    with open(dictionary, "rt", encoding="utf-8") as _dict:
        key = (i.rstrip("\n")
               for i in iter(lambda: _dict.readline(), ""))
        for n, i in enumerate(key):
            try:
                result = run(["7z", "x", "-y", "-oout", "-p{}".format(i),
                              compressed], stdout=DEVNULL, stderr=PIPE, encoding="utf-8")
                print("{}: #{}#".format(n, i))
                if result.returncode == 0:
                    print("findout: --- #{}# ---".format(i))
                    break
                else:
                    if "Wrong password" in result.stderr:
                        continue
                    else:
                        print("unknown error")
                        break
            except Exception as e:
                print(e)
                break
        else:
            print("no password matched.")


if __name__ == "__main__":
    cli_test("README.zip")
