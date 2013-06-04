###ttjfit translation from C++ to PyRoot###
###Sean O'Neill###

import ROOT as r
from ROOT import TF1
import sys

if len(sys.argv)<2:
    print "Usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]  

#Opens file
tf = r.TFile.Open(file_name)

#Dictionary of data
hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])

#Stores number of events
ndata = hists["data"].Integral()

#Creates histogram and fills them
bg = r.TH1F("bg","bg",50,0,0.11)
bg.Add(hists["wj"],hists["st"],0.54,0.46)
ttg = r.TH1F("ttg","ttg",50,0,0.11)
ttg.Add(hists["ttgg"],hists["ttqq"],0.87,0.13)
ttq = r.TH1F("ttq","ttq",50,0,0.11) 
ttq.Add(hists["ttqg"],hists["ttag"],0.84,0.16)
bg1 = r.TH1F("bg1","bg1",50,0,0.11)
bg1.Add(hists["wj"],hists["st"],0.54,0.46)
ttg1 = r.TH1F("ttg1","ttg1",50,0,0.11)
ttg1.Add(hists["ttgg"],hists["ttqq"],0.87,0.13)
ttq1 = r.TH1F("ttq1","ttq1",50,0,0.11)
ttq1.Add(hists["ttqg"],hists["ttag"],0.84,0.16) 

#Monte Carlo histogram array
mc80 = r.TObjArray(3)
mc80.Add(bg)
mc80.Add(ttg)
mc80.Add(ttq)

#Initializes the fitter
fit0 = r.TFractionFitter(hists["data"],mc80)
fit0.Constrain(1,0.095,0.105)   #Background constraint
fit0.Constrain(2,0.0,0.9)       #ttg constraint
fit0.Constrain(3,0.0,0.9)       #ttq constraint

status = fit0.Fit()
c0 = r.TCanvas("c0","ttj fit",600,400)

if status == 0:
   result0 = fit0.GetPlot()
   hists["data"].Draw("Ep")

#allow to pass-by-ref to GetResult
fbg , dfbg = r.Double(0) , r.Double(0) 

#Gets results from the fitting
fit0.GetResult(0,fbg,dfbg)
scale = ndata*fbg
bg1.Scale(scale)                        #scales bg1

fttg , dfttg = r.Double(0) , r.Double(0)
fit0.GetResult(1,fttg,dfttg)
scale = ndata*fttg
ttg1.Scale(scale)                       #scales ttg1
sm1 = r.TH1F("sm1", "sm1",50,0,0.11)    #histogram sm1
sm1.Add(bg1,ttg1,1.,1.)

fttq , dfttq = r.Double(0) , r.Double(0)
fit0.GetResult(2,fttq,dfttq)
scale = ndata*fttq
ttq1.Scale(scale)                       #scales ttq1
sm2 = r.TH1F("sm2","sm2",50,0,0.11)     #histogram sm2
sm2.Add(sm1,ttq1,1.,1.)

#Color settings for histograms
sm2.SetFillColor(r.kRed)
sm1.SetFillColor(r.kYellow)
bg1.SetFillColor(r.kBlue)

sm2.Draw("same")
sm1.Draw("same")
bg1.Draw("same")

#Outputs fractions
print "fttg from Lhood=", fttg, "+/-", dfttg
print "fttq from Lhood=", fttq, "+/-", dfttq
