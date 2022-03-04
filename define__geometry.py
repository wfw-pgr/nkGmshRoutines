import numpy as np
import os, sys, re
import gmsh
import nkGmshRoutines.generate__sector180 as sec


# ========================================================= #
# ===  define__geometry                                 === #
# ========================================================= #
def define__geometry( inpFile="test/geometry.conf", keys=None, names=None, \
                      table=None, dimtags=None ):

    geometry_types = [ "quadring", "cube", "cylinder", "pipe", "sphere", \
                       "hollowpipe", "polygon", "prism", "revolve", "rotated" ]
    
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
    if ( dimtags is None ):
        dimtags = {}
    
    # ------------------------------------------------- #
    # --- [2] make geometry for every key           --- #
    # ------------------------------------------------- #
    for key in keys:
        card = table[key]

        if ( not( "geometry_type" in card ) ):
            continue
        
        # ------------------------------------------------- #
        # --- [2-1] sector shape                        --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "quadring" ):
            dimtags[key] = define__QuadRing( card=card )
        # ------------------------------------------------- #
        # --- [2-2] cube shape                          --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "cube"     ):
            dimtags[key] = define__cube    ( card=card )
        # ------------------------------------------------- #
        # --- [2-3] cylinder shape                      --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in [ "cylinder", "pipe" ] ):
            dimtags[key] = define__cylinder( card=card )
        # ------------------------------------------------- #
        # --- [2-4] hollow pipe shape                   --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "hollowpipe" ):
            dimtags[key] = define__hollowPipe( card=card )
        # ------------------------------------------------- #
        # --- [2-5] sphere  shape                       --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "sphere"   ):
            dimtags[key] = define__sphere  ( card=card )
        # ------------------------------------------------- #
        # --- [2-6] polygon  shape                      --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["polygon","prism"]  ):
            dimtags[key] = define__polygon ( card=card )
        # ------------------------------------------------- #
        # --- [2-7] rovolve  shape                      --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["revole","rotated"]  ):
            dimtags[key] = define__revolve ( card=card )

        # ------------------------------------------------- #
        # --- [2-x] exception                           --- #
        # ------------------------------------------------- #
        if ( not( card["geometry_type"].lower() in geometry_types ) ):
            print( "[define__geometry.py] unknown geometry_type :: {0} "\
                   .format( card["geometry_type"] ) )
            sys.exit()

    return( dimtags )


# ========================================================= #
# ===  define__cube                                     === #
# ========================================================= #

