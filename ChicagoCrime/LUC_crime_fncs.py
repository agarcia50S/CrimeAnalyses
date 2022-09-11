# import dependencies
import math
import pandas as pd
from pyproj import Transformer
from ast import literal_eval
from random import sample

def otherMerc(Coords):
    Coordinates = literal_eval(Coords)
    lat = Coordinates[0]
    lon = Coordinates[1]
    
    r_major = 6378137.000   # equatorial radius of earth (meters)
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + 
        lat * (math.pi/180.0)/2.0)) * scale
    return (x, y)

# read in CSV file
def sampleDF(csvFilePath, n, csvSampleName=False):

    '''
    Randomly selects n rows from a given csv file and returns a pandas 
    dataframe. It can also create a CSV file of the dataframe if a 
    file path (string type) is assigned to csvSampleName.  

    Arguments:
    csvFilePath -- string value that is the original CSV file path
    n -- integer value that represents the number of rows you want (i.e. 
    size of sample)
    
    Optional keyword arguments:
    csvSampleName -- default is False, but can be take on a string value
    that is a new file path to convert the dataframe into a CSV file
    (e.g. 'DESIRED_FILE_PATH/DesiredFileName.csv')
    '''
    if type(csvFilePath) != str or (type(csvSampleName) != str and csvSampleName != False):
        return 'File path and file name must be strings.'
    if '.csv' not in csvFilePath:
        csvFilePath = csvFilePath + '.csv'
    if csvSampleName != False:
        if '.csv' not in csvSampleName:
            csvSampleName = csvSampleName + '.csv'

    # length of original csv file
    totalRows = len(pd.read_csv(csvFilePath))

    # produces random sample (list type) from range() seq. of size totalRows - n
    skip = sorted(sample(range(1, totalRows), totalRows - n))

    # will skip (total - n) rows, leaving 5000 rows
    mySample = pd.read_csv(csvFilePath, skiprows=skip) 
    mySampleDF = pd.DataFrame(mySample)
    if csvSampleName != False:
        mySampleDF.to_csv(csvSampleName, index=False)
    return mySampleDF

def myDfCleaner(myDF, lower=False, dropna=False):
    '''
    For string type column names of a dataframe, it removes trailing spaces, 
    replaces between-character spaces with '_', and coverts all uppercase 
    letters to lowercase letters if lower=True. 

    All changes are updates to the dataframe, thus the fnc returns None

    Arguments:
    myDF -- pandas DataFrame type; this is your DF
    
    Optional Keyword Arguments:
    lower -- boolean value; if True uppercase letters are converted to lowercase 
    letters, otherwise uppercase letters remain uppercased

    dropna -- boolean value, if True all NaN values in the dataframe are removed, 
    otherwise all NaN values remain 
    '''
    for name in list(myDF.columns):
        if name[0] == ' ':
            myDF.rename(columns={name:name[1:]}, inplace=True) # inplace=True update DF and return None
    for name in list(myDF.columns):
        if '  ' in name:
            myDF.rename(columns={name:name.replace('  ', '_')}, inplace=True)
    for name in list(myDF.columns):
        if ' ' in name:
            myDF.rename(columns={name:name.replace(' ', '_')},inplace=True)
    if lower == True:
        for name in list(myDF.columns):
            myDF.rename(columns={name:name.lower()}, inplace=True)
    if dropna == True:
        myDF.dropna(inplace=True) # removes all rows with NaN values

def toMerc(coordinates, lat=True, lon=True):
    '''
    Converts latitude and longitude coordinates into web 
    Mercator projection coordinates and returns the WMP coordinates
    as tuple (x,y) when lat and lon are both True. If only lat is True then only 
    latitude convertion is returned and if only lon is True then only 
    longitude convertion is returned.

    Arguments:
    latitude -- int or float type that represents the latitude value
    longitude -- int or float type that represent the longitude value

    lat -- boolean type; if True then latitude conversion is 
    returned

    lon -- boolean type; if True then longitude converstion is 
    returned
    '''
    # converts string, '(LAT, LONG)', into tuple, (LAT, LONG)
    myCoords = literal_eval(coordinates)

    latitude = myCoords[0]
    longitude = myCoords[1]
    
    # making instance of Transformer that has "epsg:4326" and "epsg:3857"
    # passed into from_crs() 
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")

    # condition statements allow user to specify whether 
    # LAT and LONG, LAT, or LONG are returned
    if lon == True and lat == True:
        return transformer.transform(latitude, longitude)
    elif lon == True:
        return transformer.transform(latitude, longitude)[0]
    elif lat == True:
        return transformer.transform(latitude, longitude)[1]
    else:
        return

def lucCrimeFinder(myDF, blockCol, horiSt, vertSt):
    '''
    Used to iterate over DF column that contains house numbers and 
    put all of the house numbers that are near LUC into a list
    
    HoriSt -- list of all the streets that 1 mile west of LUC
    vertSt -- list all the streets that are 1 mile South and 
                North of luc
    blockCol -- name of column that contains address
    '''
    crimesNearLoyola = []
    for block in myDF[blockCol]:

            for nStreet in vertSt:
                if nStreet in block:
                    num = int(block.split()[0][1:3])
                    if 56 <= num <= 72:
                        crimesNearLoyola.append(block)

            for wStreet in horiSt:
                if wStreet in block:
                    num2 = int(block.split()[0][1:3])
                    if 'W SHERIDAN RD' in block:
                        if 10 <= num2 <= 19:
                            crimesNearLoyola.append(block)
                    elif num2 <= 19 and block[0] == '0':
                        crimesNearLoyola.append(block)
    return crimesNearLoyola