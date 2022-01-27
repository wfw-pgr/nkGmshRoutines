import sys
import numpy         as np
import gmsh

# ========================================================= #
# ===  generate polygon                                 === #
# ========================================================= #
def generate__polygon( lc=0.0, vertex=None, key="polygon", \
                       extrude_vector=None, returnType="dimtags" ):

    surfDim, voluDim   = 2, 3
    pts,line,surf,volu = {}, {}, {}, {}
    x_,y_,z_,lc_,tag_  = 0, 1, 2, 3, 4

    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( vertex is None ):
        sys.exit( "[generate__polygon] vertex == ???" )
    if ( type( vertex ) is not np.ndarray ):
        if ( type( vertex ) is list ):
            vertex = np.array( vertex )
        else:
            sys.exit( "[generate__polygon.py] type( vertex ) == {0} ???".format(type(vertex)) )
    if   ( vertex.shape[0] <  3 ):
        print( "[generate__polygon.py] number of vertex >= 3. [ERROR]" )
        print( "[generate__polygon.py] vertex.shape[0] == {0}".format( vertex.shape[0] ) )
        sys.exit()
    if   ( vertex.shape[1] == 3 ):
        vertex_ = np.copy( vertex )
        vertex  = np.zeros( (vertex_.shape[0],5) )
        vertex[:,x_:z_+1] = np.copy( vertex_ )
        vertex[:,lc_    ] = lc
        vertex[:,tag_   ] = -1
    elif ( vertex.shape[1] == 4 ):
        pass
    else:
        print( "[generate__polygon.py] dim. of vertex > 4. [ERROR]" )
        sys.exit()
        
    # ------------------------------------------------- #
    # --- [2] generate Arc / End Lines              --- #
    # ------------------------------------------------- #
    #  -- [2-1] generate points                     --  #
    ptkeys       = []
    for ik,vert in enumerate( vertex ):
        key            = "pt{0:04}".format( ik+1 )
        pts[key]       = [ vert[x_], vert[y_], vert[z_], vert[lc_], vert[tag_] ]
        # pts[key][tag_] = gmsh.model.occ.addPoint( vert[x_], vert[y_], vert[z_], \
        #                                           meshSize=vert[lc_] )
        pts[key][tag_] = gmsh.model.occ.addPoint( vert[x_], vert[y_], vert[z_] )
        ptkeys.append( key )
        
    #  -- [2-2] generate lines                      --  #
    lineLoop = []
    keys_1   = np.roll( np.array( ptkeys ),  0 )
    keys_2   = np.roll( np.array( ptkeys ), -1 )
    for ik in range( keys_1.shape[0] ):
        linekey        = "line{0}".format( ik )
        line[linekey]  = gmsh.model.occ.addLine( pts[keys_1[ik]][tag_], pts[keys_2[ik]][tag_] )
        lineLoop.append( line[linekey] )

    #  -- [2-3] generate surfaces                   --  #
    lineGroup          = gmsh.model.occ.addCurveLoop( lineLoop )
    surf["polygon"]    = gmsh.model.occ.addPlaneSurface( [ lineGroup ] )

    #  -- [2-4] generate volume                     --  #
    if ( extrude_vector is not None ):
        ret            = gmsh.model.occ.extrude( [ (surfDim,surf["polygon"]) ], \
                                                 extrude_vector[0], extrude_vector[1], \
                                                 extrude_vector[2] )
        volu["polygon"]   = ret[1][1]
    
    # ------------------------------------------------- #
    # --- [4] PostProcess                           --- #
    # ------------------------------------------------- #
    if   ( returnType.lower() == "dict"    ):
        return( { "pts":pts, "line":line, "surf":surf, "volu":volu } )
    elif ( returnType.lower() == "dimtags" ):
        if ( "polygon" in volu ):
            return( [(voluDim,volu["polygon"])] )
        else:
            return( [(surfDim,surf["polygon"])] )
    else:
        print( "[generate__polygon.py] unknown returnType :: {0}".format( returnType ) )
        

# ======================================== #
# ===  実行部                          === #
# ======================================== #
if ( __name__=="__main__" ):

    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "example" )

    lc    =  0.0
    x1    =  [0.0,0.0,0.0]
    x2    =  [0.4,0.0,0.0]
    x3    =  [0.6,0.5,0.0]
    x4    =  [0.0,0.8,0.0]
    delta =  [0.0,0.0,1.0]
    vertex = np.array( [ x1, x2, x3, x4 ] )
    print( vertex.shape )
    generate__polygon( lc=lc, vertex=vertex, extrude_vector=delta )
    
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/example.geo_unrolled" )
    gmsh.write( "test/example.msh" )
    gmsh.finalize()

