# -*- coding:utf-8 -*-

##############################################
############### BY Caplabs Team ##############
##############################################
#              Date: 05/27/23                #
##############################################

from flask import Flask, request, send_file
from flask_cors import CORS
import os
import numpy as np
import pydicom
from skimage import measure
from stl import mesh

from dataLoader import loadData
from slc_gen import Gen3dArr, imgResample


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://172.19.208.228:5173"}})

# Define the directories for different DICOM packs
directories = {
    'pack1': './dicom_files/pack1',
    'pack2': './dicom_files/pack2',
    'pack3': './dicom_files/pack3',
}

@app.route('/capsApi/process', methods=['POST'])
def process_dcm():
    """
    Process the set of DICOM files selected by the client and return a 3D mesh in the STL file format
    """
    if request.method == 'POST':
        # Get the DICOM pack to use and the different configs
        pack = request.json.get('pack')

        try:
            min_hu = int(request.json.get('min'))
        except:
            min_hu = 300
            
        try:
            max_hu = int(request.json.get('max'))
        except:
            max_hu = 2000
            
        try:
            surflevel = float(request.json.get('surflevel'))
        except:
            surflevel = 299

        seg_flag = request.json.get('seg_flag')
        if(seg_flag == "false"):
            seg_flag = False
        elif (seg_flag == "true"):
            seg_flag = True

        #print("seg_flag= "+str(seg_flag))
        
        # Get the DICOM files path from the pack selected
        dicom_directory = directories.get(pack)

        # Retrieve DICOM files from the specified directory
        slices=loadData(dicom_directory)
        if(slices != None):
            volume=Gen3dArr(slices) # Resampling process is done internally with a (1.0,1.0,1.0) spacing

        segmented_volume = volume.point3d
        # Perform segmentation using a range of threshold values
        if seg_flag == True:    
            segmented_volume = np.zeros(volume.point3d.shape,dtype="uint32")
            for i in range(volume.point3d.shape[2]):
                for j in range(volume.point3d.shape[1]):
                    for k in range(volume.point3d.shape[0]):
                        if (volume.hu_point3d[k,j,i]>=min_hu and volume.hu_point3d[k,j,i]<=max_hu):
                            segmented_volume[k,j,i] = volume.point3d[k,j,i]

        # Generate mesh object
        verts, faces, _, _ = measure.marching_cubes(segmented_volume,surflevel)
        mesh_data = mesh.Mesh(np.zeros(faces.shape[0], dtype=mesh.Mesh.dtype))
        for i, face in enumerate(faces):
            for j in range(3):
                mesh_data.vectors[i][j] = verts[face[j], :]

        #save the stl file
        mesh_data.save("./stl_files/test_stl.stl")

        # Check the content of the './loaded_img/' directory
        os.chdir('./loaded_img')

        # Delete the content of the directory if there is something in
        if(len(os.listdir()) != 0):
            os.system('rm ./* -R')

        os.chdir('../')
        #save images of the different axis: coronal, sagital, axial
        volume.saveSlices()
        
        return send_file("./stl_files/test_stl.stl", as_attachment=True, download_name="test_stl.stl")

    else:
        return {'message': 'Invalid request method.'}

    
@app.route('/capsApi/slices', methods=['POST'])
def getImg():
    """Get the a given slice and send it to the client"""

    if request.method == 'POST':
        slice_type = request.json.get('slice_type')
        slice_nbr = int(request.json.get('slice_nbr'))

        os.chdir('./loaded_img')
        if(len(os.listdir()) != 0):
            os.chdir('../')
            
            # Build the file path based on the data sent by the client
            if slice_type == 'axial':
                ref = 'ax_img'
                basepath = './loaded_img/axial_slices/'
                lookpath = basepath+ref+str(slice_nbr)+'.png'

                os.chdir('./loaded_img/axial_slices/')
            elif slice_type == 'sagital':
                ref = 'sag_img'
                basepath = './loaded_img/sagital_slices/'
                lookpath = basepath+ref+str(slice_nbr)+'.png'
                
                os.chdir('./loaded_img/sagital_slices/')
            else:
                ref = 'cor_img'
                basepath = './loaded_img/coronal_slices/'
                lookpath = basepath+ref+str(slice_nbr)+'.png'
                
                os.chdir('./loaded_img/coronal_slices/')

                
            content = os.listdir()
            finded = False
            look = ref+str(slice_nbr)+'.png'
            
            # Test if the requested file is in the directory
            for i in content:
                if i == look:
                    finded = True

            os.chdir("/home/justus/projects/capsApi/")
            # Send a response based on wether the requested file was found or not
            if finded:
                print('Image '+str(slice_nbr)+' loaded! File: '+lookpath)
                return send_file(lookpath,as_attachment=True, download_name=slice_type+'_img.png')
            else:
                tmp_var = []
                for i in content:
                    tmp_var.append(int(i.replace(ref,'').replace('.png','')))

                tmp_var.sort()
                tmp_var = tmp_var.pop()

                print('Replacement... imaage '+str(tmp_var)+' loaded! file: '+basepath+ref+str(tmp_var)+'.png')
                return send_file(basepath+ref+str(tmp_var)+'.png',as_attachment=True, download_name=slice_type+'_img.png')
        else:
            return {'message': 'Requested data not found!'}
    else:
        return {'message': 'Invalid request method.'}



    
if __name__ == '__main__':
    app.run(host='192.168.0.128', port='8000')
