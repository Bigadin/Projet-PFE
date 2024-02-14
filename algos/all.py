import vtk
import SimpleITK as sitk
import numpy as np

def generate_mesh(filename_nii):
    filename = filename_nii.split(".")[0]

    # read all the labels present in the file
    multi_label_image = sitk.ReadImage(filename_nii)
    img_npy = sitk.GetArrayFromImage(multi_label_image)
    labels = np.unique(img_npy)

    # read the file
    reader = vtk.vtkNIFTIImageReader()
    reader.SetFileName(filename_nii)
    reader.Update()

    # for all labels presented in the segmented file
    for label in labels:
        if int(label) != 0:
            # apply marching cube surface generation
            surf = vtk.vtkDiscreteMarchingCubes()
            surf.SetInputConnection(reader.GetOutputPort())
            surf.SetValue(0, int(label))
            surf.Update()

            # smoothing the mesh
            smoother = vtk.vtkWindowedSincPolyDataFilter()
            if vtk.VTK_MAJOR_VERSION <= 5:
                smoother.SetInput(surf.GetOutput())
            else:
                smoother.SetInputConnection(surf.GetOutputPort())
            smoother.SetNumberOfIterations(30)
            smoother.NonManifoldSmoothingOn()
            smoother.NormalizeCoordinatesOn()
            smoother.GenerateErrorScalarsOn()
            smoother.Update()

            # Save as STL
            save_as_stl(smoother.GetOutput(), f'{filename}_{label}.stl')

            # Save as OBJ
            save_as_obj(smoother.GetOutput(), f'{filename}_{label}.obj')

def save_as_stl(mesh, filename):
    writer = vtk.vtkSTLWriter()
    writer.SetInputData(mesh)
    writer.SetFileName(filename)
    writer.SetFileTypeToASCII()
    writer.Write()

def save_as_obj(mesh, filename):
    writer = vtk.vtkOBJWriter()
    writer.SetInputData(mesh)
    writer.SetFileName(filename)
    writer.Write()


if __name__ == '__main__':
    filename_nii = 'lung_test.nii'
    generate_mesh(filename_nii)
