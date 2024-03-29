import numpy as np
import os, sys
import gmsh


# ========================================================= #
# ===  transform__affine                                === #
# ========================================================= #
def transform__affine( inpFile="test/transform.conf", dimtags=None, keys=None, \
                       names=None, table=None ):

    # ------------------------------------------------- #
    # --- [1] load table                            --- #
    # ------------------------------------------------- #
    if ( dimtags is None ):
        sys.exit( "[transform__affine.py] dimtags == ??? [ERROR]" )
    if ( table is None ):
        import nkUtilities.load__keyedTable as lkt
        table = lkt.load__keyedTable( inpFile=inpFile )
    if ( keys  is None ):
        keys  = list(   table.keys() )
    if ( names is None ):
        names = list( ( table[keys[0]] ).keys() )
    
    # ------------------------------------------------- #
    # --- [2] affine transform for every key        --- #
    # ------------------------------------------------- #
    for key in keys:
        card = table[key]
        if ( "transform_type" in card ):
            if ( card["transform_type"].lower() == "affine" ):
                ret = affine__transform( dimtags=dimtags, card=card )
                    
    return()


# ========================================================= #
# ===  each transform :: affine__transform              === #
# ========================================================= #

def affine__transform( dimtags=None, card=None ):

    deg2rad = 1.0 / 180.0 * np.pi
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( card    is None ): sys.exit( "[affine__transform] card   == ???" )
    if ( dimtags is None ): sys.exit( "[affine__transform] dimtags == ???" )

    target = []
    for ik,key in enumerate( card["targetKeys"] ):
        target += dimtags[key]
    
    # ------------------------------------------------- #
    # --- [2] rotate object                         --- #
    # ------------------------------------------------- #
    if ( "rot.x" in card ):
        gmsh.model.occ.rotate( target, 0,0,0, 1,0,0, card["rot.x"]*deg2rad )
    if ( "rot.y" in card ):
        gmsh.model.occ.rotate( target, 0,0,0, 0,1,0, card["rot.y"]*deg2rad )
    if ( "rot.z" in card ):
        gmsh.model.occ.rotate( target, 0,0,0, 0,0,1, card["rot.z"]*deg2rad )

    # ------------------------------------------------- #
    # --- [3] translate object                      --- #
    # ------------------------------------------------- #
    dx, dy, dz = 0.0, 0.0, 0.0
    if ( ( "move.r.r" in card ) and ( "move.r.th" in card ) ):
        dx += card["move.r.r"] * np.cos( card["move.r.th"] * deg2rad )
        dy += card["move.r.r"] * np.sin( card["move.r.th"] * deg2rad )
    if ( "move.x" in card ):
        dx += card["move.x"]
    if ( "move.y" in card ):
        dy += card["move.y"]
    if ( "move.z" in card ):
        dz += card["move.z"]
    if ( ( dx != 0.0 ) or ( dy != 0.0 ) or ( dz != 0.0 ) ):
        gmsh.model.occ.translate( target, dx, dy, dz )
    return( target )
    
    
# ========================================================= #
# ===   Execution of Pragram                            === #
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
    table   = { "cube01": { "geometry_type":"cube", "xc":0.0, "yc":0.0, "zc":0.0, \
                            "wx":1.0, "wy":1.0, "wz":1.0, "centering":False },
                "cube02": { "geometry_type":"cube", "xc":1.0, "yc":1.0, "zc":1.0, \
                            "wx":1.0, "wy":1.0, "wz":1.0, "centering":False } }
    import nkGmshRoutines.define__geometry as dgm
    dimtags = dgm.define__geometry( table=table )
    gmsh.model.occ.synchronize()
    table   = { "group01": { "boolean_type":"regroup", "targetKeys":["cube01","cube02"] } }
    import nkGmshRoutines.boolean__fromTable as bft
    dimtags = bft.boolean__fromTable( table=table, dimtags=dimtags )

    table   = { "transform1": { "transform_type":"affine", "targetKeys":["group01"], \
                                "rot.z":0.0, "move.x":0.1 } }
    transform__affine( dimtags=dimtags, table=table )
    
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
    gmsh.write( "test/transform_test.msh" )
    gmsh.finalize()
    
