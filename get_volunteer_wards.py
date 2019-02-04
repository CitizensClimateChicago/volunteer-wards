#!/usr/bin/env python
from __future__ import print_function
import numpy as np
import sys
import os
import pandas as pd
from urllib import quote
import requests
import shapefile
from shapely.geometry import Point, Polygon


def get_latlng(v):
    'Get latitude and longitude from mailing address.'

    if pd.notnull(v['Mailing Street']):
        addr = '{street:s},{city:s},{state:s}'\
            .format(street=v['Mailing Street'],
                    city=v['Mailing City'],
                    state=v['Mailing State/Province'])\
            .replace(' ', '+')

        # Quote special characters like '#'
        addr = quote(addr, safe='+,')

        query = geocode_url + '?address={addr:s}&key={key:s}'\
            .format(addr=addr.replace(' ', '+'), key=api_key)

        # Make request to Google Maps API
        print('{:25s}... '.format(v['First Name'] + ' ' + v['Last Name']),
              end='')

        r = requests.get(query).json()

        n_tries = 1
        while r['status'] != 'OK' and n_tries < 5:

            n_tries = n_tries + 1

            print(r['status'])
            print('   {:s}'.format(r['error_message']))
            print(' * RETRY {:d}               ... '.format(n_tries), end='')
            r = requests.get(query).json()

        if r['status'] == 'OK':

            lat = r['results'][0]['geometry']['location']['lat']
            lng = r['results'][0]['geometry']['location']['lng']

            print('OK')
            return (lat, lng)

        else:  # Google query error
            print('MAXIMUM RETRIES')
            print('   {:s}'.format(r['status']))
            print('   {:s}'.format(r['error_message']))
            return np.nan

    else:  # No address data
        print('{:25s}... NO ADDRESS'
              .format(v['First Name'] + ' ' + v['Last Name']))
        return np.nan


def get_ward(v, wards):
    'Check which ward a volunteer is in.'

    if pd.notnull(v['lat_lng']):

        p = Point(v['lat_lng'][1], v['lat_lng'][0])

        # Iterate through wards
        for i, w in wards.iterrows():
            if w['poly'].contains(p):
                return w['num']
                break

        return 0.

    return np.nan


def get_wards_from_zip(v, wards, zips):
    'Get list of wards intersecting with zip'

    if pd.notnull(v['Mailing Zip/Postal Code']):
        if type(v['Mailing Zip/Postal Code']) is str:
            zip5 = int(v['Mailing Zip/Postal Code'].split('-')[0])
        else:
            zip5 = int(v['Mailing Zip/Postal Code'])

        # Find corresponding zip in zips DataFrame
        if zip5 in zips.index:
            ward_list = []
            for i, w in wards.iterrows():
                if zips.loc[zip5]['poly'].intersects(w['poly']):
                    ward_list.append(w['num'])

            return ','.join(str(wn) for wn in ward_list)

    return np.nan


api_key = 'AIzaSyCY7rrYoIueSJ0KR9pcP4iP-aGWfyVXMyw'
geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'

# Get filename from command line argument
if len(sys.argv) > 1:
    volunteers_file = os.path.splitext(sys.argv[1])[0]
else:
    print('Please specify a filename for the volunteer list in .CSV format.')
    sys.exit(0)

# Import CCL volunteer data
vols = pd.read_csv(volunteers_file + '.csv')

# Get latitude/longitude for each volunteer
print('Geolocating mailing addresses...')
vols['lat_lng'] = vols.apply(get_latlng, axis=1)
print('Done.\n')

print('FIND VOLUNTEER WARDS     ... ', end='')

# Load ward boundaries
sf = shapefile.Reader('wards/wards.shp')
wards = pd.DataFrame({'poly': [Polygon(s.points) for s in sf.shapes()],
                      'num': [int(r[0]) for r in sf.records()]})

# Get ward number for each volunteer
vols['Ward'] = vols.apply(lambda x: get_ward(x, wards), axis=1)

print('OK')


print('FIND POTENTIAL WARDS     ... ', end='')

# Read ZIP shapefile
sf_zips = shapefile.Reader('zips/zips.shp')
zips = pd.DataFrame({'poly': [Polygon(s.points) for s in sf_zips.shapes()],
                     'zip': [int(r[2]) for r in sf_zips.records()]})
zips.set_index('zip', inplace=True)

# Remove duplicate zip code records
zips = zips[~zips.index.duplicated(keep='first')]

vols['Potential Wards'] = vols.apply(lambda x: get_wards_from_zip(x, wards, zips), axis=1)

print('OK')

# Write CSV file
print('PRINT CSV FILE           ... ', end='')
vols.to_csv(volunteers_file + ' with Wards.csv', index=False)
print('OK')
