import sys, gmsh
import numpy as np
import generateXYplaneArcCurve as arc

# ========================================================= #
# ===  generate Square Region                           === #
# ========================================================= #
def generateSquare( x1Leng=1.0, x2Leng=1.0, offset=0.0, lc=0.1, nElems=10 ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    pts, Lines, Surfaces, Volumes, Parts = {}, {}, {}, {}, {}
    # ------------------------------------------------- #
    # --- [2] generate Arc / End Lines              --- #
    # ------------------------------------------------- #
    if   ( plane.lower() == "xy" ):
        points = [ [ -x1Leng, -x2Leng, offset, lc, 0 ], \
                   [ +x1Leng, -x2Leng, offset, lc, 0 ], \
                   [ -x1Leng, +x2Leng, offset, lc, 0 ], \
                   [ +x1Leng, +x2Leng, offset, lc, 0 ]  ]
    elif ( plane.lower() == "yz" ):
        points = [ [ offset, -x1Leng, -x2Leng, lc, 0 ], \
                   [ offset, +x1Leng, -x2Leng, lc, 0 ], \
                   [ offset, -x1Leng, +x2Leng, lc, 0 ], \
                   [ offset, +x1Leng, +x2Leng, lc, 0 ]  ]
    elif ( plane.lower() == "xz" ):
        points = [ [ -x1Leng, offset, -x2Leng, lc, 0 ], \
                   [ +x1Leng, offset, -x2Leng, lc, 0 ], \
                   [ -x1Leng, offset, +x2Leng, lc, 0 ], \
                   [ +x1Leng, offset, +x2Leng, lc, 0 ]  ]
        
        
    if  ( ( x1Leng > 0.0 ) & ( x2Leng > 0.0 ) ):
        Parts["arc1"]   = arc.generateXYplaneArcCurve( radius=x1Leng, zoffset=zoffset, lc=lc )
        Parts["arc2"]   = arc.generateXYplaneArcCurve( radius=x2Leng, zoffset=zoffset, lc=lc )
        Lines["arc1_1"] = Parts["arc1"]["Lines"]["line1"]
        Lines["arc1_2"] = Parts["arc1"]["Lines"]["line2"]
        Lines["arc2_1"] = Parts["arc2"]["Lines"]["line1"]
        Lines["arc2_2"] = Parts["arc2"]["Lines"]["line2"]
        Lines["end1"]   = gmsh.model.occ.addLine( ( Parts["arc1"]["pts"] )["-x"][4], ( Parts["arc2"]["pts"] )["-x"][4] )
        Lines["end2"]   = gmsh.model.occ.addLine( ( Parts["arc2"]["pts"] )["+x"][4], ( Parts["arc1"]["pts"] )["+x"][4] )
        LineLoop        = [ + Lines["arc1_1"], + Lines["arc1_2"], Lines["end1"], \
                            - Lines["arc2_2"], - Lines["arc2_1"], Lines["end2"]  ]
    elif( ( x1Leng == 0.0 ) & ( x2Leng > 0.0 ) ):
        Parts["arc2"]   = arc.generateXYplaneArcCurve( radius=x2Leng, zoffset=zoffset, lc=lc )
        Lines["arc2_1"] = Parts["arc2"]["Lines"]["line1"]
        Lines["arc2_2"] = Parts["arc2"]["Lines"]["line2"]
        Lines["end2"]   = gmsh.model.occ.addLine( ( Parts["arc2"]["pts"] )["-x"][4], ( Parts["arc2"]["pts"] )["+x"][4] )
        LineLoop        = [ + Lines["arc2_1"], + Lines["arc2_2"], Lines["end2"] ]
    else:
        print( "[generateXYplaneArcBox] ( x1Leng, x2Leng ) = ( {0}, {1} ) ?? ".format( x1Leng, x2Leng ) )
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

    generateXYplaneArcBox( x1Leng=0.0, x2Leng=2.0, zWidth=1.0 )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

