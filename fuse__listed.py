import numpy as np
import os, sys
import gmsh


# ========================================================= #
# ===  fuse__listed                                     === #
# ========================================================= #    

def fuse__listed( inpFile="dat/fuse.conf", dim=3 ):

    # ------------------------------------------------- #
    # --- [1] load config file                      --- #
    # ------------------------------------------------- #
    conf     = load__entityList( inpFile=inpFile )
    keys     = conf["keys"]
    fuseNums = conf["fuseNums"]
    entities = conf["entities"]

    # ------------------------------------------------- #
    # --- [2] fuse entities                         --- #
    # ------------------------------------------------- #
    for key in keys:
        ent = entities[key]
        tag = fuseNums[key]
        if   ( len(ent) == 1 ):
            target = [ (dim,ent[0]) ]
            tools  = [ (dim,ent[0]) ]
        elif ( len(ent)  > 1 ):
            target = [ (dim,ent[0]) ]
            tools  = [ (dim,entity) for entity in ent[1:] ]
        gmsh.model.occ.fuse( target, tools, tag=tag )
    return()


# ========================================================= #
# === load entity list                                  === #
# ========================================================= #

def load__entityList( inpFile=None ):
    
    if ( inpFile is None ): sys.exit( "[load__entityList] inpFile == ???" )

    with open( inpFile, "r" ) as f:
        lines  = f.readlines()
        
    
    keys     = []
    fuseNums = {}
    entities = {}
    for line in lines:
        if ( len( line.strip() ) == 0 ):
            continue
        if ( ( line.strip() )[0] == "#" ):
            continue

        contents = ( line.strip() ).split()
        vkey     =      contents[0]
        vtype    =      contents[1]
        fuseNum  = int( contents[2] )
        ents     = ( ( contents[3].strip( "[" ) ).strip( "]" ) ).split(",")
        ents     = [ int(ent) for ent in ents ]

        keys.append( vkey )
        fuseNums[vkey]  = fuseNum
        entities[vkey]  = ents

    dicts = { "keys":keys, "fuseNums":fuseNums, "entities":entities }
        
    return( dicts )




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
    gmsh.model.occ.addBox( -0.5, -0.5, -0.5, \
		           +1.0, +1.0, +1.0 )
    gmsh.model.occ.addBox( +0.0,  0.0,  0.0, \
		           +1.0, +1.0, +1.0 )
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    fuse__listed()
    
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
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    
    

    
