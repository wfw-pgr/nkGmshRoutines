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
            dimtags[key] = define__QuadRing( card=card )
        
        # ------------------------------------------------- #
        # --- [2-2] cube shape                          --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "cube"     ):
            dimtags[key] = define__cube( card=card )

        # ------------------------------------------------- #
        # --- [2-2] cylinder shape                      --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "cylinder" ):
            dimtags[key] = define__cylinder( card=card )

    return( dimtags )


# ========================================================= #
# ===  define__cube                                     === #
# ========================================================= #

def define__cube( card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__cube] card == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    x1,x2,x3  = card["xc"]-0.5*card["wx"], card["yc"]-0.5*card["wy"], card["zc"]-0.5*card["wz"]
    dx,dy,dz  = card["wx"]               , card["wy"]               , card["wz"]
    ret       = gmsh.model.occ.addBox( x1, x2, x3, dx, dy, dz )
    ret       = [(3,ret)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__cylinder                                 === #
# ========================================================= #

def define__cylinder( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__cylinder] card == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    x1,x2,x3  = card["xc"]-0.5*card["dx"], card["yc"]-0.5*card["dy"], card["zc"]-0.5*card["dz"]
    dx,dy,dz  = card["dx"]               , card["dy"]               , card["dz"]
    r1        = card["r1"]
    if ( "r2" in card ):
        r2    = card["r2"]
        ret   = gmsh.model.occ.addCone    ( x1, x2, x3, dx, dy, dz, r1, r2 )
    else:
        ret   = gmsh.model.occ.addCylinder( x1, x2, x3, dx, dy, dz, r1     )
    ret       = [(3,ret)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__sphere                                   === #
# ========================================================= #

def define__sphere( card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__sphere] card == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call addSphere                        --- #
    # ------------------------------------------------- #
    x1,x2,x3  = card["xc"], card["yc"], card["zc"]
    rc        = card["r1"]
    ret       = gmsh.model.occ.addSphere( x1, x2, x3, rc )
    ret       = [(3,ret)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define Quad Ring                                 === #
# ========================================================= #

def define__QuadRing( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__QuadRing] card == ???" )
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    zH   = card["z2"] - card["z1"]
    ret1 = sec.generate__sector180( r1=card["r1"], r2=card["r2"], side="+", zoffset=card["z1"],\
                                    height=zH, fuse=True, defineVolu=True )
    ret2 = sec.generate__sector180( r1=card["r1"], r2=card["r2"], side="-", zoffset=card["z1"],\
                                    height=zH, fuse=True, defineVolu=True )
    gmsh.model.occ.synchronize()
    ret,fm = gmsh.model.occ.fuse( ret1, ret2 )
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    
    # ------------------------------------------------- #
    # --- [4] return                                --- #
    # ------------------------------------------------- #
    return( ret )
    

# ========================================================= #
# ===  affine__transform                                === #
# ========================================================= #

def affine__transform( target=None, card=None ):

    deg2rad = 1.0 / 180.0 * np.pi
    
    # ------------------------------------------------- #
    # --- [1] arguments                             --- #
    # ------------------------------------------------- #
    if ( card   is None ): sys.exit( "[affine__transform] card   == ???" )
    if ( target is None ): sys.exit( "[affine__transform] target == ???" )
    
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
    if ( ( "move.r" in card ) and ( "move.r.th" in card ) ):
        ptheta      = card["move.r.th"] / 180.0 * np.pi
        dx         += card["move.r.th"] * np.cos( ptheta )
        dy         += card["move.r.th"] * np.sin( ptheta )
        dz         += 0.0
    if ( "move.x" in card ):
        dx         += dx+card["move.x"]
    if ( "move.y" in card ):
        dy         += dy+card["move.y"]
    if ( "move.z" in card ):
        dz         += dz+card["move.z"]
    if ( ( dx != 0.0 ) or ( dy != 0.0 ) or ( dz != 0.0 ) ):
        gmsh.model.occ.translate( target, dx, dy, dz )
    return( target )


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
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMin", 0.1 )
    gmsh.option.setNumber( "Mesh.CharacteristicLengthMax", 0.1 )

    # ------------------------------------------------- #
    # --- [4] post process                          --- #
    # ------------------------------------------------- #
    gmsh.model.occ.synchronize()
    gmsh.model.mesh.generate(3)
    gmsh.write( "msh/model.msh" )
    gmsh.finalize()
    

