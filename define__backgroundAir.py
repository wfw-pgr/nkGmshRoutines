import numpy as np
import os, sys
import gmsh

# ----------------------------------------------------------- #
# -- [usage] ::
#  * key: name to register in the dimtags.
# --
#  * geometry_type: [cube]
#  * params :: { xyz0: [0,0,0], xyz1:[1,1,1] etc. }
# --
# ----------------------------------------------------------- #

# ========================================================= #
# ===  define__backgroundAir                            === #
# ========================================================= #

def define__backgroundAir( dimtags={}, key=None, itarget=None, target=None, \
                           geometry_type=None, params=None ):

    # ------------------------------------------------- #
    # --- [1] preparation                           --- #
    # ------------------------------------------------- #
    if ( geometry_type is None ): sys.exit( "[define__backgroundAir.py] geometry_type == ???" )
    if ( params        is None ): sys.exit( "[define__backgroundAir.py] params        == ???" )
    if ( itarget is None ):
        if ( target is None ):
            if ( len(dimtags) > 0 ):
                itarget = max( [ dt[0] for key in dimtags.keys() for dt in dimtags[key] ] )
            else:
                print( "[define__backgroundAir.py] specify itarget / target,.... " )
                print( "[define__backgroundAir.py] e.g.)  itarget=3, target=volume, etc. " )
                sys.exit()
        else:
            itarget  = [ "point", "line", "surface", "volume" ].index( target )
    if ( key is None ):
        if ( "bg_air" in dimtags ):
            print( "[define__backgroundAir.py] bg_air already exist, and key is not specified.... [ERROR] " )
            sys.exit()
        else:
            key = "bg_air"
    entities = gmsh.model.getEntities( itarget )
    if ( len( entities ) > 0 ):
        pass
    else:
        print( "[define__backgroundAir.py] entities is empty.... [ERROR] " )
        sys.exit()
    
    # ------------------------------------------------- #
    # --- [2] define Air region                     --- #
    # ------------------------------------------------- #
    if ( geometry_type in ["cube"] ):
        if ( params is None ):
            print( "[define__backgroundAir.py] params = { xyz0:, xyz1: } must be given. [ERROR]")
            sys.exit()
        table   = { "bg_air": { "geometry_type":"nkCube", \
                                "xyz0":params["xyz0"], "xyz1":params["xyz1"] } }
    else:
        print( "[define__backgroundAir.py] geometry_type == ??? [{}] ".format( geometry_type ) )
        
    import nkGmshRoutines.geometrize__fromTable as gft
    bg_air = gft.geometrize__fromTable( table=table )

    # ------------------------------------------------- #
    # --- [3] boolean                               --- #
    # ------------------------------------------------- #
    ret,fmp      = gmsh.model.occ.cut( bg_air["bg_air"], entities, \
                                       removeObject=True, removeTool=False )
    dimtags[key] = ret
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()
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
    dimtags       = {}
    dimtags       = { "dummy":[(3,1),(3,2)] }
    import nkGmshRoutines.import__stepFile as isf
    stpFile       = "msh/sample.stp"
    dimtags       = isf.import__stepFile( inpFile=stpFile )
    params  = { "xyz0":[-2,-2,-2], "xyz1":[+2,+2,+2],  }
    dimtags = define__backgroundAir( dimtags=dimtags, \
                                     geometry_type="cube", params=params )
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = False         # from nkGMshRoutines/test/mesh.conf, phys.conf
    uniform_size     = 0.2
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
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()

