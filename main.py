import sys
from src.encode import enc

def main():
    #enc('0123')
    #enc('HELLO WORLD')
    enc('abcdefg')
    #enc('漢字')
    #enc('ＡＢＣ０')

if __name__ == "__main__":
    sys.exit(int(main() or 0))