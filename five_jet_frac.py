###Converts the preselection fractions into 4 jet fractions then 5 jet fractions
###Author: Sean O'Neill
import ROOT as r
import sys
import numpy as np

class fiveJetEfficiencyFilter(object):
    def __init__(self,rootFile):
        '''Calculates the background fraction as well as the background and tt components'''

        self.bgComps = ["wj","st","dy","mj"]
        self.ttComps = ["ttgg","ttqg","ttag","ttqq"]

        channelList = self.parseArgument(rootFile)

        effDict, preFracDict, eff4_5Dict, signalDict = self.parseData(channelList)

        tt_5jet,bg_5jet = self.calculateFractions(effDict, preFracDict, eff4_5Dict, signalDict)

        backgroundFrac = self.calculateBackground(tt_5jet,bg_5jet)

        

        for item in ["backgroundFrac","tt_5jet","bg_5jet","effDict", "preFracDict", "eff4_5Dict", "signalDict"]:
            setattr(self,item,eval(item))

############################################################################################        
    def parseArgument(self,rootFile):
        '''Makes sure a root file is specified and sets the channel'''

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
        '''Selects what columns to read from each file based on the channel'''

        if ch == "el":
            num = [0,7,2,10,2,2,7]
        else:
            num = [7,14,11,19,1,2,7]
        name = ["loFrac", "hiFrac", "loCerba", "hiCerba", "column", "loExpect", "hiExpect"]
        return dict(zip(name,num))
#return dict([(name[k],num[k]) for k in range(len(num))])

############################################################################################    
    def parseData(self,channelList):
        '''Parses the data from three different files and stores them in four dictionaries'''
        
        fracEffFile = "data/fracs_effs_edit.txt"
        cerbaEffFile = "data/cerba_efficiencies.txt"
        cerbaExpFile = "data/cerba_expect_4j.txt"
        fileList = [fracEffFile,cerbaEffFile,cerbaExpFile]
        files = []
        for item in fileList:
            files.append(self.fileStrip(item))
        
        #Extracts data from the preselection file
        name = files[0][channelList["loFrac"]:channelList["hiFrac"]]
        eff = self.makeDictionary(name,2)
        preFrac = self.makeDictionary(name,4)

        #Extracts data from the 4->5 efficiency file
        name = files[1][channelList["loCerba"]:channelList["hiCerba"]]
        eff4_5 = self.makeDictionary(name,1)
        
        #Extracts data from the preselection signal file 
        name = files[2][channelList["loExpect"]:channelList["hiExpect"]]
        signal = self.makeDictionary(name,channelList["column"])
        
        return eff,preFrac,eff4_5,signal

    def fileStrip(self,fileName):
        '''Strips the files so they are readable'''
        
        with open(fileName) as f:
            stripped = [line.strip() for line in f.readlines()]
            translated = [s.translate(None, ";:") for s in stripped]
            if fileName == "data/cerba_efficiencies.txt":
                return [s.split("\t0") for s in translated]
            else:
                return [s.split() for s in translated]

    def makeDictionary(self,dic,columnNum):
        '''Stuffs dictionaries for storing data'''
        return dict([(dic[k][0],float(dic[k][columnNum]))for k in range(len(dic))])

####################################################################################
    def formatsDictionaries(self):
        '''Formats the dictionaries to make sure the files have been parsed correctly'''
        return "".join(["Preselection Eff ",str(self.effDict),"\n","PreFraction ",str(self.preFracDict),"\n","Eff4_5 ",
                    str(self.eff4_5Dict),"\n ","Signal ",str(self.signalDict),"\n"])

####################################################################################
    def calculateFractions(self,effDict,preFracDict,eff4_5Dict,signalDict):
        '''Calculates the background fraction as well as background and tt components by applying efficiency filters'''
        
        #Unpacks dictionaries depending on their components
        bg_4jet = [signalDict[k] for k in self.bgComps]
        ttPreEff = [effDict[k] for k in self.ttComps]
        ttPreFrac = [preFracDict[k] for k in self.ttComps]
        ttEff4_5 = [eff4_5Dict[k] for k in self.ttComps]
                
        bg_4jet[0] += bg_4jet[-1]    #mj gets absorbed into wj                                    
        self.bgComps.remove("mj")                                                                                                           
        bg_4jet.remove(bg_4jet[-1])                                                                                                   
        
        bgEff4_5 = [eff4_5Dict[k] for k in self.bgComps]         
        
        #Moves the tt components from preselection->4 jet
        tt_4jet = self.efficiencyFilter(ttPreEff,ttPreFrac,signalDict["tt"])
        
        #Moves both the background and tt components from 4->5 jet
        tt_5jet = self.efficiencyFilter(tt_4jet,ttEff4_5)
        bg_5jet = self.efficiencyFilter(bg_4jet,bgEff4_5)
        return tt_5jet, bg_5jet

    def calculateBackground(self,tt_5jet,bg_5jet):
        ttTotal = sum(tt_5jet)
        bgTotal = sum(bg_5jet)
        bckgrndFrac = bgTotal/(ttTotal+bgTotal)
        
        return bckgrndFrac

    def efficiencyFilter(self,vector1,vector2,number=1):
        '''Filters the events depending on the respective efficiencies, to move them from one selection to another'''
        piecewiseProduct = [x*y for x,y in zip(vector1,vector2)]
        dotProduct = np.dot(vector1,vector2)
        normalizedComponents = [s/dotProduct for s in piecewiseProduct]
        event = [s*number for s in normalizedComponents]
        if number != 1:
            return event
        return piecewiseProduct

#####################################################################################
    def formatsFractions(self):
        '''Formats the background fraction, background components, and tt components'''
        return "".join(["Background Fraction: %.6f \n" %self.backgroundFrac,
                    "Background Components: \n \n", str(zip(self.bgComps,self.bg_5jet)),
                    "tt Components: \n \n", str(zip(self.ttComps,self.tt_5jet))])

    def __str__(self):
        return self.formatsDictionaries() + self.formatsFractions()

if __name__=='__main__':
    print fiveJetEfficiencyFilter(sys.argv)
