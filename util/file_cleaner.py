from datetime import datetime
import logging
from pathlib import Path
import sys
import time


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
    def format(self, record):
        record.levelname = record.levelname[0]
        return super().format(record)

def build_logger():
    handler = logging.StreamHandler()
    formatter = LogFormatter(
        fmt='[%(levelname)s %(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger

log = build_logger()

class FileCleaner:
    def clean(
        self,
        cleanable: bool,
        target_dir: Path,
        # second
        start_timestamp: int | None = None,
        # second
        end_timestamp: int | None = None,
    ):
        count = 0
        size = 0

        target_files: list[Path] = []
        max_recorded_file_count = 10

        last_log = time.time()
        interval = 5
        
        action = "已发现"
        if cleanable:
            action = "已删除"
        
        if start_timestamp is None and end_timestamp is None:
            log.error("日期范围不能均为空")
            sys.exit(1)

        for root, dirs, files in target_dir.walk():
            for file in files:
                file = root / file
                stat = file.stat()
                mtime = stat.st_mtime

                if (start_timestamp is None or mtime >= start_timestamp) and (end_timestamp is None or mtime < end_timestamp):
                    if cleanable:
                        try:
                            file.unlink()
                        except FileNotFoundError:
                            continue

                    count += 1
                    size += stat.st_size

                    if not cleanable and len(target_files) < max_recorded_file_count:
                        target_files.append(file)
                    
                    if time.time() - last_log >= interval:
                        log.info(f"{action} {count} 个文件，共计 {FileSizeUtils.format(size)}")
                        last_log = time.time()
        
        log.info(f"{action} {count} 个文件，共计 {FileSizeUtils.format(size)}")
        for file in target_files:
            log.debug(f"- {file.as_posix()}")
        
        log.info("完成")
    
    def run(self):
        date_pattern = "%Y%m%d"

        log.debug(f"argv: {sys.argv}")

        args = iter(sys.argv)
        cleanable = False
        target_dir = Path(r"D:\Documents\Tencent Files\123456879\Image")
        start_timestamp = None
        end_timestamp = None

        for arg in args:
            if arg == "-D":
                cleanable = True
            elif arg == "-p":
                target_dir = Path(next(args))
            elif arg == "-a":
                start_timestamp = int(datetime.strptime(next(args), date_pattern).timestamp())
            elif arg == "-b":
                end_timestamp = int(datetime.strptime(next(args), date_pattern).timestamp())
        
        if target_dir is None:
            log.error("目标目录不能为空")
            sys.exit(1)

        self.clean(
            cleanable=cleanable,
            target_dir=target_dir,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp,
        )

if __name__ == "__main__":
    FileCleaner().run()