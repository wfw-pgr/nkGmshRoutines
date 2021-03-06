import sys
import numpy         as np
import gmsh_api.gmsh as gmsh


# ========================================================= #
# ===  generate quad shape                              === #
# ========================================================= #
def generate__squareTube( Li1=None, Li2=None, Lo1=None, Lo2=None, height=None, origin=None, \
                          lc =0.1 , extrude_delta=None, defineVolu=False ):
    # ------------------------------------------------- #
    # --- [0] Arguments                             --- #
    # ------------------------------------------------- #
    if ( Li1    is None ): sys.exit( "[generate__squareTube] Li1    == ???" )
    if ( Li2    is None ): sys.exit( "[generate__squareTube] Li2    == ???" )
    if ( Lo1    is None ): sys.exit( "[generate__squareTube] Lo1    == ???" )
    if ( Lo2    is None ): sys.exit( "[generate__squareTube] Lo2    == ???" )
    if ( origin is None ): sys.exit( "[generate__squareTube] origin == ???" )
    if ( defineVolu ):
        if ( extrude_delta is None ):
            sys.exit( "[generate__squareTube] defineVolu=True, but, extrude_delta is None" )

    w1 = ( Lo1 - Li1 ) * 0.5
    w2 = ( Lo2 - Li2 ) * 0.5
    
    # ------------------------------------------------- #
    # --- [1] Preparation                           --- #
    # ------------------------------------------------- #
    ptsPhys, linePhys, surfPhys, voluPhys = 0,  1,  2,  3
    pts    , line    , surf    , volu     = {}, {}, {}, {}
    x_,y_,z_,lc_,tag_                     = 0, 1, 2, 3, 4
        
    # ------------------------------------------------- #
    # --- [2] generate Arc / End Lines              --- #
    # ------------------------------------------------- #
    #  -- [2-1] generate points                     --  #

    pts["vL_1"] = [ origin[0]    , origin[1]    , origin[2], lc, 0 ]
    pts["vL_2"] = [ origin[0]+w1 , origin[1]    , origin[2], lc, 0 ]
    pts["vL_3"] = [ origin[0]+w1 , origin[1]+Li2, origin[2], lc, 0 ]
    pts["vL_4"] = [ origin[0]    , origin[1]+Li2, origin[2], lc, 0 ]
    
    pts["vB_1"] = [ origin[0]+w1    , origin[1]    , origin[2], lc, 0 ]
    pts["vB_2"] = [ origin[0]+w1+Li1, origin[1]    , origin[2], lc, 0 ]
    pts["vB_3"] = [ origin[0]+w1+Li1, origin[1]+Li2, origin[2], lc, 0 ]
    pts["vB_4"] = [ origin[0]+w1    , origin[1]+Li2, origin[2], lc, 0 ]
    for ik in [ i+1 for i in range(4) ]:
        key1, key2     = "xi{0}".format(ik), "xo{0}".format(ik)
        pts[key1][tag_] = gmsh.model.occ.addPoint( pts[key1][x_], pts[key1][y_], pts[key1][z_], \
                                                   meshSize=pts[key1][lc_] )
        pts[key2][tag_] = gmsh.model.occ.addPoint( pts[key2][x_], pts[key2][y_], pts[key2][z_], \
                                                   meshSize=pts[key2][lc_] )
    #  -- [2-2] generate lines                      --  #
    lineLoops = []
    for keybody in [ "xi{0}", "xo{0}" ]:
        lineLoop = []
        for ik1,ik2 in [ (1,2), (2,3), (3,4), (4,1) ]:
            ptkey1, ptkey2 = keybody.format(ik1), keybody.format(ik2)
            linekey        = "line_{0}_{1}".format(ik1,ik2)
            line[linekey]  = gmsh.model.occ.addLine( pts[ptkey1][tag_], pts[ptkey2][tag_] )
            lineLoop.append( line[linekey] )
        lineLoops.append( lineLoop )
        
    #  -- [2-3] generate surfaces                   --  #
    lineGroup1         = gmsh.model.occ.addCurveLoop( lineLoops[0] )
    lineGroup2         = gmsh.model.occ.addCurveLoop( lineLoops[1] )
    surf["tube"]       = gmsh.model.occ.addPlaneSurface( [ lineGroup1, lineGroup2 ] )
    #  -- [2-4] generate volume                     --  #
    ret                = gmsh.model.occ.extrude( [ (surfPhys,surf["tube"]) ], extrude_delta[0], \
                                                 extrude_delta[1], extrude_delta[2] )
    volu["tube"]       = ret[1][1]
    
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

    lc     =  0.02
    len_i  =  0.6
    len_o  =  0.8
    hlen_i =  0.5 * len_i
    hlen_o =  0.5 * len_o
    xi1    =  [ -hlen_i, -hlen_i, 0.0 ]
    xi2    =  [ +hlen_i, -hlen_i, 0.0 ]
    xi3    =  [ +hlen_i, +hlen_i, 0.0 ]
    xi4    =  [ -hlen_i, +hlen_i, 0.0 ]
    xo1    =  [ -hlen_o, -hlen_o, 0.0 ]
    xo2    =  [ +hlen_o, -hlen_o, 0.0 ]
    xo3    =  [ +hlen_o, +hlen_o, 0.0 ]
    xo4    =  [ -hlen_o, +hlen_o, 0.0 ]
    delta  =  [     0.0,     0.0, 1.0 ]
    
    generate__squareTube( xi1=xi1, xi2=xi2, xi3=xi3, xi4=xi4,
                          xo1=xo1, xo2=xo2, xo3=xo3, xo4=xo4,
                          lc=lc  , defineVolu=True, extrude_delta=delta )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

