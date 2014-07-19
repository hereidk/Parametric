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
        self.filepath = os.getcwd() + '\GeoData\\'
        
    def initializeSHP(self, layername):
        # Set projection
        spatialReference = osgeo.osr.SpatialReference()
        spatialReference.ImportFromProj4('+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs')
        
        # If the file was previously created, remove the old version
        if os.path.exists(self.filepath+layername+'%s' % '.shp'):
            os.remove(self.filepath+layername+'%s' % '.shp')
            os.remove(self.filepath+layername+'%s' % '.dbf')
            os.remove(self.filepath+layername+'%s' % '.prj')
            os.remove(self.filepath+layername+'%s' % '.shx')
            
        driver = osgeo.ogr.GetDriverByName('ESRI Shapefile')
        shapeData = driver.CreateDataSource(self.filepath[:-1])
        
        return spatialReference, shapeData
        
    
    def genParamBox(self, box_file):
        
        # Upload .csv with lat/lon coordinates of box corners
        box = np.loadtxt(box_file,delimiter=',',skiprows=1)
        
        # Check to make sure box is closed
        if np.any(box[0,:] != box[-1,:]):
            box = np.append(box,np.reshape(box[0,:],(1,np.shape(box)[1])),axis=0)
        
        box = pandas.DataFrame(box, columns = ['Lon','Lat'])
        
        self.boxlat = box.Lat
        self.boxlon = box.Lon
        
        # Build coordinates into shapefile
        
        layername = 'box_layer'
        
        spatialReference, shapeData = self.initializeSHP(layername)
               
        # Define layer for box
        boxLayer = shapeData.CreateLayer(layername,spatialReference,osgeo.ogr.wkbPolygon)
        try:
            layerDefinition = boxLayer.GetLayerDefn()
        except:
            print ('UGH.')
        
        # Create linear ring feature, add points from data file
        ring = osgeo.ogr.Geometry(osgeo.ogr.wkbLinearRing)        
        for i in range(box.shape[0]):
            ring.AddPoint(box.Lon[i],box.Lat[i])
            
        # Convert ring to polygon
        poly = osgeo.ogr.Geometry(osgeo.ogr.wkbPolygon)
        poly.AddGeometry(ring)
        
        # Create feature using geometry
        featureIndex = 0
        feature = osgeo.ogr.Feature(layerDefinition)
        feature.SetGeometry(poly)
        feature.SetFID(featureIndex)
        
        boxLayer.CreateFeature(feature)
        
        shapeData.Destroy()
        
        # Return name of new shapefile
        return self.filepath+layername+'.shp'
        
    def loadIBTRACSData(self, data_file):
        # Load historical hurricane dataset
        
        hudata = pandas.DataFrame()
        hudata = hudata.from_csv(data_file, index_col=False, header=0, sep=',', infer_datetime_format=True)
        
#         latest_update = 2013.
#         record_length = latest_update-1848+1
        
        # Set variables to attributes of data file
        lat = hudata.Latitude
        lon = hudata.Longitude
        year = hudata.Year.astype('float')
        serial = hudata.Serial_Num # Individual storm identifier
        category = hudata.Category.astype('float')
        
        layername = 'stormpts_layer'
        
        spatialReference, shapeData = self.initializeSHP(layername)
               
        # Define layer for storm points
        ptsLayer = shapeData.CreateLayer(layername,spatialReference,osgeo.ogr.wkbPoint)
        layerDefinition = ptsLayer.GetLayerDefn()
        
        # Add data fields
        serialField = osgeo.ogr.FieldDefn('Serial', osgeo.ogr.OFTString)
        ptsLayer.CreateField(serialField)
        
        catField = osgeo.ogr.FieldDefn('Category', osgeo.ogr.OFTInteger)
        ptsLayer.CreateField(catField)
        
        catField = osgeo.ogr.FieldDefn('Year', osgeo.ogr.OFTInteger)
        ptsLayer.CreateField(catField)
        
        # Create point feature, add points from data file
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)        
        for i in range(lat.shape[0]):
            pts.AddPoint(lon.iloc[i],lat.iloc[i])
        
            featureIndex = i
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
            
            # Add storm characteristics to each point
            feature.SetField('Serial', serial.iloc[i])
            feature.SetField('Category', category.iloc[i])
            feature.SetField('Year', year.iloc[i])
            
            ptsLayer.CreateFeature(feature)
        
        shapeData.Destroy()
        
        # Return name of new shapefile
        return self.filepath+layername+'.shp'
        
    def loadUSGSEQData(self):
        
        f = open('USGSoutput.txt', 'w') # Text file for error messages
        output_file = 'USGSoutput.csv'
        
        def printResults(data):
                        
            json = geojson.loads(data)
                              
            count = json['metadata']['count']
