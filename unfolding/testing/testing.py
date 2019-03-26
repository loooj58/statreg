from unfolding.discretization import PointWiseBasis
from unfolding.interface.interface import CheckoutInformation
from unfolding.discretization.observedFunction import UniformUnfoldingResult
from ..interface.interface import IUnfolder
from unfolding.model import GaussErrorUnfolder
from unfolding.tools.kernels import *
from unfolding.tools.example_phi import *

import numpy as np


n = 15
phi = gauss(0, 1)
kernel = lambda x,y: gaussian(x-y, 1)
boundary = (-1,1)
basis = PointWiseBasis(10, boundary)
y = np.linspace(-1,1,n, endpoint=True)
fTrue = convolveFunc(kernel, phi, y, boundary)
sig = 0.1*f + 0.01
fError = np.zeros(y.shape[0])
for i in range(f.shape[0]):
    fError[i] = np.random.normal(fTrue[i], scale=sig[i])

checkInfo = CheckoutInformation(phi)

model = GaussErrorUnfolder(kernel, basis=basis, y=y)
result = model.process(fError, sig, checkInfo=checkInfo)

class TestUniformUnfoldigResult:
    def __init__(self, result: UniformUnfoldingResult):
        self.result = result

    def checkInverseMatrixTransform(self, metrics=None):
        dataTrue = self.result.modelParameter['arguments']['process']['data']
        dataErrorTrue = self.result.modelParameter['arguments']['process']['dataError']

        K = self.result.modelParameter['kernel']['matrix']
        dataUnfolding = K.dot(self.result.observedSignal.coef)
        if metrics is None:
            metrics = lambda x,y: np.sum((x - y)**2)
        return metrics(dataTrue, dataUnfolding)












