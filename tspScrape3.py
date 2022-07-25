#!/usr/bin/env python3

import requests
import csv
import os
import sys
from datetime import datetime, timedelta, date

fundTag = {
    'L Income'  : 'TSPLINCOME',
    'L 2025' : 'TSPL2025',
    'L 2030' : 'TSPL2030',
    'L 2035' : 'TSPL2035',
    'L 2040' : 'TSPL2040',
    'L 2045' : 'TSPL2045',
    'L 2050' : 'TSPL2050',
    'L 2055' : 'TSPL2055',
    'L 2060' : 'TSPL2060',
    'L 2065' : 'TSPL2065',
    'G Fund'     : 'TSPGFUND',
    'F Fund'     : 'TSPFFUND',
    'C Fund'     : 'TSPCFUND',
    'S Fund'     : 'TSPSFUND',
    'I Fund'     : 'TSPIFUND'}

now = date.today().strftime('%Y%m%d')
tspPricesUrl = 'http://www.tsp.gov/data/fund-price-history.csv'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36'}

def writeNewRows(fileObject, rows):
    writer = csv.writer(fileObject)
    writer.writerows(rows)

def getPricesFromPage(pageUrl, startDate, endDate = now, headers=headers):
    #fundStrings = ['{}=1'.format(fund) for fund in fundTag.keys()]
    fundStrings = ['LFunds', 'InvFunds']
    dateStrings = ['startdate={}'.format(startDate),
                   'enddate={}'.format(endDate),
                   'format=CSV', 'download=1']
    restString = '?' +  '&'.join(dateStrings + fundStrings)
    return requests.get(pageUrl+restString, headers=headers)
    #return requests.get(pageUrl, headers=headers)

def convertRowsForQuicken(page):
    reader = csv.reader(page.text.splitlines())
    rows = [row for row in reader if row[0] != '']
    tagRow = rows[0]
    newRows = []

    for row in reversed(rows[1:]): # first row is header
        if row[0] == '':
            continue
        currDate = datetime.strptime(row[0],
                                     '%Y-%m-%d').strftime('%Y%m%d')
        for i in range(1, len(row)):
            tag = tagRow[i].lstrip()
            if tag in fundTag:
                try:
                    price = float(row[i])
                except:
                    continue
                newRows.append([fundTag[tag], price, currDate])
                print('found', [fundTag[tag], price, currDate])
    return newRows

if __name__ == '__main__':
    # set path for csv files, don't just create them in the current directory
    # default to Documents directory if TSPDIR is not set in environment
    filePath = os.getenv('TSPDIR', os.path.expanduser('~/Documents'))

    # one file is just for new prices for faster importing
    latestPricesFile = os.path.join(filePath, 'tspNew.csv')

    # one file is for entire history in case you need to re-import everything
    priceHistoryFile = os.path.join(filePath, 'tspQuicken.csv')

    lastDate = ''
    # Read last line of history file to get most recent prices
    try:
        with open(priceHistoryFile, 'r') as readHist:
            quickenReader = csv.reader(readHist)
            lastDate = [row for row in quickenReader][-1][2]
    # set a default if there's a problem (usually b/c the file doesn't exist)
    except:
        lastDate = '20110425'

    if lastDate == date.today().strftime('%Y%m%d'):
        print('already have prices through', lastDate)
        sys.exit()

    startDate = (datetime.strptime(lastDate, '%Y%m%d') +
                 timedelta(1)).strftime('%Y%m%d')

    print('checking for new prices starting on', startDate)

    page = getPricesFromPage(tspPricesUrl, startDate, now, headers)
    newRows = [row for row in convertRowsForQuicken(page) if row[-1] > lastDate]
    if newRows == []:
        print('no new prices found')
        sys.exit()

    # overwrite the new prices file
    with open(latestPricesFile, 'w', newline='') as writeLatest:
        writeNewRows(writeLatest, newRows)
    # append to the history file
    with open(priceHistoryFile, 'a', newline='') as writeHist:
        writeNewRows(writeHist, newRows)
