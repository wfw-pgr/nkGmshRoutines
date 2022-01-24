import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  generate__hollowPipe                             === #
# ========================================================= #
def generate__hollowPipe( lc=0.0, r1=None, r2=None, Opt=None, axis=None ):

    x_, y_, z_ = 0, 1, 2
    surfDim    = 2
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #
    if ( r1   is None ): r1   = 0.0
    if ( r2   is None ): sys.exit( "[generate__hollowPipe.py] r2   == ???" )
    if ( Opt  is None ): Opt  = [ 0.0, 0.0, 0.0 ]
    if ( axis is None ): axis = [ 0.0, 0.0, 1.0 ]
    if ( r1 > r2 ):
        sys.exit( "[generate__hollowPipe.py] r1 > r2. [ERROR]" )
    
    # ------------------------------------------------- #
    # --- [2] add circle                            --- #
    # ------------------------------------------------- #
    if ( r1 > 0.0 ):
        disk1     = gmsh.model.occ.addDisk( Opt[x_], Opt[y_], Opt[z_], r1, r1 )
        disk2     = gmsh.model.occ.addDisk( Opt[x_], Opt[y_], Opt[z_], r2, r2 )
        sfc, fmap = gmsh.model.occ.cut( [(surfDim,disk2)], [(surfDim,disk1)] )
    else:
        sfc       = gmsh.model.occ.addDisk( Opt[x_], Opt[y_], Opt[z_], r2, r2 )
        sfc       = [(surfDim,sfc)]
    
    # ------------------------------------------------- #
    # --- [3] add volume                            --- #
    # ------------------------------------------------- #
    vol = gmsh.model.occ.extrude( sfc, axis[x_], axis[y_], axis[z_] )
    vol = [ vol[1] ]
    print( vol )
    return( vol )


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

    generate__hollowPipe( r1=0.5, r2=1.0 )
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()


    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    
    # meshFile = "dat/mesh.conf"
    # physFile = "dat/phys.conf"
    # import nkGmshRoutines.assign__meshsize as ams
    # meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile )
    
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    

