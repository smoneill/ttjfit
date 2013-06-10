import ROOT as r
import sys


f = open("data/cerba_efficiencies.txt", "r")

#f = open("data/test.txt", "r")
#words = dict([(line,f.line.split()) for line in f])
eff = {}

for line in f:
    line = line.strip()
    name = line.split()
    eff[name[0]]=name[1]
    #eff[int()] = { name[0] : name[1]}
print eff
#i = 1
#for line in f:
#    words = line.split()
#    print words[1]
#    l = dict([(f.GetKeys(),words[1]) for ])
#    i = i+1
