from __future__ import annotations
from typing import Iterable
import subprocess
import os

# --- use lastest ffmpeg ---
#ffmpeg -hide_banner -i "<source_file>" -c:v libx264 -preset veryslow -crf 23 -refs 6 -bf 6 -g 600 -keyint_min 1 -sc_threshold 60 -deblock 1:1 -qcomp 0.5 -psy-rd 0.4:0 -aq-mode 3 -aq-strength 0.8 -me_method 3 -c:a aac -ar 44100 -b:a 128k "<output_file>"
#ffmpeg -hide_banner -i "<source_file>" -c:v libx264 -preset veryslow -crf 23 -refs 6 -bf 6 -g 600 -keyint_min 1 -sc_threshold 60 -deblock 1:1 -qcomp 0.5 -psy-rd 0.4:0 -aq-mode 3 -aq-strength 0.8 -me_method 3 -c:a copy "<output_file>"
##x264 --crf 23 --preset veryslow -r 6 -b 6 -I 600 -i 1 --scenecut 60 -f 1:1 --qcomp 0.5 --psy-rd 0.4:0 --aq-mode 3 --aq-strength 0.8 --me esa -o "<output_file>" "<source_file>"

# --- experimental ---
# -c:v hevc -x265-params range=full -dst_range 1

def convert(outputDir: str, inputPaths: Iterable[str], allowTrimPath: bool = True) -> None:
    def getCommandLine(inputPath: str, outputPath: str) -> list[str]:
        return ('ffmpeg', '-hide_banner', '-i', inputPath, '-c:v', 'libx264', '-preset', 'veryslow', '-crf', '23', '-refs', '6', '-bf', '6', '-g', '600', '-keyint_min', '1', '-sc_threshold', '60', '-deblock', '1:1', '-qcomp',
'0.5', '-psy-rd', '0.4:0', '-aq-mode', '2', '-aq-strength', '0.8', '-me_method', '2', '-c:a', 'copy', outputPath)

    def trimPath(path: str) -> str:
        return path.strip('" ') if allowTrimPath else path

    def getOutputPath(inputPath: str) -> str:
        base, ext = os.path.splitext(os.path.basename(inputPath))
        return os.path.join(outputDir, base + '_ffx264' + ext)
    
    outputDir = trimPath(outputDir)
    for i in inputPaths:
        i = trimPath(i)
        if not i: continue
        print(f'[>] %s ...' % i)
        # print(getCommandLine(i, getOutputPath(i)))
        try:
            subprocess.run(getCommandLine(i, getOutputPath(i)), capture_output=True, check=True, text=True)
        except subprocess.CalledProcessError as e:
            print()
            print(e.stderr)

convert(r'D:\a\1', [
    r"D:\_TODO\zzzz.mp4"
])

convert(r'D:\a\1', r'''
D:\_todo\xxxx.mp4
D:\_todo\yyyy.mp4
'''.splitlines()) #[1:])

os.system('pause')
