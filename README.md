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
* **lat** - GPS latitude of yard data is being generated for NASA Ames Research Center used in the provided config.
* **lon** - GPS longitude of yard data is being generated for NASA Ames Research Center used in the provided config.
* **yard** - List of JSON objects noting azimuth/altitude measurements in a 360 degree view from the yard location where targets will be viewed from. I used an app called Dioptra and my phone on a tripod at the location to measure altitude of objects restricting horizon in about 5 degree steps. You should create a new list for the yard yourself ideally sorted, the more accurate the better. 
