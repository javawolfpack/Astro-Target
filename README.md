# Astro-Target
Repo to build tool to process a complex horizon line, astro setup, and determine available targets and when they're available. 

## config.json

The config.json is the default config file used to generate the view data. I hope to tweak this in the future so you can have named configurations and not need to generate some of the data that would be the same for different configurations. Here is an example of the configuration file. 

```json
{
    "sen_pixel_width": 8256,
    "sen_pixel_height": 5504,
    "sen_width": 35.9,
    "sen_height": 23.9,
    "scope_focal": 350,
    "concurrency": 4,
    "pixel_size": 4.35,
    "percent_capture": 15,
    "crop_factor":2,
    "lat":37.42744540096071, 
    "lon":-122.06191613072063,
    "yard": [ 
        {
            "az": 1.0,
            "alt": 17.3
        }
        ...
    ]
}
```

### Config Fields

* **sen_pixel_width** - Camera Resolution Width Pixels
* **sen_pixel_height** - Camera Resolution Height Pixels
* **sen_width** - Camera Sensor Width in mm
* **sen_height** - Camera Sensor Height in mm
* **scope_focal** - Telescope or lens focal length in mm
* **concurrency** - Python concurrency, ideally set this to match the number of CPU cores on your machine.
* **pixel_size** - Size of camera sensor pixel in μm or micrometers
* **percent_capture** - What percentage of the camera diagonal should the DSO fill
* **crop_factor** - What is the crop factor for your camera sensor, used to multiply the focal length
    * For more info on crop factor: [Understanding Crop Factor](https://www.bhphotovideo.com/explora/photography/tips-and-solutions/understanding-crop-factor)
* **lat** - GPS latitude of yard data is being generated for NASA Ames Research Center used in the provided config.
* **lon** - GPS longitude of yard data is being generated for NASA Ames Research Center used in the provided config.
* **yard** - List of JSON objects noting azimuth/altitude measurements in a 360 degree view from the yard location where targets will be viewed from. I used an app called Dioptra and my phone on a tripod at the location to measure altitude of objects restricting horizon in about 5 degree steps. You should create a new list for the yard yourself ideally sorted, the more accurate the better. 


## Catalogs

Two different catalog files are used both are able to be used for non-commercial applications. Details below:

* **NGC 2000.0**
    * Hosted: [https://heasarc.gsfc.nasa.gov/W3Browse/all/ngc2000.html](https://heasarc.gsfc.nasa.gov/W3Browse/all/ngc2000.html)
    * File: ./VII_118/ngc2000.dat
    * Copyright: This catalog is copyrighted by Sky Publishing Corporation, which has kindly deposited the machine-readble version in the data centers for permanent archiving and dissemination to astronomers for scientific research purposes only. The data should not be used for commercial purposes without the explicit permission of Sky Publishing Corporation. Information on how to contact Sky Publishing is available at http://www.shopatsky.com/contacts.
    * Only for use for non-commercial use.

* **Stellarium**
    * Hosted: [https://github.com/Stellarium/stellarium](https://github.com/Stellarium/stellarium)
    * Direct Link: [https://github.com/Stellarium/stellarium/blob/master/nebulae/default/catalog.txt](https://github.com/Stellarium/stellarium/blob/master/nebulae/default/catalog.txt)
    * File: stellarium_catalog.txt
    * GNU General Public License v2.0

## Running Scripts

There are two primary scripts at this point:

* **generate_annual_view_data.py** - leverage *config.json* or a specified alternative config file to generate view data for targets over the next year based on the complex horizon line given and your setup/location. 

* **csv_data.py** - Will give you a numbered list of DSOs that are visible over the next year from the data the *generate_annual_view_data.py* script created. Select the one you wish to get the view data for and it'll generate a CSV file with the nights of the next year, how much time the given target is visible in your horizon, how much time it's above 30 degress, how much time the moon is up that night, and what the maximum fraction the moon is at that night. It's then easy to port this into a spreadsheet app to sort/graph. 

### Step 1 - Get environment setup

The first step is to make sure your [Python](https://www.python.org/) environment it setup correctly. You need to install Python 3.8 or newer, it may work with earlier versions of Python3 but it has been tested with Python 3.8 & 3.9. 

* Create a virtual environment:
```bash
$ python3 -m venv <name of your virtual environment>
# I typically use venv as my virtual environment name so
$ python3 -m venv venv
```
* Enable virtual environment:
```bash
# I'm using the fact mine is named venv going forward
$ source venv/bin/activate
# Once active you should see something like this with your shell
(venv) $
```
* Install Requirements:
```bash
# Install list of python environment requirements 
# from the requirements.txt file
(venv) $ pip install -r requirements.txt
```

### Step 2 - Generate view data for the next year

Make sure you run the *generate_annual_view_data.py* first as otherwise you won't have any data. 

```bash
# Default way to run it
(venv) $ python generate_annual_view_data.py
# Alternatively you can use a config other than config.json
(venv) $ python generate_annual_view_data.py alternative_config.json
```

Now wait a while... have gotten some performance gains so instead of taking days should take hours. It's about 2-3 hours on my highend consumer systems. The process of iterating over a year is CPU bound and Python is inherently slow, so this is something to revisit. 

After this has completed you should have an *astro.db* file, that is a SQLite database. Considered building this in Docker with a MongoDB container but felt this was more portable after discovering you can insert JSON into SQLite. 

### Step 3 - Generate CSV files as you wish

Now you can use the data to generate an annual view file for a given target you can see into a CSV that you can open in Excel/Numbers or copy the contents into a Google Sheet. This is pretty functional for now but may revisit expanding this soon. 

```bash
(venv) $ python csv_data.py
```





