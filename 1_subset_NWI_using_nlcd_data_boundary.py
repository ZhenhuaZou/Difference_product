#!/usr/bin/env python3

print('start...')
#import fiona
import rasterio as rio
from osgeo import ogr
import geopandas as gpd
import os
import glob,time
from shapely.geometry import Polygon
import numpy

time0=time.time()

#clip function
# define clip functions
def clip_points(shp, clip_obj):
    '''
    Docs Here
    '''

    poly = clip_obj.geometry.unary_union
    return(shp[shp.geometry.intersects(poly)])

# Create function to clip line and polygon data using geopandas
def clip_line_poly(shp, clip_obj):

    # Create a single polygon object for clipping
    poly = clip_obj.geometry.unary_union
    
    clipped = shp.copy()
    #print('clipped before: ', clipped)
    
    clipped['geometry'] = shp.intersection(poly)
    #print('clipped after: ', clipped)

    # Return the clipped layer with no null geometry values
    return(clipped[clipped.geometry.notnull()])

def clip_shp(shp, clip_obj):
    '''
    '''
    if shp["geometry"].iloc[0].type == "Point":
        return(clip_points(shp, clip_obj))
    else:
        return(clip_line_poly(shp, clip_obj))

#### below is the function to subset NWI using the boundary of ccap data
def process(nlcd_fn,nwi_fn,nwi_out_fn):
    
    nlcd_conus_ds = rio.open(nlcd_fn)
    bbox = nlcd_conus_ds.bounds
    left = bbox.left
    bottom = bbox.bottom
    right = bbox.right
    top = bbox.top
    bbox2 = (left-1000, bottom-1000, right+1000, top+1000)

    time2 = time.time()
    gdb_nwi = gpd.read_file(nwi_fn, layer = 4, bbox=bbox2)


    try:
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if gdb_nwi.empty:
            print('this region has no nwi records: ')
        else:
            if os.path.exists(nwi_out_fn):
                driver.DeleteDataSource(nwi_out_fn)

            gdb_nwi.to_file(nwi_out_fn)
        
        time3 = time.time()
        print('****time takes to load the nwi conus dataset: '+ str((time3-time2)/60.0)) 
    except Exception as oops:
        print('\nProblem: ')
        print(oops)


### apply the function
nwi_fn = 'CONUS_wetlands.gdb' ##### 7/20,, ### 8/30

nwi_out_fn = 'NWI_cut_by_nlcd_boundary.shp'
    
nlcd_fn = 'nlcd.img'
result = process(nlcd_fn,nwi_fn,nwi_out_fn)
    

time1=time.time()
print('****time takes to finish: '+ str((time1-time0)/60.0)+' minutes') 