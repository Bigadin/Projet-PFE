
from stl2obj import Stl2Obj

src = 'path-to-src-file'  # may be stl or obj
dst = 'path-to-dst-file'  # may be stl or obj
callback = lambda code: print(code)

Stl2Obj().convert(src, dst, callback)