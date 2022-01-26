import numpy as np
import sys
import gmsh


# ========================================================= #
# ===  generate Rectangular Box                         === #
# ========================================================= #
def generateRectangularBox( v1=[1.0,0.0,0.0], v2=[0.0,1.0,0.0], v3=[0.0,0.0,1.0], \
                            origin=[0.0,0.0,0.0], lc=0.1 ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    x_, y_, z_ = 0, 1, 2
    pts, lines, surfs, volus, parts = {}, {}, {}, {}, {}
    # ------------------------------------------------- #
    # --- [2] generate points / lines               --- #
    # ------------------------------------------------- #
    pts["square0"]  = gmsh.model.occ.addPoint( origin[x_]              , origin[y_]              , origin[z_]              , meshSize=lc )
    pts["square1"]  = gmsh.model.occ.addPoint( origin[x_]+v1[x_]       , origin[y_]+v1[y_]       , origin[z_]+v1[z_]       , meshSize=lc )
    pts["square2"]  = gmsh.model.occ.addPoint( origin[x_]+v1[x_]+v2[x_], origin[y_]+v1[y_]+v2[y_], origin[z_]+v1[z_]+v2[z_], meshSize=lc )
    pts["square3"]  = gmsh.model.occ.addPoint( origin[x_]+v2[x_]       , origin[y_]+v2[y_]       , origin[z_]+v2[z_]       , meshSize=lc )
    lines["line01"] = gmsh.model.occ.addLine ( pts["square0"], pts["square1"] )
    lines["line12"] = gmsh.model.occ.addLine ( pts["square1"], pts["square2"] )
    lines["line23"] = gmsh.model.occ.addLine ( pts["square2"], pts["square3"] )
    lines["line30"] = gmsh.model.occ.addLine ( pts["square3"], pts["square0"] )
    LineLoopGroup   = gmsh.model.occ.addCurveLoop   ( [ lines["line01"], lines["line12"], \
                                                        lines["line23"], lines["line30"]  ] )
    surfs["bottom"] = gmsh.model.occ.addPlaneSurface( [ LineLoopGroup ] )
    extrude_ret     = gmsh.model.occ.extrude ( [ (2,surfs["bottom"]) ], v3[x_], v3[y_], v3[z_] )
    surfs["top"]    = ( extrude_ret[0] )[1]
    volus["box"]    = ( extrude_ret[1] )[1]
    surfs["side1"]  = ( extrude_ret[2] )[1]
    surfs["side2"]  = ( extrude_ret[3] )[1]
    surfs["side3"]  = ( extrude_ret[4] )[1]
    surfs["side4"]  = ( extrude_ret[5] )[1]
    ret             = { "pts":pts, "lines":lines, "surfs":surfs, "volus":volus, "parts":parts }
    return( ret )
    

# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "model" )

    generateRectangularBox()

    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "model.geo_unrolled" )
    gmsh.write( "model.msh" )
    gmsh.finalize()

