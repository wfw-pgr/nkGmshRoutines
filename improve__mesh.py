import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  improve__mesh                                    === #
# ========================================================= #

def improve__mesh():

    # ------------------------------------------------- #
    # --- [0] Arguments                             --- #
    # ------------------------------------------------- #
    import nkUtilities.genArgs as gar
    args      = gar.genArgs()
    mode      = args["mode"]
    inpFile   = args["file"]
    threshold = args["float"]

    if ( mode      is None ):
        print( "[improve__mesh.py]   mode  == ???   :: " )
        print( "[improve__mesh.py]  specify --mode ( relocate, netgen, laplace, all ) " )
        sys.exit()
    if ( inpFile   is None ):
        print( "[improve__mesh.py] file == ???   :: " )
        print( "[improve__mesh.py]  specify --file xxx.msh / xxx.bdf " )
        sys.exit()
    if ( threshold is None ):
        threshold = 0.6
        print( "[improve__mesh.py] threshold is set as 0.6, or specify --float 0.8 etc." )
    
    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal"      ,         1 )
    gmsh.option.setNumber( "Mesh.OptimizeThreshold", threshold )
    gmsh.model.add( "model" )

    # ------------------------------------------------- #
    # --- [2] Merge Model                           --- #
    # ------------------------------------------------- #
    gmsh.merge( inpFile )

    # ------------------------------------------------- #
    # --- [3] optimize                              --- #
    # ------------------------------------------------- #
    if ( mode.lower() in ["laplace" ,"all"] ):
        gmsh.model.mesh.optimize( "Laplace2D"  )
    if ( mode.lower() in ["relocate","all"] ):
        gmsh.model.mesh.optimize( "Relocate3D" )
    if ( mode.lower() in ["netgen"  ,"all"] ):
        gmsh.model.mesh.optimize( "Netgen" )

    # ------------------------------------------------- #
    # --- [4] save                                  --- #
    # ------------------------------------------------- #
    if   ( ".bdf" in inpFile ):
        outFile = inpFile.replace( ".bdf", "_opt.bdf" )
    elif ( ".msh" in inpFile ):
        outFile = inpFile.replace( ".msh", "_opt.msh" )
    gmsh.write( outFile )
    gmsh.finalize()
    
    return()



# ========================================================= #
# ===   実行部                                          === #
# ========================================================= #

if ( __name__=="__main__" ):

    improve__mesh()

    
