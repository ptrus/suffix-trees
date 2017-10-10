import string
import random
def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

import STree

if __name__ == '__main__':
    a = ["abeceda", "abecednik", "abeabecedabeabeced", "abecedaaaa", "aaabbbeeecceeeddaaaaabeceda"]
    st = STree.STree(a)
    print(st.lcs())

    text = "name language w en url http w namelanguage en url http"
    stree = STree.STree(text)
    print(stree.find('law'))
    
    st = STree.STree("abcdefghab")
    print(st.find("abc")) # 0
    print(st.find_all("ab")) # [0, 8] ---> [] :-(

