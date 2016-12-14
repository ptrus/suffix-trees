import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

from suffix_trees import STree

if __name__ == '__main__':
    a = ["abeceda", "abecednik", "abeabecedabeabeced", "abecedaaaa", "aaabbbeeecceeeddaaaaabeceda"]
    st = STree.STree(a)
    print(st.lcs())
