# volunteer-wards
Determine wards from volunteer mailing addresses using Google Geocode API.

Convert the volunteers spreadsheet into .CSV format and save it in the same directory as get_volunteer_wards.py. Run the script by entering

`python get_volunteer_wards.py 'Volunteer Spreadsheet.CSV'`

The script will add two new columns and save to a separate spreadsheet:
1. "Ward" - The volunteer's ward determined from their mailing address (if available).
2. "Potential Wards" - A list of wards overlapping the volunteer's zip code.

The Geocoding requests take some time, so be patient for large lists of volunteers!
