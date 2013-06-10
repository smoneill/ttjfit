###ttjfit translation from C++ to PyRoot###
###Sean O'Neill###

import ROOT as r
import sys

if len(sys.argv)<2:
    print "Usage: ttjfit_trans <file.root>"
    exit()
else:
    file_name = sys.argv[1]  

#Where to print to
s = file_name.split(".")
s1 = s[0].split("_")
path_name = "graphs/frac_"+s1[1]+".pdf"

#Opens ROOT file
tf = r.TFile.Open(file_name)

#Opens efficiency file
f = open("data/test.txt","r")

#Dictionary of data
hists = dict([(h.GetName(),tf.Get(h.GetName())) for h in tf.GetListOfKeys()])

#Opens efficiency file
f = open("data/cerba_efficiencies.txt","r")

#Dictionary of efficiencies based on the file entered
eff = {}
i = 1
for line in f:
    line = line.strip()
    name = line.split()
    eff[name[0]]=name[1]
    i +=1
    if s1[1] == "el" and i ==11:
        break

#Deletes non-digit entries
del eff["#"]

#Converts string values to floats
eff["st"]=float(eff["st"])
eff["wj"]=float(eff["wj"])
eff["ttqq"]=float(eff["ttqq"])
eff["ttgg"]=float(eff["ttgg"])
eff["ttqg"]=float(eff["ttqg"])
eff["ttag"]=float(eff["ttag"])

#Stores number of events
ndata = hists["data"].Integral()

#Creates histogram and fills them from file, efficiencies from file
bg = r.TH1F("bg","bg",50,0,0.11)
bg.Add(hists["wj"],hists["st"],eff["wj"],eff["st"])
ttg = r.TH1F("ttg","ttg",50,0,0.11)
ttg.Add(hists["ttgg"],hists["ttqq"],eff["ttgg"],eff["ttqq"])
ttq = r.TH1F("ttq","ttq",50,0,0.11) 
ttq.Add(hists["ttqg"],hists["ttag"],eff["ttqg"],eff["ttag"])
bg1 = r.TH1F("bg1","bg1",50,0,0.11)
bg1.Add(hists["wj"],hists["st"],eff["wj"],eff["st"])
ttg1 = r.TH1F("ttg1","ttg1",50,0,0.11)
ttg1.Add(hists["ttgg"],hists["ttqq"],eff["ttgg"],eff["ttqq"])
ttq1 = r.TH1F("ttq1","ttq1",50,0,0.11)
ttq1.Add(hists["ttqg"],hists["ttag"],eff["ttqg"],eff["ttag"]) 

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

#tf.Close()

#Allows to pass-by-ref to GetResult
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
sm1.Add(bg1,ttg1,1.,1.)                 #fills sm1

fttq , dfttq = r.Double(0) , r.Double(0)
fit0.GetResult(2,fttq,dfttq)
scale = ndata*fttq
ttq1.Scale(scale)                       #scales ttq1
sm2 = r.TH1F("sm2","sm2",50,0,0.11)     #histogram sm2
sm2.Add(sm1,ttq1,1.,1.)                 #fills sm2

#Color settings for histograms
sm2.SetLineColor(r.kRed)
sm1.SetLineColor(r.kBlue+2)
bg1.SetLineColor(r.kRed-7)

#Draws the three fits created with c0 on one canvas
sm2.Draw("same")                        #draws sm1
sm1.Draw("same")                        #draws sm2
bg1.Draw("same")                        #draws bg1

#Rounds all the values for display purposes
fttg = round(fttg,7)
fttq = round(fttq,7)
dfttg = round(dfttg,7)
dfttq = round(dfttq,7)

#Outputs fractions to screen
if s1[1] == "el":
    print "Electron Channel"
if s1[1] == "mu":
    print "Muon Channel"

print "fttg from Lhood=", fttg, "+/-", dfttg
print "fttq from Lhood=", fttq, "+/-", dfttq

#Prints histograms to file                                            
c0.Print(path_name)

#Opens a file for storing fraction values
f = open("frac_el.txt","a+r")

#Makes sure to append only for two fractions
length = len(f.readlines())
if length < 6:

    if s1[1] == "el":
        f.write("Electron ")
    if s1[1] == "mu"
        f.write("Muon ")

    f.write("Fractions\n")
    table1 = "fttg  = "+str(fttg)+"  +/- "+str(dfttg)+"\n"
    table2 = "fttq  = "+str(fttq)+" +/- "+str(dfttq)+"\n"

#Writes the two fractions to the file
    f.write(table1)
    f.write(table2)

else:
    print "File full"
    exit()
