import segment
import train
from jug import value, Task, TaskGenerator
dna = train.dna
parameters = train.lambdas
models = train.models
@TaskGenerator
def to_solution(ref):
    return ref, ref.max()
@TaskGenerator
def retrieve(dnai):
    dna = dnai.get('dna')
    dnai.unload()
    return dna

all_dna = [[Task(segment.evaluate, retrieve(dna), to_solution(ref), parameters, models)
            for ref in train.ic100_ref]
            for dna in train.ic100_imgs]

