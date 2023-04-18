#!/usr/bin/env python3
#import matplotlib.pyplot as plt
print('start....')
import geopandas as gpd
import pandas as pd
import numpy as np
from osgeo import ogr
import rasterio
import time
from rasterio import features
import os
## Learn
time0=time.time()

### below is the function to convert NWI polygons into raster file with the same boundary of ccap data
def converCodeAndRasterize(nwi_fn,rst_fn,out_fn):
    time01 = time.time()
        
    if os.path.exists(nwi_fn):
        try:
            ################ below is for empty
            df100All = gpd.read_file(nwi_fn)

            if df100All.empty:
                print('this  is empty:  ')
                time1=time.time()
                # read in the nlcd file
                rst = rasterio.open(rst_fn)
                Arr = rst.read(1)
                out_arr = Arr *0 # this is the out band
                meta = rst.meta.copy()
                meta.update(compress='lzw',dtype='uint8', nodata=255)            
                with rasterio.open(out_fn, 'w+', **meta) as out:
                    out.write_band(1, out_arr)

                time2=time.time()
               
            ###################### below is for not empty
            
            else:
                
                df100All['ATTRIBUTE'] = df100All['ATTRIBUTE'].replace(['None','Null'],[np.nan,np.nan])

                df100All = df100All.dropna(subset=['ATTRIBUTE'])

                df100All['LEN'] = df100All.apply(lambda row: len(row.ATTRIBUTE),axis=1)

                ################################################################################################
                df100 = df100All[df100All.LEN>3]

                df100['WaterR'] = df100.apply(lambda row: row.ATTRIBUTE.replace('b','').replace('d','').replace('f','').replace('m','').replace('h','').replace('r','').replace('s','').replace('x','').replace('1','').replace('2','').replace('3','').replace('4','').replace('5','').replace('6','').replace('0','').replace('a','').replace('t','').replace('i','').replace('g','').replace('n','')[-1],axis=1)

                               
                df100['Sys1'] = df100.apply(lambda row: row.ATTRIBUTE[0],axis=1)
                df100['Sys2'] = df100.apply(lambda row: row.ATTRIBUTE[0:2],axis=1)
                df100['Sys3'] = df100.apply(lambda row: row.ATTRIBUTE[0:3],axis=1)
                df100['Sys4'] = df100.apply(lambda row: row.ATTRIBUTE[0:4],axis=1)

                

                df100['Class'] = 1 # wetland that should not be used for water gain analysis
                df100.loc[df100['Sys1']=='M','Class'] = 2
                df100.loc[df100['Sys2']=='E1','Class'] = 3
                df100.loc[df100['Sys2']=='L1','Class'] = 4
                df100.loc[df100['Sys1']=='R','Class'] = 5
                
                # class for vegetated wetland 
                df100['WaterRForWaterGain'] = 0
                df100.loc[((df100['WaterR']=='A')|(df100['WaterR']=='B')|(df100['WaterR']=='C')|(df100['WaterR']=='D')|(df100['WaterR']=='J')|(df100['WaterR']=='N')|(df100['WaterR']=='P')|(df100['WaterR']=='R')|(df100['WaterR']=='S')),'WaterRForWaterGain'] = 1
                df100['VegTForWaterGain'] = 0
                df100.loc[((df100['Sys3']=='PEM')|(df100['Sys3']=='PSS')|(df100['Sys3']=='PFO')|(df100['Sys4']=='E2EM')|(df100['Sys4']=='E2SS')|(df100['Sys4']=='E2FO')),'VegTForWaterGain'] = 1

                df100.loc[((df100['WaterRForWaterGain']==1)&(df100['VegTForWaterGain']==1)),'Class'] = 6 # wetland that should be used for wate gain analysis
                                
                ###################################################################################################################

                df100Other = df100All[df100All.LEN<=3]
                if len(df100Other.index)>0:
                    df100Other['WaterR'] = ''
                    df100Other['Sys1'] = df100Other.apply(lambda row: row.ATTRIBUTE[0],axis=1)
                    df100Other['Sys2'] = df100Other.apply(lambda row: row.ATTRIBUTE[0:2],axis=1)
                    df100Other['Sys3'] = df100Other.apply(lambda row: row.ATTRIBUTE[0:3],axis=1)
                    df100Other['Sys4'] = df100Other.apply(lambda row: row.ATTRIBUTE[0:4],axis=1)
                    df100Other['Class'] = 1
                    df100Other.loc[df100Other['Sys1']=='M','Class'] = 2
                    df100Other.loc[df100Other['Sys2']=='E1','Class'] = 3
                    df100Other.loc[df100Other['Sys2']=='L1','Class'] = 4
                    df100Other.loc[df100Other['Sys1']=='R','Class'] = 5
                    df100Other['WaterRForWaterGain'] = 0
                    df100Other['VegTForWaterGain'] = 0
                    df100Other.loc[((df100Other['Sys3']=='PEM')|(df100Other['Sys3']=='PSS')|(df100Other['Sys3']=='PFO')|(df100Other['Sys2']=='Pf')),'VegTForWaterGain'] = 1
                    df100Other.loc[(df100Other['VegTForWaterGain']==1),'Class'] = 6
                    df100AllNew = pd.concat([df100,df100Other]).reset_index(drop=True)
                else:
                    df100AllNew = df100

               

                time1=time.time()
      
                rst = rasterio.open(rst_fn)
                meta = rst.meta.copy()
                meta.update(compress='lzw',dtype='uint8', nodata=255)

            

            
                with rasterio.open(out_fn, 'w+', **meta) as out:
                    out_arr = out.read(1)
                    out_arr.fill(0)

                    # this is where we create a generator of geom, value pairs to use in rasterizing
                    shapes = ((geom,value) for geom, value in zip(df100AllNew.geometry, df100AllNew.Class))

                    burned = features.rasterize(shapes=shapes, out=out_arr, transform=out.transform)
                    out.write_band(1, burned)

                time2=time.time()
                print('time to rasterize: ', (time2-time1)/60.0)
            
        except Exception as oops:
            print('\nCan not be open, Problem: ')
            print(oops)
    # below is for the ones with no nwi records
    else:
        print('this do not exist: ')
        time1=time.time()
        # read in the nlcd file
        rst = rasterio.open(rst_fn)
        Arr = rst.read(1)
        out_arr = Arr *0 # this is the out band, assume all regions are highland
        meta = rst.meta.copy()
        meta.update(compress='lzw',dtype='uint8', nodata=255)

       

    
        with rasterio.open(out_fn, 'w+', **meta) as out:

            out.write_band(1, out_arr)

        time2=time.time()
        


#### apply the function
nwi_fn = 'NWI_cut_by_nlcd_boundary.shp'
rst_fn = 'nlcd.img'
out_fn = 'NWI_cut_by_nlcd_boundary.tif' 
# legend of the output, 0:upland, 1: wetland, 2: Marine, 3: E1, 4: L1, 5: riverine, 6: vegetated wetland
result = converCodeAndRasterize(nwi_fn,rst_fn,out_fn)


time3=time.time()
print('time to finish whole script: ', (time3-time0)/60.0 )