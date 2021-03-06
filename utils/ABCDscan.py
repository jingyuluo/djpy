import supy,math,ROOT as r
from supy.__plotter__ import setupTdrStyle
from supy.utils import cmsStamp

def getCounts(histo):
	keys = ['A','B','C','D','E','F','G','H']
	dict = {}
	for i in range(len(keys)):
		dict[keys[i]] = (histo.GetBinContent(i+1),histo.GetBinError(i+1))

	results = []
	results.append(dict['H'])
	combinations = [('F','G','B'),('E','G','C'),('D','G','A'),('B','E','A'),('C','F','A'),('E','F','D')]
	for comb in combinations:
		b,c,a = dict[comb[0]],dict[comb[1]],dict[comb[2]]
		results.append(estimate(b,c,a))
	results.append(estimate(dict['B'],dict['C'],dict['D'],dict['A']))
	return results

def estimate(b,c,a,d=None):
	if not b[0]>0 or not c[0]>0 or not a[0]>0 : return (0,0)
	est = b[0]*c[0]/float(a[0])
	err = est*math.sqrt(pow(a[1]/float(a[0]),2)+
						pow(b[1]/float(b[0]),2)+
						pow(c[1]/float(c[0]),2))
	if d is not None and d[0]>0:
		est = b[0]*c[0]*a[0]/d[0]/d[0]
		err = est*math.sqrt(pow(a[1]/float(a[0]),2)+
							pow(b[1]/float(b[0]),2)+
							pow(c[1]/float(c[0]),2)+
							4*pow(d[1]/float(d[0]),2))
	return (est,err)

def pvalue(b,be,obs,ntoys):

	nbins = max(int(b)*10,20)
	hist=r.TH1F("h","h",nbins,-0.5,nbins-0.5)
	rand=r.TRandom()

	for i in range(int(ntoys)):
		bkg=rand.Gaus(b,be)
		if bkg<=0. : continue
		hist.Fill(rand.Poisson(bkg),r.TMath.Gaus(bkg,b,be,True))

	hist.Scale(1./hist.Integral())
	return hist.Integral(hist.FindFixBin(obs),hist.GetNbinsX())

def string(obj): return '('+','.join(str(a) for a in obj)+')' if type(obj)==tuple else str(obj)

def listdiff(a,b): return [i for i,j in zip(a,b) if i!=j]

def lumistring(lumi): 
	if lumi>1e3: return str(round(lumi/float(1e3),1))+' fb^{-1}'
	else : return str(round(lumi,1))+' pb^{-1}'

