# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division

def borders(img, solution, iborder_model):
    labeled, n_regions = solution
    nborders = 0.
    for i in xrange(n_regions):
        for j in xrange(i+1, n_regions):
            if has_border(labeled, i, j):
                border = border_for(solution, i, j)
                val += bborder_model.apply(border_features(img, border))
                nborders += 1.
    return val/nborders


def borders_background(img, solution, bborder_model):
    labeled, n_regions = solution
    val = 0.
    for i in xrange(n_regions):
        border = border_for(solution, i, 0)
        val += bborder_model.apply(border_features(img, border))
    return val
