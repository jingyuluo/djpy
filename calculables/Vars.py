from supy import wrappedChain
from utils import DeltaR

class DijetVar(wrappedChain.calculable):
	def __init__(self,indices=None):
		self.indices = indices if indices is not None else 'dijetIndices'

	def update(self,ignored):
		self.value = [-1 for i in range(len(self.source['dijetPt']))]
		for idx in self.source[self.indices]:
			self.value[idx] = self.calculate(idx)

class dijetVtxNTotRatio(DijetVar):
	def calculate(self,idx):
		return self.source['dijetVtxN'][idx]/float(self.source['dijetNDispTracks'][idx]
				+self.source['dijetNPromptTracks'][idx])

class dijetVtxNRatio(DijetVar):
	def calculate(self,idx):
		return self.source['dijetVtxN'][idx]/float(self.source['dijetNDispTracks'][idx]) if self.source['dijetNDispTracks'][idx] > 0 else -1

class dijetVtxptRatio(DijetVar):
	def calculate(self,idx):
		return self.source['dijetVtxpt'][idx]/float(self.source['dijetPt'][idx])

class dijetPromptness(DijetVar):
	def calculate(self,idx):
		return self.source['dijetNPromptTracks'][idx]*self.source['dijetPromptEnergyFrac'][idx]

class dijetPromptness1(DijetVar):
	def calculate(self,idx):
		return self.source['jetNPromptTracks'][self.source['dijetIdx1'][idx]]*self.source['jetPromptEnergyFrac'][self.source['dijetIdx1'][idx]]

class dijetPromptness2(DijetVar):
	def calculate(self,idx):
		return self.source['jetNPromptTracks'][self.source['dijetIdx2'][idx]]*self.source['jetPromptEnergyFrac'][self.source['dijetIdx2'][idx]]

