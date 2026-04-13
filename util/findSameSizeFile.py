#!/usr/bin/env python3
import argparse
from collections import defaultdict
import hashlib
import logging
from os import stat_result
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

class FileHasher:
    # Fast hash file threshold, 3 MiB
    THRESHOLD = 1024 * 1024 * 3
    # Fast hash sample size, 64 KiB
    SAMPLE_SIZE = 1024 * 64

    type Hashes = dict[tuple[int, int], bytes]

    fast_hashes: Hashes = {}
    full_hashes: Hashes = {}

    @staticmethod
    def hasher():
        return hashlib.blake2b()
    
    @staticmethod
    def get_file_id(stat: stat_result):
        return (stat.st_dev, stat.st_ino)

    @classmethod
    def full_hash(cls, file: Path):
        file_id = cls.get_file_id(file.stat())
        cache = cls.full_hashes.get(file_id)
        if cache:
            return cache
        
        with open(file, "rb") as f:
            cls.full_hashes[file_id] = full_hash = hashlib.file_digest(f, cls.hasher).digest()
        
        return full_hash
    
    @classmethod
    def fast_hash(cls, file: Path):
        stat = file.stat()
        if stat.st_size < cls.THRESHOLD:
            return b''

        file_id = cls.get_file_id(stat)
        cache = cls.fast_hashes.get(file_id)
        if cache:
            return cache
        
        with open(file, "rb") as f:
            # head
            head_chunk = f.read(cls.SAMPLE_SIZE)

            # middle
            f.seek((file.stat().st_size // 2) - (cls.SAMPLE_SIZE // 2))
            middle_chunk = f.read(cls.SAMPLE_SIZE)

            # tail
            f.seek(-cls.SAMPLE_SIZE, 2)
            tail_chunk = f.read(cls.SAMPLE_SIZE)

        hasher = cls.hasher()
        hasher.update(head_chunk)
        hasher.update(middle_chunk)
        hasher.update(tail_chunk)

        cls.fast_hashes[file_id] = fast_hash = hasher.digest()

        return fast_hash
    
    @classmethod
    def compare(cls, file1: Path, file2: Path):
        file1_size = file1.stat().st_size

        if file1_size != file2.stat().st_size:
            return False
        if file1_size == 0:
            return True
        if cls.fast_hash(file1) != cls.fast_hash(file2):
            return False
        return cls.full_hash(file1) == cls.full_hash(file2)

class FileSet:
    def __init__(self):
        self.src: set[Path] = set()
        self.dst: set[Path] = set()

# size -> fast_hash -> full_hash -> src|dst -> Path
type FileHashMap = dict[int, dict[bytes, dict[bytes, FileSet]]]

class DuplicateFileScanner:
    @staticmethod
    def build_file_hash_map(src_files: list[str], hash=False):
        file_hash_map: FileHashMap = defaultdict(
            lambda: defaultdict(
                lambda: defaultdict(FileSet)
            )
        )

        fast_hash = b""
        full_hash = b""

        for file in src_files:
            file = Path(file).resolve()
            if file.is_file():
                if hash:
                    fast_hash = FileHasher.fast_hash(file)
                    full_hash = FileHasher.full_hash(file)

                file_hash_map \
                    [file.stat().st_size] \
                    [fast_hash] \
                    [full_hash] \
                    .src.add(file)
            else:
                log.debug(f"- Not a file: {file.as_posix()}")
        
        return file_hash_map
    
    @staticmethod
    def scan_files(file_hash_map: FileHashMap, base_dir: str, hash = False):
        for root, dirs, files in Path(base_dir).resolve().walk():
            for file in files:
                file = (root / file).resolve()

                if file.is_file():
                    if (
                        (v := file_hash_map.get(file.stat().st_size)) is not None
                        and (v := v.get(FileHasher.fast_hash(file) if hash else b"")) is not None
                        and (v := v.get(FileHasher.full_hash(file) if hash else b"")) is not None
                        and file not in v.src
                    ):
                        v.dst.add(file)
                else:
                    log.debug(f"- Not a file: {file.as_posix()}")
    
    @staticmethod
    def print_result(file_hash_map: FileHashMap, *, color_output = True):
        if color_output:
            size_color = "\033[97m"
            dst_color = "\033[93m"
            reset_style = "\033[0m"
        else:
            size_color = ""
            dst_color = ""
            reset_style = ""

        for group_id, (size, map0) in enumerate(file_hash_map.items()):
            for map1 in map0.values():
                for file_set in map1.values():
                    prefix = ", SRC ONLY" if not file_set.dst else ""
                
                    print(f"--- #{group_id + 1}, {size_color}{size} B ({FileSizeUtils.format(size)}){prefix} ---{reset_style}\n")

                    for file in file_set.src:
                        print(f"<src> {file.as_posix()}")
                    
                    # print()

                    for file in file_set.dst:
                        print(f"{dst_color}<dst>{reset_style} {file.as_posix()}")

                    print()
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Find same size files")

        parser.add_argument(
            "-s",
            action="append",
            dest="src_files",
            default=[],
            help="Source file"
        )

        parser.add_argument(
            "-d",
            dest="base_dir",
            default="/sdcard",
            help="Scan base directory (default: /sdcard)"
        )

        parser.add_argument(
            "-H", "--hash",
            action="store_true",
            dest="hash_compare",
            default=False,
            help="Hash compare (slow)"
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

        file_hash_map = cls.build_file_hash_map(args.src_files, args.hash_compare)
        cls.scan_files(file_hash_map, args.base_dir, args.hash_compare)

        log.info("Files of same size:")
        cls.print_result(file_hash_map, color_output=args.color_output)
    

if __name__ == "__main__":
    try:
        DuplicateFileScanner.run()
    except KeyboardInterrupt:
        log.info("Received interrupt signal, exiting...")
        sys.exit(130)
