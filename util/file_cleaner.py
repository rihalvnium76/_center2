import argparse
from dataclasses import dataclass
from datetime import datetime
from genericpath import isfile
import logging
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable


class FileSizeUtils:
    SIZE_UNITS = ("B", "KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "NiB")

    @classmethod
    def format(cls, byte_size: int | float, precision=2):
        unit = cls.SIZE_UNITS[0]
        for unit in cls.SIZE_UNITS:
            if byte_size < 1024:
                break
            byte_size /= 1024
        return f"{byte_size:.{precision}f} {unit}"

class LogFormatter(logging.Formatter):
    HEADER_COLORS = {
        "D": "\033[34m",
        "I": "\033[32m",
        "W": "\033[93m",
        "E": "\033[91m",
        "C": "\033[91m",
    }
    DEFAULT_HEADER_COLOR = "\033[97m"
    RESET_STYLE = "\033[0m"

    color_output = True

    def format(self, record):
        record.levelname = level = record.levelname[0]

        if self.color_output:
            record.header_color = self.HEADER_COLORS.get(level, self.DEFAULT_HEADER_COLOR)
            record.reset_style = self.RESET_STYLE
        else:
            record.header_color = ""
            record.reset_style = ""

        return super().format(record)

def build_logger():
    handler = logging.StreamHandler()
    formatter = LogFormatter(
        fmt='%(header_color)s[%(levelname)s %(asctime)s]%(reset_style)s %(message)s',
        # full: %Y-%m-%d %H:%M:%S
        datefmt='%H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

log = build_logger()

class DateTimeUtils:
    DATETIME_PATTERNS = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y%m%d %H%M%S",
        "%Y%m%d",
    ]

    @classmethod
    def to_mtime(cls, v: str):
        for pattern in cls.DATETIME_PATTERNS:
            try:
                return datetime.strptime(v, pattern).timestamp()
            except ValueError:
                pass

class Params(argparse.Namespace):
    dir: str
    after: float | None
    before: float | None
    yes: bool
    color: bool
    sort: str

@dataclass
class File:
    path: str
    size: int
    mtime: float

    @classmethod
    def from_stat(cls, path: str, stat: os.stat_result):
        return cls(
            path=path,
            size=stat.st_size,
            mtime=stat.st_mtime
        )


class Progress:
    interval = 5

    def __init__(
        self,
        total_count = 0,
        name = "",
    ):
        self.total_count = f"/{total_count}" if total_count else ""
        self.name = f"- ({name}) " if name else "- "

        self.unmodified = True
        self.acc_count = 0

        self.last_time = time.monotonic()
        self.last_count = 0
        self.last_size = 0

    def output(self, check_interval = True):
        if self.unmodified:
            return
        
        elapsed_time = (now := time.monotonic()) - self.last_time
        if check_interval and elapsed_time < self.interval:
            return
        
        self.unmodified = True
        self.last_time = now
        
        count_per_sec = self.last_count / elapsed_time
        self.last_count = 0

        if self.last_size:
            size_per_sec = f", {FileSizeUtils.format(self.last_size / elapsed_time)}/s"
            self.last_size = 0
        else:
            size_per_sec = ""
        
        log.info(f"{self.name}已处理: {self.acc_count}{self.total_count} 项 ({count_per_sec:.1f} 项/秒{size_per_sec})")
    
    def stat(self, size: int):
        self.unmodified = False
        self.acc_count += 1

        self.last_count += 1
        self.last_size += size

        self.output()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.output(False)
    
    def stat_item(self):
        self.stat(0)

    def stat_file(self, file: File):
        self.stat(file.size)

class FileCleaner:
    @classmethod
    def walk_dir(cls, real_path: str, visited: set[str]):
        visited.add(real_path)

        with os.scandir(real_path) as entries:
            for entry in entries:
                path = os.path.realpath(entry.path)
                if entry.is_file():
                    yield File.from_stat(path, entry.stat())
                elif entry.is_dir():
                    if path not in visited:
                        yield from cls.walk_dir(path, visited)

    @classmethod
    def scan_files(cls, args: Params) -> list[File]:
        log.info("正在扫描文件 ...")

        files: list[File] = []
        size = 0
        with Progress() as p:
            for file in cls.walk_dir(os.path.realpath(args.dir), set()):
                if (args.after is None or file.mtime >= args.after) and (args.before is None or file.mtime <= args.before):
                    files.append(file)
                    size += file.size
                    p.stat_item()
        
        log.info(f"已发现 {len(files)} 个待清理文件，总计 {FileSizeUtils.format(size)}:")

        files.sort(key=(lambda f: f.mtime) if args.sort == "mtime" else (lambda f: f.size), reverse=True)

        for i in range(min(10, len(files))):
            file = files[i]
            log.info(f"- {file.path} ({FileSizeUtils.format(file.size)}, {datetime.fromtimestamp(file.mtime).strftime("%Y-%m-%d %H:%M:%S")})")

        if files and (args.yes or input(">>> 是否清理文件？[Y/N] ").lower() == "y"):
            return files
        
        return []
    
    @staticmethod
    def remove_files(files: list[File]):
        if not files:
            return
        
        log.info("正在删除文件 ...")

        size = 0
        with Progress(total_count=len(files)) as p:
            for file in files:
                try:
                    os.remove(file.path)
                    # log.debug(f"- {file.path}")
                    size += file.size
                    p.stat_file(file)
                except FileNotFoundError:
                    pass
                except Exception as e:
                    log.warning(f"- 无法删除 {file.path}: {e}")
        
        log.info(f"已清理 {len(files)} 个文件，总计 {FileSizeUtils.format(size)}")

    @staticmethod
    def parse_args():
        cwd = os.getcwd()

        p = argparse.ArgumentParser(description="文件按日期批量清理")
        p.add_argument("-d", "--dir", nargs="?", default=cwd, const=cwd, help="扫描目录")
        p.add_argument("-a", "--after", nargs="?", type=DateTimeUtils.to_mtime, help="起始文件修改时间")
        p.add_argument("-b", "--before", nargs="?", type=DateTimeUtils.to_mtime, help="结束文件修改时间")
        p.add_argument("-y", "--yes", action="store_true", help="静默删除")
        p.add_argument("--no-color", action="store_false", dest="color", help="禁用控制台彩色输出")
        p.add_argument("-s", "--sort", nargs="?", default="size", const="size", help="降序排序方式：size - 按大小；mtime - 按修改日期")

        return p.parse_args(namespace=Params())
    
    @classmethod
    def run(cls):
        args = cls.parse_args()
        LogFormatter.color_output = args.color
        log.debug(f"入参: {args}")

        if args.after is None and args.before is None:
            log.error("起始日期和结束日期不能同时为空")
            sys.exit(1)

        files = cls.scan_files(args)
        cls.remove_files(files)

if __name__ == "__main__":
    FileCleaner.run()
