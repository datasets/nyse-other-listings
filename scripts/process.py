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
PACKAGE_DESCRIPTION = (
    'Stock symbols and company names for securities listed on the NYSE and other '
    'U.S. exchanges (NYSE American, NYSE Arca, CBOE/BATS), sourced daily from the '
    'NASDAQ Trader FTP symbol directory.'
)

LICENSES = [
    {
        'name': 'ODC-PDDL-1.0',
        'path': 'https://opendatacommons.org/licenses/pddl/',
        'title': 'Open Data Commons Public Domain Dedication and License'
    }
]

SOURCES = [
    {
        'name': 'NASDAQ Trader Symbol Directory',
        'path': 'http://www.nasdaqtrader.com/trader.aspx?id=symboldirdefs',
        'title': 'NASDAQ Trader Symbol Directory Definitions'
    }
]

RESOURCE_DESCRIPTIONS = {
    'nyse-listed': (
        'Securities listed on the New York Stock Exchange (NYSE), filtered from the '
        'NASDAQ other-listed file where Exchange = N. Contains ACT symbol and company name only.'
    ),
    'other-listed': (
        'All securities listed on exchanges other than NASDAQ: NYSE (N), NYSE American (A), '
        'NYSE Arca (P), and CBOE/BATS (Z). Test issues are excluded. Company Name is derived '
        'from Security Name by taking the text before the first hyphen.'
    ),
}

FIELD_DESCRIPTIONS = {
    'ACT Symbol': 'Ticker symbol used in the Automated Confirmation of Transactions (ACT) system.',
    'Company Name': 'Company name parsed from Security Name by taking the text before the first hyphen.',
    'Security Name': 'Full security name as published in the NASDAQ symbol directory.',
    'Exchange': 'Exchange where the security is listed: N=NYSE, A=NYSE American, P=NYSE Arca, Z=CBOE/BATS.',
    'CQS Symbol': 'Consolidated Quotation System (CQS) symbol used for trade reporting.',
    'ETF': 'Indicates whether the security is an Exchange-Traded Fund (Y=yes, N=no).',
    'Round Lot Size': 'Standard trading unit (round lot) size in number of shares.',
    'Test Issue': 'Indicates whether the listing is a test issue (Y=yes, N=no). Always N in this file as test issues are excluded.',
    'NASDAQ Symbol': 'NASDAQ trading symbol for the security.',
}

# Fields whose Y/N values map to Frictionless boolean type
BOOLEAN_FIELDS = {'ETF', 'Test Issue'}

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
        if name in BOOLEAN_FIELDS:
            field = {
                'name': name,
                'description': FIELD_DESCRIPTIONS.get(name, ''),
                'type': 'boolean',
                'trueValues': ['Y'],
                'falseValues': ['N'],
            }
        elif str(dtype) == 'object' or str(dtype) == 'bool':
            field = {
                'name': name,
                'description': FIELD_DESCRIPTIONS.get(name, ''),
                'type': 'string',
            }
        else:
            field = {
                'name': name,
                'description': FIELD_DESCRIPTIONS.get(name, ''),
                'type': 'number',
            }
        fields.append(field)

    return {
        'name': filename,
        'description': RESOURCE_DESCRIPTIONS.get(filename, ''),
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
        'description': PACKAGE_DESCRIPTION,
        'licenses': LICENSES,
        'sources': SOURCES,
        'resources': resources,
    }


if __name__ == '__main__':
    process()
