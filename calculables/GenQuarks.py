from supy import wrappedChain
from utils import DeltaR

class gendijet(wrappedChain.calculable):
	def update(self,ignored):
		self.value=[]
		lxy=self.source['genqLxy']
		N=len(self.source['genqLxy'])
		for i in range(N-1):
			for j in range(i+1,N):
				if lxy[i]==lxy[j] : self.value.append((i,j))

class gendijetIndices(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [i for i in range(len(self.source['gendijet']))]

class gendijetLxy(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [self.source['genqLxy'][pair[0]] for pair in self.source['gendijet']]

class gendijetCtau(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [self.source['genqCtau'][pair[0]] for pair in self.source['gendijet']]

class gendijetPt1(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [self.source['genqPt'][pair[0]] for pair in self.source['gendijet']]

class gendijetPt2(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [self.source['genqPt'][pair[1]] for pair in self.source['gendijet']]

class gendijetEta1(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [abs(self.source['genqEta'][pair[0]]) for pair in self.source['gendijet']]

class gendijetEta2(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [self.source['genqEta'][pair[1]] for pair in self.source['gendijet']]

class gendijetIP2dMin(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [min(self.source['genqIP2d'][pair[0]],self.source['genqIP2d'][pair[1]]) 
					  for pair in self.source['gendijet']]

class gendijetIP2dMax(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [max(self.source['genqIP2d'][pair[0]],self.source['genqIP2d'][pair[1]]) 
					  for pair in self.source['gendijet']]

class gendijetIP3dMin(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [min(self.source['genqIP3d'][pair[0]],self.source['genqIP3d'][pair[1]]) 
					  for pair in self.source['gendijet']]

class gendijetIP3dMax(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [max(self.source['genqIP3d'][pair[0]],self.source['genqIP3d'][pair[1]]) 
					  for pair in self.source['gendijet']]

class gendijetFlavor(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [(self.source['genqFlavor'][pair[0]]+self.source['genqFlavor'][pair[1]])/2. 
                      for pair in self.source['gendijet']]

class gendijetNLep(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [self.source['genqNLep'][pair[0]]+self.source['genqNLep'][pair[1]] for pair in self.source['gendijet']]

class gendijetBlxyz(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [(self.source['genqBlxyz'][pair[0]]+self.source['genqBlxyz'][pair[1]])/2. for pair in self.source['gendijet']]

class gendijetDR(wrappedChain.calculable):
	def update(self,ignored):
		self.value = [DeltaR(self.source['genqEta'][pair[0]],
							 self.source['genqPhi'][pair[0]],
							 self.source['genqEta'][pair[1]],
							 self.source['genqPhi'][pair[1]]) for pair in self.source['gendijet']]
