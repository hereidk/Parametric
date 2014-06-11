'''
Created on Jun 9, 2014

@author: kahere
'''

import tkinter
from root.nested.ParamBox import Parametric
import numpy as np
import sys

def HUCatPayout():
    master = tkinter.Tk()
    
    tkinter.Label(master, text='Storm Category').grid(row=0)
    tkinter.Label(master, text='TS').grid(row=1)
    tkinter.Label(master, text='Cat 1').grid(row=2)
    tkinter.Label(master, text='Cat 2').grid(row=3)
    tkinter.Label(master, text='Cat 3').grid(row=4)
    tkinter.Label(master, text='Cat 4').grid(row=5)
    tkinter.Label(master, text='Cat 5').grid(row=6)
    
    tkinter.Label(master, text='Payout').grid(row=0, column=1)
    e0 = tkinter.Entry(master)
    e1 = tkinter.Entry(master)
    e2 = tkinter.Entry(master)
    e3 = tkinter.Entry(master)
    e4 = tkinter.Entry(master)
    e5 = tkinter.Entry(master)
    
    e0.insert(0,0)
    e1.insert(0,0)
    e2.insert(0,0)
    e3.insert(0,0)
    e4.insert(0,0)
    e5.insert(0,0)
    
    e0.grid(row=1, column=1)
    e1.grid(row=2, column=1)
    e2.grid(row=3, column=1)
    e3.grid(row=4, column=1)
    e4.grid(row=5, column=1)
    e5.grid(row=6, column=1)
    
    e0.focus_set()
    
    def getPayouts():
        payouts = np.zeros((6,1), dtype=float)
#         payouts[:] = range(6)
        payouts[0] = float(e0.get())
        payouts[1] = float(e1.get())
        payouts[2] = float(e2.get())
        payouts[3] = float(e3.get())
        payouts[4] = float(e4.get())
        payouts[5] = float(e5.get())
#         print(payouts)
        master.quit()
        global globpayouts
        globpayouts = payouts
        return payouts
    
    def cancel():
        master.destroy()
        sys.exit()
        
    def createArray(p0,p1,p2,p3,p4,p5):
        payouts = np.zeros((6,1), dtype=float)
#         payouts[:] = range(6)
        payouts[0] = p0.get()
        payouts[1] = p1.get()
        payouts[2] = p2.get()
        payouts[3] = p3.get()
        payouts[4] = p4.get()
        payouts[5] = p5.get()
        print(payouts, payouts[5])
        return payouts
    
    button = tkinter.Button(master, text='OK', command=getPayouts, padx=10)
#     button = tkinter.Button(master, text='OK', command=lambda p0=e0,p1=e1,p2=e2,p3=e3,p4=e4,p5=e5: createArray(p0,p1,p2,p3,p4,p5))
    button.grid(row=7, column=0)
    tkinter.Button(master, text='Cancel', command = cancel).grid(row=7, column=1)
    
    
    tkinter.mainloop()
    payouts = button.invoke()
    master.withdraw()
    return payouts

def reloadHist(hist_file,reload=True):
    if reload:
        return param.loadIBTRACSData(hist_file)
    else:
        return r'C:\PF2\QGIS Valmiera\Datasets\Parametric\stormpts_layer.shp'
    

def resultsBox(aal,losscost):
    master = tkinter.Tk()
    
    def cancel():
        master.destroy()
        sys.exit()
    
    tkinter.Label(master, text=('AAL=',aal)).grid(row=0)
    tkinter.Label(master, text=('LossCost=',(losscost*100),'%')).grid(row=1)
    tkinter.Button(master, text='OK', command = cancel).grid(row=2)
    
    tkinter.mainloop()


if __name__ == '__main__':
    box_file = r'C:\Python code\Parametric\src\root\nested\Box_template.csv'
    hist_file = r'Y:\XP transfer\US\US GoM\Allstorms.ibtracs_wmo.v03r05.csv'
    param = Parametric()
    box = param.genParamBox(box_file)
    ibtracsData = reloadHist(hist_file, reload=False)
    intersect = param.intersect(box,ibtracsData)
    
    intersect_max = intersect.groupby('Serial', group_keys=False).apply(lambda x: x.ix[x.Category.idxmax()])
    intersect_max.index = range(len(intersect_max))
        
    HUCatPayout()
    
    intersect_max['Payout'] = ''
    for i in intersect_max.index:
        intersect_max.Payout[i] = globpayouts[intersect_max.Category[i],0]
        

    print(intersect_max)
    
    startYear = 1848
    currentYear = 2013
    yearRange = currentYear - startYear + 1
    
    totalPayout = sum(intersect_max.Payout.values)
    maxpayout = np.max(globpayouts)
    aal = totalPayout/yearRange
    losscost = aal/maxpayout
    
    print('AAL=',aal,', Loss Cost=',losscost*100,'%')
    resultsBox(aal,losscost)
    