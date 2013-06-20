###Converts the preselection fractions into 4 jet fractions then 5 jet fractions
###Author: Sean O'Neill
import ROOT as r
import sys
import numpy as np
import RedConDict as rdc

if len(sys.argv)<2:
    print "usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]

tf = r.TFile.Open(file_name)
s = file_name.split(".")
s1 = s[0].split("_")
channel = s1[1]

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

print "Background components: \n", zip(bgComps,bg_5j)
print "tt components: \n", zip(ttComps,tt_5j)
print "Background fraction: \n",backgrdFrac
