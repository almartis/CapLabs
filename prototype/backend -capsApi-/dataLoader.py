# -*- coding:utf-8 -*-

##############################################
############### BY Caplab Team ###############
##############################################
#              Date: 11/21/22                #
##############################################

from pathlib import Path
import glob
import pydicom

def loadData(path: str):
    """"""
    dcm_elm,slices=[],[]
    dir=Path(path)

    if(dir.is_dir()):

        path=path+"/*.dcm"
                
        path_list=glob.glob(path)
        
        for path in path_list:
            try:
                dcm_elm.append(pydicom.dcmread(path))
            except:
                return None
             
        for elm in dcm_elm:
            if(hasattr(elm,"SliceLocation")):
                slices.append(elm)
                slices.sort(key= lambda s:s.SliceLocation) # Order the slices by their SliceLocation value
  
        return slices
    
    else:
        return None
        