#             f.write('\n' + str(count) + ' events recorded\n')
             
            EQinfo = pandas.DataFrame(columns=('year','mag','lon','lat','depth'), index=range(count), dtype=float)
            for i in range(count):
                # Loop through all events, scrape event features from json
                epoch_millisecs = json['features'][i]['properties']['time']
                try:
                    format_time = datetime.datetime.fromtimestamp(epoch_millisecs/1000)
                    EQinfo.year[i] = format_time.year
                except OSError: # If error, pull year from event code
                    EQinfo.year[i] = json['features'][i]['properties']['code'][:4]              
                EQinfo.mag[i] = json['features'][i]['properties']['mag']
                EQinfo.lon[i] = json['features'][i]['geometry']['coordinates'][0]
                EQinfo.lat[i] = json['features'][i]['geometry']['coordinates'][1]
                EQinfo.depth[i] = json['features'][i]['geometry']['coordinates'][2]
            
            # Output USGS data to .csv file
            EQinfo.to_csv(output_file, sep=',', columns=('year','mag','lon','lat','depth'), index=False)
            
        def loadData():
            # Query to scrape events larger than M6.0 since 1900 from USGS feed
            html = 'http://comcat.cr.usgs.gov/fdsnws/event/1/query?starttime=1900-01-01&endtime=%s&minmagnitude=6.0&format=geojson' % strftime('%Y-%m-%d', gmtime())
            
            webURL = urlopen(html)
            print (webURL.getcode())
            
            if webURL.getcode() == 200: # Check if search returns valid results
                data = webURL.read().decode('utf-8')
                printResults(data)
            else: # If no valid results, write error message to file
                f.write( 'Received an error from server,cannot retrieve results' + str(webURL.getcode()))
                
        loadData()
        
        data_file = sys.path[0]+'\\'+output_file
        
        # Load USGS output from .csv
        eqdata = pandas.DataFrame()
        eqdata = eqdata.from_csv(data_file, index_col=False, header=0, sep=',', infer_datetime_format=True)
        
#         latest_update = 2013.
#         record_length = latest_update-1848+1
        
        # Set key event characteristics to variables
        lat = eqdata.lat
        lon = eqdata.lon
        year = eqdata.year.astype('float')
#         serial = eqdata.Serial_Num
        magnitude = eqdata.mag.astype('float')
        
        layername = 'eqpts_layer'
        
        spatialReference, shapeData = self.initializeSHP(layername)
        
        # Define layer for earthquake points
        ptsLayer = shapeData.CreateLayer(layername,spatialReference,osgeo.ogr.wkbPoint)
        layerDefinition = ptsLayer.GetLayerDefn()
        
        # Add data fields
#         serialField = osgeo.ogr.FieldDefn('Serial', osgeo.ogr.OFTString)
#         ptsLayer.CreateField(serialField)
        
        catField = osgeo.ogr.FieldDefn('Mag', osgeo.ogr.OFTReal)
        ptsLayer.CreateField(catField)
        
        catField = osgeo.ogr.FieldDefn('Year', osgeo.ogr.OFTInteger)
        ptsLayer.CreateField(catField)
        
        # Create point feature, add points from data file
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)        
        for i in range(lat.shape[0]):
            pts.AddPoint(lon.iloc[i],lat.iloc[i])
        
            featureIndex = i
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
            
            # Add earthquake characteristics to each point
#             feature.SetField('Serial', serial.iloc[i])
            feature.SetField('Mag', magnitude.iloc[i])
            feature.SetField('Year', year.iloc[i])
            
            ptsLayer.CreateFeature(feature)
        
        shapeData.Destroy()
        
        # Return name of new shapefile
        return self.filepath+layername+'.shp'
    
        
    def intersect(self, box, data, fields): # Fields in dict with data type
        
        layername = 'intersect_layer'
        
        spatialReference, shapeData = self.initializeSHP(layername)
        
        # Define layer for intersect
        intersectshp = shapeData.CreateLayer(layername, spatialReference, geom_type=osgeo.ogr.wkbPoint)
        
        # Add data fields
        for field in fields:
            field_name = field
            function = getattr(osgeo.ogr,fields[field])
            catField = osgeo.ogr.FieldDefn(field_name, function)
            intersectshp.CreateField(catField)
        
        layerDefinition = intersectshp.GetLayerDefn()
        
        DriverName = "ESRI Shapefile"
        driver = osgeo.ogr.GetDriverByName(DriverName)
        
        # Get box from shapefile
        boxshp = driver.Open(box)
        boxlyr = boxshp.GetLayer()
        boxfeat = boxlyr.GetFeature(0)
        boxgeom = boxfeat.GetGeometryRef()
        
        # Get dataset from shapefile
        datashp = driver.Open(data)
        datalyr = datashp.GetLayer()          
        datalyr.SetSpatialFilter(boxgeom)
        
        # Create point feature, add points from data layer
        count = 0
        field_list = list(fields.keys())
        pts = osgeo.ogr.Geometry(osgeo.ogr.wkbPoint)        
        hazard_array = pandas.DataFrame(columns=field_list, index = range(datalyr.GetFeatureCount()))
        for feat in datalyr:
            datapt = feat.GetGeometryRef()
            pts.AddPoint(datapt.GetX(), datapt.GetY())
            
            featureIndex = count
            feature = osgeo.ogr.Feature(layerDefinition)
            feature.SetGeometry(pts)
            feature.SetFID(featureIndex)
            
            # Add hazard characteristics to each point
            for i in field_list:
                feature.SetField(i, feat.GetField(i))
                hazard_array[i][count] = feat.GetField(i)
            
            intersectshp.CreateFeature(feature)
            count+=1

        shapeData.Destroy()
        
        # Return array of storms falling within box
        return hazard_array