def plotABCDscan(analysis,org,plotter,n,blind=True,onlyB=False):

	setupTdrStyle()


	plotter.pdfFileName = plotter.pdfFileName.replace(analysis.name+'.pdf','Scans_'+analysis.name+'.pdf')
	plotter.canvas.Clear()
	plotter.printCanvas("[")
	text1 = plotter.printTimeStamp()
	plotter.flushPage()

	# get all the counts
	counts = [[0]*len(analysis.scan) for sample in org.samples]
	for step in org.steps : 
		for plotName in sorted(step.keys()) :
			if 'ABCDEFGHcounts' not in plotName: continue
			i = eval(plotName[:plotName.find('ABCDEFGH')])
			for j in range(len(org.samples)): counts[j][i] = getCounts(step[plotName][j])

	# pick points to scan
	scans=[]
	for cut in analysis.scanPrompt: scans.append((cut,cut,None))

	# constant names
	cutNames = ['(NPrompt1,PromptFrac1)','(NPrompt2,PromptFrac2)','DiscVtx']
	histNames = ['observed','FG/B','EG/C','DG/A','BE/A','CF/A','EF/D','BCD/A^{2}']

	# plot scans
	for scan in scans:
		plotter.canvas=r.TCanvas("c","c",600,600)
		plotter.canvas.Divide(1,2)
		plotter.canvas.cd(1).SetPad(0.01,0.30+0.0,0.99,0.99)
		plotter.canvas.cd(1).SetTopMargin(0.07)
		plotter.canvas.cd(1).SetBottomMargin(0.)
		plotter.canvas.cd(2).SetPad(0.01,0.01,0.99,0.30)
		plotter.canvas.cd(2).SetTopMargin(0.)
		plotter.canvas.cd(2).SetBottomMargin(0.35)
		plotter.canvas.cd(1)
		r.gPad.SetLogy()
		#r.gPad.SetTicky(0)
	
		title=''
		#title='max Prompt Tracks = %s, max Prompt Energy Fraction = %s'%(scan[0][0],scan[0][1])
		xtitle = 'Vertex/cluster discriminant'
		ytitle = 'Number of events'

		indices = [i for i,cuts in enumerate(analysis.scan) if len(listdiff(cuts,scan))<=1]
		labels = [string(cuts[scan.index(None)]) for i,cuts in enumerate(analysis.scan) if i in indices]
		# first make a plot of signal efficiency
		sigSamples = [sample for sample in org.samples if 'H' in sample['name']]		
	 	sigeff = [r.TH1F('','',len(indices),0,1) for sample in sigSamples]
		for j,sample in enumerate(sigSamples):
			i = org.indexOfSampleWithName(sample['name'])
			norm = sample['xs']*org.lumi
			for k,idx in enumerate(indices):
				sigeff[j].SetBinContent(k+1,100*counts[i][idx][0][0]/float(2*norm))
				sigeff[j].SetBinError(k+1,100*counts[i][idx][0][1]/float(norm))
				sigeff[j].GetXaxis().SetBinLabel(k+1,labels[k])

		# Data/QCD plots with signal efficiency on the same plot
		for j,sample in enumerate(org.samples):
			if 'H' in sample['name'] : continue

			histos = [r.TH1F(name,title,len(indices),0,1) for name in histNames]
			histob = r.TH1F('predicted bkg.',title,len(indices),0,1)
			histob0 = r.TH1F('predicted bkg.',title,len(indices),0,1)
			histoz = r.TH1F('','',len(indices),0,1)

			for h in histos: h.GetXaxis().SetNdivisions(len(indices)*100+10,False)
			histoz.GetXaxis().SetNdivisions(len(indices)*100+10,False)

			for k,idx in enumerate(indices):
				b,berr = getBkg(counts[j][idx],None)
				histob.SetBinContent(k+1,b)
				histob.SetBinError(k+1,berr)
				histob0.SetBinContent(k+1,b)
				histob0.SetBinError(k+1,0.00001)
				N=int(counts[j][idx][0][0])
				if N==0: 
					histoz.SetBinContent(k+1,-1e5)
					continue
				p=pvalue(b,berr,N,1e4)
				z=r.RooStats.PValueToSignificance(p)
				histoz.SetBinContent(k+1,z)
				histoz.SetBinError(k+1,0.)

			if onlyB:
				legend = r.TLegend(0.5, 0.65, 0.93, 0.83)
			else:
				legend = r.TLegend(0.7, 0.55, 0.93, 0.93)
			for i in reversed(range(n)):
				if blind and 'Data' in sample['name'] and i==0: continue
				for k,idx in enumerate(indices):
					histos[i].SetBinContent(k+1,counts[j][idx][i][0])
					histos[i].SetBinError(k+1,counts[j][idx][i][1])
					histos[i].GetXaxis().SetBinLabel(k+1,labels[k])
					histoz.GetXaxis().SetBinLabel(k+1,labels[k])
					histob.GetXaxis().SetBinLabel(k+1,'')
					histob0.GetXaxis().SetBinLabel(k+1,'')
					
				histos[i].GetXaxis().SetTitle(xtitle)
				histos[i].GetYaxis().SetTitle(ytitle)
				histos[i].SetStats(False)
				histob.SetStats(False)
				histos[i].GetYaxis().SetTitleOffset(1.25)
				histos[i].GetYaxis().SetTitleSize(0.066)
				histos[i].GetYaxis().SetLabelSize(0.062)
				histoz.GetXaxis().SetTitle(xtitle)
				histoz.SetTitle('')
				histoz.SetStats(0)
				histoz.SetMarkerStyle(8)
				histob.SetMarkerSize(0)
				histob0.SetMarkerSize(0)
				histos[i].SetMarkerStyle(25 if i!=0 else 8)
				if i==(n-1):histos[i].SetMarkerStyle(21)
				histos[i].SetMarkerColor(i+1)
				histos[i].SetFillColor(0)
				histos[i].SetLabelSize(0.07)
				if onlyB: 
					if i==0:
						legend.AddEntry(histos[i],'Observed background')
				else:
					legend.AddEntry(histos[i],histNames[i])
				option='EX0' if i==(n-1) else 'EX0same'
				histos[i].Draw(option)
			if onlyB:
				legend.AddEntry(histob,'Predicted background')
				histob.SetFillColor(r.kBlue)
				histob0.SetFillColor(r.kWhite)
				histob.SetFillStyle(3001)
				histob0.SetLineWidth(3)
				histob.SetLineWidth(3)
				histob0.SetLineColor(r.kBlue)
				histob.SetLineColor(r.kBlue)
				histos[0].SetLineWidth(2)
				histos[0].Draw('EX0')
				histob.Draw("E2same")
				histob0.Draw("Lsame")
				histos[0].Draw('EX0same')
			histos_tmp=tuple([histos[i] for i in range(n)])
			plotter.setRanges(histos_tmp,*plotter.getExtremes(1,histos_tmp,[False]*n))
			
			if onlyB:
				cmsStamp(lumi=18500,coords=(0.71,0.84),preliminary=False)
				#cmsStamp(lumi=None,coords=(0.78,0.88))
			else:
				cmsStamp(lumi=org.lumi,coords=(0.45,0.88),simulation=True)
				#cmsStamp(lumi=None,coords=(0.45,0.85))
			
			pad = r.TPad("pad2","",0,0,1,1)
			pad.SetFillStyle(4000)
			pad.SetFrameFillStyle(0)
			pad.SetLogy(0)
			pad.Draw()
			pad.cd()
			for i,sample in enumerate(sigSamples):
				option='histY+' + ('same' if i>0 else '')
				sigeff[i].SetLineWidth(1)
				sigeff[i].SetStats(False)
				sigeff[i].SetLabelSize(0.06)
				sigeff[i].SetLineColor(i+2)
				sigeff[i].SetLineStyle(2)
				sigeff[i].GetYaxis().SetRangeUser(0,45)
				sigeff[i].GetYaxis().SetTitle('efficiency [%]')
				sigeff[i].Draw(option)
				legend.AddEntry(sigeff[i],sample['name'].split('.')[0])
			
			legend.SetFillColor(0)
			legend.SetBorderSize(0)
			legend.Draw("same")

			plotter.canvas.cd(2)
			r.gPad.SetGridy()
			histoz.GetYaxis().SetNdivisions(505,True)
			histoz.GetYaxis().SetTitleOffset(0.5)
			histoz.GetYaxis().SetTitleSize(0.16)
			histoz.GetXaxis().SetTitleOffset(1.0)
			histoz.GetXaxis().SetTitleSize(0.16)
			histoz.GetYaxis().SetLabelSize(0.14)
			histoz.GetYaxis().SetLabelOffset(0.015)
			histoz.GetYaxis().SetTickLength(1.3*histoz.GetYaxis().GetTickLength())
			histoz.GetXaxis().SetTickLength(2.*histoz.GetXaxis().GetTickLength())
			histoz.GetXaxis().SetLabelSize(0.19)
			histoz.GetXaxis().SetLabelOffset(0.02)
			histoz.GetYaxis().SetTitle('Significance ')
			#histoz.GetYaxis().CenterTitle()
			histoz.GetYaxis().SetRangeUser(-2.99,2.99)
			histoz.Draw('P')
			plotter.printCanvas()
			#plotter.canvas.Clear()

	plotter.printCanvas("]")
	print plotter.pdfFileName, "has been written."

