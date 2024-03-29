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
                           keys=None, names=None, table=None, setEntityName=False, verbose=True ):
    
    # ------------------------------------------------- #
    # --- [1] load table                            --- #
    # ------------------------------------------------- #
    if ( dimtags is None ):
        dimtags = {}
    if ( table is None ):
        import nkUtilities.load__keyedTable as lkt
        table = lkt.load__keyedTable( inpFile=inpFile )
        print( table )
    if ( keys  is None ):
        keys  = list(   table.keys() )
    if ( names is None ):
        names = list( ( table[keys[0]] ).keys() )
    
    # ------------------------------------------------- #
    # --- [2] make geometry for every key           --- #
    # ------------------------------------------------- #
    for key in keys:
        card      = table[key]
        table_loc = { key:card }

        if ( verbose ):
            print()
            print( " key    :: ", key  )
            print( " card   :: ", card )
            print( "dimtags :: ", dimtags )
        
        # ------------------------------------------------- #
        # --- [2-1] define__geometry                    --- #
        # ------------------------------------------------- #
        if ( "geometry_type"  in card ):
            ret     = geo.define__geometry  ( dimtags=dimtags, table=table_loc )
            dimtags = { **dimtags, **ret }
            nop     = False
        # ------------------------------------------------- #
        # --- [2-2] boolean__fromTable                  --- #
        # ------------------------------------------------- #
        if ( "boolean_type"   in card ):
            ret     = bol.boolean__fromTable( dimtags=dimtags, table=table_loc )
            dimtags = { **dimtags, **ret }
            nop     = False
        # ------------------------------------------------- #
        # --- [2-3] affine__transform                   --- #
        # ------------------------------------------------- #
        if ( "transform_type" in card ):
            ret     = tra.transform__affine ( dimtags=dimtags, table=table_loc )
            nop     = False
        # ------------------------------------------------- #
        # --- [2-x] exception                           --- #
        # ------------------------------------------------- #
        if ( nop ):
            sys.exit( "[geometrize__fromTable.py] None-Operation with key :: {0}".format( key ) )

    if ( verbose ):
        print( "dimtags :: ", dimtags )

    # ------------------------------------------------- #
    # --- [3] set Entity Name                       --- #
    # ------------------------------------------------- #
    if ( setEntityName ):
        keys = list( dimtags.keys() )
        for key in keys:
            if ( len( dimtags[key] ) == 1 ):
                dim, tag = dimtags[key][0]
                gmsh.model.setEntityName( dim, tag, key )

    # ------------------------------------------------- #
    # --- [4] return                                --- #
    # ------------------------------------------------- #
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
    dimtags = geometrize__fromTable( inpFile="test/geometry4.conf" )
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
    gmsh.write( "test/example.msh" )
    gmsh.write( "test/example.stp" )
    gmsh.finalize()
