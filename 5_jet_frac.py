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

#Components of background and tt
comps = ["ttgg","ttqg","ttag","ttqq","wj","st","dy","mj"]
tt_comps = ["ttgg","ttqg","ttag","ttqq"]
bg_comps = ["wj","st","dy","mj"]

#Takes specified comps out of the three dicts
tt_pre_eff = [eff_dict[k] for k in tt_comps]
tt_pre_frac = [frac_pre_dict[k] for k in tt_comps]

tt_eff4 = Normalize(tt_pre_eff, tt_pre_frac)
tt_4j_evnts = [tt_eff4.norm_comps[k]*signal["tt"] for k in range(len(tt_eff4.norm_comps))]

bg_4j_evnts = [signal[k] for k in bg_comps]
bg_4j_evnts[0] += bg_4j_evnts[-1]    #wj gets absorbed into mj
#bg_comps[0] += "+"+bg_comps[-1]
bg_comps.remove("mj")
bg_4j_evnts.remove(bg_4j_evnts[-1])
tt_eff4_5 = [eff4_5[k] for k in tt_comps]
tt_5j_evnts = Normalize(tt_4j_evnts, tt_eff4_5)

bg_eff4_5 = [eff4_5[k] for k in bg_comps]
bg_5j_evnts = Normalize(bg_4j_evnts, bg_eff4_5)

#Total background and tt events for 5-jets
tt_total = sum(tt_5j_evnts.comps)
bg_total = sum(bg_5j_evnts.comps)

#Relative background signal for 5-jets
backgrd_frac = bg_total/(tt_total+bg_total)

print "Background components: \n", zip(bg_comps,bg_5j_evnts.comps)
print "tt components: \n", zip(tt_comps,tt_5j_evnts.comps)
print "Background fraction: \n",backgrd_frac
print "Normalized tt components: \n",tt_5j_evnts.norm_comps


'''
#Takes mj, wj, st, dy from the efficiency and preselection dicts !(mj uses the wj eff)!
bg_eff5 = [eff4_5[k] for k in bg_inter]
bg_inter.append("mj")
bg_4 = [signal[k] for k in bg_inter]
bg_eff5.append(eff4_5["wj"])

#Multiplies the eff and the signal for background
bg_5 = Normalize(bg_4,bg_eff5)

#Creates the norm of the 4 jets and 5 jets (using Normalize)
jets_4 = Normalize(eff4,frac_pre)
jets_5 = Normalize(temp4_5,jets_4.norm_comps)

#Multiples the tt comps by the efficiencies and signal
bg_tt = Normalize(temp4_5, frac_pre)#could be jets_4.comps
tt = [signal["tt"]*y for y in bg_tt.comps]

#Background fraction
bg_frac = sum(bg_5.comps)/(sum(bg_5.comps)+sum(tt))
print "Background Fraction: ",bg_frac

#print "4 Jets components:","\n", zip(comps,jets_4.comps)
#print "4 Jets normed components:","\n", zip(comps,jets_4.norm_comps) 
#print "5 Jets normed components:","\n", zip(comps,jets_5.norm_comps)
print "5 jets normed components:", "\n", zip(comps,bg_tt.norm_comps)
'''