def getBkg(counts,cuts):
	list=counts[1:]
	b=list[-1][0]
	err_stat=list[-1][1]
	combs = [obj[0] for obj in list]
	dists= [abs(comb-b) for comb in combs]
	err_sys = max(dists)
	#err_sys=0.5*(max(combs)-min(combs))
	#b=0.5*(max(combs)+min(combs))
	err=math.sqrt(pow(err_stat,2)+pow(err_sys,2))
	#err=err_stat
	print cuts,round(b,2),round(err,2),round(err_stat/b,2), round(err_sys/b,2),counts[0][0]
	return b,err

def plotExpLimit(analysis,n,org):

	denom = []
	for step in org.steps: 
		for plotName in sorted(step.keys()):
			if plotName == 'NE': denom=step[plotName]

	data={'bkg':[],'obs':[]}
	for step in org.steps:
		for plotName in sorted(step.keys()):
			if 'ABCDEFGHcounts' not in plotName : continue
			cutsidx=eval(plotName[:plotName.find('ABCDEFGH')])
			for j,sample in enumerate(org.samples):
				counts = getCounts(step[plotName][j])
				name=sample['name'].split('.')[0]
				if 'Data' in name: # get background estimate
					print cutsidx
					data['bkg'].append(getBkg(counts[:n],(analysis.scan[cutsidx],cutsidx)))
					data['obs'].append(counts[0])
				elif 'H' in name:
					if name not in data.keys(): 
						data[name] = []
						nEvents = float(sample['nEvents'])*0.09
					data[name].append((counts[0][0]/(denom[j].Integral()/4.),counts[0][1]/(denom[j].Integral()/4.)))

	import pickle
	pickle.dump(data,open(supy.whereami()+'/../results/data/data.pkl','w'))
