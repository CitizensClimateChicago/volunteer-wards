# volunteer-wards

Determine wards from volunteer mailing addresses using Google Geocode API.

## Installation

1. Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html), or your favorite flavor of Python.

2. Open an Anaconda Prompt and create a new Python2 environment

```
conda create --name ccl-wards python=2.7 numpy pandas pyshp shapely
```

3. Activate the new environment

```
conda activate ccl-wards
```

## Usage

1. Convert the volunteers spreadsheet into .CSV format and save it in the same directory as get_volunteer_wards.py. 
2. Delete the rows at the end that say "Chicago Supports\ Copyright ..."
3. Open an Anaconda Prompt in the same directory as the .CSV file and run the script

`python get_volunteer_wards.py "<name of volunteer spreadsheet>.CSV"`

The script will add two new columns and save to a separate spreadsheet:
1. "Ward" - The volunteer's ward determined from their mailing address (if available).
2. "Potential Wards" - A list of wards overlapping the volunteer's zip code.

The Geocoding requests take some time, so be patient for large lists of volunteers!
