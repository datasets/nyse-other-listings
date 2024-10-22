''' process.py

    Grab stock listing data from Nasdaq FTP

    - Downloads data from FTP
    - Does some basic cleaning
    - Creates 4 csv files:
        (nasdaq full, nasdaq just symbol/names, all other, nyse only)
    - Creates datapackage.json file w/ schema

    Data Source: ftp://ftp.nasdaqtrader.com/symboldirectory/
    Data Documentation: http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs

    Author: Joe Hand
'''
import pandas as pd
import json
import os

PACKAGE_NAME = 'nyse-other-listings'
PACKAGE_TITLE = 'NYSE and Other Listings'

# NYSE and other exchanges
other_listings = 'ftp://ftp.nasdaqtrader.com/symboldirectory/otherlisted.txt'


def process():
    try:
        # Load the data from the provided FTP link
        other = pd.read_csv(other_listings, sep='|')

        other = _clean_data(other)

        # Create a few other data sets
        nyse = other[other['Exchange'] == 'N'][['ACT Symbol', 'Company Name']]  # NYSE Only

        # (dataframe, filename) datasets we will put in schema & create csv
        datasets = [(nyse, 'nyse-listed'), (other, 'other-listed')]

        # Ensure data directory exists
        os.makedirs('data', exist_ok=True)

        for df, filename in datasets:
            df.to_csv(f'data/{filename}.csv', index=False)

        # Create datapackage.json
        with open("datapackage.json", "w") as outfile:
            json.dump(_create_datapackage(datasets), outfile, indent=4, sort_keys=True)
            
    except Exception as e:
        print(f"Error processing data: {e}")


def _clean_data(df):
    df = df.copy()

    # Remove test listings
    df = df[df['Test Issue'] == 'N']

    # Create New Column with Just Company Name
    df['Company Name'] = df['Security Name'].apply(lambda x: x.split('-')[0])

    # Move 'Company Name' to 2nd Column
    cols = list(df.columns)
    cols.insert(1, cols.pop(-1))

    # Replacing df.ix with df.loc
    df = df.loc[:, cols]  # Using loc for label-based indexing

    return df


def _create_file_schema(df, filename):
    fields = []
    for name, dtype in zip(df.columns, df.dtypes):
        if str(dtype) == 'object' or str(dtype) == 'bool':  # Updated 'boolean' type check
            dtype = 'string'
        else:
            dtype = 'number'

        fields.append({'name': name, 'description': '', 'type': dtype})

    return {
        'name': filename,
        'path': f'data/{filename}.csv',
        'format': 'csv',
        'mediatype': 'text/csv',
        'schema': {'fields': fields}
    }


def _create_datapackage(datasets):
    resources = []
    for df, filename in datasets:
        resources.append(_create_file_schema(df, filename))

    return {
        'name': PACKAGE_NAME,
        'title': PACKAGE_TITLE,
        'license': '',
        'resources': resources,
    }


if __name__ == '__main__':
    process()