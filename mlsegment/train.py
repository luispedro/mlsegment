# -*- coding: utf-8 -*-
# Copyright (C) 2010 Luis Pedro Coelho <lpc@cmu.edu>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation; either version 2 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
#
# For additional information visit http://murphylab.web.cmu.edu or
# send email to murphy@cmu.edu

from __future__ import division
import segment
from images import ic100_imgs, ic100_ref
from jug import TaskGenerator
import numpy as np

@TaskGenerator
def get_one(dnaimg, ref):
    solution = (ref,ref.max())
    dna = dnaimg.get('dna')
    dnaimg.unload()
    return segment.extract1(dna, solution)

def rotate1(lst):
    lst = lst[:]
    lst.append(lst.pop(0))
    return lst

@TaskGenerator
def condensate_features(positives, negatives, index):
    if len(np.array(positives[0][index]).shape) == 2:
        group = np.concatenate
    else:
        group = np.vstack
    pos = group([p[index] for p in positives])
    negs = group([n[index] for n in negatives])
    features = np.concatenate((negs,pos))
    labels = np.zeros(len(features))
    labels[len(negs):] = 1
    return features, labels

@TaskGenerator
def train_model((features,labels)):
    import milk
    learner = milk.defaultclassifier()
    return learner.train(features, labels)

@TaskGenerator
def kde_model((features,_)):
    import scipy.stats.kde
    return scipy.stats.kde.gaussian_kde(features.T)


positives = [get_one(dna, ref) for dna,ref in zip(ic100_imgs, ic100_ref)]
negatives = [get_one(dna, ref) for dna,ref in zip(ic100_imgs, rotate1(ic100_ref))]

feature_labels = [condensate_features(positives, negatives, i)
            for i in xrange(4)]
models = [train_model(feature_labels[0])
         ,kde_model(feature_labels[1])
         ,train_model(feature_labels[2])
         ,train_model(feature_labels[3])
         ]

