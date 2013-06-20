###Converts the preselection fractions into 4 jet fractions then 5 jet fractions
###Author: Sean O'Neill
import ROOT as r
import sys
import numpy as np

if len(sys.argv)<2:
    print "usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]

tf = r.TFile.Open(file_name)
s = file_name.split(".")
s1 = s[0].split("_")
channel = s1[1]

########################################
eff_dict = {}       #Dict of 4 jet efficiencies
frac_pre_dict = {}  #Dict of pre-selection fractions
eff4_5 = {}         #Dict of 4->5 jet efficiencies

class Convert(object):
    def __init__(self,vec1,vec2,event):
        self.prod = [x*y for x,y in zip(vec1,vec2)]
        self.norm = self.normalize(self.prod)
        self.frac = self.scale(self.norm,event)

    def normalize(self,product):
        return [x/sum(product) for x in product]

    def scale(self,fracVec, num):
        return [x*num for x in fracVec]

#Stuffs pre-sel into 4 jet efficiency dict and fraction dict 
with open("data/fracs_effs_edit.txt") as f:
    line_strip = [line.strip() for line in f.readlines()]
    trans = [line_strip[k].translate(None, ";:") for k in range(len(line_strip))]
    name = [trans[k].split() for k in range(len(trans))]
    if s1[1] == "el":
        low, high = 0,7
    if s1[1] == "mu":
        low, high = 7,14
    name = name[low:high]
    eff_dict = dict([(name[k][0],float(name[k][2])) for k in range(len(name))])
    frac_pre_dict= dict([(name[k][0],float(name[k][4])) for k in range(len(name))])
    
#Stuffs 4->5 efficiency file into 4_5 dict
with open("data/cerba_efficiencies.txt") as ef:
    line_strip = [line.strip() for line in ef.readlines()]  
    name = [line_strip[k].split("\t0") for k in range(len(line_strip))]
    if s1[1] == "el":
        low, high = 2,10
    if s1[1] == "mu":
        low, high = 11,19
    name = name[low:high] 
    eff4_5 = dict([(name[k][0],float(name[k][1])) for k in range(len(name))])

#Stuffs expected events into signal dict
with open("data/cerba_expect_4j.txt") as ex:
    line_strip = [line.strip() for line in ex.readlines()]
    name = [line_strip[k].split() for k in range(len(line_strip))]
    if s1[1] == "el":
        column = 2
    if s1[1] == "mu":
        column = 1
    name = [name[k] for k in range(2,7)]
    signal = dict([(name[k][0], float(name[k][column])) for k in range(len(name))])

#Components of background and tt
comps = ["ttgg","ttqg","ttag","ttqq","wj","st","dy","mj"]
tt_comps = ["ttgg","ttqg","ttag","ttqq"]
bg_comps = ["wj","st","dy","mj"]

#Takes specified comps out of the three dicts
tt_pre_eff = [eff_dict[k] for k in tt_comps]
tt_pre_frac = [frac_pre_dict[k] for k in tt_comps]

bg_4j_evnts = [signal[k] for k in bg_comps]

tt_eff4_5 = [eff4_5[k] for k in tt_comps]
bg_4j_evnts[0] += bg_4j_evnts[-1]    #wj gets absorbed into mj
bg_comps.remove("mj")
bg_4j_evnts.remove(bg_4j_evnts[-1])
bg_eff4_5 = [eff4_5[k] for k in bg_comps]

tt_4j = Convert(tt_pre_eff, tt_pre_frac,signal["tt"])

tt_5j = Convert(tt_4j.frac, tt_eff4_5,1)
bg_5j = Convert(bg_4j_evnts, bg_eff4_5,1)

#Total background and tt events for 5-jets
tt_total = sum(tt_5j.prod)
bg_total = sum(bg_5j.prod)

#Relative background signal for 5-jets
backgrd_frac = bg_total/(tt_total+bg_total)

#print "Background components: \n", zip(bg_comps,bg_5j_evnts.comps)
#print "tt components: \n", zip(tt_comps,tt_5j_evnts.comps)
print "Background fraction: \n",backgrd_frac
#print "Normalized tt components: \n",tt_5j_evnts.norm_comps



