# import dependencies
import math
import pandas as pd
from ast import literal_eval
from random import sample

def gps_to_merc(coords):
    ''' 
    Coverts string of wsg84 (GPS) coordinates into Web Mercator 
    Projection coordinates and returns them as tuple (x,y).

    Arguments:

    coords -- coordinates; string in the form of tuple '(x, y)'
    '''
    Coordinates = literal_eval(coords)
    lat = Coordinates[0]
    lon = Coordinates[1]
    
    r_major = 6378137.000   # equatorial radius of earth (meters)
    x = r_major * math.radians(lon)
    scale = x/lon
    y = 180.0/math.pi * math.log(math.tan(math.pi/4.0 + 
        lat * (math.pi/180.0)/2.0)) * scale
    return (x, y)

# used for testing
def get_sample(csvFilePath, n, csvSampleName=False):
    '''
    Randomly selects n rows from a given csv file and returns a pandas 
    dataframe. It can also creates a CSV file of the dataframe if a 
    file path (string type) is assigned to csvSampleName.  

    Arguments:

    csvFilePath -- string value that is the original CSV file path
    n -- integer value that represents the number of rows you want (i.e. 
         size of sample)
    
    Optional kw Arguments:

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

def cleaner(myDF, lower=False, dropna=False):
    '''
    For string type column names of a dataframe, it removes trailing spaces, 
    replaces between-character spaces with '_', and coverts all uppercase 
    letters to lowercase letters if lower=True. 

    * All changes are updates to the dataframe, thus the fnc returns None * 

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

def find_all_address(myDF, addressCol, horiSt, vertSt):
    '''
    Used to create list of addresses near LUC where crimes occurred at.
    
    Iterates over DF address column, parses address to get house number, 
    and adds address if house number is near LUC
    
    Arguments: 

    horiSt -- list of W/E streets with house numbers <= 19XX
    vertSt -- list of N/S streets with 56XX to 72XX house numbers  
    addressCol -- name of column that contains address
    '''

    crimesNearLoyola = []
    for address in myDF[addressCol]: # iterating over address col

            for nStreet in vertSt: # iterating over N/S streets

                # append address if house num in given range
                if nStreet in address: 
                    num = int(address.split()[0][1:3]) # parse address to house num
                    if 56 <= num <= 72:
                        crimesNearLoyola.append(address)

            for wStreet in horiSt: # iterates over E/W stre] 

                # append address if house num with given range
                if wStreet in address:
                    num2 = int(address.split()[0][1:3]) # parse address to house num
                    if 'W SHERIDAN RD' in address: # bug fix
                        if 10 <= num2 <= 19:
                            crimesNearLoyola.append(address)
                    elif num2 <= 19 and address[0] == '0':
                        crimesNearLoyola.append(address)
    return crimesNearLoyola