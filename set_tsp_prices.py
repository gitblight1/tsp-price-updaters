from urllib2 import urlopen
from urllib import urlencode
import csv
from datetime import datetime, timedelta, date
from string import lstrip

fundTag = {'G' : 'TSPGFUND',
           'F' : 'TSPFFUND',
           'C' : 'TSPCFUND',
           'S' : 'TSPSFUND',
           'I' : 'TSPIFUND'}

now = datetime.today()
tspPricesUrl ='https://secure.tsp.gov/components/CORS/getSharePrices.html'

book = moneydance.getCurrentAccountBook()
currencies = book.getCurrencies()

def getPricesFromPage(pageUrl, startDate, endDate = now.strftime('%Y%m%d')):
    fundStrings = ['{}=1'.format(fund) for fund in fundTag.keys()]
    dateStrings = ['startdate={}'.format(startDate),
                'enddate={}'.format(endDate),
                'format=CSV', 'download=1']
    restString = '?' +  '&'.join(dateStrings + fundStrings)
    return urlopen(pageUrl+restString)


def addRowsToMoneydance(page):
    reader = csv.reader(page)
    rows = [row for row in reader if len(row) > 0]
    tagRow = rows[0]
    newRows = 0

    for row in rows[:0:-1]:
        currDate = datetime.strptime(row[0],
                                     '%Y-%m-%d').strftime('%Y%m%d')
        for i in range(1, len(row)):
            tag = lstrip(tagRow[i])
            if tag in fundTag:
                try:
                    price = float(row[i])
                except:
                    continue
                setPriceForSecurity(fundTag[tag], price, int(currDate))
                newRows += 1
                print 'found', [fundTag[tag], price, currDate]

    return newRows

def getLastDate(symbol):
    security = currencies.getCurrencyByTickerSymbol(symbol)
    snap = security.getSnapshotForDate(int(now.strftime('%Y%m%d')))
    if snap is None:
        lastDate = 20100101
    else:
        lastDate = snap.getDateInt()
    return datetime.strptime(str(lastDate), '%Y%m%d')

def setPriceForSecurity(symbol, price, dateint):
    price = 1/price
    security = currencies.getCurrencyByTickerSymbol(symbol)
    if not security:
        print "No security with symbol/name: %s"%(symbol)
        return
    if dateint:
        security.setSnapshotInt(dateint, price).syncItem()
    security.setUserRate(price)
    security.syncItem()
    print "Successfully set price for %s"%(security)

lastDate = now
for symbol in fundTag.values():
    newDate = getLastDate(symbol)
    if newDate < lastDate:
        lastDate = newDate

startDate = (lastDate + timedelta(1)).strftime('%Y%m%d')

page = getPricesFromPage(tspPricesUrl,
                         startDate,
                         now.strftime('%Y%m%d'))
updated = addRowsToMoneydance(page)

print 'Added %d prices'%(updated)
