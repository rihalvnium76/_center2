#!/usr/bin/env python3
import argparse
from collections import defaultdict
from dataclasses import dataclass, field
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

    def __init__(self, enabled = True, interval = 5):
        self.enabled = enabled
        self.interval = interval

        self.total_count = 0

        self.last_time = time.time()
        self.last_count = 0
        self.last_size = 0

        self.modified = True

    def reset(self):
        self.total_count = 0

        self.last_time = time.time()
        self.last_count = 0
        self.last_size = 0

        self.modified = True
    
    def output(self, immediate = False):
        if not self.enabled:
            return
        
        now = time.time()
        elapsed_time = now - self.last_time
        if not self.modified or (not immediate and elapsed_time < self.interval):
            return
        self.modified = False
        self.last_time = now

        count_per_sec = self.last_count / elapsed_time
        self.last_count = 0

        if self.last_size:
            size_per_sec = f", {FileSizeUtils.format(self.last_size / elapsed_time)}/s"
        else:
            size_per_sec = ""
        self.last_size = 0

        log.info(f"- Processed: {self.total_count} files ({count_per_sec:.1f} files/s{size_per_sec})")
    
    def record(self, size: int):
        if not self.enabled:
            return
        
        self.modified = True
        
        self.total_count += 1

        self.last_count += 1
        self.last_size += size

        self.output()
    
    def record_memory_item(self):
        self.record(0)

    def record_fast_hash(self, hash: bytes):
        self.record(self.FAST_HASH_SAMPLE_SIZE if hash else 0)
    
    def record_full_hash(self, file: Path):
        self.record(file.stat().st_size)

@dataclass(frozen=True)
class File:
    src: bool = field(compare=False, hash=False) 
    path: Path

