#!/usr/bin/env python3
print('start...')
import os,sys
import numpy as np
from numpy import ma
from osgeo import gdal
from osgeo import ogr
import time, glob
#print (waffls.__version__)
import rasterio
import geopandas as gpd
from scipy import ndimage


gdal.AllRegister()

def get_statistics(nlcd_fn,nwi_fn,out_fn):
    
      if os.path.exists(nwi_fn):

            try:
                  # read in the images
                  src = rasterio.open(nwi_fn)
                  nwiArr = src.read(1)
                  nlcdArr = rasterio.open(nlcd_fn).read(1) # nlcdArr means ccap array

                  # remove background values based on ccap
                  validID = np.where(nlcdArr==255) # background value is 100, and 0
                  nwiArr[validID] = 255 # background value is 255

                  outArr = nwiArr + 0

                  ArrForLossAss = ((nwiArr==1)|(nwiArr==6)).astype(np.uint8)
                                  
              

                  ################# loss assessment
                  # get the wetland region in nwi
                  totalWetSPN = np.sum(ArrForLossAss)
                  nwiWetID = (ArrForLossAss==1)
                  nlcdSelWet = nlcdArr[nwiWetID]
                  nwiArrSelWet = nwiArr[nwiWetID]
                  

                  nlcd52WetPN = np.sum((nlcdSelWet==22)|(nlcdSelWet==23)|(nlcdSelWet==24)) # impervious high intensity

                  # reset outSelWet values
                  outSelWet = outArr[nwiWetID]
                  outSelWet[(nlcdSelWet==22)|(nlcdSelWet==23)|(nlcdSelWet==24)] = 52
                  
                  
                  # put it back
                  outArr[nwiWetID] = outSelWet


                  
                  meta = src.meta.copy()
                  meta.update(compress='lzw',dtype='uint8', nodata=255, count=1)
                  if os.path.exists(out_fn):
                        filenamesrm = glob.glob(out_fn[:-4]+'.*')
                        for i in filenamesrm:
                              os.remove(i)

                  with rasterio.open(out_fn, 'w', **meta) as dst:
                        dst.write(outArr.astype(rasterio.uint8), 1)


            except Exception as oops:
                  print('\nProblem: ')
                  print(oops)


### apply the function
time0=time.time()
print('start time: ', time.ctime())
nwi_fn = 'NWI_cut_by_nlcd_boundary.tif'
nlcd_fn = 'nlcd.img'
out_fn = 'rasterChange_nwi_vs_nlcd.tif'
# legend of the output, 52: wetland to impervious surface, 121: upland to open water, 221: vegetated wetland to open water
result = get_statistics(nlcd_fn,nwi_fn,out_fn)
time1=time.time()
print('**************Finished in: '+ str((time1-time0)/60.0)+' minutes')  


    