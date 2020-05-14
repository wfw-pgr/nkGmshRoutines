import sys
import numpy         as np
import gmsh_api.gmsh as gmsh

# ========================================================= #
# ===  generate cylinder volume                         === #
# ========================================================= #
def generate__cylinder( lc=0.01, xc=None, radius=None, \
                        extrude_delta=None, defineVolu=False ):
    # ------------------------------------------------- #
    # --- [0] Arguments                             --- #
    # ------------------------------------------------- #
    if ( xc is None ): sys.exit( "[generate__cylinder] x1 == ???" )
    if ( defineVolu ):
        if ( extrude_delta is None ):
            sys.exit( "[generate__cylinder] defineVolu=True, but, extrude_delta is None" )

    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    ptsDim , lineDim , surfDim , voluDim  = 0, 1, 2, 3
    ptsPhys, linePhys, surfPhys, voluPhys = 0, 1, 2, 3
    x_,y_,z_,lc_,tag_                     = 0, 1, 2, 3, 4
    pts    , line    , surf    , volu     = {}, {}, {}, {}
    
    # ------------------------------------------------- #
    # --- [2] generate Arc / End Lines              --- #
    # ------------------------------------------------- #
    #  -- [2-1] generate points                     --  #
    pts["xc"]          = [ xc[0]       , xc[1]       , xc[2], lc, 0 ]
    pts["xc"][tag_]    = gmsh.model.occ.addPoint ( pts["xc"][x_]  , pts["xc"][y_], \
                                                   pts["xc"][z_]  , meshSize=pts["xc"][lc_] )
    pts["ref1"]        = [ xc[0]-radius, xc[1]       , xc[2], lc, 0 ]
    pts["ref2"]        = [ xc[0]+radius, xc[1]       , xc[2], lc, 0 ]
    pts["ref3"]        = [ xc[0]       , xc[1]-radius, xc[2], lc, 0 ]
    pts["ref4"]        = [ xc[0]       , xc[1]+radius, xc[2], lc, 0 ]

    for ik in range(4):
        key            = "ref{0}".format( ik+1 )
        pts[key][tag_] = gmsh.model.occ.addPoint( pts[key][x_], pts[key][y_], \
                                                  pts[key][z_], meshSize=pts[key][lc_] )
    #  -- [2-2] generate lines                      --  #
    line["circle"]   = gmsh.model.occ.addCircle( pts["xc"][x_], pts["xc"][y_], pts["xc"][z_], \
                                                 radius )
    #  -- [2-3] generate surfaces                   --  #
    lineGroup        = gmsh.model.occ.addCurveLoop( [ line["circle"] ] )
    surf["circle"]   = gmsh.model.occ.addPlaneSurface( [ lineGroup ] )
    gmsh.model.occ.synchronize()
    tags = [ pts["ref1"][tag_], pts["ref2"][tag_], \
             pts["ref3"][tag_], pts["ref4"][tag_]  ]
    gmsh.model.mesh.embed( ptsDim, tags, surfDim, surf["circle"] )
    
    #  -- [2-4] generate volume                     --  #
    if ( defineVolu ):
        ret = gmsh.model.occ.extrude( [ (surfPhys,surf["circle"]) ], extrude_delta[0], \
                                      extrude_delta[1], extrude_delta[2] )
        volu["cylinder"] = ret[1][1]
        
    # ------------------------------------------------- #
    # --- [4] PostProcess                           --- #
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

    lc     =  0.10
    xc     =  [0.0,0.0,0.0]
    radius =  1.0
    delta  =  [0.0,0.0,1.0]
    generate__cylinder( lc=lc, xc=xc, radius=radius, \
                        defineVolu=True, extrude_delta=delta )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

