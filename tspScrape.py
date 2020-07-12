#!/usr/bin/python

from urllib2 import urlopen
from urllib import urlencode
import csv
import os
from datetime import datetime, timedelta
from string import lstrip

fundTag = {
    'Linc'  : 'TSPLINCOME',
    'L2020' : 'TSPL2020',
    'L2025' : 'TSPL2025',
    'L2030' : 'TSPL2030',
    'L2035' : 'TSPL2035',
    'L2040' : 'TSPL2040',
    'L2045' : 'TSPL2045',
    'L2050' : 'TSPL2050',
    'L2055' : 'TSPL2055',
    'L2060' : 'TSPL2060',
    'L2065' : 'TSPL2065',
    'G'     : 'TSPGFUND',
    'F'     : 'TSPFFUND',
    'C'     : 'TSPCFUND',
    'S'     : 'TSPSFUND',
    'I'     : 'TSPIFUND'}

now = datetime.today().strftime('%Y%m%d')
tspPricesUrl ='https://secure.tsp.gov/components/CORS/getSharePrices.html'

def writeNewRows(fileObject, rows):
    writer = csv.writer(fileObject)
    writer.writerows(newRows)

def getPricesFromPage(pageUrl, startDate, endDate = now):
    fundStrings = ['{}=1'.format(fund) for fund in fundTag.keys()]
    dateStrings = ['startdate={}'.format(startDate),
                   'enddate={}'.format(endDate),
                   'format=CSV', 'download=1']
    restString = '?' +  '&'.join(dateStrings + fundStrings)
    return urlopen(pageUrl+restString)

def convertRowsForQuicken(page):
    reader = csv.reader(page)
    rows = [row for row in reader if len(row) > 0]
    tagRow = rows[0]
    foundNew = False
    newRows = []

    for row in rows[:0:-1]:
        currDate = datetime.strptime(row[0],
                                     '%Y-%m-%d').strftime('%m/%d/%Y')
        for i in range(1, len(row)):
            tag = lstrip(tagRow[i])
            if tag in fundTag:
                try:
                    price = float(row[i])
                except:
                    continue
                newRows.append([fundTag[tag], price, currDate])
                foundNew = True
                print 'found', [fundTag[tag], price, currDate]
    return newRows if foundNew else None

if __name__ == '__main__':
    # set path for csv files, don't just create them in the current directory
    # default to Documents directory if TSPDIR is not set in environment
    # one file is for entire history in case you need to re-import everything
    # one file is just for new prices for faster importing
    filePath = os.getenv('TSPDIR', os.path.expanduser('~/Documents'))
    latestPricesFile = os.path.join(filePath, 'tspNew.csv')
    priceHistoryFile = os.path.join(filePath, 'tspQuicken.csv')

    lastDate = ''
    # Read last line of history file to get most recent prices
    try:
        with open(priceHistoryFile, 'r') as readHist:
            quickenReader = csv.reader(readHist)
            lastDate = [row for row in quickenReader][-1][2]
    # set a default if there's a problem (usually b/c the file doesn't exist)
    except:
        lastDate = '01/01/2010'

    if lastDate == date.today().strftime('%m/%d/%Y'):
        print 'already have prices through', lastDate
        exit(0)

    startDate = (datetime.strptime(lastDate, '%m/%d/%Y') +
                 timedelta(1)).strftime('%Y%m%d')

    print 'checking for new prices starting on', startDate

    page = getPricesFromPage(tspPricesUrl, startDate, now)
    newRows = convertRowsForQuicken(page)
    if newRows is None:
        print 'no new prices found'
        exit(0)

    # overwrite the new prices file
    with open(latestPricesFile, 'w') as writeLatest:
        writeNewRows(writeLatest, newRows)

    with open(priceHistoryFile, 'a') as writeHist:
        writeNewRows(writeHist, newRows)
