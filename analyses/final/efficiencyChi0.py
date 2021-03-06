import supy,samples,calculables,steps,ROOT as r
from utils.other import removeLowStats,rnd
import math,re,pickle

class efficiencyChi0(supy.analysis) :

	MSquark = [1500,1000,350]
	MChi0 = [494,148,148]
	ctau = [17.3,5.9,17.8]
	MSquark_p = [1500,1000,700,700]
	MChi0_p = [150,500,500,150]
	ctau += [4.5,22.7,8.1,27.9]
	sig_names = ['SQ_'+str(a)+'_CHI_'+str(b) for a,b in zip(MSquark,MChi0)]
	sig_names += ['SQ_'+str(a)+'_CHI_'+str(b)+'_priv' for a,b in zip(MSquark_p,MChi0_p)]
	qcd_bins = [str(q) for q in [80,120,170,300,470,600,800]]
	qcd_names = ["qcd_%s_%s" %(low,high) for low,high in zip(qcd_bins[:-1],qcd_bins[1:])]

	AccCuts=[
		{'name':'gendijet'},
		#{'name':'gendijetFlavor','max':6,'min':0},
		{'name':'gendijetLxy','max':60},
		{'name':'gendijetEta1','max':2.1},		
		{'name':'gendijetEta2','max':2.1},
		{'name':'gendijetPt1','min':40},
		{'name':'gendijetPt2','min':40},
		{'name':'gendijetDR','min':0.5},
	]
 
	IniCuts=[
        {'name':'dijet'},
		{'name':'dijetTrueLxy','min':0},
        {'name':'dijetPt1','min':40},
        {'name':'dijetPt2','min':40},
		#{'name':'dijetTrueLxy','min':0},
        # vertex minimal
        {'name':'dijetVtxN1','min':1},
        {'name':'dijetVtxN2','min':1},
        # cluster minimal
        {'name':'dijetbestclusterN','min':2},
        #{'name':'dijetbestclusterN1','min':1},
        #{'name':'dijetbestclusterN2','min':1},
        {'name':'dijetVtxChi2','min':0,'max':5},
    ]
	Cuts=[
        # clean up cuts 
        {'name':'dijetVtxmass','min':4},
        {'name':'dijetVtxpt','min':8},
        {'name':'dijetNAvgMissHitsAfterVert','max':2},
        {'name':'dijetLxysig','min':8},
        #{'name':'dijetNoOverlaps','val':True},
        {'name':'dijetBestCand','val':True},
    ]
	
	ABCDCutsLow = [
		{'name':'Prompt1','vars':({'name':'dijetNPromptTracks1','max':1},
   	                              {'name':'dijetPromptEnergyFrac1','max':0.15})
		},
		{'name':'Prompt2','vars':({'name':'dijetNPromptTracks2','max':1},
	                              {'name':'dijetPromptEnergyFrac2','max':0.15})
		},
		{'name':'Disc','vars':({'name':'dijetDiscriminant','min':0.9},)}
		]
	
	ABCDCutsHigh = [
		{'name':'Prompt1','vars':({'name':'dijetNPromptTracks1','max':1},
   	                              {'name':'dijetPromptEnergyFrac1','max':0.09})
		},
		{'name':'Prompt2','vars':({'name':'dijetNPromptTracks2','max':1},
	                              {'name':'dijetPromptEnergyFrac2','max':0.09})
		},
		{'name':'Disc','vars':({'name':'dijetDiscriminant','min':0.8},)}
		]
	ABCDCutsSets=[ABCDCutsLow,ABCDCutsHigh]

	def dijetSteps0(self):
		mysteps = []
		for cut in self.AccCuts:
			mysteps.append(supy.steps.filters.multiplicity(cut['name']+'Indices',min=0))
		return([supy.steps.filters.label('Acceptance Cuts')]+mysteps)
	
	def dijetSteps1(self):
		mysteps = []
		for cut in self.IniCuts+self.Cuts:
			mysteps.append(supy.steps.filters.multiplicity(cut['name']+'Indices',min=1))
			#if cut == self.IniCuts[-1]: mysteps.append(steps.plots.cutvars(indices=cut['name']+'Indices'))
			#if cut == self.Cuts[-1]: mysteps.append(steps.plots.cutvars(indices=cut['name']+'Indices'))
			#if cut == self.ABCDCutsHigh[-1]: mysteps.append(steps.plots.cutvars(indices=cut['name']+'Indices'))
		return ([supy.steps.filters.label('dijet multiplicity filters')]+mysteps)

	def dijetSteps2(self):
		mysteps=[]
		for i in range(len(self.ABCDCutsSets)) :
			mysteps.append(steps.plots.ABCDEFGHplots(indices='ABCDEFGHIndices'+str(i)))
		for cut in self.ABCDCutsLow:
			mysteps.append(supy.steps.filters.multiplicity(cut['name']+'Indices',min=1))
			if cut == self.ABCDCutsLow[-1]: mysteps.append(steps.plots.cutvars(indices=cut['name']+'Indices'))
			if cut == self.ABCDCutsLow[-1]: mysteps.append(steps.plots.observables(indices=cut['name']+'Indices'))
		return ([supy.steps.filters.label('dijet ABCD cuts filters')]+mysteps)


	def calcsIndices(self):
		calcs = []
		cuts = self.IniCuts + self.Cuts +self.ABCDCutsLow
		for cutPrev,cutNext in zip(cuts[:-1],cuts[1:]):
			calcs.append(calculables.Indices.Indices(indices=cutPrev['name']+'Indices',cut=cutNext))
		for i in range(len(self.ABCDCutsSets)) :
			calcs.append(calculables.Indices.ABCDEFGHIndices(indices=self.Cuts[-1]['name']+'Indices',
                                                             cuts=self.ABCDCutsSets[i],suffix=str(i)))
		for cutPrev,cutNext in zip(self.AccCuts[:-1],self.AccCuts[1:]):
			calcs.append(calculables.Indices.Indices(indices=cutPrev['name']+'Indices',cut=cutNext))
		return calcs

	def discs(self):
		discSamplesRight=[name+'.pileupTrueInteractionsBX0Target' for name in self.sig_names]
		discSamplesLeft=[name+'.pileupTrueInteractionsBX0Target' for name in self.qcd_names]
		return([supy.calculables.other.Discriminant(fixes=("dijet",""),
													right = {"pre":"H","tag":"","samples":discSamplesRight},
													left = {"pre":"qcd","tag":"","samples":discSamplesLeft},
													dists = {"dijetVtxN":(7,1.5,8.5),
															 "dijetglxyrmsclr": (10,0,1),
															 "dijetbestclusterN": (7,1.5,8.5),
															 "dijetPosip2dFrac": (5,0.5001,1.001),
															},
													indices=self.Cuts[-1]['name']+'Indices',
													bins = 14),
			   ])

	def calcsVars(self):
		calcs = []
		calcs.append(calculables.Overlaps.dijetNoOverlaps('dijetLxysigIndices'))
		calcs.append(calculables.Overlaps.dijetBestCand('dijetLxysigIndices'))
		return calcs

	def listOfSteps(self,config) :
		return ([
		supy.steps.printer.progressPrinter()]
		### pile-up reweighting
		+[supy.calculables.other.Target("pileupTrueNumInteractionsBX0",thisSample=config['baseSample'],
                                    target=(supy.whereami()+"/../data/pileup/HT300_Double_R12BCD_true.root","pileup"),
                                    groups=[('SQ',[])]).onlySim()] 

		### acceptance filters
		+self.dijetSteps0()
		+[steps.event.general()]
		+[steps.event.genevent()]
		#+[steps.efficiency.NX(pdfweights=None)]	
		#+[steps.efficiency.NXAcc(indicesAcc=self.AccCuts[-1]['name']+'Indices',pdfweights=None)]	
		+[steps.efficiency.NE(pdfweights=None)]	
	
		+[supy.steps.filters.label('data cleanup'),
		supy.steps.filters.value('primaryVertexFilterFlag',min=1),
		supy.steps.filters.value('physicsDeclaredFilterFlag',min=1).onlyData(),
		supy.steps.filters.value('beamScrapingFilterFlag',min=1),
		supy.steps.filters.value('beamHaloTightFilterFlag',min=1),
		supy.steps.filters.value('hbheNoiseFilterFlag',min=1),
		supy.steps.filters.value('hcalLaserEventFilterFlag',min=1),
		supy.steps.filters.value('ecalLaserCorrFilterFlag',min=1),
		supy.steps.filters.value('eeBadScFilterFlag',min=1),
		supy.steps.filters.value('ecalDeadCellTPFilterFlag',min=1),
		supy.steps.filters.value('trackingFailureFilterFlag',min=1),
		]
		
		### trigger
		+[supy.steps.filters.label("hlt trigger"),
		#steps.trigger.hltFilterWildcard("HLT_HT300_v"),
		#steps.trigger.hltTriggerObjectMultiplicity('hlt2DisplacedHT300L1FastJetL3Filter',min=0),
		#steps.trigger.hltTriggerObjectMultiplicity('hlt2PFDisplacedJetsPt50',min=0),
		#supy.steps.filters.multiplicity('TrigPromptGenQ1',min=2),
		#supy.steps.filters.multiplicity('TrigPromptGenQ2',min=2),
		steps.trigger.hltFilterWildcard("HLT_HT300_DoubleDisplacedPFJet60_v"),
		supy.steps.filters.value('caloHT',min=325),
		#supy.steps.filters.value('mycaloHT',min=325),
		]

		+self.dijetSteps1()
		+self.discs()
		+self.dijetSteps2()
		+[steps.event.general(tag='1')]
		#+[
		#  steps.efficiency.NXReco(pdfweights=None,
		#	  indicesRecoLow='ABCDEFGHIndices0',
		#	  indicesRecoHigh='ABCDEFGHIndices1')
		# ]
		+[
          steps.efficiency.multiplicity(pdfweights=None,
              indicesRecoLow='ABCDEFGHIndices0',
              indicesRecoHigh='ABCDEFGHIndices1')
         ]
		+[
          steps.efficiency.NEReco(pdfweights=None,
              indicesRecoLow='ABCDEFGHIndices0',
              indicesRecoHigh='ABCDEFGHIndices1')
         ]
		)

	def listOfCalculables(self,config) :
		return ( supy.calculables.zeroArgs(supy.calculables) +
		supy.calculables.zeroArgs(calculables)
		+self.calcsVars()
		+self.calcsIndices()
		+[calculables.TrigMatching.TrigPromptGenQ(tag='hlt2DisplacedHT300L1FastJetL3Filter',instance='1')]
		+[calculables.TrigMatching.TrigPromptGenQ(tag='hlt2PFDisplacedJetsPt50',instance='2')]
		)

	def listOfSampleDictionaries(self) :
		return [samples.qcd,samples.data,samples.sigmc]
    
	def listOfSamples(self,config) :
		nFiles = None # or None for all
		nEvents = None # or None for all
		sig_samples = []

		for i in range(len(self.sig_names)):
			sig_samples+=(supy.samples.specify(names = self.sig_names[i], markerStyle=20, color=i+1,  nEventsMax=nEvents, nFilesMax=nFiles, weights = ['pileupTrueNumInteractionsBX0Target']))
			#sig_samples+=(supy.samples.specify(names = self.sig_names[i], markerStyle=20, color=i+1,  nEventsMax=nEvents, nFilesMax=nFiles))
		toPlot=[sample for i,sample in enumerate(sig_samples) if i in [0,1,2]]

		return [sig_samples[i] for i in [2,6,5,1,4,3,0]]

		#return toPlot

	def conclude(self,pars) :
		#make a pdf file with plots from the histograms created above
		org = self.organizer(pars)
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(1500)#rightarrow#tilde{#chi}(500) c#tau=18.1cm", "color":r.kRed,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_1500_CHI_494")                
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(1500)#rightarrow#tilde{#chi}(150) c#tau=4.5cm", "color":r.kYellow,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_1500_CHI_150")                
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(1000)#rightarrow#tilde{#chi}(150) c#tau=5.9cm", "color":r.kBlack,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_1000_CHI_148")                
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(1000)#rightarrow#tilde{#chi}(500) c#tau=22.7cm", "color":r.kOrange,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_1000_CHI_500")                
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(350)#rightarrow#tilde{#chi}(150) c#tau=18.8cm", "color":r.kGreen,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_350_CHI_148")                
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(700)#rightarrow#tilde{#chi}(150) c#tau=8.1cm", "color":r.kBlue,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_700_CHI_150")                
		#org.mergeSamples(targetSpec = {"name":"#tilde{q}(700)#rightarrow#tilde{#chi}(500) c#tau=27.9cm", "color":r.kMagenta,"lineWidth":3,"goptions":"hist","lineStyle":1}, allWithPrefix = "SQ_700_CHI_500")                
		org.scale(lumiToUseInAbsenceOfData=18600)
		plotter = supy.plotter( org,
			pdfFileName = self.pdfFileName(org.tag),
			doLog=True,
			anMode=True,
			showStatBox=True,
			pegMinimum=0.1,
			shiftUnderOverFlows=False,
			blackList = ["lumiHisto","xsHisto","nJobsHisto"],
			)
		plotter.plotAll()
		#plotter.doLog=False
		plotter.anMode=True
	
		#self.meanLxy(org)
		#self.sqsqRatio(org)
		org.lumi=None
		#self.flavors(org)
		#self.effPlots(org,plotter,denName='NE',numName='NEReco',sel='Low',flavor='')
		#self.sigPlots(plotter)	
		self.totEvtEff(org,dir='eff2Neu')
		#self.totalEfficiencies(org,dir='eff2Neu',flavor='')
		#self.puEff(org,plotter)


	def sigPlots(self,plotter):			
		plotter.individualPlots(simulation=True, plotSpecs = [{"plotName":"Mass_h_Disc",
                                              "stepName":"observables",
                                              "stepDesc":"observables",
                                              "newTitle":";Invariant Mass [GeV];dijets / bin",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),
                                              },
											  {"plotName":"Lxy_h_Disc",
                                              "stepName":"observables",
                                              "stepDesc":"observables",
                                              "newTitle":";L_{xy} [cm];dijets / bin",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),
                                              },
											  #{"plotName":"TrkAvgPt_h_Disc",
                                              #"stepName":"observables",
                                              #"stepDesc":"observables",
                                              #"newTitle":";Average Track p_{T} [GeV];dijets / bin",
                                              #"legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              #"stampCoords": (0.37, 0.85),},
                                              #},
											  {"plotName":"VtxNRatio_h_Disc",
                                              "stepName":"observables",
                                              "stepDesc":"observables",
                                              "newTitle":";Fraction of displaced tracks in the Vertex;dijets / bin",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),
                                              },
											  {"plotName":"ClrNRatio_h_Disc",
                                              "stepName":"observables",
                                              "stepDesc":"observables",
                                              "newTitle":";Fraction of displaced tracks in the Cluster;dijets / bin",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),
                                              },
											  {"plotName":"VtxN_h_Disc",
                                              "stepName":"cutvars",
                                              "stepDesc":"cutvars",
                                              "newTitle":";Vertex Track Multiplicity;dijets / bin",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),
                                              },
											  {"plotName":"bestclusterN_h_Disc",
                                              "stepName":"cutvars",
                                              "stepDesc":"cutvars",
                                              "newTitle":";Cluster Track Multiplicity;dijets / bin",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),
                                              },
                                            ]
                               )

	def sqsqRatio(self,org):
		sqsq=None
		for step in org.steps:
			for plotName in sorted(step.keys()):
				if plotName=='SqSq': sqsq=step[plotName]

		for i,sample in enumerate(org.samples):
			tot=sqsq[i].Integral()
			print sample['name'],sqsq[i].GetBinContent(1)/tot, sqsq[i].GetBinContent(2)/tot


	def meanLxy(self,org):
		lxy0,lxy1,lxy2=None,None,None
		for step in org.steps:
			for plotName in sorted(step.keys()):
				if plotName == 'Lxy': lxy0=step[plotName]
		for i,sample in enumerate(org.samples):
			print sample['name'],round(lxy0[i].GetMean(),2)

	def flavors(self,org):
		hists,names=[],[]
		for step in org.steps:
			for name in step.keys():
				if name.startswith('LowLxy'): hists.append(step[name]); names.append(name)
		print names

		for i,sample in enumerate(org.samples):
			for hist,name in zip(hists,names):
				flavor = name[6:]
				if hist[i] is not None: print sample['name'],flavor, hist[i].Integral()

	def effPlots(self,org,plotter,denName,numName,sel,flavor):
		flavorMap={'ud':'q#bar{q}','qmu':'q#mu/#bar{q}#mu','':''}
		nlist,dlist,names=[],[],[]
		names2=[]
		for step in org.steps:
			if step.name==denName: 
				for plotName in sorted(step.keys()):
					if plotName.endswith(flavor) : dlist.append(step[plotName]);names.append(plotName)
			if step.name==numName: 
				for plotName in sorted(step.keys()): 
					if plotName.startswith(sel) and plotName.endswith(flavor) and '+' not in plotName: nlist.append(step[plotName]);names2.append(plotName)
		print names
		print names2
		'''
		num,denom=nlist[names2.index(sel+'XDR'+flavor)][0],dlist[names.index('XDR'+flavor)][0]
		print num,denom
		for i in range(0,num.GetNbinsX()):
			n,d = num.GetBinContent(i),denom.GetBinContent(i)
			print n,d
		'''

		for n in nlist: print n[0].GetName();removeLowStats(n,relErrMax=0.7)

		effs=[ tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(num,denom) ]) for num,denom in zip(nlist,dlist) ]
		plotter.individualPlots(simulation=True, plotSpecs = [
											  {"plotName":"HPt"+flavor,
                                              "histos":effs[names.index("HPt"+flavor)],
                                              "newTitle":"; H^{0} p_{T} [GeV] ; efficiency %s."%flavorMap[flavor],
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
											  {"plotName":"XPt"+flavor,
                                              "histos":effs[names.index("XPt"+flavor)],
                                              "newTitle":"; best #tilde{#chi}^{0}_{1} p_{T} [GeV] ; efficiency %s"%flavorMap[flavor],
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
											  {"plotName":"Lxy"+flavor,
                                              "histos":effs[names.index("Lxy"+flavor)],
                                              "newTitle":"; best #tilde{#chi}^{0}_{1} L_{xy} [cm] ; efficiency %s"%flavorMap[flavor],
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
											  {"plotName":"SmallLxy"+flavor,
                                              "histos":effs[names.index("SmallLxy"+flavor)],
                                              "newTitle":"; best #tilde{#chi}^{0}_{1} L_{xy} [cm] ; efficiency %s"%flavorMap[flavor],
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
											  {"plotName":"IP2dMin"+flavor,
                                              "histos":effs[names.index("IP2dMin"+flavor)],
                                              "newTitle":"; best #tilde{#chi}^{0}_{1} min(IP^{xy}(q),IP^{xy}(#bar{q})) [cm] ; efficiency %s%s"%(flavorMap[flavor],flavorMap[flavor]),
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
											  {"plotName":"IP2dMax"+flavor,
                                              "histos":effs[names.index("IP2dMax"+flavor)],
                                              "newTitle":"; best #tilde{#chi}^{0}_{1} max(IP^{xy}(q),IP^{xy}(#bar{q})) [cm] ; efficiency %s%s"%(flavorMap[flavor],flavorMap[flavor]),
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
											  {"plotName":"XDR"+flavor,
                                              "histos":effs[names.index("XDR"+flavor)],
                                              "newTitle":"; best #tilde{#chi}^{0}_{1} #Delta R (q#bar{q},#tilde{#chi}^{0}_{1}) ; efficiency %s%s"%(flavorMap[flavor],flavorMap[flavor]),
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),},
                                            ],
                               )

	def puEff(self,org,plotter):
		num,denom=None,None
		for step in org.steps:
			for plotName in sorted(step.keys()):
				if plotName == '1nPV': num=step[plotName]
				if plotName == 'nPV': denom=step[plotName]
		eff=tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(num,denom)])
		plotter.individualPlots(simulation=True, plotSpecs = [{"plotName":"effPU",
                                              "histos":eff,
                                              "newTitle":"; pile-up vertices; efficiency",
                                              "legendCoords": (0.55, 0.7, 0.9, 0.92),
                                              "stampCoords": (0.37, 0.85),}
                                            ],
                               )

	def totEvtEff(self,org,dir=None):
		low1p,low1,low2p,denom,lowNX,denomX=None,None,None,None,None,None
		for step in org.steps:
			for plotName in sorted(step.keys()):
				if 'LowNE1' == plotName : low1=step[plotName]
				if 'NE' == plotName : denom=step[plotName]
				if 'NX' == plotName: denomX=step[plotName]

		efflow1 = tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(low1,denom)])

		#fs = [0.01,0.02,0.03,0.06,0.1,0.2,0.3,0.6,1.,2.,3.,6.,10.,20.,30.,60.,100.]
		fs = [0.4,0.6,1.,1.4]
		fs = [round(a,5) for a in fs] 
		N=len(fs)

		sysmap={'1500494':0.10,'1000148':0.10,'350148':0.10,'12048':0.10}
		f=0.89

		for i,sample in enumerate(org.samples):
			digits=re.findall(r'\d+',sample['name'])
			SQ,CHI=digits[0],digits[1]
			name='SQ_'+str(SQ)+"_CHI_"+str(CHI) + ('_priv' if 'priv' in sample['name'] else '')
			sys=0.1

			ctau = self.ctau[self.sig_names.index(name)]

			for j in range(N):
				x,y=r.Double(0),r.Double(0)
				efflow1[i].GetPoint(j,x,y)
				e1 = f*float(y)
				e1Err = f*efflow1[i].GetErrorY(j)
				if e1 > 0. : e1Err = e1*math.sqrt(sys*sys+pow(e1Err/e1,2))
				factor=fs[j]
				#if factor in [0.1,1,10]:
				objects=[ SQ,CHI,factor*ctau,rnd(100*e1,3),rnd(100*e1Err,3)]
				print " & ".join(str(a) for a in objects ) + ' \\\\'
				output=[(e1,e1Err),(e1,e1Err),[e1,e1Err]]
				name = name.replace('_priv','')
				pickle.dump(output,open(supy.whereami()+'/../results/'+dir+'/efficiencies/'+name+'_'+str(factor)+'.pkl','w'))

	def totalEfficiencies(self,org,dir=None,flavor='') :
		recoLow,recoHigh,acceptance,denom=None,None,None,None
		for step in org.steps:
			for plotName in sorted(step.keys()):
				if 'LowNX'+flavor == plotName : recoLow=step[plotName]
				if 'HighNX'+flavor == plotName : recoHigh=step[plotName]
				if 'AccNX'+flavor == plotName : acceptance=step[plotName]
				if 'NX'+flavor == plotName : denom=step[plotName]

		acc = tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(acceptance,denom)])
		efflow = tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(recoLow,denom)])
		effhigh = tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(recoHigh,denom)])
		effacclow = tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(recoLow,acceptance)])
		effacchigh = tuple([r.TGraphAsymmErrors(n,d,"cl=0.683 n") for n,d in zip(recoHigh,acceptance)])
	
		fs = [0.01,0.02,0.03,0.06,0.1,0.2,0.3,0.6,1.,2.,3.,6.,10.,20.,30.,60.,100.]
		fs = [round(a,5) for a in fs] 
		N=len(fs)

		f=0.89
		sysmap={'1500494':0.10,'1000148':0.10,'350148':0.10,'12048':0.10}


		import pickle,math,re
		for i,sample in enumerate(org.samples):
			digits = re.findall(r'\d+',sample['name'])
			SQ,CHI=digits[0],digits[2]
			name='SQ_'+str(SQ)+"_CHI_"+str(CHI)
			sys=0.10
			ctau = self.ctau[self.sig_names.index(name)]
			for j in range(N):
				x,y=r.Double(0),r.Double(0)
				eff = efflow
				effacc = effacclow
				eff[i].GetPoint(j,x,y)
				e = f*float(y)
				eErr = f*eff[i].GetErrorY(j)
				effacc[i].GetPoint(j,x,y)
				ea = f*float(y)
				eaErr = f*effacc[i].GetErrorY(j)
				acc[i].GetPoint(j,x,y)
				a = float(y)
				aErr = acc[i].GetErrorY(j)
				if e > 0. : eErr = e*math.sqrt(sys*sys+pow(eErr/e,2))
				else : eErr = 0.
				if ea > 0. : eaErr = ea*math.sqrt(sys*sys+pow(eaErr/ea,2))
				else : eaErr = 0.
				factor=fs[j]
				print SQ,CHI,factor,a,aErr,e,eErr,ea,eaErr
				data=[(a,aErr),(e,eErr),[ea,eaErr]]
				pickle.dump(data,open(supy.whereami()+'/../results/'+dir+'/efficiencies/'+name+'_'+str(factor)+'.pkl','w'))
