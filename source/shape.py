# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division

def shapes(img, solution, shape_model):
    labeled, n_regions = solution
    val = 0.
    for i in xrange(n_regions):
        shape = (labeled == (i+1))
        val += shape_model.apply(shape_features(shape))
    return val

