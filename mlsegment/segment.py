# Copyright (C) 2010, Luis Pedro Coelho <lpc@cmu.edu>
# vim: set ts=4 sts=4 sw=4 expandtab smartindent:
# License: MIT

from __future__ import division

def evaluate(img, solution, parameters, models):
    texture_model, shape_model, intensity_model, iborder_model, bborder_model = models
    Lt,Li,Lib,Lbb = parameters
    return Lt*textures(img, solution, texture_model) + \
        Ls*shapes(img, solution, shape_model) + \
        Li*intensity(img, solution, intensity_model) + \
        Lib*borders(img, solution, iborder_model) + \
        Lbb*borders_background(img, solution, bborder_model)
