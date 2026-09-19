from dataclasses import dataclass
import logging
import subprocess

YT_DLP_EXEC = "yt-dlp"
YTB_COOKIES = "cookie_ytb.txt"
BILI_COOKIES = "cookie_bili.txt"
PROXY = "socks5://127.0.0.1:XXXX/"

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

        record.mod_name = getattr(record, "mod_name", "-")

        return super().format(record)

def build_logger():
    handler = logging.StreamHandler()
    formatter = LogFormatter(
        fmt='%(header_color)s[%(levelname)s %(asctime)s %(mod_name)s]%(reset_style)s %(message)s',
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
            task.url
        ]
        subprocess.run(args)
        # print(args)

    @classmethod
    def fetch_metadata(cls):
        n = len(cls.tasks)
        for i, task in enumerate(cls.tasks):
            i += 1
            log.info(f"({i}/{n}) Fetching {task.url} ...", extra={"mod_name": task.source_name})
            cls.call_core(task)

            task.format_id = input(f">>> ({i}/{n}) Enter format ID (xx+xx, skip empty): ")

    @classmethod
    def download(cls):
        n = len(cls.tasks)
        for i, task in enumerate(cls.tasks):
            i += 1
            if task.format_id:
                log.info(f"({i}/{n}) Downloading {task.url} ...", extra={"mod_name": task.source_name})
                cls.call_core(task)
            else:
                log.info(f"({i}/{n}) Skipped {task.url} : Empty format ID", extra={"mod_name": task.source_name})

    @staticmethod
    def complete():
        log.info("")
        log.info(f"Complete")
        input(">>> Press enter to exit ...")

class DownloadTaskAdder:
    @staticmethod
    def ytb(id: str):
        Downloader.add_task(DownloadTask(
            source_name="ytb",
            format_id="",
            cookies=YTB_COOKIES,
            proxy=PROXY,
            url=f"https://www.youtube.com/watch?v={id}" if not id.startswith("http") else id
        ))

    @staticmethod
    def bili(id: str):
        Downloader.add_task(DownloadTask(
            source_name="bili",
            format_id="",
            cookies=BILI_COOKIES,
            proxy="",
            url=f"https://www.bilibili.com/video/{id}" if not id.startswith("http") else id
        ))

def main():
    DownloadTaskAdder.ytb("XXXXXXXXXXX")
    DownloadTaskAdder.bili("BVxxxxxxxxxx")

    Downloader.fetch_metadata()
    Downloader.download()
    Downloader.complete()

if __name__ == "__main__":
    main()
