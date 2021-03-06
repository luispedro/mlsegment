# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division
from mahotas import features

def texture_features(texture):
    '''
    features = texture_features(texture)
    '''
    return features.lbp(texture, 8, 6, ignore_zeros=True)

def extract1(img, solution):
    labeled, n_regions = solution
    features = []
    for i in xrange(n_regions):
        texture = img * (labeled == (i+1))
        yield texture_features(texture)

def textures(img, solution, texture_model):
    return sum(texture_model.apply(feats) for feats in extract1(img, solution))
apply = textures

def apply1(img, reg, texture_model):
    return texture_model.apply(texture_features(img * reg))
