import ROOT as r
import sys

if len(sys.argv)<2:
    print "usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]

tf = r.TFile.Open(file_name)
f = open("data/fracs_effs_edit.txt")

s = file_name.split(".")
s1 = s[0].split("_")
channel = s1[1]

hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])
########################################
eff = {}
frac_pre = {}
i = 1
total = 0
f_4 = {}
f_5 = {}

for line in f:
    line = line.strip()
    line = line.translate(None,";:")
    name = line.split()

    eff[name[0]]=float(name[2])
    frac_pre[name[0]]=float(name[4])    
    f_4[name[0]]=eff[name[0]]*frac_pre[name[0]]
    if len(name[0]) != 4:
        del f_4[name[0]]
    if channel == "el" and i == 7:
            break
    if channel == "mu" and i == 14:
        break
    i += 1
print eff, frac_pre
print f_4

for name[0] in f_4:
    print name[0]
    total += f_4[name[0]]
for name[0] in f_4:
    f_5[name[0]] = f_4[name[0]]/total
print f_5
