# -*- coding: utf-8 -*-

from matplotlib.path        import Path
from matplotlib.patches     import PathPatch
from matplotlib.collections import PatchCollection
from shapely.geometry       import Polygon
from xml.dom                import minidom
import matplotlib.pyplot as plt
import numpy             as np

def main():
    # file_path = "simple.svg"
    file_path = "a.svg"

    doc = minidom.parse( file_path )
    polygons = []
    
    for path in doc.getElementsByTagName('path'):
        if path.getAttribute('class') != "outer":
            continue

        pathds = path.getAttribute('d').strip().split()
        
        for i, pathd in enumerate( pathds ):
            if "." in pathd:
                pathds[i] = float( pathd )

        shell, holes = conv_pathd_to_shapely( pathds )

        polygons.append( Polygon( shell=shell, holes=holes) )

    fig, ax = plt.subplots()
    
    for polygon in polygons:
        plot_polygon(ax, polygon, facecolor='lightblue', edgecolor='red')
        
    plt.show()
    
def conv_pathd_to_shapely( pathds ):
    holes = []
    holes_tmp = []
    
    while len(pathds):
        if pathds[0] in ["M","L"]:
            pathds.pop(0)
            continue
        if pathds[0] == "Z":
            pathds.pop(0)
            holes.append( holes_tmp )
            holes_tmp = []
            continue
        
        # co_x = pathds.pop(0)
        # co_y = pathds.pop(0)
        co_y = pathds.pop(0)
        co_x = pathds.pop(0)
        co_x, co_y = conv_affine_rotate( co_x, co_y )
        holes_tmp.append( (co_x, co_y) )

    shell = holes.pop(0)
    return shell, holes

# cf https://end0tknr.hateblo.jp/entry/20220923/1663900289
def conv_affine_rotate( org_x, org_y ):

    # アフィン変換行列 180度回転
    affine = np.array([[-1, 0, 0],
                       [ 0,-1, 0],
                       [ 0, 0, 1]])
    org_co = np.array([[org_x],
                       [org_y],
                       [  1  ]])
    new_co = affine.dot(org_co)
    
    return new_co[0],new_co[1]
    

# Plots a Polygon to pyplot `ax`
# cf. https://stackoverflow.com/questions/55522395
def plot_polygon(ax, poly, **kwargs):
    path = Path.make_compound_path(
        Path(np.asarray(poly.exterior.coords)[:, :2]),
        *[Path(np.asarray(ring.coords)[:, :2]) for ring in poly.interiors])

    patch = PathPatch(path, **kwargs)
    collection = PatchCollection([patch], **kwargs)
    
    ax.add_collection(collection, autolim=True)
    ax.autoscale_view()
    return collection

if __name__ == '__main__':
    main()