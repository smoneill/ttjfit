###Attempting to open TCanvas option in PyRoot###
###Sean O'Neill###
import ROOT as r
import sys

# keep a pointer to the original TCanvas constructor
oldinit = r.TCanvas.__init__

# define a new TCanvas class (inheriting from the original one),
# setting the memory ownership in the constructor
class GarbageCollectionResistentCanvas(r.TCanvas):
  def __init__(self, *args):
    oldinit(self,*args)
    r.SetOwnership(self,False)

# replace the old TCanvas class by the new one
r.TCanvas = GarbageCollectionResistentCanvas

c0 = r.TCanvas("c0","ttj fit",600,400)
bg = r.TH1F("bg","bg",50,0,1)
bg.Draw()
