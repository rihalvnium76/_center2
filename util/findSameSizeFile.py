#!/usr/bin/env python3
import argparse
from collections import defaultdict
from datetime import datetime
import hashlib
import logging
from os import stat_result
import os
from pathlib import Path
import sys
import time
from typing import Any, Callable

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

class FileProgress:
    FAST_HASH_SAMPLE_SIZE = FileHasher.SAMPLE_SIZE * 3

    def __init__(self,
        output_fn: Callable[[str], None] | None = None,
        interval = 5,
    ):
        self.interval = interval
        self.output_fn: Callable[[str], None] = output_fn if callable(output_fn) else log.info

        self.total_count = 0

        self.last_time = time.time()
        self.last_count = 0
        self.last_size = 0
        self.outputted = False
    
    def output(self, immediate = False):
        now = time.time()
        elapsed_time = now - self.last_time
        if self.outputted or (not immediate and elapsed_time < self.interval):
            return
        self.outputted = True
        self.last_time = now

        count_per_sec = self.last_count / elapsed_time
        self.last_count = 0

        if self.last_size:
            size_per_sec = FileSizeUtils.format(self.last_size / elapsed_time)
            size_per_sec = f", {size_per_sec}/s"
        else:
            size_per_sec = ""
        self.last_size = 0

        self.output_fn(f"- Processed: {self.total_count} files ({count_per_sec:.1f} files/s{size_per_sec})")

    def record(self, size: int):
        self.outputted = False

        self.total_count += 1

        self.last_count += 1
        self.last_size += size

        self.output()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.output(True)

    def record_memory_item(self):
        self.record(0)
    
    def record_fast_hash(self, hash: bytes):
        self.record(self.FAST_HASH_SAMPLE_SIZE if hash else 0)
    
    def record_full_hash(self, file: Path):
        self.record(file.stat().st_size)

