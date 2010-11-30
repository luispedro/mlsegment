# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division
import texture
import shape
import intensity
import borders

def evaluate(img, solution, parameters, models):
    texture_model, shape_model, intensity_model, iborder_model, bborder_model = models
    Lt,Li,Lib,Lbb = parameters
    return Lt*texture.apply(img, solution, texture_model) + \
        Ls*shape.apply(img, solution, shape_model) + \
        Li*intensity.apply(img, solution, intensity_model) + \
        Lib*borders.apply(img, solution, iborder_model)
        # Lbb*borders_background(img, solution, bborder_model)
