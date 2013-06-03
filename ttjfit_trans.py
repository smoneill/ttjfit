#! /usr/bin/python

import numpy
from scipy import integrate

#f=raw_input("What is the file name?")
#file_name=open(f,"r")   #Opens the file selected


x2 = lambda x: x**3
low = raw_input("Lower bound")
high = raw_input("Upper bound")
ndata = integrate.quad(x2,low,high)   #Totals the events

print results

#file_name.close()







