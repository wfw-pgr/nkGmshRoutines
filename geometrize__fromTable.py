import numpy as np
import os, sys
import gmsh

import nkGmshRoutines.define__geometry   as geo
import nkGmshRoutines.boolean__fromTable as bol
import nkGmshRoutines.transform__affine  as tra


# ========================================================= #
# ===  geometrize__fromTable.py                         === #
# ========================================================= #
def geometrize__fromTable( inpFile="test/geometry.conf", dimtags=None, \
                           keys=None, names=None, table=None ):
    
    # ------------------------------------------------- #
    # --- [1] load table                            --- #
    # ------------------------------------------------- #
    if ( dimtags is None ):
        dimtags = {}
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
    
    for key in keys:
        card = table[key]
        print( key )
        print( card )
        print( dimtags )
        
        table_loc = { key:card }
        print( table_loc )
        
        # ------------------------------------------------- #
        # --- [2-1] define__geometry                    --- #
        # ------------------------------------------------- #
        if ( "geometry_type"  in card ):
            ret = geo.define__geometry  ( dimtags=dimtags, table=table_loc )
            dimtags = { **dimtags, **ret }
        # ------------------------------------------------- #
        # --- [2-2] boolean__fromTable                  --- #
        # ------------------------------------------------- #
        if ( "boolean_type"   in card ):
            ret = bol.boolean__fromTable( dimtags=dimtags, table=table_loc )
            dimtags = { **dimtags, **ret }
        # ------------------------------------------------- #
        # --- [2-3] affine__transform                   --- #
        # ------------------------------------------------- #
        if ( "transform_type" in card ):
            ret = tra.transform__affine ( dimtags=dimtags, table=table_loc )
            dimtags = { **dimtags, **ret }

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
    dimtags = geometrize__fromTable( inpFile="test/geometry3.conf" )
    
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
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
