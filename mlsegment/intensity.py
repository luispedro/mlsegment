# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division
import numpy as np
import mahotas
from mahotas.thresholding import otsu, rc

def _corrcoef(x,y):
    return np.corrcoef(x,y)[0,1]

def intensity_features(img, binary):
    bg = img[~binary].ravel()
    objects = img[binary].ravel()
    bstd = bg.std()
    if bstd == 0:
        bstd = 1
    separation = (bg.mean()-objects.mean())/bstd
    corrcoefs = []
    for T in (img.mean(), img.mean() + img.std(), otsu(img), rc(img)):
        corrcoefs.append(_corrcoef(binary, img > T))
    return np.concatenate( ([separation], corrcoefs) )


def intensity(img, solution, intensity_model):
    labeled, _ = solution
    features = intensity_features(img, labeled > 0)
    return intensity_model.apply(features)

