###ttjfit translation from C++ to PyRoot###
###Sean O'Neill###
import ROOT as r
import sys
from five_jet_frac import fiveJetEfficiencyFilter
from fractions import componentSolver
r.gROOT.SetBatch(1)

#Where to print to
file_name = sys.argv[1]
s = file_name.split(".")
s1 = s[0].split("_")
path_name = "graphs/frac_"+s1[1]+".pdf"
path_name2 = "graphs/frac_comp_Solver_"+s1[1]+".pdf"
channel = s1[1]

#Opens ROOT file
tf = r.TFile.Open(file_name)

#Dictionary of the template histograms
hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])

#Dictionaries of the components of the background and tt 5-jets
fJetFracs = fiveJetEfficiencyFilter(sys.argv)
ttDict = dict(zip(fJetFracs.ttComps,fJetFracs.tt_5jet))
bgDict = dict(zip(fJetFracs.bgComps,fJetFracs.bg_5jet))

#Total number of events
ndata = hists["data"].Integral()

#Creates histogram and fills them from file, efficiencies from file
bg = r.TH1F("bg","bg",50,0,0.11)
bg.Add(hists["wj"],hists["st"],bgDict["wj"],bgDict["st"])
ttg = r.TH1F("ttg","ttg",50,0,0.11)
ttg.Add(hists["ttgg"],hists["ttqq"],ttDict["ttgg"],ttDict["ttqq"])
ttq = r.TH1F("ttq","ttq",50,0,0.11) 
ttq.Add(hists["ttqg"],hists["ttag"],ttDict["ttqg"],ttDict["ttag"])
bg1 = r.TH1F("bg1","bg1",50,0,0.11)
bg1.Add(hists["wj"],hists["st"],bgDict["wj"],bgDict["st"])
ttg1 = r.TH1F("ttg1","ttg1",50,0,0.11)
ttg1.Add(hists["ttgg"],hists["ttqq"],ttDict["ttgg"],ttDict["ttqq"])
ttq1 = r.TH1F("ttq1","ttq1",50,0,0.11)
ttq1.Add(hists["ttqg"],hists["ttag"],ttDict["ttqg"],ttDict["ttag"]) 
data = r.TH1F("data","data",50,0,0.11)
data.Add(hists["data"],1)

#Used in implimenting the Component Solver
bg2 = bg1
ttg2 = ttg1
ttq2 = ttq1

#Scales to large number to reduce template uncertainties
bg.Scale(1000000.)
ttg.Scale(1000000.)
ttq.Scale(1000000.)

#Monte Carlo histogram array
mc80 = r.TObjArray(3)

mc80.Add(bg)
mc80.Add(ttg)
mc80.Add(ttq)

#Initializes the fitter
fit0 = r.TFractionFitter(hists["data"],mc80)
fit0.Constrain(1,fJetFracs.backgroundFrac-0.005,0.005+fJetFracs.backgroundFrac)   #Background constraint
fit0.Constrain(2,0.0,0.9)       #ttg constraint
fit0.Constrain(3,0.0,0.9)       #ttq constraint

#Opens a canvas to print the histograms 
status = fit0.Fit()
c0 = r.TCanvas("c0","ttj fit",600,400)

#Allows to pass-by-ref to GetResult
fbg , dfbg =  r.Double(0) , r.Double(0) 
fttg , dfttg = r.Double(0) , r.Double(0)
fttq , dfttq = r.Double(0) , r.Double(0)

#Gets results from the fitting
fit0.GetResult(0,fbg,dfbg)
fit0.GetResult(1,fttg,dfttg)
fit0.GetResult(2,fttq,dfttq)

def scaling(histogram, frac):
    '''Scales the histogram to the data'''
    histogram.Scale(frac*ndata/histogram.Integral()) 

#Scales the histograms
scaling(bg1,fbg)
scaling(ttg1,fttg)
scaling(ttq1,fttq)

sm1 = r.TH1F("sm1", "sm1",50,0,0.11)    #histogram sm1
sm1.Add(bg1,ttg1,1.,1.)                 #fills sm1

sm2 = r.TH1F(channel+" TFracFit",channel+" TFracFit",50,0,0.11)     #histogram sm2
sm2.Add(sm1,ttq1,1.,1.)                 #fills sm2

#Color settings for histograms
sm2.SetFillColor(r.kBlue)
sm1.SetFillColor(r.kRed)
bg1.SetFillColor(r.kGreen+3)

