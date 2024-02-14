
import nibabel as nib
import numpy as np
from stl import mesh
from skimage import measure
import matplotlib.pyplot as plt
import os


file_path = 'mask2.nii'
nifti_file = nib.load(file_path)
np_array = nifti_file.get_fdata()


verts,faces,normals, values = measure.marching_cubes(np_array,0)
obj_3D = mesh.Mesh(np.zeros(faces.shape[0],dtype=mesh.Mesh.dtype))
 
for i,f in enumerate(faces):    
    obj_3D.vectors[i] = verts[f]
 
obj_3D.save('poumon.obj')