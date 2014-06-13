'''
Created on Jun 9, 2014

@author: kahere
'''

import tkinter
from root.nested.ParamBox import Parametric
import numpy as np
import sys

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
    button.grid(row=7, column=0)
    tkinter.Button(master, text='Cancel', command = cancel).grid(row=7, column=1)
    
    tkinter.mainloop()
    button.invoke()
    master.withdraw()

def reloadHistHU(hist_file, reloadHU=True):
    '''
    if reload is true, recalculate shapefile, otherwise point to existing shapefile
    '''
    if reloadHU:
        return param.loadIBTRACSData(hist_file)
    elif reloadHU == False:
        return r'C:\PF2\QGIS Valmiera\Datasets\Parametric\stormpts_layer.shp'
    
def reloadHistEQ(reloadEQ=True):
    if reloadEQ:
        return param.loadUSGSEQData()
    elif reloadEQ == False:
        return r'C:\PF2\QGIS Valmiera\Datasets\Parametric\eqpts_layer.shp'
    
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

def radioYear():
    
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

if __name__ == '__main__':
    # CSV file with lat/lon points defining box outline
#     box_file = r'C:\Python code\Parametric\src\root\nested\Box_template.csv'
    box_file = r'C:\Python code\Parametric\src\root\nested\EQBox_template.csv'
    
    # Historical dataset, IBTrACS
    huhist_file = r'Y:\XP transfer\US\US GoM\Allstorms.ibtracs_wmo.v03r05.csv'
    eqhist_file = r'C:\Python code\Parametric\src\root\nested\USGSoutput.csv'
    
    param = Parametric()
    
    
    
    # Convert box points to polygon shapefile
    box = param.genParamBox(box_file)
    
    # Produce shapefile of storm tracks
    ibtracsData = reloadHistHU(huhist_file, reloadHU=False) # reload=False: Use current shapefile
    USGSEQData = reloadHistEQ(reloadEQ=False)
    
    # Get subset of points that fall within box
#     intersect = param.intersect(box,ibtracsData)
    intersect = param.intersectEQ(box,USGSEQData)
    
#     # Select highest category that each storm reached within box
#     intersect_max = intersect.groupby('Serial', group_keys=False).apply(lambda x: x.ix[x.Category.idxmax()])
#     intersect_max.index = range(len(intersect_max))
#         
#     # Get user-defined payout structure. Any units or %
#     HUCatPayout()
#     
#     # Set payout level based on storm category, user inputs
#     intersect_max['Payout'] = ''
#     for i in intersect_max.index:
#         intersect_max.Payout[i] = globpayouts[intersect_max.Category[i],0]
#     
#     # Determine length of historical record
#     startYear = radioYear()
#     currentYear = 2013
#     
#     if startYear < 1848:
#         startYear = 1848
#     if startYear > 2013:
#         startYear = 2013
#         
#     yearRange = currentYear - startYear + 1
#     
#     # Clip event set to user-defined year range
#     intersect_max = intersect_max[intersect_max.Year >= startYear]
#     
#     # Calculate AAL, loss cost
#     totalPayout = sum(intersect_max.Payout.values)
#     maxpayout = np.max(globpayouts)
#     aal = totalPayout/yearRange
#     losscost = aal/maxpayout
#     if np.isnan(losscost):
#         losscost=0
#     
#     # Text box with results
#     resultsBox(aal,losscost)
#     