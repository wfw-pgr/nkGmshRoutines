import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  import__stepFile                                 === #
# ========================================================= #
def import__stepFile( inpFile=None, keys=None, dimtags=None ):
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( inpFile is None ): sys.exit( "[import__stepFile] inpFile == ???" )

    # ------------------------------------------------- #
    # --- [2] import shapes                         --- #
    # ------------------------------------------------- #
    ret       = gmsh.model.occ.importShapes( inpFile )
    dim       = ret[0][0]
    nEntities = len( ret )
    entities  = [ int(dimtag[1]) for dimtag in ret ]

    # ------------------------------------------------- #
    # --- [3] display information                   --- #
    # ------------------------------------------------- #
    print()
    print( "-"*30 + "   [import__stepFile.py]    " + "-"*30 )
    print()
    print( "[import__stepFile.py] inpFile    == {0}".format( inpFile   ) )
    print( "[import__stepFile.py] dim        == {0}".format( dim       ) )
    print( "[import__stepFile.py] nEntities  == {0}".format( nEntities ) )
    print( "[import__stepFile.py] entities   == {0}".format( entities  ) )
    print()
    print( "-"*88 )
    print()
    
    # ------------------------------------------------- #
    # --- [4] naming                                --- #
    # ------------------------------------------------- #
    if ( keys is None ):
        baseName = ( inpFile.split( "/" ) )[-1] + ".{0}"
        keys     = [ baseName.format( ik+1 ) for ik in range( nEntities ) ]
    dimtags_loc = { keys[ik]:[ret[ik]] for ik in range( nEntities ) }

    # ------------------------------------------------- #
    # --- [5] merge dimtags / return                --- #
    # ------------------------------------------------- #
    if ( dimtags is None ):
        dimtags = dimtags_loc
    else:
        dimtags = { **dimtags, **dimtags_loc }
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
    inpFile = "test/example.stp"
    keys    = [ "lower_smaller", "lower_larger", "cyl_small", "cyl_larger" ]
    dimtags = import__stepFile( inpFile=inpFile, keys=keys )
    print( dimtags )
    
    gmsh.model.occ.synchronize()
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
    gmsh.write( "test/model.msh" )
    gmsh.finalize()
    

