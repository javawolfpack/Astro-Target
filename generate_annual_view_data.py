from astropy.coordinates import SkyCoord, EarthLocation, AltAz, Angle
import astropy.units as u
from astropy.time import Time
import numpy as np
from astropy.time import TimezoneInfo
import sys
from astropy.coordinates import get_moon, get_sun
import multiprocessing as mp
import json
import sqlite3

conn = sqlite3.connect(':memory:')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='astro';")
jobs = c.fetchall()
if len(jobs) <= 0:
    c.execute("CREATE TABLE astro (id INTEGER PRIMARY KEY AUTOINCREMENT, type varchar(10), data json)")

# Taken from astroplan source: https://astroplan.readthedocs.io/en/latest/_modules/astroplan/moon.html
def moon_phase_angle(moon, sun, ephemeris=None):
    """
    Calculate lunar orbital phase in radians.

    Parameters
    ----------
    moon : `~astropy.coordinates.SkyCoord`
        SkyCoord for moon at a given time
    
    sun : `~astropy.coordinates.SkyCoord`
        SkyCoord for sun at a given time

    ephemeris : str, optional
        Ephemeris to use.  If not given, use the one set with
        `~astropy.coordinates.solar_system_ephemeris` (which is
        set to 'builtin' by default).

    Returns
    -------
    i : float
        Phase angle of the moon [radians]
    """
    # TODO: cache these sun/moon SkyCoord objects

    elongation = sun.separation(moon)
    return np.arctan2(sun.distance*np.sin(elongation),
                      moon.distance - sun.distance*np.cos(elongation))



# Taken from astroplan source: https://astroplan.readthedocs.io/en/latest/_modules/astroplan/moon.html
def moon_illumination(moon, sun, ephemeris=None):
    """
    Calculate fraction of the moon illuminated.

    Parameters
    ----------
    moon : `~astropy.coordinates.SkyCoord`
        SkyCoord for moon at a given time
    
    sun : `~astropy.coordinates.SkyCoord`
        SkyCoord for sun at a given time

    ephemeris : str, optional
        Ephemeris to use.  If not given, use the one set with
        `~astropy.coordinates.solar_system_ephemeris` (which is
        set to 'builtin' by default).

    Returns
    -------
    k : float
        Fraction of moon illuminated
    """
    i = moon_phase_angle(moon, sun, ephemeris=ephemeris)
    k = (1 + np.cos(i))/2.0
    return k.value


def can_see(yard, alt, az):
    # Using list comprehension + keys() + lambda 
    # Closest key in dictionary 
    res = yard.get(az) or yard[ 
        min(yard.keys(), key = lambda key: abs(key-az))] 
    if res <= alt:
        return True
    else: 
        return False

def view_times(name, yard, sunaltazs_next_year, tz, home,dso_data):
    dsocoord = SkyCoord.from_name(name)
    dark = False
    year = None
    month = None
    day = None
    data = None
    
    print(f"Finding view times for {name} over the next year")
    for sun in sunaltazs_next_year:
        if sun.alt < -18*u.deg:
            if not dark:
                dt = sun.obstime.to_datetime(timezone=tz)
                year = dt.year
                month = dt.month
                day = dt.day
                dark = True
                if data == None:
                    data = {}
                    data["name"]=name
                    data["seen"]=[]
                    data["year"] = year
                    data["month"] = month
                    data["day"] = day
            dsoaltaz = dsocoord.transform_to(AltAz(obstime=sun.obstime,location=home))
            dsoaz = Angle(dsoaltaz.az).degree
            dsoalt = Angle(dsoaltaz.alt).degree
            if dsoalt > 0:
                if can_see(yard, dsoalt, dsoaz):
                    seen = {}
                    seen["az"] = dsoaz
                    seen["alt"] = dsoalt
                    seen["time"] = str(sun.obstime.to_datetime(timezone=tz))
                    seen["sun"]="night"
                    data["seen"]+=[seen]
        elif sun.alt < -0*u.deg:
            if not dark:
                dt = sun.obstime.to_datetime(timezone=tz)
                year = dt.year
                month = dt.month
                day = dt.day
                dark = True
                if data == None:
                    data = {}
                    data["name"]=name
                    data["seen"]=[]
                    data["year"] = year
                    data["month"] = month
                    data["day"] = day
            dsoaltaz = dsocoord.transform_to(AltAz(obstime=sun.obstime,location=home))
            dsoaz = Angle(dsoaltaz.az).degree
            dsoalt = Angle(dsoaltaz.alt).degree
            if dsoalt > 0:
                if can_see(yard, dsoalt, dsoaz):
                    seen = {}
                    seen["az"] = dsoaz
                    seen["alt"] = dsoalt
                    seen["time"] = str(sun.obstime.to_datetime(timezone=tz))
                    data["sun"]="twilight"
                    data["seen"]+=[seen]
        else:
            if data != None:
                dso_data+=[data]
            dark = False
            data = None
            continue
    print(f"Finished finding view times for {name}")

