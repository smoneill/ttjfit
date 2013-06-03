import ROOT as r
import sys

if len(sys.argv)<2:
    print "Usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]  

tf = r.TFile.Open(file_name)

tf.ls()
