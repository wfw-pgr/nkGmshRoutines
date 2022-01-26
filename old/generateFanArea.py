import numpy as np
import os, sys
import gmsh

gmshlib = os.environ["gmshLibraryPath"]
sys.path.append( gmshlib )
import generateXYplaneArcCurve as arc

# ========================================================= #
# ===  generate Fan-shaped Area                         === #
# ========================================================= #
def generateFanArea( r1=1.0, r2=2.0, th1=0.0, th2=90.0, zoffset=0.0, \
                     origin=[ 0.0, 0.0 ], lc=1.0 ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    ptsDim , lineDim , surfDim , voluDim  =  0,  1,  2,  3
    pts    , line    , surf    , volu     = {}, {}, {}, {}
    x_,y_,z_,lc_,tag_                     = 0, 1, 2, 3, 4

    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    arc1    = arc.generateXYplaneArcCurve( radius=r1, th1=th1, th2=th2, \
                                           zoffset=zoffset, origin=origin, lc=lc )
    arc2    = arc.generateXYplaneArcCurve( radius=r2, th1=th1, th2=th2, \
                                           zoffset=zoffset, origin=origin, lc=lc )
    pts["corner1"] = arc1["pts"]["+x"]
    pts["corner2"] = arc1["pts"]["-x"]
    pts["corner3"] = arc2["pts"]["+x"]
    pts["corner4"] = arc2["pts"]["-x"]
    line["arc12"]  = arc1["Lines"]["line1"]
    line["arc34"]  = arc2["Lines"]["line1"]
    line["end24"]  = gmsh.model.occ.addLine( pts["corner2"][tag_], pts["corner4"][tag_] )
    line["end31"]  = gmsh.model.occ.addLine( pts["corner3"][tag_], pts["corner1"][tag_] )
    LineLoop       = [ line["arc12"], line["end24"], - line["arc34"], line["end31"] ]
    LineLoopGroup  = gmsh.model.occ.addCurveLoop( LineLoop )
    surf["fan"]    = gmsh.model.occ.addPlaneSurface( [LineLoopGroup] )

    # ------------------------------------------------- #
    # --- [3] return                                --- #
    # ------------------------------------------------- #
    ret = { "pts":pts, "line":line, "surf":surf, "volu":volu }
    return( ret )

# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):
    
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    r1      = 0.60
    r2      = 0.70
    th1     = 270.0
    th2     = 320.0
    zoffset = 0.0
    origin  = [ 0.0, 0.0 ]
    lc      = 0.05

    generateFanArea( r1=r1, th1=th1, r2=r2, th2=th2, zoffset=zoffset, \
                     origin=origin, lc=lc )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

