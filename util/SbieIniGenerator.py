from enum import Enum
import os
from typing import Iterable

class PathAccessPolicy(Enum):
    CLOSED_FILE_PATH = "ClosedFilePath"
    OPEN_PIPE_PATH = "OpenPipePath"
    NORMAL_FILE_PATH = "NormalFilePath"

class Generator:
    SYSTEM_EXCLUDED_NAMES = {'System Volume Information', '$RECYCLE.BIN', 'Windows', 'Program Files'}

    @staticmethod
    def normalize_paths(paths: Iterable[str]):
        return [stripped_path for path in paths if (stripped_path := os.path.abspath(path.strip(' "')))]

    @staticmethod
    def print_rules(paths: Iterable[str], access_policy: PathAccessPolicy, sep = True):
        for p in paths:
            print(f"{access_policy.value}={p}{os.sep if sep and os.path.isdir(p) else ""}")

    @classmethod
    def print_closed_rules(
        cls,
        allowed_paths: list[str],
        exclude_files: bool = True,
        exclude_system_dirs: bool = True,
    ):
        """
        根据允许访问的路径列表，生成 Sandboxie 配置所需的 ClosedFilePath 条目并打印。
    
        参数：
            allowed_paths: 已规范化的允许访问的路径（文件或目录）。
            exclude_files: 是否在封闭列表中排除普通文件（只封闭目录）。
            exclude_system_dirs: 是否排除常见的系统目录（如 Windows、Program Files 等）。
        """
        # 构建“允许集合”：包含所有输入路径及其所有父目录
        allowed_set: set[str] = set()
        for path in allowed_paths:
            allowed_set.add(path)
            # 逐级添加父目录
            parts = path.split(os.sep)
            while parts:
                parts.pop()
                parent = os.sep.join(parts)
                if parent:          # 避免空字符串（例如根目录）
                    allowed_set.add(parent)
    
        # 生成“封闭集合”：
        # 对允许集合中的每条路径，扫描其所在目录，
        # 将目录下所有不在允许集合中的条目标记为封闭。
        closed_set: set[str] = set()
        for path in allowed_set:
            dirname, basename = os.path.split(path)
            if not basename or not os.path.isdir(dirname):
                continue
    
            try:
                for entry in os.scandir(dirname):
                    if entry.path in allowed_set:
                        continue
                    if exclude_files and entry.is_file():
                        continue
                    if exclude_system_dirs and entry.name in cls.SYSTEM_EXCLUDED_NAMES:
                        continue
                    closed_set.add(entry.path + (os.sep if entry.is_dir() else ''))
            except PermissionError:
                pass

        # 输出配置行
        cls.print_rules(closed_set, PathAccessPolicy.CLOSED_FILE_PATH, False)

class Presets:
    @staticmethod
    def print_rules(
        open_pipe_paths: list[str],
        normal_file_paths: list[str]
    ):
        Generator.print_rules(open_pipe_paths, PathAccessPolicy.OPEN_PIPE_PATH)
        Generator.print_rules(normal_file_paths, PathAccessPolicy.NORMAL_FILE_PATH)
        Generator.print_closed_rules([*open_pipe_paths, *normal_file_paths])
    
    @classmethod
    def harness(cls):
        cls.print_rules(
            open_pipe_paths = [
                r"D:\ws\harness",
                r"D:\proj\xxx",
            ],
            normal_file_paths = [
                r"D:\proj\rules"
            ]
        )

def main():
    Presets.harness()

if __name__ == "__main__":
    main()
