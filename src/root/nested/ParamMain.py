'''
Created on Jun 9, 2014

@author: kahere
'''

import tkinter
from ParamBox import Parametric
import numpy as np
import sys
import os
from root2.nested.GUIClasses import GUI

def CatPayout(peril):
    '''
    Get user-defined payout structure. Takes any units.
    AAL calculated in same units
    '''
    master = tkinter.Tk()
    
    # Category labels
    if peril == 'Hurricane':
        labels = ['Storm Category', 'TS', 'Cat 1', 'Cat 2', 'Cat 3', 'Cat 4', 'Cat 5']
    elif peril == 'Earthquake':
        labels = ['EQ Magnitude >=', '6.0', '6.5', '7.0', '7.5', '8.0', '8.5', '9.0', '9.5']
    num_bins = len(labels) - 1
    
    # Storm category user inputs
    for idx, label in enumerate(labels):
        tkinter.Label(master, text=label).grid(row=idx)    
        
    # Construct entry payout grid
    tkinter.Label(master, text='Payout').grid(row=0, column=1)
    e = []
    for idx in range(0,num_bins):
        e.append(tkinter.Entry(master))
        e[idx].insert(0,0)
        e[idx].grid(row=idx+1,column=1)
        if idx == 0: # Set focus on first entry
            e[idx].focus_set()
        
    # OK button, gets user payout structure
    def getPayouts(): 
        payouts = np.zeros((num_bins,1))
        try:
            for i in range(payouts.shape[0]):
                payouts[i] = float(e[i].get())
        except ValueError:
            print('ERROR: Invalid payout-please enter numeric value.')
            sys.exit()
        master.quit()
        global globpayouts
        globpayouts = payouts
    
    # Exit button
    def cancel():
        master.destroy()
        sys.exit()
        
    button = tkinter.Button(master, text='OK', command=getPayouts, padx=10)
    button.grid(row=num_bins+2, column=0)
    tkinter.Button(master, text='Cancel', command = cancel).grid(row=num_bins+2, column=1)
    
    tkinter.mainloop()
    button.invoke()
    master.withdraw()

def reloadHist(param, peril, hist_file, reload=True):
    '''
    If reload is true, recalculate shapefile, otherwise point to existing shapefile
    hist_file is required for hurricane IBTRACS data, otherwise None
    '''
    if reload:
        if peril == 'Hurricane':
            return param.loadIBTRACSData(hist_file)
        elif peril == 'Earthquake':
            return param.loadUSGSEQData()
    elif reload == False:
        if peril == 'Hurricane':
            return os.getcwd() + '\GeoData\stormpts_layer.shp'
        elif peril == 'Earthquake':
            return os.getcwd() + '\GeoData\eqpts_layer.shp'   


def runHazard(hazard, box_file, gui, reload=False):
    param = Parametric()
    
    # Convert box points to polygon shapefile
    box = param.genParamBox(box_file)
    
    if hazard == 'Hurricane':
        hist_file = 'Allstorms.ibtracs_wmo.v03r05.csv'  
        fields = {'Serial':'OFTString', 'Category':'OFTInteger', 'Year':'OFTInteger'} # Field names, data type 
    elif hazard == 'Earthquake':
        hist_file = None
        fields = {'Mag':'OFTReal', 'Year':'OFTInteger'} # Field names, data type
    
    # Produce shapefile of storm tracks
    hazardData = reloadHist(param, hazard, hist_file, reload) # reload=False: Use current shapefile
    
    # Get subset of points that fall within box    
    intersect = param.intersect(box, hazardData, fields)
    
    # Get user-defined payout structure. Any units or %
    CatPayout(hazard)    
    
    if hazard == 'Hurricane':
        # Select highest category that each storm reached within box
        intersect_max = intersect.groupby('Serial', group_keys=False).apply(lambda x: x.ix[x.Category.idxmax()])
        intersect_max.index = range(len(intersect_max))
    
        # Set payout level based on storm category, user inputs
        intersect_max['Payout'] = ''
        for i in intersect_max.index:
            intersect_max.loc[i,'Payout'] = globpayouts[intersect_max.Category[i],0]
         
        # Determine length of historical record
        choices = ['1848: Total record', '1950: Recent historical record', '1970: Satellite era']
        startYear = gui.selectFromList('Select start year for historical data', choices)
        startYear = float(startYear[:4])
        currentYear = 2014.
            
    elif hazard == 'Earthquake':    
        # Set payout level based on category, user inputs
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
        intersect_max = intersect
        
        # Determine length of historical record
        startYear = 1900.
        currentYear = 2015.
         
        if startYear < 1900:
            startYear = 1900.
        if startYear > currentYear:
            startYear = currentYear
         
    return intersect_max, startYear, currentYear
    

if __name__ == '__main__':
    
    box_file = 'EQBox_template.csv'
    gui = GUI()
    
    # Get user input to select hazard to analyze
    choices = ['Hurricane','Earthquake']
    hazard = gui.selectFromList('Select hazard type', choices)
    
    # Get user input on reloading database
    choices = ['Yes','No']
    update = gui.selectFromList('Update historical database?', choices)
    
    if update == 'Yes':
        reload = True
    elif update == 'No':
        reload = False
      
    intersect_max, startYear, currentYear = runHazard(hazard, box_file, gui, reload)
            
    yearRange = currentYear - startYear + 1
     
    # Clip event set to user-defined year range
    intersect_max = intersect_max[intersect_max.Year >= startYear]
     
    # Calculate AAL
    totalPayout = sum(intersect_max.Payout.values)
    maxpayout = np.max(globpayouts)
    aal = totalPayout/yearRange
     
    # Text box with results
    gui.textBox('AAL=%s' % aal)
    