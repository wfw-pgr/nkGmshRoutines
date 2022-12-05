import numpy as np
import os, sys
import gmsh

# ========================================================= #
# ===  make__geometry                                   === #
# ========================================================= #

def make__geometry( dimtags={} ):

    table   = { "cube01": { "geometry_type":"cube", "centering":False, \
                            "xc":0.0, "yc":0.0, "zc":0.0, "dx":1.0, "dy":1.0, "dz":1.0 }, \
                "cube02": { "geometry_type":"cube", "centering":False, \
                            "xc":0.5, "yc":0.5, "zc":0.5, "dx":1.0, "dy":1.0, "dz":1.0 }, \
                "cube03": { "boolean_type" :"fuse", \
                            "targetKeys"   :["cube01"], "toolKeys"  :["cube02"], \
                            "removeObject" : True     , "removeTool":True }, \
    }
    import nkGmshRoutines.geometrize__fromTable as gft
    dimtags = gft.geometrize__fromTable( table=table, dimtags=dimtags )
    table   = { "cube04": { "boolean_type":"copy", "targetKeys":["cube03"] }, \
                "cube05": { "boolean_type":"mirror", \
                            "targetKeys":["cube03"], "plane":"x-y", "rename":True }, \
    }
    dimtags = gft.geometrize__fromTable( table=table, dimtags=dimtags )
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
    sample__model = "make"     #  -- [ "import" / "make" ] --  #

    if   ( sample__model == "import" ):
        dimtagsFile = None
        stpFile     = "msh/model.stp"
        import nkGmshRoutines.import__stepFile as isf
        dimtags     = isf.import__stepFile( inpFile=stpFile, dimtagsFile=dimtagsFile )
        
    elif ( sample__model == "make"   ):
        dimtags = {}
        dimtags = make__geometry( dimtags=dimtags )
        gmsh.model.occ.synchronize()
    
    gmsh.model.occ.synchronize()
    gmsh.model.occ.removeAllDuplicates()
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] Mesh settings                         --- #
    # ------------------------------------------------- #
    mesh_from_config = True         # from nkGMshRoutines/test/mesh.conf, phys.conf
    if ( mesh_from_config ):
        meshFile = "test/mesh.conf"
        physFile = "test/phys.conf"
        logFile  = "test/sample.log"
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( meshFile=meshFile, physFile=physFile, \
                                       logFile=logFile, dimtags=dimtags )
    else:
        import nkGmshRoutines.assign__meshsize as ams
        meshes = ams.assign__meshsize( uniform=0.1, dimtags=dimtags )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()

