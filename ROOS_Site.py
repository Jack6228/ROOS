from distutils.util import strtobool
import pandas as pd, numpy as np
import plotly.express as px

from skyfield.api import load, wgs84, EarthSatellite
pd.options.mode.chained_assignment = None
import time
import webbrowser
from itertools import combinations as combs
from datetime import datetime, timedelta, date

date = date.today()
date_list = [date.year, date.month, date.day]
ts = load.timescale()

def GetTLEs():
    # cat = pd.read_csv(r"C:\Users\jackl\Documents\Python\GitFiles\FullSatCat.csv")
    cat = pd.read_csv("ROOS/FullSatCat.csv")

    # Goes through all duplicate rows in a catalog by NORAD_CAT_ID and gets the one with the closest epoch
    all = []
    for i in range(len(cat)):
        all.append([EarthSatellite(cat['TLE_LINE1'][i], cat['TLE_LINE2'][i], cat['OBJECT_NAME'][i], ts),cat['NORAD_CAT_ID'][i],cat['Epoch_Datetime'][i],cat['TLE_LINE1'][i], cat['TLE_LINE2'][i], cat['OBJECT_NAME'][i]])
    all = pd.DataFrame(data=all, columns=["SatelliteObject","NORAD_CAT_ID","Epoch_Datetime","TLE1","TLE2","SatName"])

    return all

# @profile
def ProcessImage(timestamp, catalog, bluffton):
    # Gets events of each satellite for this image
    satellites_in_image = []
    for s in range(len(catalog)):
        alt, az, distance = (catalog['SatelliteObject'][s] - bluffton).at(timestamp).altaz()
        if alt._degrees >= 45:
            satellites_in_image.append([catalog['SatelliteObject'][s].name,catalog['NORAD_CAT_ID'][s], catalog['TLE1'][s], catalog['TLE2'][s]])
    satellites_in_image = pd.DataFrame(satellites_in_image,columns=['Name','NORAD_CAT_ID','TLE1','TLE2'])
    print("{} satellites identified".format(len(satellites_in_image)))

    names = []
    for i in range(len(satellites_in_image)):
        names.append(satellites_in_image['Name'][i])

    satellite_mass = 750 # kg
    debris_mass = 50 # kg
    rb_mass = 5000 # kg
    rbs, debs, sats = 0, 0, 0
    for n in names:
        if "R/B" in n: rbs +=1
        elif " DEB" in n: debs += 1
        else: sats +=1
    # print(rbs,debs,sats)

    obs_ratio = (90**2) / (360**2)
    # print(obs_ratio)
    junk_small = 128E6 # < 1cm          # est. 1 g
    junk_med = 900000 # 1 - 10 cm       # est. 5 g
    junk_big = 34000 # > 10cm           # est. 15 g
    junk_mass = obs_ratio * ( (junk_small*1) + (junk_med*5) + (junk_big*15) ) / 1000
    total_mass = junk_mass + (rbs*rb_mass) + (debs*debris_mass) + (sats*satellite_mass)

    return total_mass

def WriteToHTML(value, file_name):
    with open(file_name) as f:
        contents = f.read()
        identifier_str = "class=\"python-output-here\">"
        index_start = contents.find(identifier_str)
        index_start_corr = index_start + len(identifier_str)
        index_end = contents[index_start:].find("</p2>") + index_start
        old_text = contents[index_start_corr:index_end]
        new_text = contents[:index_start_corr] + value + contents[index_end:]
    with open(file_name, 'w') as f:
        f.write(new_text)

def Main():
    ttt=time.time()
    catalog = GetTLEs()
    print(round(time.time()-ttt,2),"sec")

    ttt=time.time()
    results = []
    lat = np.linspace(-90, 89, 3)
    long = np.linspace(-180, 179, 3)#37)
    coords = []
    for a in lat:
        for o in long:
            coords.append([a, o])
    coords = np.array(coords)
    for i in coords:
        bluffton = wgs84.latlon(*i)
        mass = ProcessImage(ts.now(), catalog, bluffton)
        results.append(mass)
    print(round(time.time()-ttt,2),"sec")

    df = pd.DataFrame(data = np.zeros((180, 360)), columns = np.arange(-180,180))
    print(coords)
    for c in range(len(coords)):
        print(coords[c][0]+90, coords[c][1]+180)
        print(int(coords[c][0]+90), int(coords[c][1]+180))
        df.iat[int(coords[c][0]+90), int(coords[c][1]+180)] = results[c]

    
    df.to_csv("ROOS/Results.csv")

# Main()

df = pd.read_csv("ROOS/Results.csv", index_col=[0])

from scipy.interpolate import interp1d
import re

for i in range(len(df)):
    y = df.iloc[i].to_numpy()
    xnew = np.arange(len(y))

    zero_idx = np.where(y==0)
    xold = np.delete(xnew,zero_idx)
    yold = np.delete(y, zero_idx)

    if len(xold) > 0:
        f = interp1d(xold,yold)
        ynew = f(xnew)
        df.iloc[i] = ynew

for i in range(len(df.iloc[0])):
    y = df.iloc[:, i].to_numpy()
    xnew = np.arange(len(y))

    zero_idx = np.where(y==0)
    xold = np.delete(xnew,zero_idx)
    yold = np.delete(y, zero_idx)

    if len(xold) > 0:
        f = interp1d(xold,yold)
        ynew = f(xnew)
        df.iloc[:, i] = ynew

df.to_html("ROOS/Results.html", header=False, index=False, table_id="tab")

f = open("ROOS/Results.html", "r")
html_txt = f.read()
f.close() 

f = open("ROOS/index.html", "r")
site_txt = f.read()
f.close() 

string_to_find = "<!-- POSITION OF TABLE -->"
inds = [_.start() for _ in re.finditer("<!-- POSITION OF TABLE -->", site_txt)]
inds[0] += len(string_to_find)
output_line = site_txt[:inds[0]] + "\n<table hidden" + html_txt[6:] + "\n" + site_txt[inds[1]:]

with open('ROOS/index.html', 'w') as f:
    f.write(output_line)

df.to_csv("ROOS/Results.csv")