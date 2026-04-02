from __future__ import annotations
from typing import Iterable
import subprocess, os

# autoCompleteSymlinkName = False --> {symbolLinkPath: targetPath}
# autoCompleteSymlinkName = True --> {symbolLinkPath: (targetPath, ...)}
def isRunningAsAdmin() -> bool:
    if os.name == 'nt':
        return not subprocess.run(('cacls', r'C:\System Volume Information'), stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
    else: # unix
        return os.getuid() == 0

# autoCompleteSymlinkName = False --> {symbolLinkPath: targetPath}
# autoCompleteSymlinkName = True --> {symbolLinkPath: (targetPath, ...)}
def CreateSymbolLinks(symbolLinks: dict[str, str | Iterable[str]], autoCompleteSymlinkName: str) -> NoReturn:
    def completeSymlinkName(symbolLinkPath: str, targetPath: str) -> str:
        name = os.path.basename(targetPath)
        return os.path.join(symbolLinkPath, name) if os.path.basename(symbolLinkPath) != name else symbolLinkPath

    def createSymbolLink(symbolLinkPath: str, targetPath: str) -> NoReturn:
        if os.path.exists(symbolLinkPath):
            print(f'[-] {symbolLinkPath} -> {targetPath}')
            return
        print(f'[>] {symbolLinkPath} -> {targetPath}')
        parentDir = os.path.dirname(symbolLinkPath)
        if not os.path.exists(parentDir):
            os.makedirs(parentDir)
        os.symlink(targetPath, symbolLinkPath, os.path.isdir(targetPath))

    if isRunningAsAdmin():
        for k, v in symbolLinks.items():
            if autoCompleteSymlinkName:
                if type(v) == str:
                    v = [v]
                for v2 in v:
                    createSymbolLink(completeSymlinkName(k, v2), v2)
            else:
                createSymbolLink(k, v)
    else:
        print("This script needs to be run as admin")


def FixSymbolLinkPaths(scanRootPath: str, replacingPrefixes: dict[str, str]) -> NoReturn:
    def isInvalidSymbolLink(path: str) -> bool:
        return os.path.islink(path) and not os.path.exists(path)
    def handlePrefix(path: str) -> bool | None:
        for k, v in replacingPrefixes.items():
            if path.startswith(k):
                # rs = removePathPrefix(path[len(k):])
                # return os.path.join(v, rs)
                return path.replace(k, v, 1)
        return None
    def createSymbolLink(symbolLinkPath: str, targetPath: str) -> NoReturn:
        parentDir = os.path.dirname(symbolLinkPath)
        if not os.path.exists(parentDir):
            os.makedirs(parentDir)
        os.symlink(targetPath, symbolLinkPath, os.path.isdir(targetPath))
    def handle(path: str) -> NoReturn:
        if isInvalidSymbolLink(path):
            # recreate at original location
            targetPath = os.path.realpath(path)
            newTargetPath = handlePrefix(targetPath)
            if newTargetPath:
                print(f'[>] {path} : {targetPath} -> {newTargetPath}')
                os.remove(path)
                createSymbolLink(path, newTargetPath)
            else:
                print(f'[-] {path} : {targetPath}')

    if isRunningAsAdmin():
        for root, dirs, files in os.walk(scanRootPath):
            for dir in dirs:
                handle(os.path.join(root, dir))
            for file in files:
                handle(os.path.join(root, file))
    else:
        print("This script needs to be run as admin")

def GenerateReplacingPrefixes(paths: list[str] | dict[str, str], commonPrefix: str, keyPrefix: str, valPrefix: str, keyPrefixDirectMerge: bool, valPrefixDirectMerge: bool, keyDirectMerge: bool, valDirectMerge: bool) -> dict[str, str]:
    def removePathPrefix(path: str) -> str:
        return os.path.normpath(path[1:] if path[0] == '/' or path[0] == '\\' else path) if path else ""
    def writeResult(rs: dict[str, str], key: str, val: str) -> NoReturn:
        k = f'{commonPrefix}{keyPrefix}' if keyPrefixDirectMerge else os.path.join(commonPrefix, removePathPrefix(keyPrefix))
        k = f'{k}{key}' if keyDirectMerge else os.path.join(k, removePathPrefix(key))
        v = f'{commonPrefix}{valPrefix}' if valPrefixDirectMerge else os.path.join(commonPrefix, removePathPrefix(valPrefix))
        v = f'{v}{val}' if valDirectMerge else os.path.join(v, removePathPrefix(val))
        rs[k] = v

    rs = {}
    if isinstance(paths, list):
        for s in paths:
            writeResult(rs, s, s)
    elif isinstance(paths, dict):
        for k, v in paths.items:
            writeResult(rs, k, v)
    return rs


#LATEST_DIR = r'D:\Picture\lastest'
#CreateSymbolLinks({
#, r: r

#LATEST_DIR: (
#    r"D:\Picture\1\1.jpg"
#    , r"D:\Picture\1\2.jpg"
#)

#}, True)

#CreateSymbolLinks({
#  r"D:\Picture\lastest\1.jpg": r"D:\Picture\1\1.jpg"
#  , r"D:\Picture\lastest\2.jpg": r"D:\Picture\1\2.jpg"
#}, False)

#ROOT_DIR = r"D:\Picture"
# rules = GenerateReplacingPrefixes([
#     'TypeA'
#     , 'TypeB'
# ], ROOT_DIR, "", "_", False, False, True, True)
# FixSymbolLinkPaths(ROOT_DIR, rules)

# os.system("pause")
