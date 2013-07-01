###ttjfit translation from C++ to PyRoot###
###Sean O'Neill###

import ROOT as r
import sys
import numpy as np
import RedConDict as rdc

if len(sys.argv)<2:
    print "Usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]  

#Where to print to
s = file_name.split(".")
s1 = s[0].split("_")
path_name = "graphs/frac_"+s1[1]+".pdf"
channel = s1[1]

#Opens ROOT file
tf = r.TFile.Open(file_name)

#Dictionary of data
hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])

if channel == "el":
    lowFracs, highFracs = 0,7
    lowCerba, highCerba = 2,10
    column = 2
else:
    lowFracs, highFracs = 7,14
    lowCerba, highCerba = 11,19
    column = 1

lowExpect, highExpect = 2,7
########################################
eff_dict = {}       #Dict of 4 jet efficiencies
frac_pre_dict = {}  #Dict of pre-selection fractions
eff4_5 = {}         #Dict of 4->5 jet efficiencies

with open("data/fracs_effs_edit.txt") as f:

    name = rdc.FileStrip(f)  
    name = name[lowFracs:highFracs]
    effDict = rdc.Dict(name,2)
    preFracDict = rdc.Dict(name,4)

with open("data/cerba_efficiencies.txt") as ef:
    name = rdc.FileStrip(ef)
    name = name[lowCerba:highCerba]
    eff4_5Dict = rdc.Dict(name,1)

with open("data/cerba_expect_4j.txt") as ex:
    name = rdc.FileStrip(ex)
    name = name[lowExpect:highExpect]
    signalDict = rdc.Dict(name,column)

#Components of background and tt
comps = ["ttgg","ttqg","ttag","ttqq","wj","st","dy","mj"]
ttComps = ["ttgg","ttqg","ttag","ttqq"]
bgComps = ["wj","st","dy","mj"]

#Takes specified comps out of the three dicts
ttPreEff = [effDict[k] for k in ttComps]
ttPreFrac = [preFracDict[k] for k in ttComps]

bg_4jEvnts = [signalDict[k] for k in bgComps]

ttEff4_5 = [eff4_5Dict[k] for k in ttComps]
bg_4jEvnts[0] += bg_4jEvnts[-1]    #mj gets absorbed into wj
bgComps.remove("mj")
bg_4jEvnts.remove(bg_4jEvnts[-1])
bgEff4_5 = [eff4_5Dict[k] for k in bgComps]

tt_4j = rdc.Convert(ttPreEff, ttPreFrac,signalDict["tt"],3)

tt_5j = rdc.Convert(tt_4j, ttEff4_5,1,1)
bg_5j = rdc.Convert(bg_4jEvnts, bgEff4_5,1,1)

#Total background and tt events for 5-jets
ttTotal = sum(tt_5j)
bgTotal = sum(bg_5j)

#Relative background signal for 5-jets
backgrdFrac = bgTotal/(ttTotal+bgTotal)

ttDict = dict([(ttComps[items],tt_5j[items]) for items in range(len(tt_5j))])
bgDict = dict([(bgComps[k],bg_5j[k]) for k in range(len(bg_5j))])

#Stores number of events
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

ndata1 = bg.Integral()
ndata1 += ttg.Integral()
ndata1 += ttq.Integral()

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
fit0.Constrain(1,backgrdFrac-0.005,0.005+backgrdFrac)   #Background constraint
fit0.Constrain(2,0.0,0.9)       #ttg constraint
fit0.Constrain(3,0.0,0.9)       #ttq constraint

status = fit0.Fit()
c0 = r.TCanvas("c0","ttj fit",600,400)

#Allows to pass-by-ref to GetResult
fbg , dfbg,=  r.Double(0) , r.Double(0) 

#Gets results from the fitting
fit0.GetResult(0,fbg,dfbg)
scale = fbg#*ndata
bg1.Scale(scale)                        #scales bg1

fttg , dfttg = r.Double(0) , r.Double(0)
fit0.GetResult(1,fttg,dfttg)
scale = fttg#*ndata
ttg1.Scale(scale)                       #scales ttg1
sm1 = r.TH1F("sm1", "sm1",50,0,0.11)    #histogram sm1
sm1.Add(bg1,ttg1,1.,1.)                 #fills sm1

fttq , dfttq = r.Double(0) , r.Double(0)
fit0.GetResult(2,fttq,dfttq)
scale = fttq#*ndata
ttq1.Scale(scale)                       #scales ttq1
sm2 = r.TH1F("sm2","sm2",50,0,0.11)     #histogram sm2
sm2.Add(sm1,ttq1,1.,1.)                 #fills sm2

#Color settings for histograms
sm2.SetFillColor(r.kBlue)
sm1.SetFillColor(r.kRed)
bg1.SetFillColor(r.kGreen+3)

ndata2 = sm2.Integral()

print "Data Integral " ,ndata , "\n", "Total Result Integral ", ndata2

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

print "fttg from Lhood=", fttg, "+/-", dfttg
print "fttq from Lhood=", fttq, "+/-", dfttq

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
