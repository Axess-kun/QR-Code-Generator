import sys
from src.encode import create
from src.constants import ErrorCorrection

def main():
    #create('0123')
    create('HELLO WORLD')
    #create('HELLO WORLD', ErrorCorrection.Q, 1)
    #create('HELLO WORLD', ErrorCorrection.H, 1)
    #create('HELLO WORLD', ErrorCorrection.H, 40)
    #create('abcdefg')
    #create('abcdefg', ErrorCorrection.Q, 10)
    #create('漢字')
    #create('ＡＢＣ０')
    #create('large data buffer, 0123456789 ABCDEF', ErrorCorrection.Q)
    #create('MORE AND MORE large data buffer, 0123456789 ABCDEF, yeah! try to encode this, TRY it!, try try try try try try try try!!')
    #create('MORE AND MORE large data buffer, 0123456789 ABCDEF, yeah! try to encode this, TRY it!, try try try try try try try try!! ahfhkljsadlhfhsdalkfhlsdfs;fjkjsfj s; fhfoweif ow jflkfsad fk hhklsfdsaj fl;jfdfj js ;fl jsdlfj sdlfj', ErrorCorrection.Q)

if __name__ == "__main__":
    sys.exit(int(main() or 0))