class DuplicateFileScanner:
    DATETIME_PATTERNS = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
        "%Y%m%d %H%M%S",
        "%Y%m%d",
    ]

    def __init__(self):
        self.prog: FileProgress = FileProgress()
        self.results: list[list[File]] = []

    @classmethod
    def to_mtime(cls, arg: str):
        if arg == "-":
            return None

        for pattern in [
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%Y%m%d %H%M%S",
            "%Y%m%d",
        ]:
            try:
                return datetime.strptime(arg, pattern).timestamp()
            except ValueError:
                pass
        
        try:
            return os.stat(arg).st_mtime
        except Exception:
            log.error(f"Not a datetime or path: {arg}")
            sys.exit(1)

    def build_sources(self, src_paths: list[str], src_ranges: list[list[str]]):
        sources: set[Path] = set()
        visited: set[Path] = set()

        for src in src_paths:
            src = Path(src).resolve()
            
            if src.is_file():
                self.prog.record_memory_item()
                sources.add(src)
            
            elif src.is_dir():
                for root, dirs, files in src.walk(follow_symlinks=True):
                    if (abs_root := root.resolve()) in visited:
                        dirs.clear()
                        continue
                    visited.add(abs_root)

                    for file in files:
                        if (file := (root / file).resolve()).is_file():
                            self.prog.record_memory_item()
                            sources.add(file)

        for src_dir, start_time, end_time in src_ranges:
            start_time = self.to_mtime(start_time)
            end_time = self.to_mtime(end_time)

            if not os.path.isdir(src_dir):
                log.error(f"Not a directory: {src_dir}")
                sys.exit(1)

            for root, dirs, files in Path(src_dir).resolve().walk():
                for file in files:
                    if (file := (root / file).resolve()).is_file():
                        self.prog.record_memory_item()
                        mtime = file.stat().st_mtime
                        if (start_time is None or mtime >= start_time) and (end_time is None or mtime <= end_time):
                            sources.add(file)
        
        self.prog.output(True)

        if log.isEnabledFor(logging.DEBUG):
            log.debug(f"sources: {sources}")

        return sources
    
    def build_targets(self, sources: set[Path], base_dir: str):
        targets: set[File] = {File(True, src) for src in sources}
        visited: set[Path] = set()

        self.prog.reset()

        for root, dirs, files in Path(base_dir).resolve().walk(follow_symlinks=True):
            if (abs_root := root.resolve()) in visited:
                dirs.clear()
                continue
            visited.add(abs_root)

            for file in files:
                if (dst := (root / file).resolve()).is_file() and dst not in sources:
                    self.prog.record_memory_item()
                    targets.add(File(False, dst))
        
        self.prog.output(True)

        return targets

    def group_by_size(self, targets: set[File], hash: bool):
        size_buckets: dict[int, list[File]] = defaultdict(list)

        # sub-hash function should not be reset anymore
        self.prog.reset()

        for file in targets:
            self.prog.record_memory_item()
            size_buckets[file.path.stat().st_size].append(file)
        
        for bucket in size_buckets.values():
            if len(bucket) >= 2 and any(file.src for file in bucket):
                if hash:
                    self.group_by_fast_hash(bucket)
                else:
                    self.results.append(bucket)
        
        self.prog.output(True)
    
    def group_by_fast_hash(self, prev_bucket: list[File]):
        hash_buckets: dict[bytes, list[File]] = defaultdict(list)

        for file in prev_bucket:
            hash = FileHasher.fast_hash(file.path)
            self.prog.record_fast_hash(hash)
            hash_buckets[hash].append(file)
        
        for bucket in hash_buckets.values():
            if len(bucket) >= 2 and any(file.src for file in bucket):
                self.group_by_full_hash(bucket)
    
    def group_by_full_hash(self, prev_bucket: list[File]):
        hash_buckets: dict[bytes, list[File]] = defaultdict(list)

        for file in prev_bucket:
            hash = FileHasher.full_hash(file.path)
            self.prog.record_full_hash(file.path)
            hash_buckets[hash].append(file)
        
        for bucket in hash_buckets.values():
            if len(bucket) >= 2 and any(file.src for file in bucket):
                self.results.append(bucket)
    
    def print_result(self, sources: set[Path], color_output: bool):
        if color_output:
            size_color = "\033[97m"
            dst_color = "\033[93m"
            reset_style = "\033[0m"
        else:
            size_color = ""
            dst_color = ""
            reset_style = ""

        for i, result in enumerate(self.results):
            size = result[0].path.stat().st_size
            formatted_size = FileSizeUtils.format(size)

            print(f"{size_color}--- #{i + 1}, {size} B ({formatted_size}) ---{reset_style}")

            dst_paths = []
            for file in result:
                if file.src:
                    print(f"<src> {file.path.as_posix()}")
                    sources.remove(file.path)
                else:
                    dst_paths.append(file.path.as_posix())
            for path in dst_paths:
                print(f"{dst_color}<dst>{reset_style} {path}")
            
            print()
        
        print(f"{size_color}--- Unique source files ---{reset_style}")
        for src in sources:
            print(src)
    
    @staticmethod
    def parse_args():
        parser = argparse.ArgumentParser(description="Find same size/hash files")

        parser.add_argument(
            "-s", "--source",
            action="extend",
            nargs="+",
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
            dest="base_dir",
            help="Scan base directory (default: /sdcard)",
            default="/sdcard",
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

        return args
    
    def run(self):
        args = self.parse_args()

        if args.verbose:
            log.setLevel(logging.DEBUG)
        LogFormatter.color_output = args.color_output

        log.debug(f"args: {args}")

        self.prog.enabled = args.progress_output

        log.info("Scanning source files...")

        sources = self.build_sources(args.sources, args.source_ranges)

        log.info("Collecting files...")

        targets = self.build_targets(sources, args.base_dir)

        log.info("Grouping files...")

        self.group_by_size(targets, args.hash_compare)

        log.info("Duplicate files (same size/hash):")

        self.print_result(sources, args.color_output)


if __name__ == "__main__":
    try:
        DuplicateFileScanner().run()
    except KeyboardInterrupt:
        log.info("Received interrupt signal, exiting...")
        sys.exit(130)
