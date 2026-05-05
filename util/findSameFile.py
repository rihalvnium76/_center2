#!/usr/bin/env python3

import argparse
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
import hashlib
import logging
import os
import sys
import time
from typing import Any, Callable, Collection, Generator, Hashable, Iterable

try:
    from xxhash import xxh3_128
except ImportError:
    pass


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

@dataclass
class File:
    src: bool
    path: str
    size: int
    dev: int
    ino: int
    mtime: float

    @classmethod
    def from_stat(cls, src: bool, path: str, stat: os.stat_result):
        return cls(
            src,
            path,
            stat.st_size,
            stat.st_dev,
            stat.st_ino,
            stat.st_mtime
        )

    @cached_property
    def fast_hash(self):
        return FileHasher.fast_hash(self)
    
    @cached_property
    def full_hash(self):
        return FileHasher.full_hash(self)

try:
    import xxhash
except ImportError:
    log.warning("xxHash not installed, falling back to hashlib.blake2b")

class FileHasher:
    # Fast hash file threshold, 3 MiB
    THRESHOLD = 1024 * 1024 * 3
    # Fast hash sample size, 64 KiB
    SAMPLE_SIZE = 1024 * 64
    
    TOTAL_SAMPLE_SIZE = SAMPLE_SIZE * 3

    type HashMap = dict[tuple[int, int], bytes]

    fast_hashes: HashMap = {}
    full_hashes: HashMap = {}

    try:
        hasher = staticmethod(xxh3_128) # pyright: ignore[reportPossiblyUnboundVariable]
    except Exception:
        log.warning("xxHash.xxh3_128 not available, falling back to hashlib.blake2b")
        hasher = staticmethod(hashlib.blake2b)

    @classmethod
    def full_hash(cls, file: File):
        if (cache := cls.full_hashes.get(key := (file.dev, file.ino))) is not None:
            return cache
        
        with open(file.path, "rb") as f:
            cls.full_hashes[key] = hash = hashlib.file_digest(f, cls.hasher).digest() # pyright: ignore[reportArgumentType]
        
        return hash
    
    @classmethod
    def fast_hash(cls, file: File):
        if file.size < cls.THRESHOLD:
            return b""
        
        if (cache := cls.fast_hashes.get(key := (file.dev, file.ino))) is not None:
            return cache

        with open(file.path, "rb") as f:
            head_chunk = f.read(cls.SAMPLE_SIZE)

            f.seek((file.size // 2) - (cls.SAMPLE_SIZE // 2))
            middle_chunk = f.read(cls.SAMPLE_SIZE)

            f.seek(-cls.SAMPLE_SIZE, os.SEEK_END)
            tail_chunk = f.read(cls.SAMPLE_SIZE)
        
        hasher = cls.hasher()
        hasher.update(head_chunk)
        hasher.update(middle_chunk)
        hasher.update(tail_chunk)
        cls.fast_hashes[key] = hash = hasher.digest()

        return hash


class FileProgress:
    disabled = False
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
        if self.disabled or self.unmodified:
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
        
        log.info(f"{self.name}Processed: {self.acc_count}{self.total_count} items ({count_per_sec:.1f} items/s{size_per_sec})")
    
    def stat(self, size: int):
        if self.disabled:
            return
        
        self.unmodified = False
        self.acc_count += 1

        self.last_count += 1
        self.last_size += size

        self.output()
    
    def stat_item(self):
        self.stat(0)

    def stat_fast_hash(self, file: File):
        self.stat(0 if file.size < FileHasher.THRESHOLD else FileHasher.TOTAL_SAMPLE_SIZE)
    
    def stat_full_hash(self, file: File):
        self.stat(file.size)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc, tb):
        self.output(False)
    
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
        
        try:
            return os.stat(arg).st_mtime
        except Exception:
            pass

        for pattern in cls.DATETIME_PATTERNS:
            try:
                return datetime.strptime(arg, pattern).timestamp()
            except ValueError:
                pass
        
        log.error(f"Not a datetime or path: {arg}")
        sys.exit(1)
    
    @classmethod
    def walk_dir(cls, src: bool, real_path: str, visited: set[str]):
        visited.add(real_path)

        with os.scandir(real_path) as entries:
            for entry in entries:
                path = os.path.realpath(entry.path)
                if entry.is_file():
                    # On Windows, the st_ino, st_dev and st_nlink attributes of os.DirEntry.stat() are always set to zero.
                    # Always use os.stat()/os.lstat() instead
                    yield File.from_stat(src, path, os.lstat(path))
                elif entry.is_dir():
                    if path not in visited:
                        yield from cls.walk_dir(src, path, visited)
    
    @classmethod
    def scan_src(cls, paths: list[str], ranges: list[list[str]]):
        sources: dict[str, File] = {}

        with FileProgress() as prog:
            for path in paths:
                path = os.path.realpath(path)
                if os.path.isfile(path):
                    sources[path] = File.from_stat(True, path, os.lstat(path))
                    prog.stat_item()
                elif os.path.isdir(path):
                    for file in cls.walk_dir(True, path, set()):
                        sources[file.path] = file
                        prog.stat_item()
            
            for dir, start_time, end_time in ranges:
                dir = os.path.realpath(dir)
                start_time = cls.to_mtime(start_time)
                end_time = cls.to_mtime(end_time)
                
                if not os.path.isdir(dir):
                    log.error(f"Not a directory: {dir}")
                    sys.exit(1)
                
                for file in cls.walk_dir(True, dir, set()):
                    if (start_time is None or file.mtime >= start_time) and (end_time is None or file.mtime <= end_time):
                        sources[file.path] = file
                        prog.stat_item()
        
        return sources, set(sources.keys())
    
    @classmethod
    def scan_dst(cls, sources: dict[str, File], base_dirs: list[str]):
        with FileProgress() as prog:
            for base_dir in base_dirs:
                if not os.path.isdir(base_dir := os.path.realpath(base_dir)):
                    log.error(f"Not a directory: {dir}")
                    sys.exit(1)
                
                for file in cls.walk_dir(False, base_dir, set()):
                    if file.path not in sources:
                        sources[file.path] = file
                        prog.stat_item()
        
        return sources.values()
    
    @staticmethod
    def group_filter_files(
        files: Iterable[File],
        key: Callable[[File], Hashable],
        stat: Callable[[File], Any],
    ):
        buckets: dict[Hashable, list[File]] = defaultdict(list)

        for file in files:
            buckets[key(file)].append(file)
            stat(file)
        
        return (bucket for bucket in buckets.values() if len(bucket) > 1 and any(file.src for file in bucket))
    
    @staticmethod
    def flatten_groups(buckets: Iterable[list[File]]):
        for bucket in buckets:
            yield from bucket
    
    @classmethod
    def find_duplicate(cls, targets: Collection[File], hash: bool):
        with FileProgress(len(targets), "size") as p:
            results = [result for result in cls.group_filter_files(
                targets,
                lambda f: f.size,
                lambda f: p.stat_item(),
            )]
        
        if not hash:
            return results

        with FileProgress(len(results := list(cls.flatten_groups(results))), "fast_hash") as p:
            results = [result for result in cls.group_filter_files(
                results,
                lambda f: f.fast_hash,
                lambda f: p.stat_fast_hash(f),
            )]

        with FileProgress(len(results := list(cls.flatten_groups(results))), "full_hash") as p:
            return [result for result in cls.group_filter_files(
                results,
                lambda f: f.full_hash,
                lambda f: p.stat_full_hash(f),
            )]
    
    @staticmethod
    def print_result(results: Iterable[list[File]], src_paths: set[str], color_output: bool):
        if color_output:
            size_color = "\033[97m"
            dst_color = "\033[93m"
            reset_style = "\033[0m"
        else:
            size_color = ""
            dst_color = ""
            reset_style = ""
        
        dst_paths = []
        
        for i, result in enumerate(results):
            size = result[0].size
            formatted_size = FileSizeUtils.format(size)
            print(f"{size_color}--- #{i + 1}, {formatted_size} ({size} B) ---{reset_style}")

            dst_paths.clear()

            for file in result:
                if file.src:
                    print(f"<src> {file.path}")
                    src_paths.remove(file.path)
                else:
                    dst_paths.append(file.path)
            
            for path in dst_paths:
                print(f"{dst_color}<dst>{reset_style} {path}")
            
            print()
        
        print(f"{size_color}--- Unique source files ---{reset_style}")
        for src in src_paths:
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
            action="extend",
            nargs="+",
            dest="base_dirs",
            help='Scan base directories (default: ["/sdcard"])',
            default=[],
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
        
        if not args.base_dirs:
            args.base_dirs.append("/sdcard")

        return args
    
    @classmethod
    def run(cls):
        args = cls.parse_args()

        if args.verbose:
            log.setLevel(logging.DEBUG)
            log.debug(f"args: {args}")
        
        LogFormatter.color_output = args.color_output
        FileProgress.disabled = not args.progress_output
        
        log.info("Scanning source files...")
        sources, src_paths = cls.scan_src(args.sources, args.source_ranges)

        log.info("Scanning target files...")
        targets = cls.scan_dst(sources, args.base_dirs)
        del sources

        log.info("Grouping and filtering files...")
        results = list(cls.find_duplicate(targets, args.hash_compare))
        del targets

        log.info("Duplicate files (same size/hash):")
        cls.print_result(results, src_paths, args.color_output)

if __name__ == "__main__":
    VERSION = "2.1.0"
    try:
        DuplicateFileScanner.run()
    except KeyboardInterrupt:
        log.info("Received interrupt signal, exiting...")
        sys.exit(130)
