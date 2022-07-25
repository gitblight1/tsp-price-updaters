# tsp-price-updaters
Scripts to automate download of current [TSP](https://www.tsp.gov) fund prices.

## Scripts
* `tspScrape.py` gets prices from a given start date for TSP funds, and creates two csv files for import into Quicken. The first file has all prices since the start date, the second file only contains dates after the last date in the first file (i.e., since the last time the script was run). NOTE: this script has NOT been updated to reflect the June 2022 changes to the TSP site, and may not ever be. Switch to Python 3 already.
* `tspScrape3.py` is the Python 3 version of tspScrape, for those who live in the now. This script HAS been updated to run with the updated TSP site.
* `set_tsp_prices.py` is meant for use with [Moneydance](https://infinitekind.com/moneydance). It assumes you've already created securities for any funds you wish to get prices for.

## Usage
`tspScrape` and `tspScrape3` are meant to be executed directly from the command line. I haven't set up argument parsing, but there is some control over functionality: 

* Set `TSPDIR` as an environment variable to control where the files are executed.
* Edit the `fundTag` variable to control which funds you download (e.g., by commenting out funds you don't want to track)
* edit the `lastDate` variable (currently set to 20100101) to set the default date when you want to begin tracking. Note that if `$TSPDIR/tspQuicken.csv` already exists, lastDate will automatically be set to the latest date in that file.

## Credits
users 'Simbilis' and 'jsprag' created the original versions of these scripts on [this Bogleheads forum thread](https://www.bogleheads.org/forum/viewtopic.php?f=1&t=108388). In fact, @jsprag maintains the original version [here](https://github.com/jsprag/TSP-Scrape).
