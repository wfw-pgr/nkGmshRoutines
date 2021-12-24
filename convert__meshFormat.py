import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  convert__meshFormat                              === #
# ========================================================= #

def convert__meshFormat( inpFile="msh/model.stp", outFile="msh/model.stl", \
                         logFile="dat/entities.log", delete_entities=[] ):
    
    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "model" )
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #
    gmsh.model.occ.importShapes( inpFile )
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] delete unnecessaries                  --- #
    # ------------------------------------------------- #
    entities = gmsh.model.getEntities(3)
    with open( logFile, "w" ) as f:
        f.write( "[before]\n" )
        for ent in entities:
            f.write( "{0[0]} :: {0[1]}\n".format( ent ) )
        

    if ( len( delete_entities ) > 0 ):
        dimtags  = [ (3,ent) for ent in delete_entities ]
        gmsh.model.occ.remove( dimtags, recursive=True )
        gmsh.model.occ.synchronize()
        entities = gmsh.model.getEntities(3)
    
    with open( logFile, "a" ) as f:
        f.write( "[after]\n" )
        for ent in entities:
            f.write( "{0[0]} :: {0[1]}\n".format( ent ) )
    
    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.write( outFile )
    gmsh.finalize()
    

    
# ========================================================= #
# ===  generate__testModel.py                           === #
# ========================================================= #
def generate__testModel( outFile="msh/model.stp" ):

    # ------------------------------------------------- #
    # --- [1] initialization of the gmsh            --- #
    # ------------------------------------------------- #
    gmsh.initialize()
    gmsh.option.setNumber( "General.Terminal", 1 )
    gmsh.model.add( "model" )
    
    
    # ------------------------------------------------- #
    # --- [2] Modeling                              --- #
    # ------------------------------------------------- #

    gmsh.model.occ.addBox( -0.5, -0.5, -0.5, \
		           +1.0, +1.0, +1.0 )
    gmsh.model.occ.addBox( +0.0,  0.0,  0.0, \
		           +1.0, +1.0, +1.0 )
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()


    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    
    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.write( outFile )
    gmsh.finalize()
    
    
# ========================================================= #
# ===   Execution of Pragram                            === #
# ========================================================= #

if ( __name__=="__main__" ):

    delete_entities = [1]
    inpFile = "test/model.stp"
    outFile = "test/model.stl"
    logFile = "test/entities.log"
    
    generate__testModel( outFile=inpFile )
    convert__meshFormat( inpFile=inpFile, outFile=outFile, logFile=logFile, \
                         delete_entities=delete_entities )
