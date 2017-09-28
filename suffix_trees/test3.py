from suffix_trees import STree
from hypothesis import given, assume
from hypothesis.strategies import composite, text, integers, data
from random import sample
import unittest
import string

@composite
def string_and_substring(draw):
    x = draw(text(min_size=2, alphabet=string.printable))
    i = draw(integers(min_value=0, max_value=len(x)-2))
    j = draw(integers(min_value=i+1, max_value=len(x)-1))
    return (x, x[i:j])

@composite
def string_and_not_substring(draw):
    x = draw(text(min_size=2, alphabet=string.printable))
    i = draw(integers(min_value=1, max_value=len(x)-1))
    y = ''.join(sample(x, i))
    assume(x.find(y) == -1)
    return (x, y)

class TestEncoding(unittest.TestCase):
    @given(data())
    def test_find_substring_true(self, data):
        (string, substr) = data.draw(string_and_substring())
        assert STree.STree(string).find(substr) > -1


    @given(data())
    def test_find_substring_false(self, data):
        (string, substr) = data.draw(string_and_not_substring())
        assert STree.STree(string).find(substr) == -1

    @given(data())
    def test_find_all_substring_true(self, data):
        (string, substr) = data.draw(string_and_substring())
        assert len(STree.STree(string).find_all(substr)) > 0


    @given(data())
    def test_find_all_substring_false(self, data):
        (string, substr) = data.draw(string_and_not_substring())
        assert STree.STree(string).find_all(substr) == []

if __name__ == '__main__':
    unittest.main()