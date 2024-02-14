import vtk
import os
def render():
    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    
    renWin.AddRenderer(ren)
    # Create a RenderWindowInteractor to permit manipulating the camera
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    style = vtk.vtkInteractorStyleTrackballCamera()
    iren.SetInteractorStyle(style)
    filenames = ["lung_test_1.0.stl","lung_test_2.0.stl"]
    #for filename in os.listdir("PYTHONS"):
    ## Check if the path is a file (not a subfolder)
    #    file_path = os.path.join("PYTHONS", filename)
    #
    #    if os.path.isfile(file_path) and filename.lower().endswith('.stl'):
    #        filenames.append(file_path)
    #        print(filenames[:4])

    for stlFilename in filenames:
        polydata = loadStl(stlFilename)
        if(stlFilename == 'lung_test_1.0.stl'):
            ren.AddActor(polyDataToActor(polydata,(.1,.5,.7),0.4))
        else:
            ren.AddActor(polyDataToActor(polydata,(0.8,0.1,0.1),1))

    ren.SetBackground(0.1, 0.1, 0.1)
    
    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()
    

def loadStl(fname):
    """Load the given STL file, and return a vtkPolyData object for it."""
    reader = vtk.vtkSTLReader()
    reader.SetFileName(fname)
    reader.Update()
    polydata = reader.GetOutput()
    return polydata

def polyDataToActor(polydata,color,opacity):
    """Wrap the provided vtkPolyData object in a mapper and an actor, returning
    the actor."""
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        #mapper.SetInput(reader.GetOutput())
        mapper.SetInput(polydata)
    else:
        mapper.SetInputData(polydata)
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    #actor.GetProperty().SetRepresentationToWireframe()
    actor.GetProperty().SetColor(color)
    actor.GetProperty().SetOpacity(opacity)
    return actor

render()