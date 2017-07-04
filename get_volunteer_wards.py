import numpy as np
import pandas as pd
import requests
import shapefile
import sys
import os.path
from shapely.geometry import Point, Polygon


def get_latlng(v):
    'Get latitude and longitude from mailing address.'

    if pd.notnull(v['Mailing Street']):
        addr = '{street:s},{city:s},{state:s}'\
            .format(street=v['Mailing Street'],
                    city=v['Mailing City'],
                    state=v['Mailing State/Province'])

        query = geocode_url + '?address={addr:s}&key={key:s}'\
            .format(addr=addr.replace(' ', '+'), key=api_key)

        # Make request to Google Maps API
        r = requests.get(query).json()

        if r['status'] == 'OK':

            lat = r['results'][0]['geometry']['location']['lat']
            lng = r['results'][0]['geometry']['location']['lng']

            print('{:20s}... OK'.format(v['First Name'] + ' ' +
                                        v['Last Name']))
            return (lat, lng)

        else:  # Google query error
            print('{:20s}... QUERY ERROR'.format(v['First Name'] + ' ' +
                                                 v['Last Name']))
            return np.nan

    else:  # No address data
        print '{:20s}... NO ADDRESS'\
            .format(v['First Name'] + ' ' + v['Last Name'])
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
        zip5 = int(v['Mailing Zip/Postal Code'].split('-')[0])

        # Find corresponding zip in zips DataFrame
        if zip5 in zips.index:
            ward_list = []
            for i, w in wards.iterrows():
                if zips.loc[zip5]['poly'].intersects(w['poly']):
                    ward_list.append(w['num'])

            return ','.join(str(wn) for wn in ward_list)

    return np.nan


api_key = 'AIzaSyBkWHGsmS7qOfIXRvgxRJQxQ3NdQ1SIgQA'
geocode_url = 'https://maps.googleapis.com/maps/api/geocode/json'

if len(sys.argv) > 1:
    vols_file = sys.argv[1]
else:
    print('Please specify a filename for the volunteer list in .CSV format.')
    sys.exit(0)

# Import CCL volunteer data
vols_filename = os.path.splitext(vols_file)[0]
vols = pd.read_csv(vols_filename + '.csv')

# Load ward and ZIP boundary shapefiles
sf_wards = shapefile.Reader('wards/wards.shp')
wards = pd.DataFrame({'poly': [Polygon(s.points) for s in sf_wards.shapes()],
                      'num': [int(r[0]) for r in sf_wards.records()]})

sf_zips = shapefile.Reader('zips/zips.shp')
zips = pd.DataFrame({'poly': [Polygon(s.points) for s in sf_zips.shapes()],
                     'zip': [int(r[2]) for r in sf_zips.records()]})
zips.set_index('zip', inplace=True)

# Remove duplicate zip code records
zips = zips[~zips.index.duplicated(keep='first')]

# Get latitude/longitude for each volunteer
print('Geolocating mailing addresses...')
vols['lat_lng'] = vols.apply(get_latlng, axis=1)
print('Done.\n')

# Get ward number for each volunteer
vols['Ward'] = vols.apply(lambda x: get_ward(x, wards), axis=1)

# Get potential wards overlapping the volunteer's zip code
vols['Potential Wards'] = vols.apply(lambda x: get_wards_from_zip(x, wards, zips), axis=1)

# Write CSV file
vols.to_csv(vols_filename + ' with Wards.csv', index=False)
