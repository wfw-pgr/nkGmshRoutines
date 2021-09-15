import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  delete volumes                                   === #
# ========================================================= #

def extract__volumes( stpFile=None, volume_list=None, list__dimtags_detail=True ):

    voluDim = 3
    
    # ------------------------------------------------- #
    # --- [1] Arguments                             --- #
    # ------------------------------------------------- #

    if ( stpFile     is None ): sys.exit( "[delete__volumes] stpFile == ???" )
    if ( volume_list is None ): sys.exit( "[delete__volumes] volume_list == ???" )

    gmsh.model.occ.importShapes( stpFile )
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [2] straight method                       --- #
    # ------------------------------------------------- #
    all_dimtags      = gmsh.model.getEntities( dim=3 )
    used_dimtags     = [ (voluDim,num) for num in volume_list ]
    delete_dimtags   = list( set( all_dimtags ) - set( used_dimtags ) )

    if ( list__dimtags_detail ):
        print()
        print( "all dimtags" )
        print( all_dimtags )
        print()
        print( "used dimtags" )
        print( used_dimtags   )
        print()
        print( "delete dimtags" )
        print( delete_dimtags )
        
    gmsh.model.occ.remove( delete_dimtags, recursive=True )

    return()


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

    volume_list = [2]
    extract__volumes( stpFile="msh/model.stp", volume_list=volume_list  )
    gmsh.model.occ.synchronize()

    if ( len( volume_list ) >= 2 ):
        gmsh.model.occ.removeAllDuplicates()
        gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )
    

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model_.msh" )
    gmsh.finalize()
    



    # # ------------------------------------------------- #
    # # --- [3] failed method                         --- #
    # # ------------------------------------------------- #
    # all_dimtags      = gmsh.model.getEntities()
    # surf_dimtags     = gmsh.model.getBoundary( volu_dimtags, combined=False, \
    #                                            oriented=False, recursive=False )
    # line_dimtags     = gmsh.model.getBoundary( surf_dimtags, combined=False, \
    #                                            oriented=False, recursive=False )
    # point_dimtags    = gmsh.model.getBoundary( line_dimtags, combined=False, \
    #                                            oriented=False, recursive=False )
    # used_dimtags     = volu_dimtags + surf_dimtags + line_dimtags + point_dimtags
    # delete_dimtags   = list( set( all_dimtags ) - set( used_dimtags ) )

