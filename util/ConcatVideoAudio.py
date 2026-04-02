import subprocess
import os

def concat(outDir: str, names: list[str], videoExt = 'mp4', audioExt = 'm4a'):
    def getCli(videoPath, audioPath, outPath):
        return [
            'ffmpeg', '-hide_banner',
            '-i', videoPath,
            '-i', audioPath,
            '-c:v', 'copy',
            '-c:a', 'copy',
            '-strict', 'experimental',
            outPath
        ]
    def getVideoPath(name):
        return name + '.' + videoExt
    def getAudioPath(name):
        return name + '.' + audioExt
    def getOutputPath(name):
        return outDir + os.sep + name + '_ff.mp4'
    
    for i in names:
        i = i.strip('" ')
        if not i: continue
        print('[I] %s' % i)
        cli = getCli(getVideoPath(i), getAudioPath(i), getOutputPath(i))
        # print('[D] %s' % cli)
        try:
            subprocess.run(cli, capture_output=True, check=True, text=True, encoding='UTF-8')
        except subprocess.CalledProcessError as e:
            print('[E] ffmpeg concat failed:')
            print(e.stderr)

concat(r'X:\bangumi', [
    '01 - Intro',
    '02 - Sky'
])
