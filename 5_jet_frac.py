import ROOT as r
import sys
import numpy as np

if len(sys.argv)<2:
    print "usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]

tf = r.TFile.Open(file_name)
f = open("data/fracs_effs_edit.txt")
ef = open("data/cerba_efficiencies.txt")

s = file_name.split(".")
s1 = s[0].split("_")
channel = s1[1]

hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])
########################################
eff_dict = {}       #Dict of 4 jet efficiencies
frac_pre_dict = {}  #Dict of pre-selection fractions
eff4_5 = {}         #Dict of 4->5 jet efficiencies
i = 1               
k = 1

class Normalize:
    def __init__(self,vec1,vec2):
        #gives dot product of lists, product components, normed comps
        if len(vec1) != len(vec2):
            print "lists are not of equal length"
            exit()
        self.total = np.dot(vec1,vec2)
        self.comps = [vec1[k]*vec2[k] for k in range(len(vec1))]
        self.norm_comps = [vec1[k]*vec2[k]/self.total for k in range(len(vec1))] 

#Stuffs pre-sel into 4 jet efficiency dict and fraction dict 
for line in f:
    line = line.strip()
    line = line.translate(None,";:")
    name = line.split()

    eff_dict[name[0]]=float(name[2])
    frac_pre_dict[name[0]]=float(name[4])    

    #Stops at specified lines in file   
    if channel == "el" and i == 7:
            break
    if channel == "mu" and i == 14:
        break
    i += 1

#Stuffs 4->5 jets efficiencies into dict
for line in ef:
    line = line.strip()
    name4_5 = line.split()
    eff4_5[name4_5[0]] = name4_5[1]
    k += 1
    if s1[1] == "el" and k == 11:
        break

#Creates ordered list of interactions
comps = ["ttgg","ttqg","ttag","ttqq"]

#Takes specified comps out of the three dicts
frac_pre = [frac_pre_dict[k] for k in comps]
eff4 = [eff_dict[k] for k in comps]
temp4_5 = [float(eff4_5[k]) for k in comps]

#Creates the norm of the 4 jets and 5 jets (using Normalize)
jets_4 = Normalize(eff4,frac_pre)
jets_5 = Normalize(temp4_5,jets_4.norm_comps)

print "4 Jets components:","\n", zip(comps,jets_4.comps)
#print "4 Jets normed components:","\n", zip(comps,jets_4.norm_comps) 
print "5 Jets components:","\n", zip(comps,jets_5.comps)


