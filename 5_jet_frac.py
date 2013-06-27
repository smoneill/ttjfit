###Converts the preselection fractions into 4 jet fractions then 5 jet fractions
###Author: Sean O'Neill
import ROOT as r
import sys
import numpy as np
import RedConDict as rdc

class program(object):
    def __init__(self,rootFile):
        channelList = self.parseArgument(rootFile)
        effDict, preFracDict, eff4_5Dict, signalDict = self.parseData(channelList)
        self.calculateFractions(effDict, preFracDict, eff4_5Dict, signalDict)
        self.printFractions()
        
    def parseArgument(self,rootFile):
        if len(rootFile)<2: 
            print "usage: ttjfit_trans <file.root>"   
            exit() 
        else:
            file_name = rootFile[1]   
        tf = r.TFile.Open(file_name)
        s = file_name.split(".")  
        channel = s[0].split("_")[1]
        return self.channelSelect(channel)

    def channelSelect(self,ch):
        if ch == "el":
            num = [0,7,2,10,2,2,7]
        else:
            num = [7,14,11,19,1,2,7]
        name = ["loFrac", "hiFrac", "loCerba", "hiCerba", "column", "loExpect", "hiExpect"]
        return dict([(name[k],num[k]) for k in range(len(num))])
    



    def parseData(self,channelList):
        fracEffFile = "data/fracs_effs_edit.txt"
        cerbaEffFile = "data/cerba_efficiencies.txt"
        cerbaExpFile = "data/cerba_expect_4j.txt"
        fileList = [fracEffFile,cerbaEffFile,cerbaExpFile]
        files = []
        for item in fileList:
            files.append(self.fileStrip(item))
        
        name = files[0][channelList["loFrac"]:channelList["hiFrac"]]
        eff = self.makeDictionary(name,2)
        preFrac = self.makeDictionary(name,4)
        
        name = files[1][channelList["loCerba"]:channelList["hiCerba"]]
        eff4_5 = self.makeDictionary(name,1)
        
        name = files[2][channelList["loExpect"]:channelList["hiExpect"]]
        signal = self.makeDictionary(name,channelList["column"])
        return eff,preFrac,eff4_5,signal

    def fileStrip(self,fileName):
        with open(fileName) as f:
        
            stripped = [line.strip() for line in f.readlines()]
            translated = [stripped[k].translate(None, ";:") for k in range(len(stripped))]
            if fileName == "data/cerba_efficiencies.txt":
                return [translated[k].split("\t0") for k in range(len(translated))]
            else:
                return [translated[k].split() for k in range(len(translated))]

    def makeDictionary(self,dic,columnNum):
        return dict([(dic[k][0],float(dic[k][columnNum]))for k in range(len(dic))])




    def calculateFractions(self,effDict,preFracDict,eff4_5Dict,signalDict):
        comps = ["ttgg","ttqg","ttag","ttqq","wj","st","dy","mj"]
        ttComps = ["ttgg","ttqg","ttag","ttqq"]
        bgComps = ["wj","st","dy","mj"]

        ttPreEff = [effDict[k] for k in ttComps]
        ttPreFrac = [preFracDict[k] for k in ttComps]
        bg_4jEvents = [signalDict[k] for k in bgComps]
        ttEff4_5 = [eff4_5Dict[k] for k in ttComps]

        

        print zip(ttComps,ttPreEff)
        print zip(ttComps,ttPreFrac)
        print zip(ttComps, ttEff4_5)
        print zip(bgComps,bg_4jEvents)






    def printFractions(self):
        print "ya fractions!"

if __name__=='__main__':
    program(sys.argv)
'''
#Takes specified comps out of the three dicts
ttPreEff = [effDict[k] for k in ttComps]
ttPreFrac = [preFracDict[k] for k in ttComps]

bg_4jEvnts = [signalDict[k] for k in bgComps]

ttEff4_5 = [eff4_5Dict[k] for k in ttComps]
bg_4jEvnts[0] += bg_4jEvnts[-1]    #mj gets absorbed into wj
bgComps.remove("mj")
bg_4jEvnts.remove(bg_4jEvnts[-1])
bgEff4_5 = [eff4_5Dict[k] for k in bgComps]

tt_4j = rdc.Convert(ttPreEff, ttPreFrac,signalDict["tt"],3)

tt_5j = rdc.Convert(tt_4j, ttEff4_5,1,1)
bg_5j = rdc.Convert(bg_4jEvnts, bgEff4_5,1,1)

#Total background and tt events for 5-jets
ttTotal = sum(tt_5j)
bgTotal = sum(bg_5j)

#Relative background signal for 5-jets
backgrdFrac = bgTotal/(ttTotal+bgTotal)

tt = dict([(ttComps[items],tt_5j[items]) for items in range(len(tt_5j))])
bg = dict([(bgComps[k],bg_5j[k]) for k in range(len(bg_5j))])
print bg["wj"]

print "Background components: \n", zip(bgComps,bg_5j)
print "tt components: \n", zip(ttComps,tt_5j)
print "Background fraction: \n",backgrdFrac
'''
