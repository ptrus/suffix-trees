import random
import string
import os

random.seed(42)

OUTPUT = "vectors.txt"


def random_str(n):
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(n))


def random_substr(string, length):
    # [0, len(string)-length]
    s = random.randint(0, len(string) - 1 - length)
    # Note: we cannot just return index 's' here, as this might not be the
    # first occurence of the substring in string.
    return string[s:s+length]


if __name__ == '__main__':

    if os.path.exists(OUTPUT):
        raise Exception("File already exists: " + OUTPUT)

    # String lengths to generate.
    nlens = [100, 1000, 10000, 100000, 1000000]

    # Strings that will be searched.
    search_strings = []
    # Test strings that will be tested with search strings.
    test_strings = []
    results = []
    for n in nlens:
        print("Generating cases for length n:", n)

        # Search string.
        ss = random_str(n)

        s_test_strings = []
        res = []
        # Generate search strings of lengths 1 to len(ss).
        for x in range(1, min(len(ss), 300)):
            # Generate 50 random search strings of length x.
            random_cases = [random_str(x) for _ in range(50)]
            # Compute correct results for random strings.
            random_results = [ss.find(s) for s in random_cases]

            # For positive cases select 50 random substrings of length x.
            pos_cases = [random_substr(ss, x) for _ in range(50)]
            pos_results = [ss.find(s) for s in pos_cases]

            s_test_strings.append(random_cases + pos_cases)
            res.append(random_results + pos_results)

        search_strings.append(ss)
        test_strings.append(s_test_strings)
        results.append(res)

    print("Writing test vectors to file:")

    # vectors.txt is in: <search_string>,[<test_string>:<expected>] format.
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT), 'w') as f:
        for i in range(len(search_strings)):
            f.write(search_strings[i] + ",")
            for j in range(len(test_strings[i])):
                for k in range(len(test_strings[i][j])):
                    f.write(test_strings[i][j][k] + ":" + str(results[i][j][k])+",")
            f.write("\n")
