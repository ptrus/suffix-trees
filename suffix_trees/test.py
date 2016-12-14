from suffix_trees import STree
import random, string

import time


def random_string(n=100):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))

if __name__ == '__main__':
    nlens = [100,1000,10000,100000,1000000]

    build_times = {}
    find_times_st = {}
    find_times_native = {}

    for n in nlens:
        print("n:",n)
        r = random_string(n)

        build_start = time.time()
        st = STree.STree(r)
        build_times[n] = time.time() - build_start
        print(build_times[n])

        found = 0
        find_times_st[n] = []
        for x in range(1,300):
            search_strs = [random_string(x) for _ in range(100)]
            find_time_sum = 0
            for str in search_strs:
                find_start = time.time()
                if st.find(str) > -1:
                    found += 1
                find_time_sum += time.time() - find_start
            find_times_st[n].append(find_time_sum / 100.0)
            #print(find_time_sum / 1000.0)

        print("Found:", found)
        print(find_times_st[n])

        found2 = 0
        find_times_native[n] = []
        for x in range(1,300):
            search_strs = [random_string(x) for _ in range(100)]
            find_time_sum = 0
            for str in search_strs:
                find_start = time.time()
                if r.find(str) > -1:
                    found2 += 1
                find_time_sum += time.time() - find_start
            find_times_native[n].append(find_time_sum / 100.0)
            #print(find_time_sum / 1000.0)

        print("Found2:", found2)
        print(find_times_native[n])
