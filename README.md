List of companies in the NYSE, and other exchanges.

## Data

Data and documentation are available on [NASDAQ's official webpage](http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs). Data is updated regularly on the FTP site.

The file used in this repository:
* [Other Exchanges Listed Securities](ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt)

Notes:

* Company Name is a parsed field using the Security Name field.
* Test Listings are excluded in the final dataset

### Preparation

You need python plus pandas library tool installed to run the
scripts. You also probably need to be on Linux/Unix or Mac for the shell
scripts to work.


#### all datasets

***Creates all csv files and datapackage.json***

Run python script:

      python scripts/process.py


## License

All data is licensed under ***????***. All code is licensed under the MIT/BSD license.
