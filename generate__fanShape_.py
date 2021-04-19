import os, sys
import numpy         as np
import gmsh
# import gmsh_api.gmsh as gmsh

import nkGmshRoutines.generate__sectorShape as arc

# ========================================================= #
# ===  generate Fan-shaped Area                         === #
# ========================================================= #
def generate__fanShape( r1=0.0, r2=2.0, th1=0.0, th2=90.0, zoffset=0.0, height=1.0, side="+", \
                        origin=[ 0.0, 0.0 ], lc=1.0, defineSurf=False, defineVolu=False ):
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    ptsDim , lineDim , surfDim , voluDim  =  0,  1,  2,  3
    pts    , line    , surf    , volu     = {}, {}, {}, {}
    x_,y_,z_,lc_,tag_                     = 0, 1, 2, 3, 4
    if ( defineVolu ): defineSurf = True
    if   ( th2-th1 <= 90.0 ):
        acute, obtuse = True, False
    elif ( th2-th1 >  90.0 ):
        acute, obtuse = False, True
    elif ( ( th2-th1 > 180.0 ) | ( th2-th1 < 0.0 ) ) :
        sys.exit( "[generate__fanShape] th2-th1 == ??? ( 0 < th2-th1 < 180 )" )
        
    # ------------------------------------------------- #
    # --- [2] Modeling (1)  0 < r1 < r2 ver.        --- #
    # ------------------------------------------------- #
    
    if ( ( r1 > 0.0 ) & ( r2 > 0.0 ) ):
        arc1    = arc.generate__sectorShape( radius=r1, th1=th1, th2=th2, side=side, \
                                             zoffset=zoffset, origin=origin, lc=lc )
        arc2    = arc.generate__sectorShape( radius=r2, th1=th1, th2=th2, side=side, \
                                             zoffset=zoffset, origin=origin, lc=lc )
        #   -- [2-1] acute angle ver.               --  #
        if ( acute ):
            pts["corner1"] = arc1["pts"]["P1"]
            pts["corner2"] = arc1["pts"]["P2"]
            pts["corner3"] = arc2["pts"]["P1"]
            pts["corner4"] = arc2["pts"]["P2"]
            line["arc12"]  = arc1["line"]["arc1"]
            line["arc34"]  = arc2["line"]["arc1"]
            line["end24"]  = gmsh.model.occ.addLine( pts["corner2"][tag_], pts["corner4"][tag_] )
            line["end31"]  = gmsh.model.occ.addLine( pts["corner3"][tag_], pts["corner1"][tag_] )
            LineLoop       = [ line["arc12"], line["end24"], - line["arc34"], line["end31"] ]

        #   -- [2-2] obtuse angle ver.              --  #
        if ( obtuse ):
            pts["corner1"]  = arc1["pts"]["P1"]
            pts["corner2"]  = arc1["pts"]["P2"]
            pts["corner3"]  = arc2["pts"]["P1"]
            pts["corner4"]  = arc2["pts"]["P2"]
            line["arc12_1"] = arc1["line"]["arc1"]
            line["arc12_2"] = arc1["line"]["arc2"]
            line["arc34_1"] = arc2["line"]["arc1"]
            line["arc34_2"] = arc2["line"]["arc2"]
            line["end24"]  = gmsh.model.occ.addLine( pts["corner2"][tag_], pts["corner4"][tag_] )
            line["end31"]  = gmsh.model.occ.addLine( pts["corner3"][tag_], pts["corner1"][tag_] )
            LineLoop       = [ + line["arc12_1"], + line["arc12_2"], + line["end24"], \
                               - line["arc34_2"], - line["arc34_1"], + line["end31"] ]

    # ------------------------------------------------- #
    # --- [3] Modeling (2)  r1=0,  r2 >0  fan ver.  --- #
    # ------------------------------------------------- #

    if ( ( r1 == 0.0 ) & ( r2 > 0.0 ) ):
        arc2    = arc.generate__sectorShape( radius=r2, th1=th1, th2=th2, side=side, \
                                             zoffset=zoffset, origin=origin, lc=lc )

        #   -- [3-1] acute  angle ver.              --  #
        if ( acute ):
            pts["origin"]   = arc2["pts"]["OP"]
            pts["corner1"]  = arc2["pts"]["P1"]
            pts["corner2"]  = arc2["pts"]["P2"]
            line["arc12"]   = arc2["line"]["arc1"]
            line["end01"]   = gmsh.model.occ.addLine( pts["origin"][tag_], pts["corner1"][tag_] )
            line["end20"]   = gmsh.model.occ.addLine( pts["corner2"][tag_], pts["origin"][tag_] )
            LineLoop        = [ line["end01"], line["arc12"], line["end20"] ]

        #   -- [3-2] obtuse angle ver.              --  #
        if ( obtuse ):
            pts["origin"]   = arc2["pts"]["OP"]
            pts["corner1"]  = arc2["pts"]["P1"]
            pts["corner2"]  = arc2["pts"]["P2"]
            line["arc12_1"] = arc2["line"]["arc1"]
            line["arc12_2"] = arc2["line"]["arc2"]
            line["end01"]   = gmsh.model.occ.addLine( pts["origin"][tag_], pts["corner1"][tag_] )
            line["end20"]   = gmsh.model.occ.addLine( pts["corner2"][tag_], pts["origin"][tag_] )
            LineLoop        = [ line["end01"], line["arc12_1"], line["arc12_2"], line["end20"] ]

    # ------------------------------------------------- #
    # --- [4] define surface / volume               --- #
    # ------------------------------------------------- #
    if ( defineSurf ):
        LineLoopGroup  = gmsh.model.occ.addCurveLoop( LineLoop )
        surf["fan"]    = gmsh.model.occ.addPlaneSurface( [LineLoopGroup] )
    if ( defineVolu ):
        ret            = gmsh.model.occ.extrude( [ (2,surf["fan"])], 0.0, 0.0, height )
        volu["fan"]    = ret[1][1]
        
    # ------------------------------------------------- #
    # --- [5] return                                --- #
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

    r1      = 0.00
    r2      = 0.70
    th1     = -90.0
    th2     = +90.0
    zoffset = 0.0
    origin  = [ 0.0, 0.0 ]
    lc      = 0.05

    generate__fanShape( r1=r1, th1=th1, r2=r2, th2=th2, zoffset=zoffset, \
                        origin=origin, lc=lc, defineVolu=True )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(2)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

