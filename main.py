import sys
from src.encode import create
from src.constants import ErrorCorrection

def main():
    #create('0123')
    create('HELLO WORLD')
    #create('HELLO WORLD', ErrorCorrection.H, 1)
    #create('abcdefg')
    #create('abcdefg', ErrorCorrection.Q, 10)
    #create('漢字')
    #create('ＡＢＣ０')
    #create('large data buffer, 0123456789 ABCDEF', ErrorCorrection.Q)
    #create('MORE AND MORE large data buffer, 0123456789 ABCDEF, yeah! try to encode this, TRY it!, try try try try try try try try!!')

if __name__ == "__main__":
    sys.exit(int(main() or 0))