def get_moon_data(sun, moon_data, home):
    if sun.alt < -0*u.deg:
        moon = get_moon(sun.obstime).transform_to(AltAz(obstime=sun.obstime, location=home))
        moon_frac = moon_illumination(moon,sun)
        moon_phases={
            "time":str(sun.obstime.to_datetime(timezone=tz)),
            "moonalt": Angle(moon.alt).degree,
            "moonfrac": moon_frac
        }
        moon_data+=[moon_phases]

def quick_view_times(dsocoord, yard, sunaltazs_next_year, home):
    for sun in sunaltazs_next_year:
        dsoaltaz = dsocoord.transform_to(AltAz(obstime=sun.obstime,location=home))
        dsoaz = Angle(dsoaltaz.az).degree
        dsoalt = Angle(dsoaltaz.alt).degree
        if dsoalt > 0:
            if can_see(yard, dsoalt, dsoaz):
                return True
    return False





if __name__ == "__main__":
    print("Opening Config File")
    if len(sys.argv) > 1:
        with open(sys.argv[1]) as f:
            config_data = json.load(f)
    else:
        with open('config.json') as f:
            config_data = json.load(f)
    print("Calculating FOV Details")
    focal = config_data["scope_focal"]*config_data["crop_factor"]
    print(f"Calculated Focal Length {focal} from crop factor")
    # Math from https://www.scantips.com/lights/fieldofviewmath.html
    # FOV angle in degrees for diagonal view based on given sensor
    diagonal = np.sqrt(np.power(config_data["sen_width"],2)+np.power(config_data["sen_height"],2))
    diangle = np.degrees(2*np.arctan((diagonal/2)/focal))
    #arc sec/pixel not sure if it's useful
    as_pixel = (config_data["pixel_size"]/focal)*206.265
    #arc degree/pixel conversion (not needed)
    as_pixel_degree = as_pixel*0.000277778
    #Percent of Diagonal Field of View for minimum target size
    size_min = diangle*(config_data["percent_capture"]/100)
    print("Parsing Stellarium Catalog")
    f = open("stellarium_catalog.txt","r")
    count = 0
    obj_list = []
    for line in f:
        if line.startswith("#"):
            continue
        line = line.split("	")
        if line[16]=="0" and line[17] == "0" and line[18]=="0":
            continue
        if float(line[7])/60 > size_min:
            data = {
                "NGC":int(line[16]),
                "IC":int(line[17]),
                "M":int(line[18]),
                "mag":float(line[3]),
                "absmag":float(line[4]),
                "size":float(line[7])/60
            }
            obj_list+=[data]
            count+=1
    print("Parsing NGC 2000.0 Catalog")
    f = open("VII_118/ngc2000.dat")
    for line in f:
        try: # 34- 38
            size = float(line[33:38])*0.0166667
        except:
            size = 0
        if size > size_min:
            name = line[0:5]
            IC = 0
            NGC = 0
            if "I" in name:
                IC = int(name[1:5])
                name = "IC"+str(IC)            
                res = next((sub for sub in obj_list if sub['IC'] == IC), None)
            else:
                name = "NGC"+name
                NGC = int(line[0:5])
                res = next((sub for sub in obj_list if sub['NGC'] == NGC), None)
            if res == None:
                try:
                    coord = SkyCoord.from_name(name)
                    try:
                        mag = float(line[40:44])
                    except:
                        mag = 99
                    data = {
                        "NGC":NGC,
                        "IC":IC,
                        "M":0,
                        "mag":mag,
                        "absmag":mag,
                        "size":size
                    }
                    obj_list+=[data]
                    count+=1
                except:
                    continue
    percent = config_data["percent_capture"]
    print(f"Found {count} objects {percent}% or larger than the FOV diagonal angle")
    print("Quick DSO visibility check started, may take a few minutes")
    yard = {}    
    for y in config_data["yard"]:
        yard[y["az"]]=y["alt"]

    home = EarthLocation(lat=config_data["lat"]*u.deg, lon=config_data["lon"]*u.deg, height=74.1*u.m)
    utcoffset = -8*u.hour  # Pacific Time
    time = Time.now()  - utcoffset
    tz = TimezoneInfo(utc_offset=utcoffset) # UTC+8

    delta_midnight = np.linspace(0, 1, 4380)*u.year #1 year in 2 hour increments
    times_next_year = time + delta_midnight
    frame_next_year = AltAz(obstime=times_next_year, location=home)
    sunaltazs_next_year = get_sun(times_next_year).transform_to(frame_next_year)

    suntimes = []
    for sun in sunaltazs_next_year:
        if sun.alt < -0*u.deg:
            suntimes+=[sun]

    obj_list_visible = []
    for dso in obj_list:
        name = ""
        succeed = False
        dsocoord = None
        if dso["NGC"]>0:
            try:
                name = "NGC"+str(dso["NGC"])
                dsocoord = SkyCoord.from_name(name)
                succeed = True
            except:
                succeed = False
        if dso["IC"]>0 and not succeed:
            try:
                name = "IC"+str(dso["IC"])
                dsocoord = SkyCoord.from_name(name)
                succeed = True
            except:
                succeed = False
        if dso["M"]>0 and not succeed:
            try:
                name = "M"+str(dso["M"])
                dsocoord = SkyCoord.from_name(name)
                succeed = True
            except:
                succeed = False
        if succeed:
            see = quick_view_times(dsocoord, yard, suntimes, home)
            if see:
                obj_list_visible+=[dso]

    print("Quick DSO visibility check finished")
    count = len(obj_list_visible)
    print(f"{count} objects visible at some point in the year")
    print("Calculating Annual Moon Phase Data - takes some time")
    delta_midnight = np.linspace(0, 1, 104832)*u.year #24 hours in 5 min increments
    times_next_year = time + delta_midnight
    frame_next_year = AltAz(obstime=times_next_year, location=home)
    sunaltazs_next_year = get_sun(times_next_year).transform_to(frame_next_year)
    
    with mp.Manager() as manager:
        moon_data = manager.list()
        pool2 = mp.Pool(processes=config_data["concurrency"])
        for sun in sunaltazs_next_year:
            if sun.alt <= -0*u.deg:
                pool2.apply_async(get_moon_data, args=(sun, moon_data, home))
        pool2.close()
        pool2.join()
        for line in moon_data:
            c.execute("insert into astro(type, data) values (?, ?)",
                ["moon", json.dumps(line)])
            conn.commit()
        dso_data = manager.list()
        print("Finished Calculating Annual Moon Phase Data")
        print("Calculating Annual View Data for Visible Objects - takes at least an hour")
        pool = mp.Pool(processes=config_data["concurrency"])
        first = True
        for dso in obj_list_visible:
            name = ""
            succeed=False
            if dso["NGC"]>0:
                try:
                    name = "NGC"+str(dso["NGC"])
                    dsocoord = SkyCoord.from_name(name)
                    succeed = True
                except:
                    succeed = False
            if dso["IC"]>0 and not succeed:
                try:
                    name = "IC"+str(dso["IC"])
                    dsocoord = SkyCoord.from_name(name)
                    succeed = True
                except:
                    succeed = False
            if dso["M"]>0 and not succeed:
                try:
                    name = "M"+str(dso["M"])
                    dsocoord = SkyCoord.from_name(name)
                    succeed = True
                except:
                    succeed = False
            if succeed:
                pool.apply_async(view_times, args=(name, yard, sunaltazs_next_year, tz, home,dso_data))
        pool.close()
        pool.join()
        for line in dso_data:
            c.execute("insert into astro(type, data) values (?, ?)",
                ["dso", json.dumps(line)])
            conn.commit()
        print("Finished Calculating Annual View Data for Visible Objects")
    
    # Backup a memory database to a file
    backup_db = sqlite3.connect('astro.db')
    conn.backup(backup_db)
    conn.close()
    backup_db.close()