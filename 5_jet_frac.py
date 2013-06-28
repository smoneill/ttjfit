###Converts the preselection fractions into 4 jet fractions then 5 jet fractions
###Author: Sean O'Neill
import ROOT as r
import sys
import numpy as np

class program(object):
    def __init__(self,rootFile):
        '''Calculates the background fraction as well as the background and tt components'''

        channelList = self.parseArgument(rootFile)

        effDict, preFracDict, eff4_5Dict, signalDict = self.parseData(channelList)

        backgroundFrac,ttComps,bgComps,tt_5j,bg_5j = self.calculateFractions(effDict, preFracDict, eff4_5Dict, signalDict)

        self.printFractions(backgroundFrac,ttComps,bgComps,tt_5j,bg_5j)
        
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
        return dict([(name[k],num[k]) for k in range(len(num))])

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
            translated = [stripped[k].translate(None, ";:") for k in range(len(stripped))]
            if fileName == "data/cerba_efficiencies.txt":
                return [translated[k].split("\t0") for k in range(len(translated))]
            else:
                return [translated[k].split() for k in range(len(translated))]

    def makeDictionary(self,dic,columnNum):
        '''Stuffs dictionaries for storing data'''
        return dict([(dic[k][0],float(dic[k][columnNum]))for k in range(len(dic))])

####################################################################################
    def calculateFractions(self,effDict,preFracDict,eff4_5Dict,signalDict):
        '''Calculates the background fraction as well as background and tt components by applying efficiency filters'''
        
        comps = ["ttgg","ttqg","ttag","ttqq","wj","st","dy","mj"]
        bgComps = ["wj","st","dy","mj"]
        ttComps = ["ttgg","ttqg","ttag","ttqq"]

        #Unpacks dictionaries depending on their components
        bg_4jet = [signalDict[k] for k in bgComps]
        ttPreEff = [effDict[k] for k in ttComps]
        ttPreFrac = [preFracDict[k] for k in ttComps]
        ttEff4_5 = [eff4_5Dict[k] for k in ttComps]
                
        bg_4jet[0] += bg_4jet[-1]    #mj gets absorbed into wj                                    
        bgComps.remove("mj")                                                                                                                  
        bg_4jet.remove(bg_4jet[-1])                                                                                                   
        
        bgEff4_5 = [eff4_5Dict[k] for k in bgComps]         
        
        #Moves the tt components from preselection->4 jet
        tt_4jet = self.efficiencyFilter(ttPreEff,ttPreFrac,signalDict["tt"])
        
        #Moves both the background and tt components from 4->5 jet
        tt_5jet = self.efficiencyFilter(tt_4jet,ttEff4_5)
        bg_5jet = self.efficiencyFilter(bg_4jet,bgEff4_5)

        ttTotal = sum(tt_5jet)
        bgTotal = sum(bg_5jet)

        #Calculates the background fraction
        bckgrndFrac = bgTotal/(ttTotal+bgTotal)
        
        return bckgrndFrac, ttComps, bgComps, bg_5jet, tt_5jet

    def efficiencyFilter(self,vector1,vector2,number=1):
        '''Filters the events depending on the respective efficiencies, to move them from one selection to another'''
        piecewiseProduct = [x*y for x,y in zip(vector1,vector2)]
        dotProduct = np.dot(vector1,vector2)
        normalizedComponents = [piecewiseProduct[k]/dotProduct for k in range(len(piecewiseProduct))]
        event = [normalizedComponents[k]*number for k in range(len(normalizedComponents))]
        if number != 1:
            return event
        return piecewiseProduct

#####################################################################################
    def printFractions(self,backgroundFrac,ttComps,bgComps,tt_5jet,bg_5jet):
        '''Prints the background fraction, background components, and tt components'''
        print "Background Fraction: %.6f" %backgroundFrac
        print "Background Components: \n", zip(bgComps,bg_5jet)
        print "tt Components: \n", zip(ttComps,tt_5jet)

if __name__=='__main__':
    program(sys.argv)
