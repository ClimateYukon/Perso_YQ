import urllib2
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

# %matplotlib inline
pd.set_option("max_columns", None)
address = 'http://trackleaders.com/spot/yukonquest15/allpoints.js'
js = urllib2.urlopen(address)
hold = js.readlines()

os.chdir("/workspace/Shared/Users/jschroder/TMP/YQ/YQ_process")

tif = '/workspace/Shared/Users/jschroder/TMP/YQ/dem3338.tif'


project = partial(
    pyproj.transform,
    pyproj.Proj(init='EPSG:4326'),
    pyproj.Proj(init='EPSG:3338'))

dd={}
for k in range(5,142,6) :
	lola = np.array([ i.replace('o.push(', '').replace('a.push(', '').replace(')', '') for i in hold[k].split(';')])[:-3].astype( float )
	lola_split = np.split(lola, len(lola)/2)

	if '15' in address : 
		
		name = hold[k+1].split(':')[4][2:-6]
	else :
		name = hold[k+1].split( ' ' )[7][1:-2]
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

for k,v in dd.iteritems():
	geometry = [transform(project,Point(xy)) for xy in zip(v.long, v.lat)]
	df = GeoDataFrame(v.copy(), geometry=geometry)
	df['altitude'] = rasterstats.point_query(geometry,tif)
	df['id'] = df.index
	df['distance'] = [0] + [(df.geometry[i].distance(df.geometry[i+1])/1000)*0.621371 for i in range(len(df.geometry)-1)]
	df['distance_cumsum'] = df['distance'].cumsum()
	if (df['distance_cumsum'].max() > 1000).any() or (df['distance_cumsum'].max() < 700).any() :
		dd[k]=1
	else :
		dd[k] = df
		df.crs = {'init' :'epsg:3338'}
		df.to_file("YQ15_points_%s.shp" %k.replace(" ","_"))


rm = [k for k,v in dd.items() if  isinstance(v,int)]
for k in rm : del dd[k]

lines = [ LineString([i.coords[0] for i in v.geometry]) for v in dd.itervalues()]
ok = GeoDataFrame(geometry=lines)
ok.to_file("YQ_lines_2015.shp")








# import urllib2
# import re
# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# from geopandas import GeoDataFrame
# from shapely.geometry import Point, LineString
# import glob, os,rasterstats
# from shapely.geometry import LineString
# from shapely.ops import transform
# from functools import partial
# import pyproj

# # %matplotlib inline
# pd.set_option("max_columns", None)
# address = 'http://trackleaders.com/spot/yukonquest16/tracks.js'
# js = urllib2.urlopen(address)
# hold = js.readlines()

# # os.chdir("/workspace/Shared/Users/jschroder/TMP/YQ/YQ_process")

# # tif = '/workspace/Shared/Users/jschroder/TMP/YQ/dem3338.tif'


# project = partial(
#     pyproj.transform,
#     pyproj.Proj(init='EPSG:4326'),
#     pyproj.Proj(init='EPSG:3338'))

# lines = [l for l in  hold if 'lat' in l and 'lng' in l] 
# lines =  [l.split('{')[1].split('}')[0] for l in lines]

# lola = [np.array(i.replace('lat: ','').replace('lng: ','').split(',')).astype(float) for i in lines ]

# df = pd.DataFrame(data=lola,columns = ['lat','long'])
# geometry = [transform(project,Point(xy)) for xy in zip(df.long, df.lat)]
# dfg = GeoDataFrame(df.copy(), geometry=geometry)
# # dfg['altitude'] = rasterstats.point_query(geometry,tif)
# dfg['id'] = df.index
# dfg['distance'] = [0] + [(dfg.geometry[i].distance(dfg.geometry[i+1])/1000)*0.621371 for i in range(len(dfg.geometry)-1)]
# dfg['distance_cumsum'] = dfg['distance'].cumsum()
# dfg.crs = {'init' :'epsg:3338'}
# dfg.to_file("YQ16_track_points.shp" )

# lines = [ LineString([i.coords[0] for i in dfg.geometry]) ]
# ok = GeoDataFrame(geometry=lines)
# ok.to_file("YQ_lines_2016.shp")