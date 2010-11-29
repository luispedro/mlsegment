# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division
from mahotas import features

def texture_features(texture):
    '''
    features = texture_features(texture)
    '''
    return features.lbp(img, 8, 12, ignore_zeros=True)

def textures(img, solution, texture_model):
    labeled,n_regions = solution
    val = 0.
    for i in xrange(n_regions):
        texture = img * (labeled == (i+1))
        val += texture_model.apply(texture_features(texture))
    return val
