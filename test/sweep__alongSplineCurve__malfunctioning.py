import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__geometry                                   === #
# ========================================================= #

def make__geometry( dimtags={} ):

    pt1 = gmsh.model.occ.addPoint( 0, 0, 0 )
    pt2 = gmsh.model.occ.addPoint( 0, 0, 1 )
    pt3 = gmsh.model.occ.addPoint( 1, 0, 2 )
    pt4 = gmsh.model.occ.addPoint( 2, 0, 2 )
    spl = gmsh.model.occ.addSpline( [pt1,pt2,pt3,pt4] )

    cir = gmsh.model.occ.addRectangle( 0,0,0, 0.1,0.1 )
    cir = [(2,cir)]

    ret = gmsh.model.occ.addPipe( cir, spl, trihedron="DiscreteTrihedron" )
    print( ret )
    
    return( dimtags )


# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.option.setNumber( "Mesh.Algorithm"  , 5 )
    gmsh.option.setNumber( "Mesh.Algorithm3D", 4 )
    gmsh.option.setNumber( "Mesh.SubdivisionAlgorithm", 0 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    dimtags = {}
    dimtags = make__geometry( dimtags=dimtags )
    gmsh.model.occ.synchronize()
    
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()
    gmsh.write( "spline_test.geo_unrolled" )

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = False         # from nkGMshRoutines/test/mesh.conf, phys.conf
    uniform_size     = 0.10
    if ( mesh_from_config ):
        meshFile = "dat/mesh.conf"
        physFile = "dat/phys.conf"
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile, dimtags=dimtags )
    else:
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( uniform=uniform_size, dimtags=dimtags )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "spline_test.msh" )
    gmsh.finalize()

