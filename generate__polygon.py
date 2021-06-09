import sys
import numpy         as np
# import gmsh_api.gmsh as gmsh
import gmsh

# ========================================================= #
# ===  generate polygon                                 === #
# ========================================================= #
def generate__polygon( lc=0.0, vertex=None, key="poly", \
                       extrude_delta=None, defineVolu=False ):
    # ------------------------------------------------- #
    # --- [0] Arguments                             --- #
    # ------------------------------------------------- #
    if ( vertex is None ):
        sys.exit( "[generate__polygon] vertex == ???" )
    if ( defineVolu ):
        if ( extrude_delta is None ):
            sys.exit( "[generate__polygon] defineVolu=True, but, extrude_delta is None" )
    if ( type( vertex ) is not np.ndarray ):
        vertex = np.array( vertex )
    if ( vertex.shape[1] == 3 ):
        vertex_ = np.copy( vertex )
        vertex  = np.zeros( (vertex_.shape[0],5) )
        vertex[:,0:3] = np.copy( vertex_ )
        vertex[:,  3] = lc
        vertex[:,  4] = 0
        
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
    ptkeys       = []
    for ik, vert in enumerate( vertex ):
        key            = "{0}_{1:04}".format( key, ik )
        pts[key]       = [ vert[0], vert[1], vert[2], vert[3], vert[4] ]
        pts[key][tag_] = gmsh.model.occ.addPoint( pts[key][x_], pts[key][y_], pts[key][z_], \
                                                  meshSize=pts[key][lc_] )
        ptkeys.append( key )
        
    #  -- [2-2] generate lines                      --  #
    lineLoop = []
    keys_1   = np.roll( np.array( ptkeys ),  0 )
    keys_2   = np.roll( np.array( ptkeys ), -1 )
    for ik in range( keys_1.shape[0] ):
        linekey        = "line_{0}".format( ik )
        line[linekey]  = gmsh.model.occ.addLine( pts[keys_1[ik]][tag_], pts[keys_2[ik]][tag_] )
        lineLoop.append( line[linekey] )
        
    #  -- [2-3] generate surfaces                   --  #
    lineGroup          = gmsh.model.occ.addCurveLoop( lineLoop )
    surf["polygon"]    = gmsh.model.occ.addPlaneSurface( [ lineGroup ] )
    #  -- [2-4] generate volume                     --  #
    if ( defineVolu ):
        ret            = gmsh.model.occ.extrude( [ (surfPhys,surf["polygon"]) ], extrude_delta[0], \
                                                 extrude_delta[1], extrude_delta[2] )
        volu["polygon"]   = ret[1][1]
    
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
    x2    =  [0.4,0.0,0.0]
    x3    =  [0.6,0.5,0.0]
    x4    =  [0.0,0.8,0.0]
    delta =  [0.0,0.0,1.0]
    vertex = np.array( [ x1, x2, x3, x4 ] )
    print( vertex.shape )
    generate__polygon( lc=lc, vertex=vertex, \
                       defineVolu=True, extrude_delta=delta )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "example.geo_unrolled" )
    gmsh.write( "example.msh" )
    gmsh.finalize()

