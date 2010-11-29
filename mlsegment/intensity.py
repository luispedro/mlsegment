# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division

def intensity(img, solution, intensity_model):
    labeled, _ = solution
    bg = img[labeled == 0].ravel()
    objects = img[labeled > 0].ravel()
    bstd = bg.std()
    if bstd == 0:
        bstd = 1
    return (bg.mean()-objects.mean())/bstd

