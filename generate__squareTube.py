import sys, gmsh
import numpy as np


# ========================================================= #
# ===  generate quad shape                              === #
# ========================================================= #
def generate__squareTube( xi1=None, xi2=None, xi3=None, xi4=None, \
                          xo1=None, xo2=None, xo3=None, xo4=None, \
                          lc=0.1  , extrude_delta=None, defineVolu=False ):
    # ------------------------------------------------- #
    # --- [0] Arguments                             --- #
    # ------------------------------------------------- #
    if ( xi1 is None ): sys.exit( "[generate__squareTube] xi1 == ???" )
    if ( xi2 is None ): sys.exit( "[generate__squareTube] xi2 == ???" )
    if ( xi3 is None ): sys.exit( "[generate__squareTube] xi3 == ???" )
    if ( xi4 is None ): sys.exit( "[generate__squareTube] xi4 == ???" )
    if ( xo1 is None ): sys.exit( "[generate__squareTube] xo1 == ???" )
    if ( xo2 is None ): sys.exit( "[generate__squareTube] xo2 == ???" )
    if ( xo3 is None ): sys.exit( "[generate__squareTube] xo3 == ???" )
    if ( xo4 is None ): sys.exit( "[generate__squareTube] xo4 == ???" )
    if ( defineVolu ):
        if ( extrude_delta is None ):
            sys.exit( "[generate__squareTube] defineVolu=True, but, extrude_delta is None" )

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
    pts["xi1"] = [ xi1[0], xi1[1], xi1[2], lc, 0 ]
    pts["xi2"] = [ xi2[0], xi2[1], xi2[2], lc, 0 ]
    pts["xi3"] = [ xi3[0], xi3[1], xi3[2], lc, 0 ]
    pts["xi4"] = [ xi4[0], xi4[1], xi4[2], lc, 0 ]
    pts["xo1"] = [ xo1[0], xo1[1], xo1[2], lc, 0 ]
    pts["xo2"] = [ xo2[0], xo2[1], xo2[2], lc, 0 ]
    pts["xo3"] = [ xo3[0], xo3[1], xo3[2], lc, 0 ]
    pts["xo4"] = [ xo4[0], xo4[1], xo4[2], lc, 0 ]
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

