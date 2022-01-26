import sys, gmsh
import numpy as np

# ========================================================= #
# ===  generate XYplane Circle Arc Curve                === #
# ========================================================= #
def generateXYplaneArcCurve( radius=None, zoffset=0.0, lc=1.0, ysign="+" ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    pts      = {}
    Lines    = {}
    Surfaces = {}
    Volumes  = {}
    ret      = {}
    # ------------------------------------------------- #
    # --- [2] generate points                       --- #
    # ------------------------------------------------- #
    initNum       = 1
    pts["OP"]     = [      0.0,    0.0, zoffset, lc, initNum ]
    pts["+x"]     = [ + radius,    0.0, zoffset, lc, initNum ]
    pts["-x"]     = [ - radius,    0.0, zoffset, lc, initNum ]
    if   ( ysign=="+" ):
        pts["+y"] = [      0.0, + radius, zoffset, lc, initNum ]
    elif ( ysign=="-" ):
        pts["+y"] = [      0.0, - radius, zoffset, lc, initNum ]
    for key in list( pts.keys() ):
        pt              = pts[key]
        ( pts[key] )[4] = gmsh.model.occ.addPoint( pt[0], pt[1], pt[2], meshSize=pt[3] )
    # ------------------------------------------------- #
    # --- [3] generate lines                        --- #
    # ------------------------------------------------- #
    Lines["line1"] = gmsh.model.occ.addCircleArc( pts["+x"][4], pts["OP"][4], pts["+y"][4] )
    Lines["line2"] = gmsh.model.occ.addCircleArc( pts["+y"][4], pts["OP"][4], pts["-x"][4] )
    # ------------------------------------------------- #
    # --- [4] PostProcess                           --- #
    # ------------------------------------------------- #
    ret = { "pts":pts, "Lines":Lines, "Surfaces":Surfaces, "Volumes":Volumes }
    return( ret )


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    generateXYplaneArcCurve( radius= 1.0 )
    
    gmsh.model.occ.synchronize()
    gmsh.write( "example.geo_unrolled" )
    gmsh.finalize()

