import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  import__stepFile                                 === #
# ========================================================= #
def import__stepFile( inpFile=None, keys=None, dimtags=None, \
                      synchronize=True, removeAllDuplicates=False, dimtagsFile=None ):
    
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
    # --- [3] remove All Duplicates                 --- #
    # ------------------------------------------------- #
    if ( synchronize ):
        gmsh.model.occ.synchronize()
    if ( removeAllDuplicates ):
        gmsh.model.occ.synchronize()
        gmsh.model.occ.removeAllDuplicates()
        
    # ------------------------------------------------- #
    # --- [4] display information                   --- #
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
    # --- [5] entity File exists                    --- #
    # ------------------------------------------------- #
    if ( dimtagsFile is not None ):
        import nkGmshRoutines.load__dimtags as ldt
        former_dimtags = ldt.load__dimtags( inpFile=dimtagsFile )
        import nkGmshRoutines.renumbering__dimtags as rnm
        dimtags        = rnm.renumbering__dimtags( dimtags=former_dimtags )
        nEntity_dimtag = np.sum( np.array( [ len( dimtags[key] ) for key in dimtags.keys() ] ) )
        if ( not( nEntity_dimtag == nEntities ) ):
            print( "\n" + "[import__stepFile.py] incompatible #. of entities in dimtagFile & #. of entities in STEP file....[ERROR] " + "\n" )
            sys.exit()
        return( dimtags )
    
    # ------------------------------------------------- #
    # --- [6] naming                                --- #
    # ------------------------------------------------- #
    if ( keys is None ):
        baseName = ( inpFile.split( "/" ) )[-1] + ".{0}"
        keys     = [ baseName.format( ik+1 ) for ik in range( nEntities ) ]

    # ------------------------------------------------- #
    # --- [7] merge dimtags / return                --- #
    # ------------------------------------------------- #
    if ( dimtags is None ):
        dimtags = { keys[ik]:[ret[ik]] for ik in range( nEntities ) }
        
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
    dimtagsFile = "test/dimtags.json"
    inpFile     = "test/model.stp"
    dimtags     = import__stepFile( inpFile=inpFile, dimtagsFile=dimtagsFile )
    
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
    

