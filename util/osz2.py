# 找出没部署的osz
# 支持递归
import os

def get_id(s):
    try:
        return int(s[:s.find(' ')])
    except:
        pass

songs_path = input('Songs path: ').strip()
s = set(get_id(x) for x in os.listdir(songs_path) if os.path.isdir(os.path.join(songs_path, x)))
if None in s:
    s.remove(None)

for _, _, fns in os.walk(input('oszs path: ').strip()):
    for x in fns:
        if x.endswith('.osz') and get_id(x) not in s:
            print(x)
