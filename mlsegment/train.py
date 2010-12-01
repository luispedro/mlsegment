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
import texture
import shape
import intensity
import borders

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

@TaskGenerator
def apply_all(dnai, ref, models):
    solution = ref, ref.max()
    functions = [texture.textures, shape.shapes, intensity.intensity, borders.borders]
    dna = dnai.get('dna')
    dnai.unload()
    return [f(dna, solution, m) for f,m in zip(functions, models)]
@TaskGenerator
def adapt(model):
    model.models[-1] = model.models[-1].models[0][1]
    model.models[-1] = model.models[-1].models[0]
    return model
@TaskGenerator
def train_lambdas(training):
    import numpy as np
    import scipy.optimize
    A = np.sum(training, axis=0)
    f = lambda L : np.dot(A,L)/np.sqrt(np.dot(L,L))
    x = scipy.optimize.fmin(f, np.ones(len(A)))
    x /= np.sqrt(np.dot(x,x))
    return x

positives = [get_one(dna, ref) for dna,ref in zip(ic100_imgs, ic100_ref)]
negatives = [get_one(dna, ref) for dna,ref in zip(ic100_imgs, rotate1(ic100_ref))]

feature_labels = [condensate_features(positives, negatives, i)
            for i in xrange(4)]
models = [adapt(train_model(feature_labels[0]))
         ,kde_model(feature_labels[1])
         ,adapt(train_model(feature_labels[2]))
         ,adapt(train_model(feature_labels[3]))
         ]
training = [apply_all(dna, ref, models) for dna,ref in zip(ic100_imgs, ic100_ref)]
lambdas = train_lambdas(training)
