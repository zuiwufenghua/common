"""
Document representation, assuming an L2 norm.

TODO: What is the proper way to combine representations? Is adding principled?
"""

from collections import defaultdict

import sys
import math

import common.floateq
from common.mydict import sort as dictsort

class DocRepresentation:
    """
    TODO: Rename as L2DocRepresentation ?
    """
    def __init__(self, dic=None):
        """
        Import a dict, {term: weight}
        """
        self.initialize()
        if dic is not None:
            self.from_dict(dic)

    def initialize(self):
        self._repr = defaultdict(float)

    def from_dict(self, dic):
        """
        Initialize and overwrite this docrepr, from a dict.
        """
        self.initialize()
        for term in dic:
            self._repr[term] = dic[term]

    def from_weight_count_term_list(self, lis):
        """
        Initialize and overwrite this docrepr, from a (weight, count, term).
        """
        self.initialize()
        dic = {}
        for weight, count, term in lis:
            dic[term] = weight
        self.from_dict(dic)

    def __iadd__(self, r):
        """
        Add a representation in-place.
        TODO: What is the proper way to combine representations? Is adding principled?
        """
        for term in r._repr:
            self._repr[term] += r._repr[term]
        return self

    def __imul__(self, x):
        """
        Multiply a weight factor, in place.
        """
        for term in self._repr:
            self._repr[term] *= x
        return self

    @property
    def l2norm(self):
        l2norm = 0.
        for term in self._repr:
            weight = self._repr[term]
            l2norm += weight * weight
        l2norm = math.sqrt(l2norm)
        return l2norm

    def l2normalize(self):
        """
        l2normalize this representation, in-place.
        """
        orig_l2norm = self.l2norm
        for term in self._repr:
            self._repr[term] /= orig_l2norm

        if not common.floateq.floateq(self.l2norm, 1.):
            print >> sys.stderr, "WHA!?!? %f != 1." % self.l2norm

    def crop(self):
        """
        Crop the representation to the top 50 weights.
        TODO: Make 50 a hyperparameter.
        """
        keys = self._repr.keys()
#        origcnt = len(keys)
#        delcnt = 0
        for key in keys:
            if self._repr[key] < 0.01:
                del self._repr[key]
#                delcnt += 1
#        import common.str
#        import sys
#        if delcnt > 0:
#            print >> sys.stderr, "Deleted %s keys" % common.str.percent(delcnt, origcnt)
        for score, term in dictsort(self._repr)[50:]:
            del self._repr[term]

    def sqrerr(self, r):
        """
        Find the sqrerr of each term between these two representations.
        Return a list sorted by decreasing squared error, and also
        indicate whether the weight has increased or decreased from self
        to r.
        """
        allterms = frozenset(self._repr.keys() + r._repr.keys())
        err = {}
        for t in allterms:
            diff = (self._repr[t] - r._repr[t])
            err[t] = (diff * diff, +1 if diff > 0 else -1)
        return dictsort(err)[:100]

    def sqrerr_total(self, r):
        """
        Find the total sqrerr.
        """
        tot = 0.
        for (weight, direction), term in self.sqrerr(r):
            tot += weight
        return tot

    def cosine(self, r):
        """
        Find the cosine of each term between these two representations.
        Return a list sorted by descosine, and also
        indicate whether the weight has increased or decreased from self
        to r.
        """
        allterms = frozenset(self._repr.keys() + r._repr.keys())
        err = {}
        for t in allterms:
            c = (self._repr[t] * r._repr[t])
            err[t] = (c, +1 if diff > 0 else -1)
        return dictsort(err, increasing=True)[:100]

    def cosine_total(self, r):
        """
        Find the total cosine.
        """
        tot = 0.
        for (weight, direction), term in self.sqrerr(r):
            tot += weight
        tot /= self.l2norm
        tot /= r.l2norm
        return tot

    @property
    def xmlrepr(self):
        return [{"value": term, "weight": weight} for weight, term in dictsort(self._repr)[:50]]

    def __str__(self):
        return `dictsort(self._repr)[:10]`
#        return `dictsort(self._repr)[:50]`
