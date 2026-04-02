import os

def get_id(s):
    try:
        return int(s[:s.find(' ')])
    except:
        pass

songs_path = input('Songs path: ')
s = set(get_id(x) for x in os.listdir(songs_path) if os.path.isdir(os.path.join(songs_path, x)))
s.remove(None)

for x in os.listdir(input('oszs path: ')):
    if x.endswith('.osz') and get_id(x) not in s:
        print(x)