def define__cube( card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__cube] card == ???" )
    if ( not( "xc"        in card ) ): card["xc"]        = 0.0
    if ( not( "yc"        in card ) ): card["yc"]        = 0.0
    if ( not( "zc"        in card ) ): card["zc"]        = 0.0
    if ( not( "centering" in card ) ): card["centering"] = True
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    xc,yc,zc  = card["xc"], card["yc"], card["zc"]
    if ( card["centering"] ):
        xc,yc,zc  = xc-0.5*card["wx"], yc-0.5*card["wy"], zc-0.5*card["wz"]
    dx,dy,dz  = card["wx"]           , card["wy"]       , card["wz"]
    ret       = gmsh.model.occ.addBox( xc, yc, zc, dx, dy, dz )
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
    if ( not( "xc"        in card ) ): card["xc"]        = 0.0
    if ( not( "yc"        in card ) ): card["yc"]        = 0.0
    if ( not( "zc"        in card ) ): card["zc"]        = 0.0
    if ( not( "centering" in card ) ): card["centering"] = True
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    xc,yc,zc  = card["xc"], card["yc"], card["zc"]
    if ( card["centering"] ):
        xc,yc,zc  = xc-0.5*card["dx"], yc-0.5*card["dy"], zc-0.5*card["dz"]
    dx,dy,dz  = card["dx"]               , card["dy"]               , card["dz"]
    r1        = card["r1"]
    if ( "r2" in card ):
        r2    = card["r2"]
    else:
        r2    = None
    if ( r2 is not None ):
        ret   = gmsh.model.occ.addCone    ( xc, yc, zc, dx, dy, dz, r1, r2 )
    else:
        ret   = gmsh.model.occ.addCylinder( xc, yc, zc, dx, dy, dz, r1     )
    ret       = [(3,ret)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__hollowPipe                               === #
# ========================================================= #

def define__hollowPipe( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__hollowPipe] card == ???" )
    if ( not( "xc"        in card ) ): card["xc"]        = 0.0
    if ( not( "yc"        in card ) ): card["yc"]        = 0.0
    if ( not( "zc"        in card ) ): card["zc"]        = 0.0
    if ( not( "centering" in card ) ): card["centering"] = True
    
    # ------------------------------------------------- #
    # --- [2] prepare parameters                    --- #
    # ------------------------------------------------- #
    if ( card["centering"] ):
        Opt   = [ card["xc"]-0.5*card["dx"], \
                  card["yc"]-0.5*card["dy"], \
                  card["zc"]-0.5*card["dz"]  ]
    else:
        Opt   = [ card["xc"], card["yc"], card["zc"] ]
    axis      = [ card["dx"], card["dy"], card["dz"] ]
    if ( "r1" in card ):
        r1    = card["r1"]
    else:
        r1    = 0.0
    if ( "r2" in card ):
        r2    = card["r2"]
    else:
        sys.exit( "[define__hollowPipe] r2 == ??? [ERROR] " )
        
    # ------------------------------------------------- #
    # --- [3] call generate__hollowPipe             --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.generate__hollowPipe as ghp
    ret   = ghp.generate__hollowPipe( r1=r1, r2=r2, Opt=Opt, axis=axis )
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [4] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__polygon                                  === #
# ========================================================= #

def define__polygon( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__polygon] card == ???" )
    key_of_card = card.keys()
    vertex_list = []
    pattern     = "vertex[0-9]*"
    for key in key_of_card:
        ret = re.match( pattern, key )
        if ( ret is None ):
            pass
        else:
            vertex_list.append( card[key] )
    nVertex     = len( vertex_list )
    if ( nVertex < 3 ):
        print( "[define__polygon] too small nVertex number... [ERROR]" )
        sys.exit()
        
    # ------------------------------------------------- #
    # --- [2] prepare arguments                     --- #
    # ------------------------------------------------- #
    vertex         = np.array( vertex_list )
    extrude_vector = card["axis"]
    
    # ------------------------------------------------- #
    # --- [3] call generate__polygon             --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.generate__polygon as ply
    ret   = ply.generate__polygon( vertex    =vertex, extrude_vector=extrude_vector, \
                                   returnType="dimtags" )
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [4] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__revolve                                  === #
# ========================================================= #

def define__revolve( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__revolve] card == ???" )
    if ( not( "xc"        in card ) ): card["xc"]        = 0.0
    if ( not( "yc"        in card ) ): card["yc"]        = 0.0
    if ( not( "zc"        in card ) ): card["zc"]        = 0.0
    if ( not( "centering" in card ) ): card["centering"] = True
    
    key_of_card = card.keys()
    vertex_list = []
    pattern     = "vertex[0-9]*"
    for key in key_of_card:
        ret = re.match( pattern, key )
        if ( ret is None ):
            pass
        else:
            vertex_list.append( card[key] )
    nVertex     = len( vertex_list )
    if ( nVertex < 3 ):
        print( "[define__revolve] too small nVertex number... [ERROR]" )
        sys.exit()
        
    # ------------------------------------------------- #
    # --- [2] prepare arguments                     --- #
    # ------------------------------------------------- #
    vertex         = np.array( vertex_list )
    origin         = np.array( [ card["xc"], card["yc"], card["zc"] ] )
    axis           = card["axis"]
    angle          = card["angle"]
    
    # ------------------------------------------------- #
    # --- [3] call generate__revolve             --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.generate__revolve as ply
    ret   = ply.generate__revolve( vertex    =vertex, axis=axis, angle=angle, \
                                   returnType="dimtags" )
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [4] affine__transform                     --- #
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
    if ( not( "xc" in card ) ): card["xc"] = 0.0
    if ( not( "yc" in card ) ): card["yc"] = 0.0
    if ( not( "zc" in card ) ): card["zc"] = 0.0
    
    # ------------------------------------------------- #
    # --- [2] call addSphere                        --- #
    # ------------------------------------------------- #
    xc,yc,zc  = card["xc"], card["yc"], card["zc"]
    rc        = card["r1"]
    ret       = gmsh.model.occ.addSphere( xc, yc, zc, rc )
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
    zF   = card["z1"]
    zH   = card["z2"] - card["z1"]
    ret1 = sec.generate__sector180( r1=card["r1"], r2=card["r2"], side="+", zoffset=zF,\
                                    height=zH, fuse=True, defineVolu=True )
    ret2 = sec.generate__sector180( r1=card["r1"], r2=card["r2"], side="-", zoffset=zF,\
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
    if ( ( "move.r.r" in card ) and ( "move.r.th" in card ) ):
        dx         += card["move.r.r"] * np.cos( card["move.r.th"] * deg2rad )
        dy         += card["move.r.r"] * np.sin( card["move.r.th"] * deg2rad )
    if ( "move.x" in card ):
        dx         += card["move.x"]
    if ( "move.y" in card ):
        dy         += card["move.y"]
    if ( "move.z" in card ):
        dz         += card["move.z"]
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
    

