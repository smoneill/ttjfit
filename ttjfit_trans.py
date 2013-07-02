###ttjfit translation from C++ to PyRoot###
###Sean O'Neill###
from five_jet_frac import fiveJetEfficiencyFilter
import ROOT as r
r.gROOT.SetBatch(1)
import sys

#Where to print to
file_name = sys.argv[1]
s = file_name.split(".")
s1 = s[0].split("_")
path_name = "graphs/frac_"+s1[1]+".pdf"
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
    histogram.Scale(frac*ndata/histogram.Integral()) 

scaling(bg1,fbg)
scaling(ttg1,fttg)
scaling(ttq1,fttq)

sm1 = r.TH1F("sm1", "sm1",50,0,0.11)    #histogram sm1
sm1.Add(bg1,ttg1,1.,1.)                 #fills sm1

sm2 = r.TH1F("sm2","sm2",50,0,0.11)     #histogram sm2
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

#Prints histograms to file                                            
c0.Print(path_name)

#Opens a file for storing fraction values
f = open("frac_set.txt","a+r")

#Makes sure to append only for two fractions
length = len(f.readlines())
if length < 6:

    if s1[1] == "el":
        f.write("Electron ")
    if s1[1] == "mu":
        f.write("Muon ")

    f.write("Fractions\n")

else:
    print "File full"
    exit()

table1 = "fttg  = "+str(fttg)+"  +/- "+str(dfttg)+"\n"
table2 = "fttq  = "+str(fttq)+" +/- "+str(dfttq)+"\n"
#Writes the two fractions to the file
f.write(table1)
f.write(table2)
