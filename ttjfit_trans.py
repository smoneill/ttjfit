import ROOT as r
import sys

if len(sys.argv)<2:
    print "Usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]  

tf = r.TFile.Open(file_name)

hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])

print hists

ndata = hists["data"].Integral()

print ndata



