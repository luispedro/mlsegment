import numpy as np
import mahotas
import pymorph
from scipy import ndimage
from mahotas.thresholding import otsu, rc
import pymorph

def sobel_segment(img):
    vsobel = np.array([
        [1,2,1],
        [0,0,0],
        [-1,-2,-1]])
    sobel = ndimage.convolve(img.astype(float),vsobel)**2
    hsobel = vsobel.T
    sobel += ndimage.convolve(img.astype(float), hsobel)**2
    imgf = ndimage.gaussian_filter(img,2)
    maxima,nmaxima = ndimage.label(pymorph.regmax(imgf))
    overseg = mahotas.cwatershed(sobel.astype(np.uint32), maxima)
    return overseg

def segment(img, T):
    binimg = (img > T)
    binimg = ndimage.median_filter(binimg, size=5)
    dist = mahotas.distance(binimg)
    dist = dist.astype(np.int32)
    maxima = pymorph.regmax(dist)
    maxima,_ = ndimage.label(maxima)
    return mahotas.cwatershed(dist.max() - dist, maxima)


def intersec(x,y):
    l = y.max() + 1
    s = l*x + y
    sp = s.ravel().copy()
    sp.sort()
    sp = np.unique(sp)
    s = np.searchsorted(sp, s)
    return s

def oversegment(img):
    overseg = sobel_segment(img)
    for t in (img.mean(), otsu(img), rc(img)):
        overseg = intersec(overseg, segment(img, t))
    return overseg
    
