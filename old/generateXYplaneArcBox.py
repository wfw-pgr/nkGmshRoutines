import sys, gmsh
import numpy as np
import generateXYplaneArcCurve as arc

# ========================================================= #
# ===  generate XYplane Arc Box                         === #
# ========================================================= #
def generateXYplaneArcBox( r1=0.0, r2=1.0, zWidth=1.0, zoffset=0.0, lc=0.1, nElems=10 ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    pts, Lines, Surfaces, Volumes, Parts = {}, {}, {}, {}, {}
    # ------------------------------------------------- #
    # --- [2] generate Arc / End Lines              --- #
    # ------------------------------------------------- #
    if  ( ( r1 > 0.0 ) & ( r2 > 0.0 ) ):
        Parts["arc1"]   = arc.generateXYplaneArcCurve( radius=r1, zoffset=zoffset, lc=lc )
        Parts["arc2"]   = arc.generateXYplaneArcCurve( radius=r2, zoffset=zoffset, lc=lc )
        Lines["arc1_1"] = Parts["arc1"]["Lines"]["line1"]
        Lines["arc1_2"] = Parts["arc1"]["Lines"]["line2"]
        Lines["arc2_1"] = Parts["arc2"]["Lines"]["line1"]
        Lines["arc2_2"] = Parts["arc2"]["Lines"]["line2"]
        Lines["end1"]   = gmsh.model.occ.addLine( ( Parts["arc1"]["pts"] )["-x"][4], ( Parts["arc2"]["pts"] )["-x"][4] )
        Lines["end2"]   = gmsh.model.occ.addLine( ( Parts["arc2"]["pts"] )["+x"][4], ( Parts["arc1"]["pts"] )["+x"][4] )
        LineLoop        = [ + Lines["arc1_1"], + Lines["arc1_2"], Lines["end1"], \
                            - Lines["arc2_2"], - Lines["arc2_1"], Lines["end2"]  ]
    elif( ( r1 == 0.0 ) & ( r2 > 0.0 ) ):
        Parts["arc2"]   = arc.generateXYplaneArcCurve( radius=r2, zoffset=zoffset, lc=lc )
        Lines["arc2_1"] = Parts["arc2"]["Lines"]["line1"]
        Lines["arc2_2"] = Parts["arc2"]["Lines"]["line2"]
        Lines["end2"]   = gmsh.model.occ.addLine( ( Parts["arc2"]["pts"] )["-x"][4], ( Parts["arc2"]["pts"] )["+x"][4] )
        LineLoop        = [ + Lines["arc2_1"], + Lines["arc2_2"], Lines["end2"] ]
    else:
        print( "[generateXYplaneArcBox] ( r1, r2 ) = ( {0}, {1} ) ?? ".format( r1, r2 ) )
    # ------------------------------------------------- #
    # --- [3] generate Loop / Surface / Volume      --- #
    # ------------------------------------------------- #
    LineLoopGroup      = gmsh.model.occ.addCurveLoop( LineLoop )
    Surfaces["Bottom"] = gmsh.model.occ.addPlaneSurface( [ LineLoopGroup ] )
    Volumes ["ArcBox"] = gmsh.model.occ.extrude( [ (2,Surfaces["Bottom"] ) ], \
                                                 0.0, 0.0, zWidth )
    # ------------------------------------------------- #
    # --- [4] PostProcess                           --- #
    # ------------------------------------------------- #
    ret = { "pts":pts, "Lines":Lines, "Surfaces":Surfaces, "Volumes":Volumes, "Parts":Parts }
    return( ret )


# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    generateXYplaneArcBox( r1=0.0, r2=2.0, zWidth=1.0 )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

