import numpy as np
import os, sys
import gmsh


# ========================================================= #
# ===  generate__tetrahedron.py                         === #
# ========================================================= #

def generate__tetrahedron( vertex=None, defineSurf=True, defineVolu=True ):


    x_,y_,z_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( vertex       is None ):
        sys.exit( "[generate__tetrahedron] vertex == ???" )
    if ( type(vertex) is list ):
        vertex = np.array( vertex )
    if ( vertex.shape != (4,3) ):
        print( "[generate__tetrahedron] vertex irregular shape...  :: {0}".format( vertex.shape ) )
        sys.exit()

        
    # ------------------------------------------------- #
    # --- [2] add points                            --- #
    # ------------------------------------------------- #
    pts = {}
    for ip,vert in enumerate( vertex ):
        pkey      = "pt_{0}".format( ip+1 )
        pts[pkey] = gmsh.model.occ.addPoint( vert[x_], vert[y_], vert[z_] )

        
    # ------------------------------------------------- #
    # --- [3] add line                              --- #
    # ------------------------------------------------- #
    lines      = {}
    connection = [ (1,2), (1,3), (1,4), (2,3), (2,4), (3,4) ]
    for il,conn in enumerate( connection ):
        pkey1,pkey2 = "pt_{0}".format( conn[0] ), "pt_{0}".format( conn[1] )
        lkey        = "line_{0}-{1}".format( conn[0],conn[1] )
        lines[lkey] = gmsh.model.occ.addLine( pts[pkey1], pts[pkey2] )

        
    # ------------------------------------------------- #
    # --- [4] add surface                           --- #
    # ------------------------------------------------- #
    if ( defineSurf ):
        surfs       = {}
        edge_connec = [ (2,3,4), (1,3,4), (1,2,4), (1,2,3) ]
        for iS,conn in enumerate( edge_connec ):
            skey         = "surf_{0}".format( iS )
            lkey1        = "line_{0}-{1}".format( conn[1], conn[2] )
            lkey2        = "line_{0}-{1}".format( conn[0], conn[2] )
            lkey3        = "line_{0}-{1}".format( conn[0], conn[1] )
            curveLoop    = [ lines[lkey1], lines[lkey2], lines[lkey3] ]
            curveLoop    = gmsh.model.occ.addCurveLoop( curveLoop )
            surfs[skey]  = gmsh.model.occ.addPlaneSurface( [curveLoop] )

            
    # ------------------------------------------------- #
    # --- [5] add volume                            --- #
    # ------------------------------------------------- #
    if ( defineVolu ):
        skeys    = [ "surf_{0}".format( iS ) for iS in range( len( edge_connec ) ) ]
        surftags = [ surfs[key] for key in skeys ]
        surfloop = gmsh.model.occ.addSurfaceLoop( surftags )
        ret      = gmsh.model.occ.addVolume( [surfloop] )
    else:
        ret      = None
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

    vertex = [ [0,0,0], [1,0,0], [0,1,0], [0,0,1] ]
    generate__tetrahedron( vertex=vertex )
    
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
    # gmsh.write( "msh/model.msh" )
    gmsh.write( "msh/model.geo_unrolled" )
    gmsh.finalize()
    

