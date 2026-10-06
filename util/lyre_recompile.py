import subprocess
import sys
from typing import Literal

def recompile(lyre_compiler: str, songs_and_flags: dict[str, list[list[str]]]):
    for song, args_list in songs_and_flags.items():
        for args in args_list:
            final_args = [
                sys.executable,
                lyre_compiler,
                *args,
                song,
            ]
            subprocess.run(final_args)
            # print(final_args)

def avoid_none[T](v: list[T] | None) -> list[T]:
    return v if v is not None else []

def generate_args_list(lyre_args: list[str] | None, horn_args: list[str] | Literal[True] | None):
    lyre_args = avoid_none(lyre_args)

    return [
        [*lyre_args, "--midi"],
        ["--horn", *(lyre_args if horn_args is True else avoid_none(horn_args)), "--midi"]
    ]

def main():
    hold = "--hold"
    octaves = "--octaves"

    recompile(r"D:\\lyre.py", {
        r"D:\a.txt": generate_args_list([hold], True),
        r"D:\b.txt": generate_args_list([], [octaves]),
    })

    print()
    input(">>> Press Enter to exit ")

if __name__ == "__main__":
    main()