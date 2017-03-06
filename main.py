import sys
from src.encode import enc

def main():
    #enc('ABCDE123')
    enc('HELLO WORLD')
    

if __name__ == "__main__":
    sys.exit(int(main() or 0))