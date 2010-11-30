# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division
import numpy as np
from pyslic.features.hullfeatures import hullfeatures

def shape_features(binimg):
    size = binimg.sum()
    return np.concatenate(([size], hullfeatures(binimg)))

def extract1(img, solution):
    labeled, n_regions = solution
    for i in xrange(n_regions):
        shape = (labeled == (i+1))
        yield shape_features(shape)

def shapes(img, solution, shape_model):
    return sum(shape_model.apply(feats) for feats in extract1(img, solution))

