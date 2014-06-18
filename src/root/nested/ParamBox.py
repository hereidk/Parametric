'''
Created on Jun 9, 2014

@author: kahere
'''

import pandas
import osgeo.ogr, osgeo.osr
import numpy as np
import os
import geojson
from urllib.request import urlopen
from time import gmtime, strftime
import datetime
import sys


class Parametric(object):
    '''
    Import box outline, convert to shapefile. Import pricing dataset 
    (historical, model, etc.), clip with box. Input years covered by
    dataset, count event frequency, set triggers, determine pricing.
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self.filepath = 'C:\PF2\QGIS Valmiera\Datasets\Parametric\\'
        
    def genParamBox(self, box_file):
        
        box = np.loadtxt(box_file,delimiter=',',skiprows=1)
        if np.any(box[0,:] != box[-1,:]):
            box = np.append(box,np.reshape(box[0,:],(1,np.shape(box)[1])),axis=0)
        box = pandas.DataFrame(box, columns = ['Lon','Lat'])
        
        self.boxlat = box.Lat
        self.boxlon = box.Lon
        
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        
        layername = 'box_layer'
        
        if os.path.exists(self.filepath+layername+'%s' % '.shp'):
            os.remove(self.filepath+layername+'%s' % '.shp')
            os.remove(self.filepath+layername+'%s' % '.dbf')
            os.remove(self.filepath+layername+'%s' % '.prj')
            os.remove(self.filepath+layername+'%s' % '.shx')
        
        driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(self.filepath[:-1])
               
        boxLayer = shapeData.CreateLayer(layername,spatialReference,osgeo.ogr.wkbPolygon)
        layerDefinition = boxLayer.GetLayerDefn()
        
        ring = osgeo.ogr.Geometry(osgeo.ogr.wkbLinearRing)
        
        for i in range(box.shape[0]):
            ring.AddPoint(box.Lon[i],box.Lat[i])
            
        poly = osgeo.ogr.Geometry(osgeo.ogr.wkbPolygon)
        poly.AddGeometry(ring)
        
        featureIndex = 0
        feature = osgeo.ogr.Feature(layerDefinition)
        feature.SetGeometry(poly)
        feature.SetFID(featureIndex)
        
        boxLayer.CreateFeature(feature)
        
        shapeData.Destroy()
        
        return self.filepath+layername+'.shp'
        
    def loadIBTRACSData(self, data_file):
        hudata = pandas.DataFrame()
        hudata = hudata.from_csv(data_file, index_col=False, header=0, sep=',', infer_datetime_format=True)
        
#         latest_update = 2013.
#         record_length = latest_update-1848+1
        
        lat = hudata.Latitude
        lon = hudata.Longitude
        year = hudata.Year.astype('float')
        serial = hudata.Serial_Num
        category = hudata.Category.astype('float')
        
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        
        layername = 'stormpts_layer'
        
        if os.path.exists(self.filepath+layername+'%s' % '.shp'):
            os.remove(self.filepath+layername+'%s' % '.shp')
            os.remove(self.filepath+layername+'%s' % '.dbf')
            os.remove(self.filepath+layername+'%s' % '.prj')
            os.remove(self.filepath+layername+'%s' % '.shx')
        
        driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(self.filepath+layername+'.shp')
               
        ptsLayer = shapeData.CreateLayer(layername,spatialReference,osgeo.ogr.wkbPoint)
        layerDefinition = ptsLayer.GetLayerDefn()
        
        # Add data fields
        serialField = osgeo.ogr.FieldDefn('Serial', osgeo.ogr.OFTString)
        ptsLayer.CreateField(serialField)
        
        catField = osgeo.ogr.FieldDefn('Category', osgeo.ogr.OFTInteger)
        ptsLayer.CreateField(catField)
        
        catField = osgeo.ogr.FieldDefn('Year', osgeo.ogr.OFTInteger)
        ptsLayer.CreateField(catField)
        
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
        
        for i in range(lat.shape[0]):
            pts.AddPoint(lon.iloc[i],lat.iloc[i])
        
            featureIndex = i
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
            feature.SetField('Serial', serial.iloc[i])
            feature.SetField('Category', category.iloc[i])
            feature.SetField('Year', year.iloc[i])
            
            ptsLayer.CreateFeature(feature)
        
        shapeData.Destroy()
        
        return self.filepath+layername+'.shp'
        
    def loadUSGSEQData(self):
        
        f = open('USGSoutput.txt', 'w')
        output_file = 'USGSoutput.csv'
        
        def printResults(data):
            
            
            json = geojson.loads(data)
            
#             if 'title' in json['metadata']:
#                 f.write(json['metadata']['title'])
#                  
            count = json['metadata']['count']
#             f.write('\n' + str(count) + ' events recorded\n')
             
            EQinfo = pandas.DataFrame(columns=('year','mag','lon','lat','depth'), index=range(count), dtype=float)
            for i in range(count):
                epoch_millisecs = json['features'][i]['properties']['time']
                try:
                    format_time = datetime.datetime.fromtimestamp(epoch_millisecs/1000)
                    EQinfo.year[i] = format_time.year
                except OSError:
                    EQinfo.year[i] = json['features'][i]['properties']['code'][:4]              
                EQinfo.mag[i] = json['features'][i]['properties']['mag']
                EQinfo.lon[i] = json['features'][i]['geometry']['coordinates'][0]
                EQinfo.lat[i] = json['features'][i]['geometry']['coordinates'][1]
                EQinfo.depth[i] = json['features'][i]['geometry']['coordinates'][2]
            
            EQinfo.to_csv(output_file, sep=',', columns=('year','mag','lon','lat','depth'), index=False)
            
        def loadData():
            html = 'http://comcat.cr.usgs.gov/fdsnws/event/1/query?starttime=1900-01-01&endtime=%s&minmagnitude=6.0&format=geojson' % strftime('%Y-%m-%d', gmtime())
            
            webURL = urlopen(html)
            print (webURL.getcode())
            
            if webURL.getcode() == 200:
                data = webURL.read().decode('utf-8')
                printResults(data)
            else:
                f.write( 'Received an error from server,cannot retrieve results' + str(webURL.getcode()))
                
        loadData()
        
        data_file = sys.path[0]+'\\'+output_file
        
        eqdata = pandas.DataFrame()
        eqdata = eqdata.from_csv(data_file, index_col=False, header=0, sep=',', infer_datetime_format=True)
        
#         latest_update = 2013.
#         record_length = latest_update-1848+1
        
        lat = eqdata.lat
        lon = eqdata.lon
        year = eqdata.year.astype('float')
#         serial = eqdata.Serial_Num
        magnitude = eqdata.mag.astype('float')
        
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        
        layername = 'eqpts_layer'
        
        if os.path.exists(self.filepath+layername+'%s' % '.shp'):
            os.remove(self.filepath+layername+'%s' % '.shp')
            os.remove(self.filepath+layername+'%s' % '.dbf')
            os.remove(self.filepath+layername+'%s' % '.prj')
            os.remove(self.filepath+layername+'%s' % '.shx')
        
        driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(self.filepath+layername+'.shp')
               
        ptsLayer = shapeData.CreateLayer(layername,spatialReference,osgeo.ogr.wkbPoint)
        layerDefinition = ptsLayer.GetLayerDefn()
        
        # Add data fields
#         serialField = osgeo.ogr.FieldDefn('Serial', osgeo.ogr.OFTString)
#         ptsLayer.CreateField(serialField)
        
        catField = osgeo.ogr.FieldDefn('Mag', osgeo.ogr.OFTReal)
        ptsLayer.CreateField(catField)
        
        catField = osgeo.ogr.FieldDefn('Year', osgeo.ogr.OFTInteger)
        ptsLayer.CreateField(catField)
        
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
        
        for i in range(lat.shape[0]):
            pts.AddPoint(lon.iloc[i],lat.iloc[i])
        
            featureIndex = i
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
#             feature.SetField('Serial', serial.iloc[i])
            feature.SetField('Mag', magnitude.iloc[i])
            feature.SetField('Year', year.iloc[i])
            
            ptsLayer.CreateFeature(feature)
        
        shapeData.Destroy()
        
        return self.filepath+layername+'.shp'
        
        
#         return sys.path[0]+'\\'+output_file
    
    def intersect(self, box, data):
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        
        layername = 'intersect_layer'
        
        if os.path.exists(self.filepath+layername+'%s' % '.shp'):
            os.remove(self.filepath+layername+'%s' % '.shp')
            os.remove(self.filepath+layername+'%s' % '.dbf')
            os.remove(self.filepath+layername+'%s' % '.prj')
            os.remove(self.filepath+layername+'%s' % '.shx')
        
        driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(self.filepath+layername+'.shp')
        intersectshp = shapeData.CreateLayer('intersect', spatialReference, geom_type=osgeo.ogr.wkbPoint)
        
        
        # Add data fields
        serialField = osgeo.ogr.FieldDefn('Serial', osgeo.ogr.OFTString)
        intersectshp.CreateField(serialField)
        
        catField = osgeo.ogr.FieldDefn('Category', osgeo.ogr.OFTInteger)
        intersectshp.CreateField(catField)
        
        catField = osgeo.ogr.FieldDefn('Year', osgeo.ogr.OFTInteger)
        intersectshp.CreateField(catField)
        
        layerDefinition = intersectshp.GetLayerDefn()
        
        DriverName = "ESRI Shapefile"
        driver = osgeo.ogr.GetDriverByName(DriverName)
        boxshp = driver.Open(box)
        boxlyr = boxshp.GetLayer()
        boxfeat = boxlyr.GetFeature(0)
        boxgeom = boxfeat.GetGeometryRef()
        
        datashp = driver.Open(data)
        datalyr = datashp.GetLayer()          
        datalyr.SetSpatialFilter(boxgeom)
        
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
        count = 0
        storm_array = pandas.DataFrame(columns=['Serial','Category','Year'], index = range(datalyr.GetFeatureCount()))
        for feat in datalyr:
            datapt = feat.GetGeometryRef()
            pts.AddPoint(datapt.GetX(), datapt.GetY())
            
            featureIndex = count
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
            feature.SetField('Serial', feat.GetField('Serial'))
            storm_array.Serial[count] = feat.GetField('Serial')
            feature.SetField('Category', feat.GetField('Category'))
            storm_array.Category[count] = feat.GetField('Category')
            feature.SetField('Year', feat.GetField('Year'))
            storm_array.Year[count] = feat.GetField('Year')
#             storm_array.append([feat.GetField('Serial'), feat.GetField('Category')])
            
            intersectshp.CreateFeature(feature)
            count+=1

#         intersectshp.GetField('Serial')
        
        shapeData.Destroy()
        
        return storm_array
    
    
    def intersectEQ(self, box, data):
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        
        layername = 'intersect_layer'
        
        if os.path.exists(self.filepath+layername+'%s' % '.shp'):
            os.remove(self.filepath+layername+'%s' % '.shp')
            os.remove(self.filepath+layername+'%s' % '.dbf')
            os.remove(self.filepath+layername+'%s' % '.prj')
            os.remove(self.filepath+layername+'%s' % '.shx')
        
        driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(self.filepath+layername+'.shp')
        intersectshp = shapeData.CreateLayer('intersect', spatialReference, geom_type=osgeo.ogr.wkbPoint)
        
        
        # Add data fields
#         serialField = osgeo.ogr.FieldDefn('Serial', osgeo.ogr.OFTString)
#         intersectshp.CreateField(serialField)
        
        catField = osgeo.ogr.FieldDefn('Mag', osgeo.ogr.OFTReal)
        intersectshp.CreateField(catField)
        
        catField = osgeo.ogr.FieldDefn('Year', osgeo.ogr.OFTInteger)
        intersectshp.CreateField(catField)
        
        layerDefinition = intersectshp.GetLayerDefn()
        
        DriverName = "ESRI Shapefile"
        driver = osgeo.ogr.GetDriverByName(DriverName)
        boxshp = driver.Open(box)
        boxlyr = boxshp.GetLayer()
        boxfeat = boxlyr.GetFeature(0)
        boxgeom = boxfeat.GetGeometryRef()
        
        datashp = driver.Open(data)
        datalyr = datashp.GetLayer()          
        datalyr.SetSpatialFilter(boxgeom)
        
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)
        count = 0
        eq_array = pandas.DataFrame(columns=['Mag','Year'], index = range(datalyr.GetFeatureCount()))
        for feat in datalyr:
            datapt = feat.GetGeometryRef()
            pts.AddPoint(datapt.GetX(), datapt.GetY())
            
            featureIndex = count
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
#             feature.SetField('Serial', feat.GetField('Serial'))
#             storm_array.Serial[count] = feat.GetField('Serial')
            feature.SetField('Mag', feat.GetField('Mag'))
            eq_array.Mag[count] = feat.GetField('Mag')
            feature.SetField('Year', feat.GetField('Year'))
            eq_array.Year[count] = feat.GetField('Year')
#             storm_array.append([feat.GetField('Serial'), feat.GetField('Category')])
            
            intersectshp.CreateFeature(feature)
            count+=1

#         intersectshp.GetField('Serial')
        
        shapeData.Destroy()
        
        return eq_array