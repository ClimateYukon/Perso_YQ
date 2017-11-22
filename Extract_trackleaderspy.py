from urllib.request import urlopen
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from geopandas import GeoDataFrame
from shapely.geometry import Point, LineString
import glob, os,rasterstats
from shapely.geometry import LineString
from shapely.ops import transform
from functools import partial
import pyproj
for year in range (15,18):
    # %matplotlib inline
    pd.set_option("max_columns", None)
    address = 'http://trackleaders.com/spot/yukonquest{}/allpoints.js'.format(year)
    js = urlopen(address)
    hold = js.readlines()

    os.chdir("/Users/julienschroder/Desktop/YQ")

    tif = '/workspace/Shared/Users/jschroder/TMP/YQ/dem3338.tif'


    project = partial(
        pyproj.transform,
        pyproj.Proj(init='EPSG:4326'),
        pyproj.Proj(init='EPSG:3338'))

    dd={}
    for k in range(5,len(hold),6) :
    	lola = np.array([ i.decode().replace('o.push(', '').replace('a.push(', '').replace(')', '') for i in hold[k].split(b';')])[:-3].astype( float )
    	lola_split = np.split(lola, len(lola)/2)

    	if '15' in address : 
    		
    		name = hold[k+1].split(b':')[4][2:-6]
    	else :
    		name = hold[k+1].split(b' ' )[7][1:-2]
    	df = pd.DataFrame(data=lola_split,columns = ['lat','long'])
    	if len(df) < 1500 : pass
    	else : dd[name] = df
    	# df.to_csv('%s_coordinates.csv'%name.replace(" ","_"))

    # for i in glob.glob('*.csv'):
    # 	v = pd.read_csv(i)
    # 	geometry = [Point(xy) for xy in zip(v.long, v.lat)]
    # 	df = GeoDataFrame(v.copy(), geometry=geometry)
    # 	df['id'] = df.index
    # 	lines = [LineString([g.coords[0] for g in df.geometry])]
    # 	ok = GeoDataFrame(geometry=lines)
    # 	ok.to_file("%s.shp"%i)

    for k,v in dd.items():
    	geometry = [transform(project,Point(xy)) for xy in zip(v.long, v.lat)]
    	df = GeoDataFrame(v.copy(), geometry=geometry)
    	# df['altitude'] = rasterstats.point_query(geometry,tif)
    	df['id'] = df.index
    	df['distance'] = [0] + [(df.geometry[i].distance(df.geometry[i+1])/1000)*0.621371 for i in range(len(df.geometry)-1)]
    	df['distance_cumsum'] = df['distance'].cumsum()
	#careful with that line as we restrain to 950 miles .. could be dangerous
    	if (df['distance_cumsum'].max() > 950).any() or (df['distance_cumsum'].max() < 700).any() :
    		dd[k]=1
    	else :
    		dd[k] = df
    		df.crs = {'init' :'epsg:3338'}
    		df.to_file("YQ15_points_{}.shp".format(k.decode().replace(" ","_"))) 


    rm = [k for k,v in dd.items() if  isinstance(v,int)]
    for k in rm : del dd[k]

    lines = [ LineString([i.coords[0] for i in v.geometry]) for v in dd.values()]
    mushers = [i.decode() for i in dd.keys()]
    ok = GeoDataFrame(geometry=lines)

    ok.loc[:,'musher'] = mushers
    ok.crs = {'init' :'epsg:3338'}
    ok.to_file("YQ_lines_20{}.shp".format(year))
