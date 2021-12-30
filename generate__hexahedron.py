import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  generate__hexahedron                             === #
# ========================================================= #

def generate__hexahedron( vertex=None, quad1=None, quad2=None, \
                          defineVolu=True, defineSurf=True, fuse=True ):

    x_,y_,z_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( vertex       is None ):
        if ( ( quad1 is not None ) and ( quad2 is not None ) ):
            vertex = np.concatenate( [quad1,quad2], axis=0 )
        else:
            sys.exit( "[generate__hexahedron] vertex == ???" )
    if ( type(vertex) is list ):
        vertex = np.array( vertex )
    if ( vertex.shape != (8,3) ):
        print( "[generate__hexahedron] vertex irregular shape... :: {0}".format( vertex.shape ) )
        sys.exit()

        
    # ------------------------------------------------- #
    # --- [2] calculate center points               --- #
    # ------------------------------------------------- #
    s_centers = []
    s_connec  = [ [1,2,3,4], [1,2,5,6], [1,3,5,7], [2,4,6,8], [3,4,7,8], [5,6,7,8] ]
    s_connec  = [ [ val-1 for val in arr ] for arr in s_connec ]
    for conn in s_connec:
        vertex_s  = vertex[ conn ]
        s_center  = np.average( vertex_s, axis=0 )
        s_centers.append( s_center )
    s_center  = np.array( s_centers )
    v_center  = np.average( vertex, axis=0 )
    

    # ------------------------------------------------- #
    # --- [3] generate tetrahedron                  --- #
    # ------------------------------------------------- #

    import nkGmshRoutines.generate__tetrahedron as gth
    volu         = {}
    edge_connect = [ [0,1], [1,3], [2,3], [0,2] ]
    for iS,conn in enumerate( s_connec ):
        for ie, edge in enumerate( edge_connect ):
            vkey       = "volu_iS{0}_iL{1}-{2}".format( iS, edge[0], edge[1] )
            iv1,iv2    = conn[ edge[0] ], conn[ edge[1] ]
            vert1      = np.copy(  vertex [iv1,:] )
            vert2      = np.copy(  vertex [iv2,:] )
            vert3      = np.copy( s_center[iS ,:] )
            vert4      = np.copy( v_center        )
            verts      = [vert1[None,:],vert2[None,:],vert3[None,:],vert4[None,:]]
            vert_t     = np.concatenate( verts, axis=0 )
            volu[vkey] = gth.generate__tetrahedron( vertex=vert_t )

    # ------------------------------------------------- #
    # --- [4] fuse volumes                          --- #
    # ------------------------------------------------- #
    if ( fuse ):
        voluDim   = 3
        vkeys     = list( volu.keys() )
        volu_list = [ volu[key] for key in vkeys ]
        dimtags   = [ (voluDim,volu_num) for volu_num in volu_list ]
        target    = [ dimtags[0] ]
        tools     =   dimtags[1:]
        ret       = gmsh.model.occ.fuse( target, tools )
        ret       = ret[0][0][1]
    else:
        ret       = None
    return( ret )

    


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):
    

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 1 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 1 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 1 )
    gmsh.model.add( "model" )
    
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #

    vertex = [ [0,0,0],
               [0,1,0],
               [0,0,1],
               [0,1,2],
               [1,0,0],
               [1,1,0],
               [1,0,1],
               [1,1,1] ]
    
    generate__hexahedron( vertex=vertex )
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()


    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    
    # meshFile = "dat/mesh.conf"
    # import nkGmshRoutines.assign__meshsize as ams
    # meshes = ams.assign__meshsize( meshFile=meshFile )
    
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/example.msh" )
    gmsh.finalize()
    

