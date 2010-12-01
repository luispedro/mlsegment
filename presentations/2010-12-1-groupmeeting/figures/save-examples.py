import readmagick
import pymorph
import mahotas
dna = readmagick.readimg('dna-0.xcf[0]').max(2)
dna2 = readmagick.readimg('dna-1.xcf[0]').max(2)
borders = readmagick.readimg('dna-0.xcf[1]')
borders = borders[:,:,0] > borders[:,:,1]
for i in xrange(2): borders = mahotas.dilate(borders, np.ones((3,3)))
readmagick.writeimg(pymorph.overlay(dna, borders), 'dna.png')
readmagick.writeimg(pymorph.overlay(dna2, borders), 'dna2.png')

