###List of functions for calculating the background and tt events###
###Author: Sean O'Neill###

#Includes: 
#Reading in the data files
#Storing data in dictionaries
#Converting vectors to move from pre-> 4 jet events->5 jet events

####################################################################
#Opens file and reads data
def FileStrip(fileName):
    stripped = lineStrip(fileName)
    translated = trans(stripped)
    return splitter(fileName,translated)
#Strips the lines
def lineStrip(fileName):
    return [line.strip() for line in fileName.readlines()]    
#Translates any necessiary characters
def trans(stripped):
    return [stripped[k].translate(None,";:") for k in range(len(stripped))]  
#Splits the strings by
def splitter(fileName,translated):
    if fileName == "data/cerba_efficiencies.txt":
        return [translated[k].split("\t0") for k in range(len(translated))]
        
    return [translated[k].split() for k in range(len(translated))]

###################################################################
#Stuffs the dictionaries
def Dict(dic,columnNum):
    return dict([(dic[k][0],float(dic[k][columnNum])) for k in range(len(dic))])

###################################################################
#callNum 1 multiplies components
#callNum 2 normalizes product
#callNum 3 scales normed vector
def Convert(vec1,vec2,event,callNum):
    product = prod(vec1,vec2)
    if callNum == 1:
        return product
    normVec = normalize(product)
    if callNum == 2:
        return normVec
    scaled = scale(normVec,event)
    return scaled
#Multiplies vectors component wise 
def prod(vec1,vec2):
    return [x*y for x,y in zip(vec1,vec2)] 
#Normalizes the vector
def normalize(product):
    return [(x*1.0)/sum(product) for x in product]
#Scales the normalized vector
def scale(normVec, event):
    return [x*event for x in normVec]

'''
def __init__(self,fileName):
    stripped = self.lineStrip(fileName)
    translated = self.trans(stripped)
    self.file = self.splitter(fileName,translated)

def lineStrip(self,name):
    return [line.strip() for line in name.readlines()]
        
def trans(self,name):
    return [name[k].translate(None,";:") for k in range(len(name))]
#This needs to be cleaned up some how
def splitter(self,f,name):
    if f == "data/cerba_efficiencies.txt":
        return [name[k].split("\t0") for k in range(len(name))]
    else:
        return [name[k].split() for k in range(len(name))]
#class Dictionary(object):
#    def __init__(self,lists,
'''
