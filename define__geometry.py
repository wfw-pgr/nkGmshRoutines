import numpy as np
import os, sys
import gmsh
import nkGmshRoutines.generate__sector180 as sec


# ========================================================= #
# ===  define__geometry                                 === #
# ========================================================= #
def define__geometry( inpFile="test/geometry.conf", keys=None, names=None, table=None ):

    # ------------------------------------------------- #
    # --- [1] load table                            --- #
    # ------------------------------------------------- #
    if ( table is None ):
        import nkUtilities.load__keyedTable as lkt
        table = lkt.load__keyedTable( inpFile=inpFile )
    if ( keys  is None ):
        keys  = list(   table.keys() )
    if ( names is None ):
        names = list( ( table[keys[0]] ).keys() )
    
    # ------------------------------------------------- #
    # --- [2] make geometry for every key           --- #
    # ------------------------------------------------- #
    dimtags = {}
    for key in keys:
        card = table[key]
        
        # ------------------------------------------------- #
        # --- [2-1] sector shape                        --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "quadring" ):
            height = card["z2"] - card["z1"]
            origin = [ card["xc"], card["yc"] ]
            ret1   = sec.generate__sector180( r1=card["r1"], r2=card["r2"], side="+", \
                                              origin=origin, zoffset=card["z1"], height=height,\
                                              fuse=True, defineVolu=True )
            ret2   = sec.generate__sector180( r1=card["r1"], r2=card["r2"], side="-", \
                                              origin=origin, zoffset=card["z1"], height=height,\
                                              fuse=True, defineVolu=True )
            gmsh.model.occ.synchronize()
            ret,fm = gmsh.model.occ.fuse( ret1[0], ret2[0] )
            gmsh.model.occ.synchronize()
            dimtags[key] = ret
            
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

    ret = define__geometry()
    
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
    

