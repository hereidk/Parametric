'''
Created on Jun 9, 2014

@author: kahere
'''

import tkinter
from root.nested.ParamBox import Parametric
import numpy as np
import sys
import os

def selectHazard():
    # Drop-down menu to select hazard
    root = tkinter.Tk()
    root.geometry("%dx%d+%d+%d" % (330, 80, 200, 150))
    root.title('Select hazard type')
    
    choices = ['Hurricane','Earthquake']
        
    var = tkinter.StringVar(root)
    var.set(choices[0]) # Initial value
    option = tkinter.OptionMenu(root, var, *choices)
    option.pack(side='left', padx=10, pady=10)
    scrollbar = tkinter.Scrollbar(root)
    scrollbar.pack(side='right', fill='y')
    
    def get_hazard():
        select_hazard = var.get()
        root.quit()
        return select_hazard
    
    button = tkinter.Button(root, text='OK', command=get_hazard)
    button.pack(side='left', padx=20, pady=10)
        
    root.mainloop()
    hazard = button.invoke()
    root.withdraw()
    return hazard

def HUCatPayout():
    '''
    Get user-defined payout structure. Takes any units.
    AAL calculated in same units, loss cost relative to maximum payout
    '''
    master = tkinter.Tk()
    
    # Storm category labels
    tkinter.Label(master, text='Storm Category').grid(row=0)
    tkinter.Label(master, text='TS').grid(row=1)
    tkinter.Label(master, text='Cat 1').grid(row=2)
    tkinter.Label(master, text='Cat 2').grid(row=3)
    tkinter.Label(master, text='Cat 3').grid(row=4)
    tkinter.Label(master, text='Cat 4').grid(row=5)
    tkinter.Label(master, text='Cat 5').grid(row=6)
    
    # Storm category user inputs
    tkinter.Label(master, text='Payout').grid(row=0, column=1)
    e0 = tkinter.Entry(master)
    e1 = tkinter.Entry(master)
    e2 = tkinter.Entry(master)
    e3 = tkinter.Entry(master)
    e4 = tkinter.Entry(master)
    e5 = tkinter.Entry(master)
    
    # Default value = 0
    e0.insert(0,0)
    e1.insert(0,0)
    e2.insert(0,0)
    e3.insert(0,0)
    e4.insert(0,0)
    e5.insert(0,0)
    
    # Set window layout
    e0.grid(row=1, column=1)
    e1.grid(row=2, column=1)
    e2.grid(row=3, column=1)
    e3.grid(row=4, column=1)
    e4.grid(row=5, column=1)
    e5.grid(row=6, column=1)
    
    e0.focus_set()
    
    # OK button, gets user payout structure
    def getPayouts(): 
        payouts = np.zeros((6,1), dtype=float)
        try:
            payouts[0] = float(e0.get())
            payouts[1] = float(e1.get())
            payouts[2] = float(e2.get())
            payouts[3] = float(e3.get())
            payouts[4] = float(e4.get())
            payouts[5] = float(e5.get())
        except ValueError:
            print('ERROR: Invalid payout-please enter numeric value.')
            sys.exit()
        master.quit()
        global globpayouts
        globpayouts = payouts
        return payouts
    
    # Exit button
    def cancel():
        master.destroy()
        sys.exit()
        
    button = tkinter.Button(master, text='OK', command=getPayouts, padx=10)
    button.grid(row=7, column=0)
    tkinter.Button(master, text='Cancel', command = cancel).grid(row=7, column=1)
    
    tkinter.mainloop()
    button.invoke()
    master.withdraw()
    
