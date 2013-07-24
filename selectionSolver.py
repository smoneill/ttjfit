import ROOT as r

effFile = "data/sean/expected.txt"

sel = ["hiM","loM","hiY","loY"]
lep = ["el","mu"]

def getDict(selection,lepton,fileName):
    with open("data/%s_%s_%s.txt" %(fileName,selection,lepton), 'r') as f:
        stripped = [line.strip() for line in f.readlines()]    
        translated = [s.translate(None,";:") for s in stripped]
        splitted = [s.split() for s in translated]
        if fileName == "presel":
            start,end = 0,4
        if fileName == "events":
            start,end = 0,1
        return dict([(splitted[k][start],float(splitted[k][end])) for k in range(1,len(splitted))])

def ExtractROOTFile(selection,lepton):
    '''Uses the ROOT files to derive the 4-5 jet efficiencies'''
    f1 = r.TFile.Open("data/control_top_%s_ph_sn_jn_20.root"%(lepton))
    components = ["ttqq","ttqg","ttag","ttgg","wj","st","dy"]
    name = []
    value = []
    for item in components:
        compHist = f1.Get("Moments2Sum_triD_%s/%s"%(selection,item))
        histo2 = f1.Get("TridiscriminantWTopQCD/%s"%(item))
#        dataHist = f1.Get("Moments2Sum_triD_%s/data"%selection)

        compProject = compHist.ProjectionX()
#        dataProject = dataHist.ProjectionX()

#        dataEvents = dataProject.Integral(0,dataProject.GetNbinsX()+1)
        compIntegral = compProject.Integral(0,compProject.GetNbinsX()+1)
        integral2 = histo2.Integral(0,histo2.GetNbinsX()+1)

        efficiency = compIntegral/integral2
        name.append(item)
        value.append(efficiency)
        
#    print dataEvents    
    return dict([(x,y) for x,y in zip(name,value)])

    


for selection in sel:
    for lepton in lep:
        preselEffDict = getDict(selection,lepton,"presel")
        eventsDict = getDict(selection,lepton,"events")
        eff4_5Dict = ExtractROOTFile(selection,lepton)
        print preselEffDict
        print eventsDict
        print eff4_5Dict, "\n"
#        ttjfit(preselEffDict,eventsDict,eff4_5Dict,selection,lepton)
