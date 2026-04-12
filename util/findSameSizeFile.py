#!/usr/bin/env python3
import argparse
from collections import defaultdict
import hashlib
import logging
from pathlib import Path
import sys

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
        datefmt='%H:%M:%S',
    )
    handler.setFormatter(formatter)
    logger = logging.getLogger(__name__)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    return logger

log = build_logger()

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

class FileSizeScanner:
    type SizeDict = dict[int, dict[str, set[Path]]]

    @staticmethod 
    def build_sizes(src_files: set[str]):
        size_factory = lambda: {"src": set(), "dst": set()}
        sizes: FileSizeScanner.SizeDict = defaultdict(size_factory)
        for src_file in src_files:
            src_file = Path(src_file).resolve()
            if src_file.is_file():
                sizes[src_file.stat().st_size]["src"].add(src_file)
            else:
                log.warning(f"Not a file: {src_file.as_posix()}")
        return sizes
  
    @staticmethod
    def scan_files(base_dir: Path, sizes: SizeDict):
        for root, dirs, files in base_dir.walk():
            for file in files:
                file = (root / file).resolve()

                if file.is_file():
                    size = sizes.get(file.stat().st_size)
                    if size and file not in size["src"]:
                        size["dst"].add(file)
                else:
                    log.warning(f"Not a file: {file.as_posix()}")
  
    @staticmethod
    def to_printable_result(sizes: SizeDict, *, color_output = True):
        result = []
        target_types = ("src", "dst")

        if color_output:
            size_color = "\033[97m"
            dst_color = "\033[93m"
            reset_style = "\033[0m"
        else:
            size_color = ""
            dst_color = ""
            reset_style = ""

        for size, type in sizes.items():
            if not type["dst"]:
                prefix = ", SRC ONLY"
            else:
                prefix = ""

            result.append(f"--- {size_color}{size} B ({FileSizeUtils.format(size)}){prefix} ---{reset_style}\n")

            for target_type in target_types:
                for src in type[target_type]:
                    if target_type == "dst":
                        dst_color2 = dst_color
                        reset_style2 = reset_style
                    else:
                        dst_color2 = ""
                        reset_style2 = ""

                    result.append(f"{dst_color2}<{target_type}>{reset_style2} {src.as_posix()}")
        
            result.append("")
        
        return "\n".join(result)
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Find same size files")

        parser.add_argument(
            "-s",
            action="append",
            dest="src_files",
            # An empty list is used by default, which is then converted into a set
            default=[],
            help="Source file"
        )

        parser.add_argument(
            "-d",
            type=lambda p: Path(p).resolve(),
            dest="base_dir",
            default=Path("/sdcard").resolve(),
            help="Scan base directory (default: /sdcard)"
        )

        parser.add_argument(
            "--no-color",
            action="store_false",
            dest="color_output",
            default=True,
            help="Disable color output"
        )

        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            dest="verbose",
            default=False,
            help="Verbose output"
        )

        args = parser.parse_args()

        if not args.src_files:
            log.error("No source file")
            sys.exit(1)

        args.src_files = set(args.src_files)

        return args

    @classmethod
    def run(cls):
        args = cls.parse_args()

        if args.verbose:
            log.setLevel(logging.DEBUG)

        LogFormatter.color_output = args.color_output
        
        log.debug(f"src_files: {args.src_files}")
        log.debug(f"base_dir: {args.base_dir}")

        log.info("Scanning files...")

        sizes = cls.build_sizes(args.src_files)
        cls.scan_files(args.base_dir, sizes)

        log.info("Files of same size:\n\n" + cls.to_printable_result(sizes, color_output=args.color_output))

if __name__ == "__main__":
    try:
        FileSizeScanner.run()
    except KeyboardInterrupt:
        log.info("Received interrupt signal, exiting...")
        sys.exit(130)
