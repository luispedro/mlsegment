import random
import numpy as np
import _borders
_filter = np.ones((3,3),dtype=np.int32)

class state(object):
    def __init__(self, over, ref):
        self.over = over
        self.ref = ref
        self.neighbours = np.zeros((over.max()+1, over.max()+1), bool)
        self.recompute_neighbours()
        self.in_use = np.zeros(self.ref.max()*2, bool)
        self.in_use[:self.ref.max()] = 1
        self.n_free_ids = self.ref.max()

    def recompute_neighbours(self):
        _borders.neighbours(self.ref, _filter, self.neighbours)

    def get_new_id(self):
        assert self.n_free_ids
        self.n_free_ids -= 1
        return np.where(~self.in_use)[0][0]
    
    def update_whole(self, i, j):
        self.neighbours[i] |= self.neighbours[j]
        self.neighbours[i] = 0
        self.in_use[i] = 0
        self.ref[self.ref== j] = j
        self.n_free_ids += 1

    def update_parts(self, parts, j):
        self.in_use[j] = 1
        for p in parts:
            self.ref[self.over == p] = j
        self.recompute_neighbours()


def evaluate_move(state, img, move, model):
    def V(reg):
        from texture import apply1
        from shape import apply1
        Lt,Ls,Li,Lb = parameters
        Mt,Ms,Mi,Mb = models
        return  Lt * texture.apply1(img, reg, Mt) + \
                Ls * shape.apply1(img, reg, Ms) + \
                0.

    parameters, models = model
    Lt = parameters[0]
    (code, i, parts, j) = move
    if code == 'whole':
        reg_i = state.ref == i
        reg_j = state.ref == i
        reg_ij = reg_i | reg_j
        return V(reg_ij) - V(reg_i) - V(reg_j)
    if code == 'partial':
        reg_i = state.ref == i
        reg_j = state.ref == i
        reg_i_ = reg_i.copy()
        reg_j_ = reg_j.copy()
        for p in parts:
            p = (state.over == p)
            reg_i_ &= ~p
            reg_j_ |= p
        return V(reg_i_) + V(reg_j_) - V(reg_i) - V(reg_j)
    if code == 'breakup':
        reg_i = state.ref == i
        reg_j = np.zeros_like(state.ref)
        for p in parts:
            reg_j |= (state.over == p)
        reg_i_ = (reg_i & ~reg_j)
        return V(reg_i_) + V(reg_j) - V(reg_i)
    raise ValueError('unknown code: ' + code)

def perform_move(state, move):
    (code, i, parts, j) = move
    if code == 'whole':
        state.update_whole(i, j)
    elif code == 'partial':
        state.update_parts(parts, j)
    elif code == 'breakup':
        state.update_parts(parts, state.get_new_id())
    else:
        raise ValueError('unknown code: ' + code)


class generate_moves(object):
    def __init__(self, over):
        self.over = over
        self.overneighbours = np.zeros((over.max()+1, over.max()+1), bool)
        _borders.neighbours(over, _filter.astype(over.dtype), self.overneighbours)
        self.ndict = dict([(i,np.where(self.overneighbours[i])[0]) for i in xrange(self.overneighbours.shape[0])])
    
    def move(self, state):
        current = state.ref
        r = random.random
        if r() < .1: i = 0 
        else: i = random.choice(np.where(state.in_use)[0])
        if state.n_free_ids > 0 and r() < .2:
            allparts = np.unique(self.over[current == i])
            if len(allparts) == 0: return self.move(state)
            if len(allparts) == 1: return self.move(state)
            nparts = random.random()
            parts = self.select_parts(current, i, nparts)
            return ('breakup', i, parts, None)
        (neighs,) = np.where(state.neighbours[i])
        if len(neighs) == 0:
            return self.move(state)
        j = random.choice(np.where(state.neighbours[i])[0])
        if i == j: return self.move(state)
        if (j == 0) or r() < .5:
            nparts = r()
            if (j == 0):
                nparts *= r() * .2
            parts = self.select_parts(current, i, nparts)
            allparts = np.unique(self.over[current == i])
            if len(parts) == len(allparts):
                assert j != 0
                return ('whole', i, None, j)
            return ('partial', i, parts, j)
        return ('whole', i, None, j)
            

    def select_parts(self, current, i, nparts):
        allparts = np.unique(self.over[current == i])
        if len(allparts) == 0: return []
        if type(nparts) == float:
            nparts = int(nparts * len(allparts))
        ps = [random.choice(allparts)]
        for j in xrange(nparts-1):
            nps = self.ndict[ps[-1]]
            w = np.searchsorted(allparts, nps)
            valid = w < len(allparts)
            w = w[valid]
            w = (allparts[w] == nps[valid])
            nps = nps[w]
            if len(nps) == 0:
                break
            ps.append(random.choice(nps))
        return ps
        

def one_move(gm, state, img, model):
    move = gm.move(state)
    if evaluate_move(state, img, move, model) < 0.0:
        perform_move(state, move)