def EQCatPayout():
    '''
    Get user-defined payout structure. Takes any units.
    AAL calculated in same units, loss cost relative to maximum payout
    '''
    master = tkinter.Tk()
    
    # Storm category labels
    tkinter.Label(master, text='EQ Magnitude >=').grid(row=0)
    tkinter.Label(master, text='6.0').grid(row=1)
    tkinter.Label(master, text='6.5').grid(row=2)
    tkinter.Label(master, text='7.0').grid(row=3)
    tkinter.Label(master, text='7.5').grid(row=4)
    tkinter.Label(master, text='8.0').grid(row=5)
    tkinter.Label(master, text='8.5').grid(row=6)
    tkinter.Label(master, text='9.0').grid(row=7)
    tkinter.Label(master, text='9.5').grid(row=8)
    
    # Storm category user inputs
    tkinter.Label(master, text='Payout').grid(row=0, column=1)
    e0 = tkinter.Entry(master)
    e1 = tkinter.Entry(master)
    e2 = tkinter.Entry(master)
    e3 = tkinter.Entry(master)
    e4 = tkinter.Entry(master)
    e5 = tkinter.Entry(master)
    e6 = tkinter.Entry(master)
    e7 = tkinter.Entry(master)
    
    # Default value = 0
    e0.insert(0,0)
    e1.insert(0,0)
    e2.insert(0,0)
    e3.insert(0,0)
    e4.insert(0,0)
    e5.insert(0,0)
    e6.insert(0,0)
    e7.insert(0,0)
    
    # Set window layout
    e0.grid(row=1, column=1)
    e1.grid(row=2, column=1)
    e2.grid(row=3, column=1)
    e3.grid(row=4, column=1)
    e4.grid(row=5, column=1)
    e5.grid(row=6, column=1)
    e6.grid(row=7, column=1)
    e7.grid(row=8, column=1)
    
    e0.focus_set()
    
    # OK button, gets user payout structure
    def getPayouts(): 
        payouts = np.zeros((8,1), dtype=float)
        try:
            payouts[0] = float(e0.get())
            payouts[1] = float(e1.get())
            payouts[2] = float(e2.get())
            payouts[3] = float(e3.get())
            payouts[4] = float(e4.get())
            payouts[5] = float(e5.get())
            payouts[6] = float(e6.get())
            payouts[7] = float(e7.get())
        except ValueError:
#             master.destroy()
#             
#             tkinter.Label(master, text='Invalid payout-please enter numeric value.').grid(row=1)
#             button = tkinter.Button(master, text='OK', command=cancel)
#             button.grid(row=1)
#             
#             tkinter.mainloop()
            print('ERROR: Invalid payout-please enter numeric value.')
            sys.exit()
        master.quit()
        global globpayouts
        globpayouts = payouts
        return payouts
    
    # Exit button
    def cancel():
        master.destroy()
        sys.exit()
        
    button = tkinter.Button(master, text='OK', command=getPayouts, padx=10)
    button.grid(row=9, column=0)
    tkinter.Button(master, text='Cancel', command = cancel).grid(row=9, column=1)
    
    tkinter.mainloop()
    button.invoke()
    master.withdraw()

def reloadHistHU(param, hist_file, reloadHU=True):
    '''
    If reload is true, recalculate shapefile, otherwise point to existing shapefile
    '''
    if reloadHU:
        return param.loadIBTRACSData(hist_file)
    elif reloadHU == False:
        return os.getcwd() + '\GeoData\stormpts_layer.shp'
    
def reloadHistEQ(param, reloadEQ=True):
    '''
    If reload is true, recalculate shapefile, otherwise point to existing shapefile
    '''
    if reloadEQ:
        return param.loadUSGSEQData()
    elif reloadEQ == False:
        return os.getcwd() + '\GeoData\eqpts_layer.shp'
    
def resultsBox(aal,losscost):
    '''
    Text box with results
    
    '''
    master = tkinter.Tk()
    
    def cancel():
        master.destroy()
        sys.exit()
    
    tkinter.Label(master, text=('AAL=',aal)).grid(row=0)
    tkinter.Label(master, text=('LossCost=',(losscost*100),'%')).grid(row=1)
    tkinter.Button(master, text='OK', command = cancel).grid(row=2)
    
    tkinter.mainloop()

def radioYearHU():
    '''
    Set preferred start of time series-older near major population centers, up to satellite era
    '''
    master = tkinter.Tk()    
    v = tkinter.IntVar()
    v.set(None)
       
    def setYear(v, value):
        v.set(value)

    def ok(v, otherentry):
        try:
            if v.get() == 0:
                v.set(int(otherentry.get()))
        except ValueError:
            print('ERROR: Invalid year-please enter numeric value between 1848 and 2013.')
            sys.exit()
        master.quit()
    
    def cancel():
        master.destroy()
        sys.exit()
    
    total = tkinter.Radiobutton(master, text='1848: Total record', variable=v, value=1848, command=lambda: setYear(v, 1848))
    total.grid(row=0)
    total.deselect()
    
    historical = tkinter.Radiobutton(master, text='1950: Recent historical record', variable=v, value=1950, command=lambda: setYear(v, 1950))
    historical.grid(row=1)
    historical.deselect()
    
    satellite = tkinter.Radiobutton(master, text='1970: Satellite era', variable=v, value=1970, command=lambda: setYear(v, 1970))
    satellite.grid(row=2)
    satellite.deselect()
    
    otherradio = tkinter.Radiobutton(master, text='Other', variable=v, value=0, command=lambda: setYear(v, 0))
    otherradio.grid(row=3)
    otherradio.deselect()
    
    otherentry = tkinter.Entry(master, textvariable=v)
    otherentry.grid(row=4)
    
    tkinter.Button(master, text='OK', command = lambda: ok(v,otherentry)).grid(row=5)
    tkinter.Button(master, text='Cancel', command = cancel).grid(row=6)
    
    tkinter.mainloop()
    master.withdraw()
    
    return v.get()

