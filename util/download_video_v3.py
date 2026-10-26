import argparse
from dataclasses import dataclass
import logging
import random
import shlex
import subprocess
import os
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
YT_DLP_EXEC = os.path.join(SCRIPT_DIR, "yt-dlp.exe")
YTB_COOKIES = os.path.join(SCRIPT_DIR, "cookie_ytb.txt")
BILI_COOKIES = os.path.join(SCRIPT_DIR, "cookie_bili.txt")
PROXY = "socks5://127.0.0.1:xxxx/"

class ConsoleUtils:
    DEFAULT_HEADER_COLOR = "\033[97m"
    RESET_STYLE = "\033[0m"
    
    color_output = True

    @classmethod
    def input(cls, prompt: str):
        if cls.color_output:
            header_color = cls.DEFAULT_HEADER_COLOR
            reset_style = cls.RESET_STYLE
        else:
            header_color = ""
            reset_style = ""
        
        return input(f"{header_color}>>> {prompt}{reset_style} ")

class LogFormatter(logging.Formatter):
    HEADER_COLORS = {
        "D": "\033[34m",
        "I": "\033[32m",
        "W": "\033[93m",
        "E": "\033[91m",
        "C": "\033[91m",
    }

    @staticmethod
    def get_with_prefix(record: logging.LogRecord, name: str):
        v = getattr(record, name, "")
        return " " + v if v else ""

    def format(self, record):
        record.levelname = level = record.levelname[0]

        if ConsoleUtils.color_output:
            record.header_color = self.HEADER_COLORS.get(level, ConsoleUtils.DEFAULT_HEADER_COLOR)
            record.reset_style = ConsoleUtils.RESET_STYLE
        else:
            record.header_color = ""
            record.reset_style = ""

        record.ext_info = self.get_with_prefix(record, "ext_info")

        return super().format(record)

def build_logger():
    handler = logging.StreamHandler()
    formatter = LogFormatter(
        fmt='%(header_color)s[%(levelname)s %(asctime)s%(ext_info)s]%(reset_style)s %(message)s',
        # full: %Y-%m-%d %H:%M:%S
        datefmt='%H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

log = build_logger()

@dataclass
class DownloadTask:
    source_name: str
    format_id: str
    cookies: str
    proxy: str
    url: str
    dir: str

class Downloader:
    tasks: list[DownloadTask] = []
    verbose_output = False
    failed_tasks: list[DownloadTask] = []

    @classmethod
    def add_task(cls, task: DownloadTask):
        cls.tasks.append(task)

    @classmethod
    def call_core(cls, task: DownloadTask):
        args = [
            YT_DLP_EXEC,
            *(["-v"] if cls.verbose_output else []),
            *(["-f", task.format_id] if task.format_id else ["-F"]),
            "--js-runtimes", "node",
            "--cookies", task.cookies,
            *(["--proxy", task.proxy] if task.proxy else []),
            *([] if ConsoleUtils.color_output else ["--color", "no_color"]),
            *(["-o", os.path.join(os.path.abspath(task.dir), "%(uploader)s", "%(id)s_%(title)s.%(ext)s")] if task.format_id else []),
            task.url
        ]
        return subprocess.run(args).returncode
        # log.debug(f"$ {shlex.join(args)}", extra={"ext_info": "core (dry)"}); return 0

    @staticmethod
    def delay(enabled = True, prompt_header = ""):
        if not enabled:
            return
        
        # delay_sec = random.randint(10, 50) / 10
        delay_sec = 1
        log.info(f"Waiting for {delay_sec} second(s) ...", extra={"ext_info": prompt_header})
        time.sleep(delay_sec)

    @classmethod
    def fetch_metadata(cls):
        n = len(cls.tasks)
        for i, task in enumerate(cls.tasks):
            i += 1
            prompt_header = f"{i}/{n} {task.source_name}"

            log.info(f"Fetching {task.url} ...", extra={"ext_info": prompt_header})
            if cls.call_core(task):
                cls.failed_tasks.append(task)
            else:
                task.format_id = ConsoleUtils.input(f"({prompt_header}) Enter format ID (xx+xx, skip empty):")

    @classmethod
    def download(cls):
        n = len(cls.tasks)
        for i, task in enumerate(cls.tasks):
            i += 1
            prompt_header = f"{i}/{n} {task.source_name}"

            if task.format_id:
                cls.delay(i != 1, prompt_header)
                log.info(f"Downloading {task.url} ...", extra={"ext_info": prompt_header})
                if cls.call_core(task):
                    cls.failed_tasks.append(task)
            else:
                log.info(f"Skipped {task.url} : Empty format ID", extra={"ext_info": prompt_header})

    @classmethod
    def complete(cls):
        log.info(f"")
        if cls.failed_tasks:
            log.error("Failed tasks:\n" + "\n".join([f"{i + 1}: {task.url}" for i, task in enumerate(cls.failed_tasks)]))
        else:
            log.info(f"Completed")
        
        ConsoleUtils.input("Press enter to exit ...")

class DownloadTaskAdder:
    def __init__(self, dir = ""):
        self.dir = dir or os.getcwd()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        pass

    @staticmethod
    def get_url(template: str, id: str):
        return template.format(id=id) if not id.startswith("http") else id
    
    def ytb(self, id: str):
        Downloader.add_task(DownloadTask(
            source_name="ytb",
            format_id="",
            cookies=YTB_COOKIES,
            proxy=PROXY,
            url=self.get_url("https://www.youtube.com/watch?v={id}", id),
            dir=self.dir,
        ))

    def bili(self, id: str):
        Downloader.add_task(DownloadTask(
            source_name="bili",
            format_id="",
            cookies=BILI_COOKIES,
            proxy="",
            url=self.get_url("https://www.bilibili.com/video/{id}", id),
            dir=self.dir,
        ))

class App:
    @staticmethod
    def parse_args():
        p = argparse.ArgumentParser(
            description="Video Downloader",
            formatter_class=argparse.RawTextHelpFormatter
        )

        p.add_argument("-v", "--verbose", action="store_true", dest="verbose", help="Print various debugging information")
        p.add_argument("--no-color", action="store_false", dest="color", help="Disable console color output")

        args = p.parse_args()

        ConsoleUtils.color_output = args.color
        Downloader.verbose_output = args.verbose

    @staticmethod
    def add_tasks():
        with DownloadTaskAdder(r"F:\AVideo\bdvideo") as a:
            # a.ytb("xxx")
            a.bili("BVxxx")

    @classmethod
    def main(cls):
        cls.parse_args()

        cls.add_tasks()

        Downloader.fetch_metadata()
        Downloader.download()
        Downloader.complete()

if __name__ == "__main__":
    App.main()
