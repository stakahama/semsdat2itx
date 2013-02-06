#!/usr/bin/python

############################################################
## Satoshi Takahama (satoshi.takahama@gmail.com)
## March 2010
## sems2itx.py
## Originally distributed as smpsdat2itx.py or smpsdat2itxB.py
## This script converts .dat files from
##     Brechtel SEMS to Igor .itx format
## ---Usage---
## single file:
## $ python sems2itx.py /path/to/data/SCAN_CONC_100225_171945.dat
## or specify path and it will convert all .dat files in directory:
## $ python sems2itx.py /path/to/data/
############################################################

###_ * load libraries

import os
import sys
from calendar import timegm
from time import strptime, gmtime

###_* define functions

###_ . auxiliary
def igortime(t, epoch = timegm(strptime("01/01/1904 00:00:00","%m/%d/%Y %H:%M:%S"))):
    return timegm(strptime(t,'%m/%d/%y %H:%M:%S'))-epoch

def int2date(x):
    return x[2:4] + '/' + x[4:6] + '/' + x[:2]

def list2txt(x,trans=0):
    # 'trans' is an argument indicating whether to
    #     transpose or apply another transformation
    if trans == 1:
        out = map(lambda x: ['']+x, x)
    elif trans == 2:
        out = zip(['']*len(x[0]),*x)        
    else:
        out = zip(['']*len(x),x)
    return '\n'.join(map('\t'.join,out))+'\n'

###_ . read/write
def readbytime(f):
    for line in f:
        line = line.strip()
        if 'Scan Results' in line:
            tm = line.split()[0]
        elif 'Bin Diameter Limits' in line:
            diam = f.next().split()
        elif 'Bin Concentrations' in line:
            nconc = f.next().split()
        elif 'Sample Ave' in line:
            extra = dict(zip(line.split('\t'), f.next().split()))
        elif len(line)==0:
            yield {'time':tm, 'diam':diam, 'conc':nconc, 'extra':extra}

def header(args,name):
    return """WAVES%s %s
BEGIN
""" % (args,name)

def footer(args=None):
    if args:
        return "END\nX " + args + "\n"
    else:
        return "END\n"

def ReadWrite(filename):
    ## get date
    filedate = int2date(os.path.basename(filename).split('_')[2])

    ## read data
    tm = []; diam = []; nconc =[]
    extras = {'Sample Ave':[],
              'Sheath Ave':[],
              'Excess Ave':[],
              'Ave Pressure':[], 
              'Ave Temp':[],
              'Total Scan Conc':[]}
    f = open(filename,'r')
    for elem in readbytime(f):
        tm.append('%s %s' % (filedate,elem['time']))
        diam.append(elem['diam'])
        nconc.append(elem['conc'])
        for dk in extras.keys():
            extras[dk].append(elem['extra'][dk])
    f.close()

    ## convert, calculate
    timeval= map(lambda t: str(igortime(t)),tm)
    dim = (len(nconc),len(nconc[0])) # time x diameter

    ## export
    fout = open(filename.replace('.dat','.itx'),'w')
    fout.write("IGOR\n")
    fout.write(header('/D','t_wave'))
    fout.write(list2txt(timeval))
    fout.write(footer('SetScale/P d 0,0,"dat", t_wave'))
    fout.write('\n')
    fout.write(header('/D','diam'))
    fout.write(list2txt(diam[0]))
    fout.write(footer())
    fout.write('\n')
    fout.write(header('/D/N=(%d,%d)' % dim,'nconc'))
    fout.write(list2txt(nconc,1))
    fout.write(footer())
    for k in extras.keys():
        fout.write(header('/D',k.replace(' ','_').lower()))
        fout.write(list2txt(extras[k]))
        fout.write(footer())
        fout.write('\n')
    fout.close()

###_* apply
    
if __name__=="__main__":

    filename = sys.argv[1]
    if not os.path.isdir(filename):
        ReadWrite(filename)
    else:
        import glob
        datfiles = glob.glob(os.path.join(filename,'SCAN_CONC*.dat'))
        map(ReadWrite,datfiles)

