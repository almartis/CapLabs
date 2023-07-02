# -*- coding:utf-8 -*-

##############################################
############### BY Caplabs Team ##############
##############################################
#              Date: 05/17/23                #
##############################################

import os
import numpy as np
import pydicom
import math
from scipy import ndimage
import png
from pathlib import Path
from PIL import Image

def resizeImg(axis, filename, max_width, max_height):
    """Resize the given images to the specified size"""

    image = ""

    print("resizeImg cwd: "+os.getcwd())
    if (axis == 'axial'):
        os.chdir('loaded_img/axial_slices')
    elif (axis == 'coronal'):
        os.chdir('loaded_img/coronal_slices')
    elif (axis == 'sagital'):
        os.chdir('loaded_img/sagital_slices')
    
    try:
        image = Image.open(filename)

        print('Resizing '+filename+' ...')
        # Resize the images by keeping the aspect ratio
        image.thumbnail((int(max_width),int(max_height)))
        image.save('tmp.png')

        print('done!\n')
        
        # Replace the original image with the new one
        os.remove(filename)
        os.rename('tmp.png',filename)

        print(filename+' resized to {}x{}'.format(image.width,image.height))

        image.close()
        os.chdir('../..')
    except:
        if image != "":
            image.close()

        os.chdir('../..')
        print('Error! Failed to resize the file "{}" to {}x{}'.format(filename,max_width,max_height))

def imgResample(point3d,hu_point3d,dcm_2elm,spacing=[1,1,1]):
    """ This function resize the images to 1x1x1 """

    print("Resampling process...")
    
    pix_sx,pix_sy,pix_th=dcm_2elm[0].PixelSpacing[0],dcm_2elm[0].PixelSpacing[1],abs(dcm_2elm[0].ImagePositionPatient[2]-dcm_2elm[1].ImagePositionPatient[2]) # abs(...) = slice thickness

    dim_arr=np.array([pix_sx,pix_sy,pix_th])
    sp=np.array(spacing)

    resize_fact=dim_arr/sp
    point3d_shape=np.array(list(point3d.shape))

    obj3d_size=point3d_shape*resize_fact
    obj3d_size=np.round(obj3d_size)
   
    resize_fact=obj3d_size/point3d_shape
      
    rsmpl_point3d=ndimage.interpolation.zoom(point3d,resize_fact)
    rsmpl_point3d=np.minimum(rsmpl_point3d,65535) # change all the values greater than 65535 to 65535
          
    rsmpl_hu_point3d=ndimage.interpolation.zoom(hu_point3d,resize_fact)
    #rsmpl_hu_point3d=np.minimum(rsmpl_hu_point3d,65535) 

    
    return rsmpl_point3d,rsmpl_hu_point3d

class Ax3D(object):
    """ Creates an array of pixels that are linked to the axial axis """

    def __init__(self,point3d):
        """"""
        shape=list(point3d.shape)
        
        self.nbr_slices=shape.pop()

        array=np.zeros(shape)
        list_array=[]

        for i in range(0,self.nbr_slices):
            array=point3d[:,:,i]
            list_array.append(array)

        self.pixel_array_list=list_array

class Cor3D(object):
    """ Creates an array of pixels that are linked to the coronal axis """

    def __init__(self,point3d):
        """"""
        shape=list(point3d.shape)
        
        self.nbr_slices=shape.pop(1)

        array=np.zeros(shape)
        list_array=[]

        for i in range(0,self.nbr_slices):
            array=point3d[:,i,:]
            list_array.append(array)

        self.pixel_array_list=list_array

class Sag3D(object):
    """ Creates an array of pixels that are linked to the coronal axis """

    def __init__(self,point3d):
        """"""
        shape=list(point3d.shape)

        self.nbr_slices=shape.pop(0)

        array=np.zeros(shape)
        list_array=[]
        
        for i in range(0,self.nbr_slices):
            array=point3d[i,:,:]
            list_array.append(array)
            
        self.pixel_array_list=list_array


class Gen3dArr(object):
    """This class will allow you to create an array of 3d points."""

    def __init__(self,slices: pydicom.filebase.DicomFileLike):
        """ """
        self.nbr_axslices=len(slices)
        shape=list(slices[0].pixel_array.shape)
        shape.append(self.nbr_axslices)
        point3d=np.zeros(shape,dtype="uint32") # We are considering the same shape for all the slices
        hu_point3d=np.zeros(shape,dtype="float64")
        
        for i in range(0,self.nbr_axslices):

            pixel_array=np.maximum(slices[i].pixel_array,0).astype(float) # For compatibility purpose
            pixel_array=(pixel_array/slices[i].pixel_array.max())*65535 # We have used the value 65535 instead of 255 because medical images are stored with 2 bytes of gray shades. Using 255 will cause data loss.
            pixel_array=np.uint32(pixel_array)

            point2d=pixel_array
            point3d[:,:,i]=point2d
            hu_point3d[:,:,i]=(slices[i].pixel_array*slices[i].RescaleSlope)+slices[i].RescaleIntercept

        tmp=imgResample(point3d,hu_point3d,[slices[0],slices[1]])

        self.point3d=tmp[0]
        self.hu_point3d=tmp[1]
        
        self.ax3d=Ax3D(self.point3d)
        self.cor3d=Cor3D(self.point3d)
        self.sag3d=Sag3D(self.point3d)

    def saveSlices(self):
        """ Save slices in separate directory depending of the axis """
        cur=Path.cwd()
        
        ax=cur/"loaded_img/axial_slices"
        cor=cur/"loaded_img/coronal_slices"
        sag=cur/"loaded_img/sagital_slices"

        nbr=0

        print("Saving slices...",end=" ")
        try:
            ax.mkdir()
            cor.mkdir()
            sag.mkdir()
            
            for i in range(0,self.ax3d.nbr_slices):
                try:
                    img=png.from_array(self.ax3d.pixel_array_list[i],"L;16")
                    img.save("loaded_img/axial_slices/ax_img"+str(i)+".png")

                    resizeImg('axial','ax_img'+str(i)+'.png','400','400')
                    
                    nbr=nbr+1
                except:
                    print("Error while saving {}".format("ax_img"+str(i)+".png"))

            for i in range(0,self.cor3d.nbr_slices):
                try:
                    img=png.from_array(self.cor3d.pixel_array_list[i],"L;16")
                    img.save("loaded_img/coronal_slices/cor_img"+str(i)+".png")

                    resizeImg('coronal','cor_img'+str(i)+'.png','400','400')
                    
                    nbr=nbr+1
                except:
                    print("Error while saving {}".format("cor_img"+str(i)+".png"))
                          
            for i in range(0,self.sag3d.nbr_slices):
                try:
                    img=png.from_array(self.sag3d.pixel_array_list[i],"L;16")
                    img.save("loaded_img/sagital_slices/sag_img"+str(i)+".png")

                    resizeImg('sagital','sag_img'+str(i)+'.png','400','400')
                    
                    nbr=nbr+1
                except:
                    print("Error while saving {}".format("sag_img"+str(i)+".png"))
                    
            print("Done!\n\nSlice(s) saved: {}!\n".format(nbr))
            
        except:
            print("Error while creating the directories for images.\nCheck that you have the permission to write on the directory\n")
