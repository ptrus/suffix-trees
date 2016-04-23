import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

from STree import STree

if __name__ == '__main__':
    a = ["abeceda", "abecednik", "abeabecedabeabeced", "abecedaaaa", "aaabbbeeecceeeddaaaaabeceda"]
    st = STree(a)
    print(st.lcs())
    UPPAs = list(range(0xE000,0xF8FF+1) + range(0xF0000,0xFFFFD+1) + range(0x100000, 0x10FFFD))

    print(len(UPPAs))