def runHU():
    box_file = 'Box_template.csv'
    huhist_file = r'Y:\XP transfer\US\US GoM\Allstorms.ibtracs_wmo.v03r05.csv'
    
    param = Parametric()
    
    # Convert box points to polygon shapefile
    box = param.genParamBox(box_file)
    
    # Produce shapefile of storm tracks
    ibtracsData = reloadHistHU(param, huhist_file, reloadHU=False) # reload=False: Use current shapefile
    
    # Get subset of points that fall within box
#     intersect = param.intersect(box,ibtracsData)
    fields = {'Serial':'OFTString', 'Category':'OFTInteger', 'Year':'OFTInteger'} # Field names, data type
    intersect = param.intersect(box, ibtracsData, fields)
    
    # Select highest category that each storm reached within box
    intersect_max = intersect.groupby('Serial', group_keys=False).apply(lambda x: x.ix[x.Category.idxmax()])
    intersect_max.index = range(len(intersect_max))
         
    # Get user-defined payout structure. Any units or %
    HUCatPayout()
    
    # Set payout level based on storm category, user inputs
    intersect_max['Payout'] = ''
    for i in intersect_max.index:
        intersect_max.Payout[i] = globpayouts[intersect_max.Category[i],0]
     
    # Determine length of historical record
    startYear = radioYearHU()
    currentYear = 2013
     
    if startYear < 1848:
        startYear = 1848
    if startYear > currentYear:
        startYear = currentYear
         
    return intersect_max, startYear, currentYear
     
def runEQ():
    '''
    Based on magnitude only - add depth parameter??
    '''
    box_file = 'EQBox_template.csv'    
#     eqhist_file = r'C:\Python code\Parametric\src\root\nested\USGSoutput.csv'
    
    param = Parametric()
    
    # Convert box points to polygon shapefile
    box = param.genParamBox(box_file)
    
    USGSEQData = reloadHistEQ(param, reloadEQ=False)
    
    fields = {'Mag':'OFTReal', 'Year':'OFTInteger'} # Field names, data type
    intersect = param.intersect(box,USGSEQData,fields)
    
    EQCatPayout()
    
    # Set payout level based on storm category, user inputs
    intersect['Payout'] = ''
    for i in intersect.index:
#         intersect.Payout[i] = globeqpayouts[intersect.Mag[i],0]
        if intersect.Mag[i] >= 9.5:
            intersect.Payout[i] = globpayouts[-1][0]
        elif intersect.Mag[i] >= 9.0:
            intersect.Payout[i] = globpayouts[-2][0]
        elif intersect.Mag[i] >= 8.5:
            intersect.Payout[i] = globpayouts[-3][0]
        elif intersect.Mag[i] >= 8.0:
            intersect.Payout[i] = globpayouts[-4][0]
        elif intersect.Mag[i] >= 7.5:
            intersect.Payout[i] = globpayouts[-5][0]
        elif intersect.Mag[i] >= 7.0:
            intersect.Payout[i] = globpayouts[-6][0]
        elif intersect.Mag[i] >= 6.5:
            intersect.Payout[i] = globpayouts[-7][0]
        elif intersect.Mag[i] >= 6.0:
            intersect.Payout[i] = globpayouts[-8][0]
    
    # Determine length of historical record
    startYear = 1900
    currentYear = 2014
     
    if startYear < 1900:
        startYear = 1900
    if startYear > currentYear:
        startYear = currentYear
        
    return intersect, startYear, currentYear
    

if __name__ == '__main__':
    
    # Get user input to select hazard to analyze
    hazard = selectHazard()
    if hazard == 'Hurricane':   
        intersect_max, startYear, currentYear = runHU()
    elif hazard == 'Earthquake': 
        intersect_max, startYear, currentYear = runEQ()
        
    yearRange = currentYear - startYear + 1
     
    # Clip event set to user-defined year range
    intersect_max = intersect_max[intersect_max.Year >= startYear]
     
    # Calculate AAL, loss cost
    totalPayout = sum(intersect_max.Payout.values)
    maxpayout = np.max(globpayouts)
    aal = totalPayout/yearRange
    losscost = aal/maxpayout
    if np.isnan(losscost):
        losscost=0
     
    # Text box with results
    resultsBox(aal,losscost)
    