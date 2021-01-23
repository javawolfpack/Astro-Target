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

* **sen_pixel_width**
* **sen_pixel_height**
* **sen_width**
* **sen_height**
* **scope_focal**
* **concurrency**
* **pixel_size**
* **percent_capture**
* **crop_factor**
* **lat** 
* **lon**
* **yard**
