# -*- coding: utf-8 -*-
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# version 2 as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
# author: Leonardo Tonetto
#
# bwt() and ibwt() taken from the Burrows-Wheeler Transform Wikipedia
# https://en.wikipedia.org/wiki/Burrows%E2%80%93Wheeler_transform

import math

__author__  = "Leonardo Tonetto"
__license__ = "GPLv2"
__version__ = "0.1"


def bwt(s):
    """Apply Burrows-Wheeler transform to input string. Not indicated by a unique byte but use index list"""
    # Table of rotations of string
    table = [s[i:] + s[:i] for i in range(len(s))]
    # Sorted table
    table_sorted = table[:]
    table_sorted.sort()
    # Get index list of ((every string in sorted table)'s next string in unsorted table)'s index in sorted table
    indexlist = []
    for t in table_sorted:
        index1 = table.index(t)
        index1 = index1+1 if index1 < len(s)-1 else 0
        index2 = table_sorted.index(table[index1])
        indexlist.append(index2)
    # Join last characters of each row into string
    r = ''.join([row[-1] for row in table_sorted])
    return r, indexlist


def ibwt(r,indexlist):
    """Inverse Burrows-Wheeler transform. Not indicated by a unique byte but use index list
    """
    s = ''
    x = indexlist[0]
    for _ in r:
        s = s + r[x]
        x = indexlist[x]
    return s


def chunkstring(string, length):
    """Code taken from Stackoverflow:
        https://stackoverflow.com/questions/18854620
    """
    return (string[0+i:length+i] for i in range(0, len(string), length))


def bwt_entropy(z):
    """Apply BWT then calculate the entropy for the input sequence z

    [1] Cai, H., et al. (2004). Universal entropy estimation via block sorting.
    IEEE Transactions on Information Theory. Springer-Verlag Univ. Illinois Press.
    https://doi.org/10.1109/TIT.2004.830771
    """

    def bwt_(z):
        """Apply Burrows-Wheeler transform to input string. Given that we won't care about
        ibwt(), we are only interested in the output string and not in the indexlist.
        """
        z = unicode(z)
        # Table of rotations of string
        table = [z[i:] + z[:i] for i in range(len(z))]
        # Sorted table
        table_sorted = table[:]
        table_sorted.sort()
        # Join last characters of each row into string
        r = ''.join([row[-1] for row in table_sorted])
        return r

    def q_caret(a, j):
        """ From [1]:
        q(a,j) = N_j(a) / sum_{b in alphabet} N_j(b)

        That's basically the probability of 'a' in seqment 'j'
        """
        return j.count(a) / float(len(j))

    def log_q_caret(j):
        """ From [1]:
        log2 q(j) = sum_{a in alphabet} N_j(a) log2 q(a,j)

        That's the sum of occurences of every 'a' in 'j' times
        the probability of that 'a' appearing in every segment.
        We can simplify a bit: we can skip iterations when a given 'a'
        from the alphabet is not in 'j'
        """
        return math.fsum(j.count(a) * math.log(q_caret(a,j),2.) for a in set(j))

    # Call bwt_() to get the output from BWT block sorting algotithm
    bwt_output = bwt_(z)

    # Calculate the size of the segments with which we'll split the sequence k [w(n)]
    # According to [1], the best (for a simple implementation) is sqrt(n), where n
    # is the length of k.
    w = int(round(math.sqrt(len(bwt_output))))

    # Perform the entropy calculation
    H_z = -1./len(z) * math.fsum(log_q_caret(j) for j in chunkstring(bwt_output, w))

    # Finally return what we just computed
    return H_z


# Code take from this link:
# http://dabeaz.blogspot.de/2010/02/context-manager-for-timing-benchmarks.html
import time
class benchmark(object):
    def __init__(self,name):
        self.name = name

    def __enter__(self):
        self.start = time.time()

    def __exit__(self,ty,val,tb):
        end = time.time()
        print("%s : %0.3f seconds" % (self.name, end-self.start))
        return False

# Simple example to try this out
import random, string
import STree

for p in range(6):
    N = 10**p
    print '\nN = {}'.format(N)
    my_seq = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(N)).split(',')[0]

    with benchmark('BWT Wikipedia Entropy'):
        print bwt_entropy(my_seq)

    with benchmark('BWT ST Entropy'):
        print STree.STree(my_seq).bwt_entropy

