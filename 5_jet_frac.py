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
i = 1               
k = 1

class Normalize(object):
    def __init__(self,vec1,vec2):
        #gives dot product of lists, product components, normed comps
        if len(vec1) != len(vec2):
            print "lists are not of equal length"
            exit()
        self.total = np.dot(vec1,vec2)
        self.comps = [x*y for x,y in zip(vec1,vec2)]
        self.norm_comps = [x/self.total for x in self.comps]

#Stuffs pre-sel into 4 jet efficiency dict and fraction dict 
with open("data/fracs_effs_edit.txt") as f:
    line_strip = [line.strip() for line in f.readlines()]
    trans = [line_strip[k].translate(None, ";:") for k in range(len(line_strip))]
    name = [trans[k].split() for k in range(len(trans))]
    if s1[1] == "el":
        low, high = 0,7
    if s1[1] == "mu":
        low, high = 7,14
    name = [name[k] for k in range(low,high)]
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
    name = [name[k] for k in range(low,high)] 
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

#Creates ordered list of interactions
comps = ["ttgg","ttqg","ttag","ttqq"]
#List of background interactions - mj
bg_inter = ["wj","st","dy"]


#Takes specified comps out of the three dicts
frac_pre = [frac_pre_dict[k] for k in comps]
eff4 = [eff_dict[k] for k in comps]
temp4_5 = [eff4_5[k] for k in comps]

#Takes mj, wj, st, dy from the efficiency and preselection dicts !(mj uses the wj eff)!
bg_eff4 = [eff_dict[k] for k in bg_inter]
bg_eff5 = [eff4_5[k] for k in bg_inter]
bg_inter.append("mj")
bg_pre = [signal[k] for k in bg_inter]
bg_eff4.append(eff_dict["wj"])
bg_eff5.append(eff4_5["wj"])

#Multiplies the eff and the signal for background
bg_4 = Normalize(bg_pre,bg_eff4)
bg_5 = Normalize(bg_4.comps,bg_eff5)

#Creates the norm of the 4 jets and 5 jets (using Normalize)
jets_4 = Normalize(eff4,frac_pre)
jets_5 = Normalize(temp4_5,jets_4.norm_comps)

#Multiples the tt comps by the efficiencies and signal
bg_tt = Normalize(temp4_5, jets_4.comps)
tt = [signal["tt"]*y for y in bg_tt.comps]

#Background fraction
bg_frac = sum(bg_5.comps)/sum(tt)
print "Background Fraction: ",bg_frac

#print "4 Jets components:","\n", zip(comps,jets_4.comps)
#print "4 Jets normed components:","\n", zip(comps,jets_4.norm_comps) 
print "5 Jets normed components:","\n", zip(comps,jets_5.norm_comps)


