import os
from typing import Iterable, Set

# 在函数外部或开头定义为常量
SYSTEM_EXCLUDED_NAMES = {'System Volume Information', '$RECYCLE.BIN', 'Windows', 'Program Files'}

# 标准化路径：去除引号和首尾空格，转为绝对路径
def normalize(path: str) -> str:
    return os.path.abspath(path.strip(' "'))

def generate_closed_file_paths(
    allowed_paths: Iterable[str],
    exclude_files: bool = False,
    exclude_system_dirs: bool = True,
) -> None:
    """
    根据允许访问的路径列表，生成 Sandboxie 配置所需的 ClosedFilePath 条目并打印。

    参数：
        allowed_paths: 允许访问的路径（文件或目录），可以带引号或多余空格。
        exclude_files: 是否在封闭列表中排除普通文件（只封闭目录）。
        exclude_system_dirs: 是否排除常见的系统目录（如 Windows、Program Files 等）。
    """
    # 构建“允许集合”：包含所有输入路径及其所有父目录
    allowed_set: Set[str] = set()
    for raw in allowed_paths:
        path = normalize(raw)
        if not path:
            continue
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
    closed_set: Set[str] = set()
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
                if exclude_system_dirs and entry.name in SYSTEM_EXCLUDED_NAMES:
                    continue
                closed_set.add(entry.path + (os.sep if entry.is_dir() else ''))
        except PermissionError:
            pass

    # 输出配置行
    for p in closed_set:
        print(f'ClosedFilePath={p}')

generate_closed_file_paths(r'''
D:\a\1
D:\b\2\3
'''.splitlines(), True)
