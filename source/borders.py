# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division
from _borders import borders

def border_features(img, labeled, i, j, border):
    inside = (labeled == i)|(labeled == j)
    pixels = img[inside].ravel()
    borderp = img[border].ravel()
    intensity = (pixels.mean() - borderp.mean())/(1.+pixels.std())
    edginess = sobel[border].mean()/(1.+sobel[inside])
    pixels_i = img[labeled == i].ravel()
    pixels_j = img[labeled == j].ravel()
    separation = np.abs(pixels_i.mean() - pixels_j.mean())/(pixels_i.std() + pixels_j.std() + 40/pixels_i.size + 40/pixels_j.size)
    return np.array([intensity, edginess,separation])

def borders(img, solution, iborder_model):
    labeled, n_regions = solution
    nborders = 0.
    filter = np.ones((3,3), dtype=labeled.dtype)
    output = np.zeros(labeled.shape, bool)

    for i in xrange(n_regions):
        for j in xrange(i+1, n_regions):
            output.fill(False)
            border = borders(labeled, filter, output, i, j, 0)
            if border is not None:
                val += bborder_model.apply(border_features(img, labeled, i, j, border))
                nborders += 1.
    return val/nborders


def borders_background(img, solution, bborder_model):
    labeled, n_regions = solution
    val = 0.
    for i in xrange(n_regions):
        border = border_for(solution, i, 0)
        val += bborder_model.apply(border_features(img, border))
    return val
