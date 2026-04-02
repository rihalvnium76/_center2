import os
from pathlib import Path
import time

# ========= 配置区域 =========
# 目标目录
## 卡西米尔唱片机不会读取指定的目录本身，只认子目录
TARGET_DIR = r"D:\AynaLivePlayer\music\1"
# 源目录，可以写多个
SOURCE_DIRS = [
    r"D:\music",            
    r"D:\song",
]
# 要处理的音乐文件后缀
EXTENSIONS = [".mp3", ".flac", ".wav", ".m4a", ".wma", ".lrc"]
# 是否总是全量更新
FULL_UPDATE = False
# ===========================


def clear_symlinks(target_dir: Path):
    """删除目标目录下的所有符号链接"""
    for item in target_dir.iterdir():
        if item.is_symlink():
            print(f"删除符号链接: {item}")
            item.unlink()


def create_symlinks(sources, target_dir: Path, extensions):
    """遍历源目录并在目标目录下创建符号链接"""
    for src_dir in sources:
        src_dir = Path(src_dir).resolve()
        for file_path in src_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                # 相对路径（不包含文件名）
                rel_path = file_path.relative_to(src_dir).parent
                if rel_path == Path("."):
                    rel_path_str = src_dir.name
                else:
                    rel_path_str = f"{src_dir.name}_{str(rel_path).replace(os.sep, '_')}"

                # 新文件名
                new_name = f"{file_path.stem}__{rel_path_str}{file_path.suffix}"
                link_path = target_dir / new_name

                # 如果已存在同名文件，先删除
                if link_path.exists() or link_path.is_symlink():
                    if not FULL_UPDATE:
                        continue
                    link_path.unlink()

                print(f"创建符号链接: {link_path} -> {file_path}")
                os.symlink(file_path, link_path)


def main():
    target_dir = Path(TARGET_DIR).resolve()
    if not target_dir.exists():
        print(f"目标目录 {target_dir} 不存在，已创建")
        target_dir.mkdir(parents=True)

    # 清空符号链接
    if FULL_UPDATE:
        clear_symlinks(target_dir)

    # 创建符号链接
    extensions = {e.lower() for e in EXTENSIONS}
    create_symlinks(SOURCE_DIRS, target_dir, extensions)

    print("\n完成")
    time.sleep(5)


if __name__ == "__main__":
    main()
