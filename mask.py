import os
import numpy as np
import vtk
import pydicom
from pydicom.dataset import FileDataset
from skimage import measure 
from vtk.util.numpy_support import numpy_to_vtk  # Import numpy_to_vtk

class LungSegmentation3D:
    def __init__(self, dicom_dir):
        self.dicom_dir = dicom_dir
        self.load_dicom()

    def load_dicom(self):
        # Load DICOM files from the specified directory
        self.scans = [pydicom.dcmread(os.path.join(self.dicom_dir, s)) for s in os.listdir(self.dicom_dir)]
        self.scans.sort(key=lambda x: int(x.InstanceNumber))

        # Extract spacing information from DICOM metadata
        self.spacing = self.get_spacing()

    def get_spacing(self):
        # Extract spacing information (PixelSpacing and SliceThickness) from DICOM metadata
        pixel_spacing = self.scans[0].PixelSpacing
        slice_thickness = self.scans[0].SliceThickness
        spacing = [float(pixel_spacing[0]), float(pixel_spacing[1]), float(slice_thickness)]
        return spacing

    def get_pixels_hu(self):
        # Convert DICOM pixel values to Hounsfield Units (HU)
        image = np.stack([s.pixel_array for s in self.scans])
        image = image.astype(np.int16)
        image[image == -2000] = 0

        intercept = self.scans[0].RescaleIntercept
        slope = self.scans[0].RescaleSlope

        if slope != 1:
            image = slope * image.astype(np.float64)
            image = image.astype(np.int16)

        image += np.int16(intercept)

        return np.array(image, dtype=np.int16)

    def segment_lung_mask(self, image, fill_lung_structures=True):
        # Segment lung mask using thresholding and labeling
        binary_image = np.array(image >= -700, dtype=np.int8) + 1
        labels = measure.label(binary_image)
        background_label = labels[0, 0, 0]

        binary_image[background_label == labels] = 2

        if fill_lung_structures:
            for i, axial_slice in enumerate(binary_image):
                axial_slice = axial_slice - 1
                labeling = measure.label(axial_slice)
                l_max = self.largest_label_volume(labeling, bg=0)

                if l_max is not None:
                    binary_image[i][labeling != l_max] = 1
        binary_image -= 1
        binary_image = 1 - binary_image

        labels = measure.label(binary_image, background=0)
        l_max = self.largest_label_volume(labels, bg=0)
        if l_max is not None:
            binary_image[labels != l_max] = 0

        return binary_image

    @staticmethod
    def largest_label_volume(im, bg=-1):
        # Find the largest label volume in a labeled image
        vals, counts = np.unique(im, return_counts=True)
        counts = counts[vals != bg]
        vals = vals[vals != bg]
        if len(counts) > 0:
            return vals[np.argmax(counts)]
        else:
            return None

    def create_3d_model(self):
        # Create 3D model of segmented lungs using VTK
        patient_pixels = self.get_pixels_hu()
        segmented_lungs_fill = self.segment_lung_mask(patient_pixels, fill_lung_structures=True)

        for i, mask in enumerate(segmented_lungs_fill):
            get_high_vals = mask == 0
            patient_pixels[i][get_high_vals] = 0

        seg_lung_pixels = patient_pixels

        # Create VTK image data
        volume = np.stack([img for img in seg_lung_pixels])
        vtk_image_data = vtk.vtkImageData()
        vtk_image_data.SetDimensions(volume.shape[2], volume.shape[1], volume.shape[0])

        # Set spacing of VTK image data
        vtk_image_data.SetSpacing(self.spacing[0], self.spacing[1], self.spacing[2])

        # Convert NumPy array to VTK image data
        vtk_array = numpy_to_vtk(volume.ravel(), deep=True, array_type=vtk.VTK_SHORT)
        vtk_array.SetNumberOfComponents(1)
        vtk_array.SetName("HU")

        # Attach the VTK array to VTK image data
        vtk_image_data.GetPointData().SetScalars(vtk_array)

        # Create contour filter
        contour = vtk.vtkContourFilter()
        contour.SetInputData(vtk_image_data)
        contour.SetValue(0, -500)  # Adjust threshold as needed

        # Create mapper
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(contour.GetOutputPort())

        # Create actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
       
        # Adjust actor opacity
        actor.GetProperty().SetOpacity(1)

        # Create renderer
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.2, 0.4)

        # Set renderer options for smoother rendering
        renderer.SetUseDepthPeeling(1)
        renderer.SetOcclusionRatio(0.1)

        # Create render window
        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)
        
        # Set render window properties for smoother rendering
        render_window.SetMultiSamples(0)
        render_window.SetAlphaBitPlanes(1)

        # Create render window interactor
        render_window_interactor = vtk.vtkRenderWindowInteractor()
        render_window_interactor.SetRenderWindow(render_window)

        # Start visualization
        render_window.Render()
        render_window_interactor.Start()


# Example usage:
dicom_directory = 'C:/Users/Wail/Documents/pythons/VTK/files/lung'
segmentation = LungSegmentation3D(dicom_directory)
segmentation.create_3d_model()