#Draws the three fits created with c0 on one canvas
sm2.Draw("HIST Same")                        #draws sm1
sm1.Draw("HIST Same")                        #draws sm2
bg1.Draw("HIST Same")                        #draws bg1
hists["data"].Draw("Ep Same")

#Sets the legend 
leg = r.TLegend(0.7,0.4,0.9,0.7)
leg.SetHeader("The Contribution")
leg.AddEntry(sm2,"Quark","f")
leg.AddEntry(sm1,"Gluon","f")
leg.AddEntry(bg1,"Background","f")
leg.AddEntry(hists["data"],"Data","ep")
leg.Draw()

#Rounds all the values for display purposes
fttg = round(fttg,7)
fttq = round(fttq,7)
dfttg = round(dfttg,7)
dfttq = round(dfttq,7)

#Outputs fractions to screen
if s1[1] == "el":
    print "Electron Channel"
if s1[1] == "mu":
    print "Muon Channel"

print "Sum Fraction =", sum([fttg,fttq,fbg])
print "fttg from Lhood=", fttg, "+/-", dfttg
print "fttq from Lhood=", fttq, "+/-", dfttq
print "fttq/(fttg+fttq)=", fttq/sum([fttq,fttg])


################################################################################################################
'''Component Solver'''

#Converts histograms to ntuples
bgBins = [bg.GetBinContent(i)*ndata*fJetFracs.backgroundFrac/bg.Integral() for i in range(bg.GetNbinsX()+2)]
ttgBins = [ttg.GetBinContent(i)*ndata/ttg.Integral() for i in range(ttg.GetNbinsX()+2)]
ttqBins = [ttq.GetBinContent(i)*ndata/ttq.Integral() for i in range(ttq.GetNbinsX()+2)]
dataBins = [data.GetBinContent(i) for i in range(data.GetNbinsX()+2)]

#Impliments the Component Solver
compSolver = componentSolver(observed = dataBins, base = bgBins, components = [ttgBins,ttqBins])
print compSolver
print "background Fraction" ,fJetFracs.backgroundFrac
print "fraction sum ", sum(compSolver.fractions,fJetFracs.backgroundFrac)
print "fraction: ", compSolver.fractions[1]/sum(compSolver.fractions)
print ttgBins[1],ttqBins[1],bgBins[1],dataBins[1]
#Prints histograms to file                                           
c0.Print(path_name)

#Scales from the results of the Component Solver
scaling(bg2,fJetFracs.backgroundFrac)
scaling(ttq2,compSolver.fractions[1])
scaling(ttg2,compSolver.fractions[0])

c1 = r.TCanvas("c1","compSolver", 600,400)

sm3 = r.TH1F("sm3","sm3",50,0,0.11)
sm3.Add(bg2,ttg2,1.,1.)

sm4 = r.TH1F(channel+" compSolver",channel+" compSolver",50,0,0.11)
sm4.Add(sm3,ttq2,1.,1.)   

sm4.SetFillColor(r.kBlue)
sm3.SetFillColor(r.kRed)
bg2.SetFillColor(r.kGreen+3)

sm4.Draw("HIST Same")
sm3.Draw("HIST Same")
bg2.Draw("HIST Same")
hists["data"].Draw("Ep Same")

leg = r.TLegend(0.7,0.4,0.9,0.7)
leg.SetHeader("The Contribution")
leg.AddEntry(sm4,"Quark","f")
leg.AddEntry(sm3,"Gluon","f")
leg.AddEntry(bg2,"Background","f")
leg.AddEntry(hists["data"],"Data","ep")
leg.Draw()

c1.Print(path_name2)

#Opens a file for storing fraction values
f = open("frac_comparitive.txt","a+r")

table1 = "fttg  = "+str(fttg)+"  +/- "+str(dfttg)+ "\n"
table2 = "fttq  = "+str(fttq)+" +/- "+str(dfttq)+"\n"
table3 = "fttq/(fttq+fttg)  = "+str(fttq/sum([fttg,fttq]))+"\n"
table4 = "sumFraction  = "+str(sum([fttg,fttq,fbg]))+"\n \n"

table5 = str(compSolver)+"\n \n"+"ftq/(fttq+fttg)  = "+str(compSolver.fractions[1]/sum(compSolver.fractions))+"\n \n"+"sumFraction  = "+str(sum(compSolver.fractions,fJetFracs.backgroundFrac))+"\n \n \n"

#Writes the two fractions to the file
'''
f.write("TFractionFitter Results: \n")
f.write(table1)
f.write(table2)
f.write(table3)
f.write(table4)
f.write("componentSolver Results: \n")
f.write(table5)
'''
