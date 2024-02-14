import nibabel as nib
import numpy as np
import os

def merge_nifti_files(input_files, output_file):
    # Load individual NIfTI files
    nifti_images = [nib.load(filename) for filename in input_files]

    # Extract image data
    image_data = [img.get_fdata() for img in nifti_images]

    # Concatenate image data along the appropriate axis
    concatenated_data = np.stack(image_data, axis=2)  # Assuming 3D data

    # Adjust metadata if necessary
    # You may need to update the header information like affine transformation matrix, dimensions, etc.

    # Save the merged NIfTI file
    merged_img = nib.Nifti1Image(concatenated_data, nifti_images[0].affine)
    nib.save(merged_img, output_file)

# Example usage:
input_folder = r'C:\Users\Wail\Documents\pythons\VTK\files\lung_segment_nifti'
output_file = r'C:\Users\Wail\Documents\pythons\VTK\files\merged_file.nii.gz'

# Get list of NIfTI files in the input folder
input_files = [os.path.join(input_folder, file) for file in os.listdir(input_folder) if file.endswith('.nii.gz')]

merge_nifti_files(input_files, output_file)
