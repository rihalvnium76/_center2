from __future__ import annotations
from typing import Iterable
import os

def SandboxieClosedFilePathGenerator(openPaths: Iterable[str], excludingFiles: bool = False, trimmingPath: bool = True, excludingSystemDir: bool = True) -> None:
    def trimPath(path: str) -> str:
        return path.strip(' "') if trimmingPath else path

    def parsePathsToAllowSet() -> set[str]:
        rt: set = set()
        for i in openPaths:
            i = trimPath(i)
            if not i: continue
            i = os.path.abspath(i)
            rt.add(i)
            i = i.split(os.sep)
            i.pop()
            while i:
                rt.add(os.sep.join(i))
                i.pop()
        return rt

    def generateInversePaths(paths: Iterable[str]) -> set[str]:
        rt: set = set()
        for i in paths:
            dir, base = os.path.split(i)
            if base:
                for e in os.scandir(dir):
                    if e.path not in paths:
                        if excludingFiles and e.is_file():
                            continue
                        if excludingSystemDir and (
                            'System Volume Information' in e.name
                            or '$RECYCLE.BIN' in e.name
                            or 'C:\\Windows' in e.name
                            or 'C:\\Program Files' in e.name
                        ):
                            continue
                        rt.add('%s%s' % (e.path, os.sep if e.is_dir() else ''))
        return rt

    def printIniText(paths: Iterable[str]) -> None:
        for i in paths:
            print('ClosedFilePath=%s' % i)

    s = parsePathsToAllowSet()
    s = generateInversePaths(s)
    printIniText(s)

SandboxieClosedFilePathGenerator(r'''
"D:\AAA\BBB"
"D:\Documents\BBB\"
D:\a
F:\XXX
'''.splitlines())
