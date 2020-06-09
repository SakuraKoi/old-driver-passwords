import json
from argparse import ArgumentParser
from hashlib import md5
from pathlib import Path
from subprocess import DEVNULL, PIPE, run
from sys import exit, stdin
from typing import *


def cli_main():
    parser = ArgumentParser("drivers-dict")
    command = parser.add_subparsers(title="subcommands", dest="command")
    sort = command.add_parser("sort", description="排序字典中的密码，会剔除重复项")
    sort.add_argument("-d",
                      "--dictionary",
                      help="specific the dictionary file",
                      default="resource/dictionary.txt")
    test = command.add_parser("test", description="使用字典中存储的密码逐个尝试解压")
    test.add_argument("archive", help="specific the archive file to extract")
    test.add_argument("-d",
                      "--dictionary",
                      help="specific the dictionary file",
                      default="resource/dictionary.txt")
    add = command.add_parser("add", description="向字典中添加密码，每行一个，可读取文件或 stdin")
    add.add_argument("-d",
                     "--dictionary",
                     help="specific the dictionary file",
                     default="resource/dictionary.txt")
    add.add_argument("INPUT",
                     nargs="?",
                     help="输入文件路径，若留空则从 stdin 读取密码",
                     default=None)
    args = parser.parse_args()

    if "test" == args.command:
        cli_test(args.archive, args.dictionary)
    elif "sort" == args.command:
        cli_sort(args.dictionary)
    elif "add" == args.command:
        cli_add(args.dictionary, args.INPUT)
    elif "query" == args.command:
        pass


def cli_add(dictionary: str = "resource/dictionary.txt",
            input: Optional[str] = None):
    """添加密码，从文件或 stdin 读取
    """
    if input is None:
        src = stdin.read()
    else:
        print("start: add")
        src = Path(input).read_text("utf-8")
    newpasswords = set([i for i in src.split("\n") if i != ""])
    try:
        oldpasswords = set([
            i for i in Path(dictionary).read_text("utf-8").split("\n")
            if i != ""
        ])
    except FileNotFoundError:
        oldpasswords = set()
    passwords = oldpasswords | newpasswords
    sorted_password = [i for i in passwords]
    sorted_password.sort()
    Path(dictionary).write_text("\n".join(sorted_password), "utf-8")
    print("end: add")


def cli_sort(dictionary: str = "resource/dictionary.txt"):
    """排序去重
    """
    print("start: sort")
    try:
        oldpasswords = set([
            i for i in Path(dictionary).read_text("utf-8").split("\n")
            if i != ""
        ])
    except FileNotFoundError:
        oldpasswords = set()
    newpasswords = sorted(list(oldpasswords))
    Path(dictionary).write_text("\n".join(newpasswords), "utf-8")
    print("end: sort")


# todo API 已变更，找到新的 API
def deprecated_cli_query(filepath: str):
    """向 cjtecc 查询解压密码
    """
    api = "http://app.cjtecc.cn/compress.yun.php"
    content = Path(filepath).read_bytes()
    hashcode = md5(content).hexdigest()
    url = api.format(md5code=hashcode)
    resp = requests.get(url, params={"md5": hashcode})
    if resp.status_code == 200:
        answer = resp.text
        if answer == "no":
            print("没有数据")
        else:
            print(answer)
            obj = json.loads(answer)
            print(f"#{obj['password']}#")
    else:
        raise ValueError(f"无正常响应：{resp.status_code}, {hashcode}")


def cli_test(compressed: str, dictionary: str = "resource/dictionary.txt"):
    """测试解压密码"""
    # 测试 7z 是否存在
    try:
        # todo 用 ctypes 重构
        exe7z = run(["7z", "-version"],
                    stdout=PIPE,
                    stderr=PIPE,
                    encoding="utf-8")
    except FileNotFoundError:
        print("7z 不存在，请安装： https://www.7-zip.org/")
        exit(-1)

    with open(dictionary, "rt", encoding="utf-8") as _dict:
        key = (i.rstrip("\n") for i in iter(lambda: _dict.readline(), ""))
        for n, i in enumerate(key):
            try:
                result = run(
                    ["7z", "x", "-y", "-oout", "-p{}".format(i), compressed],
                    stdout=DEVNULL,
                    stderr=PIPE,
                    encoding="utf-8")
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
    cli_main()
