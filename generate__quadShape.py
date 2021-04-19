import sys
import numpy         as np
import gmsh_api.gmsh as gmsh

# ========================================================= #
# ===  generate quad shape                              === #
# ========================================================= #
def generate__quadShape( lc=0.1, x1=None, x2=None, x3=None, x4=None, \
                         extrude_delta=None, defineVolu=False, recombine=False ):
    # ------------------------------------------------- #
    # --- [0] Arguments                             --- #
    # ------------------------------------------------- #
    if ( x1 is None ): sys.exit( "[generate__quadShape] x1 == ???" )
    if ( x2 is None ): sys.exit( "[generate__quadShape] x2 == ???" )
    if ( x3 is None ): sys.exit( "[generate__quadShape] x3 == ???" )
    if ( x4 is None ): sys.exit( "[generate__quadShape] x4 == ???" )
    if ( defineVolu ):
        if ( extrude_delta is None ):
            sys.exit( "[generate__quadShape] defineVolu=True, but, extrude_delta is None" )

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
    pts["x1"] = [ x1[0], x1[1], x1[2], lc, 0 ]
    pts["x2"] = [ x2[0], x2[1], x2[2], lc, 0 ]
    pts["x3"] = [ x3[0], x3[1], x3[2], lc, 0 ]
    pts["x4"] = [ x4[0], x4[1], x4[2], lc, 0 ]
    for ik in [ i+1 for i in range(4) ]:
        key            = "x{0}".format(ik)
        pts[key][tag_] = gmsh.model.occ.addPoint( pts[key][x_], pts[key][y_], pts[key][z_], \
                                                  meshSize=pts[key][lc_] )
    #  -- [2-2] generate lines                      --  #
    lineLoop = []
    for ik1,ik2 in [ (1,2), (2,3), (3,4), (4,1) ]:
        ptkey1, ptkey2 = "x{0}".format(ik1), "x{0}".format(ik2)
        linekey        = "line_{0}_{1}".format(ik1,ik2)
        line[linekey]  = gmsh.model.occ.addLine( pts[ptkey1][tag_], pts[ptkey2][tag_] )
        lineLoop.append( line[linekey] )
        
    #  -- [2-3] generate surfaces                   --  #
    lineGroup          = gmsh.model.occ.addCurveLoop( lineLoop )
    surf["quad"]       = gmsh.model.occ.addPlaneSurface( [ lineGroup ] )
    #  -- [2-4] generate volume                     --  #
    if ( defineVolu ):
        ret            = gmsh.model.occ.extrude( [ (surfPhys,surf["quad"]) ], extrude_delta[0], \
                                                 extrude_delta[1], extrude_delta[2], \
                                                 recombine=recombine )
        volu["quad"]   = ret[1][1]
    
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

    lc    =  0.10
    x1    =  [0.0,0.0,0.0]
    x2    =  [0.6,0.0,0.0]
    x3    =  [0.6,0.6,0.0]
    x4    =  [0.0,0.6,0.0]
    delta =  [0.0,0.0,1.0]
    # generate__quadShape( lc=lc, x1=x1, x2=x2, x3=x3, x4=x4 )
    generate__quadShape( lc=lc, x1=x1, x2=x2, x3=x3, x4=x4, \
                         defineVolu=True, extrude_delta=delta )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

