import supy,samples,calculables,steps,ROOT as r

class efficiency(supy.analysis) :

	ToCalculate = ['dijetVtxNRatio','dijetPromptness']
    
	def listOfSteps(self,config) :
		return ([
		supy.steps.printer.progressPrinter()]
		### filters
		+[supy.steps.filters.label('data cleanup'),
		supy.steps.filters.value('isPrimaryVertex',min=1),
		supy.steps.filters.value('isPhysDeclared',min=1).onlyData(),
		supy.steps.filters.value('isBeamScraping',max=0),
		supy.steps.filters.value('passBeamHaloFilterTight',min=1),
		supy.steps.filters.value('passHBHENoiseFilter',min=1)]

		### pile-up reweighting
		+[supy.calculables.other.Target("pileupPUInteractionsBX0",thisSample=config['baseSample'],
                                    target=("data/ABcontrol_observed.root","pileup"),
                                    groups=[('qcd',[]),('Huds',[]),('Hb',[])]).onlySim()] 

		### trigger
		+[supy.steps.filters.label("hlt trigger"),
		steps.trigger.hltFilterWildcard("HLT_HT250_v"),
		steps.trigger.hltFilterWildcard("HLT_HT250_DoubleDisplacedJet60_v")]
		#steps.trigger.hltFilterWildcard("HLT_HT250_DoubleDisplacedJet60_PromptTrack_v")]

		#steps.effplots.histos('candsDouble'),
		#steps.effplots.histos("doubleVeryLoose"),
		+[steps.plots.general(),
		steps.plots.promptness(),
		steps.plots.fractions(),
		steps.plots.vertices(),
		steps.plots.clusters()]
		)

	def calcsVars(self):
		calcs = []
		for calc in self.ToCalculate:
			calcs.append(getattr(calculables.Vars,calc)('dijetIndices'))
		return calcs

	def listOfCalculables(self,config) :
		return ( supy.calculables.zeroArgs(supy.calculables) +
		supy.calculables.zeroArgs(calculables)
		+self.calcsVars()
		)

	def listOfSampleDictionaries(self) :
		return [samples.qcd,samples.data,samples.sigmc]
    
	def listOfSamples(self,config) :
		nFiles = None # or None for all
		nEvents = None # or None for all
		MH = [1000,1000,1000,400,400,200]
		MX = [350,150,50,150,50,50]
		sig_names_u = ['Huds_'+str(a)+'_X_'+str(b) for a,b in zip(MH,MX)]
		sig_names_b = ['Hb_'+str(a)+'_X_'+str(b) for a,b in zip(MH,MX)]
		sig_samples_u = []
		sig_samples_b = []

		qcd_samples = []
		for i in range(len(sig_names_u)):
			sig_samples_u+=(supy.samples.specify(names = sig_names_u[i], color=i+1, markerStyle=20, nEventsMax=nEvents, nFilesMax=nFiles))
			sig_samples_b+=(supy.samples.specify(names = sig_names_b[i], color=i+1, markerStyle=20, nEventsMax=nEvents, nFilesMax=nFiles))

		return sig_samples_u

	def conclude(self,pars) :
		#make a pdf file with plots from the histograms created above
		org = self.organizer(pars)
		org.scale(lumiToUseInAbsenceOfData=30)
		plotter = supy.plotter( org,
			pdfFileName = self.pdfFileName(org.tag),
			doLog=True,
			blackList = ["lumiHisto","xsHisto","nJobsHisto"],
			)
		plotter.plotAll()

		#self.makeEfficiencyPlots(org,"candsDouble","doubleVeryLoose", plotter)

	def makeEfficiencyPlots(self, org, denomName, numName, plotter):
		plotter.doLog = False
		plotter.printCanvas("[")
		text1 = plotter.printTimeStamp()
		text2 = plotter.printNEventsIn()
		plotter.flushPage()

		hists_denom = []
		hists_num = []
		for step in org.steps:
			for plotName in sorted(step.keys()):
				if denomName in plotName: hists_denom.append(step[plotName])
				if numName in plotName: hists_num.append(step[plotName])

		for num_list,denom_list in zip(hists_num,hists_denom):
			ratio_tpl = tuple([supy.utils.ratioHistogram(num,denom) for num,denom in zip(num_list,denom_list)])
			for ratio in ratio_tpl:
				ratio.GetYaxis().SetTitle("efficiency")
			plotter.onePlotFunction(ratio_tpl)
		plotter.printCanvas("]")
		print plotter.pdfFileName, 'has been written'
