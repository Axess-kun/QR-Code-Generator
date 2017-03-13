import sys
from src.encode import enc
from src.constants import ErrorCorrection

def main():
    #enc('0123')
    enc('HELLO WORLD')
    #enc('HELLO WORLD', ErrorCorrection.H, 1)
    #enc('abcdefg')
    #enc('abcdefg', ErrorCorrection.Q, 10)
    #enc('漢字')
    #enc('ＡＢＣ０')
    #enc('large data buffer, 0123456789 ABCDEF', ErrorCorrection.Q)
    #enc('MORE AND MORE large data buffer, 0123456789 ABCDEF, yeah! try to encode this, TRY it!, try try try try try try try try!!')

if __name__ == "__main__":
    sys.exit(int(main() or 0))