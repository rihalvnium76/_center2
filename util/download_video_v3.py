import argparse
from dataclasses import dataclass
import logging
import subprocess

YT_DLP_EXEC = "yt-dlp"
YTB_COOKIES = "cookie_ytb.txt"
BILI_COOKIES = "cookie_bili.txt"
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
    logger.setLevel(logging.INFO)
    return logger

log = build_logger()

@dataclass
class DownloadTask:
    source_name: str
    format_id: str
    cookies: str
    proxy: str
    url: str

class Downloader:
    tasks: list[DownloadTask] = []

    @classmethod
    def add_task(cls, task: DownloadTask):
        cls.tasks.append(task)

    @staticmethod
    def call_core(task: DownloadTask):
        args = [
            YT_DLP_EXEC,
            *(["-f", task.format_id] if task.format_id else ["-F"]),
            "--js-runtimes", "node",
            "--cookies", task.cookies,
            *(["--proxy", task.proxy] if task.proxy else []),
            *([] if ConsoleUtils.color_output else ["--color", "no_color"]),
            *(["-o", "%(uploader)s/%(id)s_%(title)s.%(ext)s"] if task.format_id else []),
            task.url
        ]
        subprocess.run(args)
        # print(args)

    @classmethod
    def fetch_metadata(cls):
        n = len(cls.tasks)
        for i, task in enumerate(cls.tasks):
            i += 1
            log.info(f"Fetching {task.url} ...", extra={"ext_info": f"{task.source_name} {i}/{n}"})
            cls.call_core(task)

            task.format_id = ConsoleUtils.input(f"({i}/{n}) Enter format ID (xx+xx, skip empty):")

    @classmethod
    def download(cls):
        n = len(cls.tasks)
        for i, task in enumerate(cls.tasks):
            i += 1
            if task.format_id:
                log.info(f"Downloading {task.url} ...", extra={"ext_info": f"{task.source_name} {i}/{n}"})
                cls.call_core(task)
            else:
                log.info(f"Skipped {task.url} : Empty format ID", extra={"ext_info": f"{task.source_name} {i}/{n}"})

    @staticmethod
    def complete():
        log.info(f"")
        log.info(f"Completed")
        ConsoleUtils.input("Press enter to exit ...")

class DownloadTaskAdder:
    @staticmethod
    def get_url(template: str, id: str):
        return template.format(id=id) if not id.startswith("http") else id
    
    @classmethod
    def ytb(cls, id: str):
        Downloader.add_task(DownloadTask(
            source_name="ytb",
            format_id="",
            cookies=YTB_COOKIES,
            proxy=PROXY,
            url=cls.get_url("https://www.youtube.com/watch?v={id}", id)
        ))

    @classmethod
    def bili(cls, id: str):
        Downloader.add_task(DownloadTask(
            source_name="bili",
            format_id="",
            cookies=BILI_COOKIES,
            proxy="",
            url=cls.get_url("https://www.bilibili.com/video/{id}", id)
        ))

class App:
    @staticmethod
    def parse_args():
        p = argparse.ArgumentParser(
            description="Video Downloader",
            formatter_class=argparse.RawTextHelpFormatter
        )

        p.add_argument("--no-color", action="store_false", dest="color", help="Disable console color output")

        args = p.parse_args()

        ConsoleUtils.color_output = args.color

    @staticmethod
    def add_tasks():
        # DownloadTaskAdder.ytb("xxxxxxxxx")
        DownloadTaskAdder.bili("BVxxxxxxxx")

    @classmethod
    def main(cls):
        cls.parse_args()

        cls.add_tasks()

        Downloader.fetch_metadata()
        Downloader.download()
        Downloader.complete()

if __name__ == "__main__":
    App.main()