class DuplicateFileScanner:
    DATETIME_PATTERNS = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y%m%d %H%M%S",
        "%Y%m%d",
    ]

    @classmethod
    def to_mtime(cls, arg: str):
        if arg == "-":
            return None

        for pattern in cls.DATETIME_PATTERNS:
            try:
                return datetime.strptime(arg, pattern).timestamp()
            except ValueError:
                pass
        
        try:
            return os.stat(arg).st_mtime
        except Exception:
            log.error(f"Not a datetime or path: {arg}")
            sys.exit(1)

    @classmethod
    def build_src_set(cls, sources: set[Path], source_ranges: list[list[str]], prog: FileProgress):
        src_set: set[Path] = set()
        visited_dir: set[Path] = set()

        for src in sources:
            # src = Path(src).resolve()
            
            if src.is_file():
                src_set.add(src)
                prog.record_memory_item()
            
            elif src.is_dir():
                for root, dirs, files in src.walk(follow_symlinks=True):
                    abs_root = root.resolve()
                    if abs_root in visited_dir:
                        dirs.clear()
                        continue
                    visited_dir.add(abs_root)

                    for file in files:
                        file = (root / file).resolve()
                        if file.is_file():
                            src_set.add(file)
                            prog.record_memory_item()
        
        for src_dir, start_time, end_time in source_ranges:
            start_time = cls.to_mtime(start_time)
            end_time = cls.to_mtime(end_time)

            if not os.path.isdir(src_dir):
                log.error(f"Not a directory: {src_dir}")
                sys.exit(1)

            for root, dirs, files in Path(src_dir).resolve().walk():
                for file in files:
                    file = (root / file).resolve()
                    prog.record_memory_item()
                    if file.is_file():
                        mtime = file.stat().st_mtime
                        if (start_time is None or mtime >= start_time) and (end_time is None or mtime <= end_time):
                            src_set.add(file)

        log.debug(f"src_set: {src_set}")
        return src_set

    @staticmethod
    def group_size(src_set: set[Path], base_dir: Path, prog: FileProgress):
        size_bucket: dict[int, set[Path]] = defaultdict(set)

        for src in src_set:
            size_bucket[src.stat().st_size].add(src)
            prog.record_memory_item()

        for root, dirs, files in base_dir.walk():
            for file in files:
                dst = (root / file).resolve()
                prog.record_memory_item()
                if dst.is_file() and (size := dst.stat().st_size) in size_bucket:
                    size_bucket[size].add(dst)
        
        return size_bucket

    @staticmethod
    def group_fast_hash(src_set: set[Path], size_bucket: dict[int, set[Path]], prog: FileProgress):
        fast_hash_bucket: dict[bytes, set[Path]] = defaultdict(set)

        for src in src_set:
            hash = FileHasher.fast_hash(src)
            fast_hash_bucket[hash].add(src)
            prog.record_fast_hash(hash)

        for file_set in size_bucket.values():
            for file in file_set:
                hash = FileHasher.fast_hash(file)
                prog.record_fast_hash(hash)
                if hash in fast_hash_bucket:
                    fast_hash_bucket[hash].add(file)
        
        return fast_hash_bucket
        
    @staticmethod
    def group_full_hash(src_set: set[Path], fast_hash_bucket: dict[bytes, set[Path]], prog: FileProgress):
        full_hash_bucket: dict[bytes, set[Path]] = defaultdict(set)

        for src in src_set:
            full_hash_bucket[FileHasher.full_hash(src)].add(src)
            prog.record_full_hash(src)

        for file_set in fast_hash_bucket.values():
            for file in file_set:
                hash = FileHasher.full_hash(file)
                prog.record_full_hash(file)
                if hash in full_hash_bucket:
                    full_hash_bucket[hash].add(file)
        
        return full_hash_bucket

    @staticmethod
    def print_result(bucket: dict[Any, set[Path]], src_set: set[Path], color_output = True):
        if color_output:
            size_color = "\033[97m"
            dst_color = "\033[93m"
            reset_style = "\033[0m"
        else:
            size_color = ""
            dst_color = ""
            reset_style = ""
        
        for group_id, file_set in enumerate(bucket.values()):
            src_list = []
            dst_list = []
            size = -1

            for file in file_set:
                if size == -1:
                    size = file.stat().st_size

                if file in src_set:
                    src_list.append(file)
                else:
                    dst_list.append(file)
                
            prefix = ", SRC ONLY" if not dst_list else ""
            formatted_size = FileSizeUtils.format(size)

            print(f"{size_color}--- #{group_id + 1}, {size} B ({formatted_size}){prefix} ---{reset_style}\n")

            for src in src_list:
                print(f"<src> {src.as_posix()}")

            for dst in dst_list:
                print(f"{dst_color}<dst>{reset_style} {dst.as_posix()}")

            print()
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Find same size/hash files")

        parser.add_argument(
            "-s", "--source",
            action="extend",
            nargs="+",
            type=lambda p: Path(p).resolve(),
            dest="sources",
            default=[],
            help="Source file or directory",
            metavar="SRC",
        )

        parser.add_argument(
            "-S", "--source-range",
            action="append",
            nargs=3,
            dest="source_ranges",
            default=[],
            help="Source files under DIR with mtime from START to END (yyyy-MM-dd HH:mm:ss). File args use their mtime; - = unbounded",
            metavar=("DIR", "START", "END"),
        )

        parser.add_argument(
            "-d", "--base-dir",
            type=lambda p: Path(p).resolve(),
            dest="base_dir",
            help="Scan base directory (default: /sdcard)",
            metavar="DIR",
        )

        parser.add_argument(
            "-H", "--hash",
            action="store_true",
            dest="hash_compare",
            default=False,
            help="Hash compare (slow)"
        )

        parser.add_argument(
            "-v", "--verbose",
            action="store_true",
            dest="verbose",
            default=False,
            help="Verbose output"
        )

        parser.add_argument(
            "--no-color",
            action="store_false",
            dest="color_output",
            default=True,
            help="Disable color output"
        )

        parser.add_argument(
            "--no-progress",
            action="store_false",
            dest="progress_output",
            default=True,
            help="Disable progress output"
        )

        args = parser.parse_args()

        if not args.sources and not args.source_ranges:
            log.error("No source file or directory")
            sys.exit(1)
        
        args.sources = set(args.sources)

        return args
    
    @classmethod
    def run(cls):
        args = cls.parse_args()

        if args.verbose:
            log.setLevel(logging.DEBUG)
        LogFormatter.color_output = args.color_output

        output_fn = None
        if not args.progress_output:
            output_fn = lambda x: None
        
        log.debug(args)

        log.info("Scanning source files...")
        with FileProgress(output_fn) as prog:
            src_set = cls.build_src_set(args.sources, args.source_ranges, prog)

        log.info("Scanning and grouping files by size...")
        with FileProgress(output_fn) as prog:
            bucket = cls.group_size(src_set, args.base_dir, prog)

        if args.hash_compare:
            log.info("Scanning and grouping files by fast hash...")
            with FileProgress(output_fn) as prog:
                bucket = cls.group_fast_hash(src_set, bucket, prog)

            log.info("Scanning and grouping files by full hash...")
            with FileProgress(output_fn) as prog:
                bucket = cls.group_full_hash(src_set, bucket, prog)
        
        log.info("Files of same size/hash:")
        cls.print_result(bucket, src_set, args.color_output)
                

if __name__ == "__main__":
    try:
        DuplicateFileScanner.run()
    except KeyboardInterrupt:
        log.info("Received interrupt signal, exiting...")
        sys.exit(130)