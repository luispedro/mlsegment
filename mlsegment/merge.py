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


def evaluate_whole(state, img, i, j, (parameters, models)):
    Lt = parameters[0]
    reg_i = state.ref == i
    reg_j = state.ref == i
    reg_ij = reg_i | reg_j
    def T(reg):
        from texture import apply1
        return apply1(img, reg, models[0])
    return Lt * (T(reg_ij) - T(reg_i) - T(reg_j))

def evaluate_partial(state, img, i, parts, j, (parameters, models)):
    Lt = parameters[0]
    reg_i = state.ref == i
    reg_j = state.ref == i
    reg_i_ = reg_i.copy()
    reg_j_ = reg_j.copy()
    for p in parts:
        p = (st.over == p)
        reg_i_ &= ~p
        reg_j_ |= p
    def T(reg):
        from texture import apply1
        return apply1(img, reg, models[0])
    return Lt * (T(reg_i_) + T(reg_j_) - T(reg_i) - T(reg_j))

def evaluate_breakup(state, img, i, parts, (parameters, models)):
    Lt = parameters[0]
    reg_i = state.ref == i
    reg_j = np.zeros_like(state.ref)
    for p in parts:
        reg_j |= (st.over == p)
    reg_i_ = (reg_i & ~reg_j)
    def T(reg):
        from texture import apply1
        return apply1(img, reg, models[0])
    return Lt * (T(reg_i_) + T(reg_j) - T(reg_i))

def evaluate_move(state, img, move, model):
    (code, i, parts, j) = move
    if code == 'whole':
        return evaluate_whole(state, img, i, j, model)
    if code == 'partial':
        return evaluate_partial(state, img, i, parts, j, model)
    if code == 'breakup':
        return evaluate_breakup(state, img, i, parts, model)
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
            if len(allparts) == 1: return self.move(state)
            nparts = random.random()
            parts = self.select_parts(current, i, nparts)
            return ('breakup', i, parts, None)
        j = random.choice(np.where(state.neighbours[i])[0])
        if (i == 0) or r() < .5:
            nparts = random.random()
            parts = self.select_parts(current, i, nparts)
            allparts = np.unique(self.over[current == i])
            if len(parts) == len(allparts):
                return ('whole', i, None, j)
            return ('partial', i, parts, j)
        return ('whole', i, None, j)
            

    def select_parts(self, current, i, nparts):
        allparts = np.unique(self.over[current == i])
        if type(nparts) == float:
            nparts = int(nparts * len(allparts))
        ps = [random.choice(allparts)]
        for j in xrange(nparts-1):
            nps = self.ndict[ps[-1]]
            w = np.searchsorted(allparts, nps)
            w = w[w < len(allparts)]
            nps = nps[allparts[w] == nps]
            if nps.size == 0:
                break
            ps.append(random.choice(nps))
        return ps
        

def one_move(gm, state, img, model):
    move = gm.move(state)
    if evaluate_move(st, img, move, model) < 0.0:
        perform_move(state, move)

