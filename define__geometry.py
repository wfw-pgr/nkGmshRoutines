import numpy as np
import os, sys, re
import gmsh
import nkGmshRoutines.generate__sector180 as sec

# ========================================================= #
# ===  define__geometry                                 === #
# ========================================================= #

def define__geometry( inpFile="test/geometry.conf", keys=None, names=None, \
                      table=None, dimtags=None ):

    geometry_types = [ "quadring", "cube", "cylinder", "pipe", "cylindrical", "sphere", \
                       "hollowpipe", "polygon", "prism", "revolve", "rotated", \
                       "disk", "circle", "circlearc", "quad", "rectangle", \
                       "sector180", "sector90", \
                       "point", "point_surf", "importstep" ]
    
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
        # --- [2-3] cylindrical shape                   --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in [ "cylindrical" ] ):
            dimtags[key] = define__cylindrical( card=card )
        # ------------------------------------------------- #
        # --- [2-4] sphere  shape                       --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "sphere"   ):
            dimtags[key] = define__sphere  ( card=card )
        # ------------------------------------------------- #
        # --- [2-5] polygon  shape                      --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["polygon","prism"]  ):
            dimtags[key] = define__polygon ( card=card )
        # ------------------------------------------------- #
        # --- [2-6] rovolve  shape                      --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["revolve","rotated"]  ):
            dimtags[key] = define__revolve ( card=card )
        # ------------------------------------------------- #
        # --- [2-7] circle  shape                       --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["circle","disk"]  ):
            dimtags[key] = define__circle ( card=card )
        # ------------------------------------------------- #
        # --- [2-7] circle  Arc shape                   --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["circlearc"] ):
            dimtags[key] = define__circleArc( card=card )
        # ------------------------------------------------- #
        # --- [2-7] sector180 shape                     --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["sector180"] ):
            dimtags[key] = define__sector180( card=card )
        # ------------------------------------------------- #
        # --- [2-8] cylinder shape (obsolete)           --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in [ "cylinder", "pipe" ] ):
            dimtags[key] = define__cylinder( card=card )
        # ------------------------------------------------- #
        # --- [2-9] hollow pipe shape (obsolete)        --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "hollowpipe" ):
            dimtags[key] = define__hollowPipe( card=card )
            
        # ------------------------------------------------- #
        # --- [2-1] add point                           --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "point" ):
            dimtags[key] = define__point( card=card )

        # ------------------------------------------------- #
        # --- [2-4] point 2 surf                        --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "point_surf" ):
            dimtags[key] = define__point_surf( dimtags=dimtags, card=card )

        # ------------------------------------------------- #
        # --- [2-1] quad shape                          --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["quad","rectangle"] ):
            dimtags[key] = define__quad( card=card )

        # ------------------------------------------------- #
        # --- [2-1] import shapes from step             --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() in ["importstep"] ):
            ret     = import__occStep( card=card, key=key )
            dimtags = { **dimtags, **ret }
            
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
    if (    ( "wx"        in card ) ): card["dx"]        = card["wx"]
    if (    ( "wy"        in card ) ): card["dy"]        = card["wy"]
    if (    ( "wz"        in card ) ): card["dz"]        = card["wz"]
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    xc,yc,zc  = card["xc"], card["yc"], card["zc"]
    if ( card["centering"] ):
        xc,yc,zc  = xc-0.5*card["dx"], yc-0.5*card["dy"], zc-0.5*card["dz"]
    dx,dy,dz  = card["dx"]           , card["dy"]       , card["dz"]
    ret       = gmsh.model.occ.addBox( xc, yc, zc, dx, dy, dz )
    ret       = [(3,ret)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__cylindrical                              === #
# ========================================================= #

def define__cylindrical( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__cylindrical] card == ???" )
    if ( not( "z1" in card ) ): card["z1"] = 0.0
    if ( not( "z2" in card ) ):
        if   ( "length" in card ):
            card["z2"] = card["z1"] + card["length"]
        elif ( "dz"     in card ):
            card["z2"] = card["z1"] + card["dz"]
        else:
            card["z2"] = 1.0
    if ( not( "theta1" in card ) ): card["theta1"]  =   0.0
    if ( not( "theta2" in card ) ): card["theta2"]  = 360.0
    if   ( ( "rI1" in card ) and ( "rI2" in card ) ):
        rI1 = card["rI1"]
        rI2 = card["rI2"]
    elif ( "rI" in card ):
        rI1 = card["rI"]
        rI2 = card["rI"]
    else:
        rI1 = 0.0
        rI2 = 0.0
    if   ( ( "rO1" in card ) and ( "rO2" in card ) ):
        rO1 = card["rO1"]
        rO2 = card["rO2"]
    elif ( "rO" in card ):
        rO1 = card["rO"]
        rO2 = card["rO"]
    else:
        rO1 = 1.0
        rO2 = 1.0
    z1    , z2     = card["z1"]    , card["z2"]
    theta1, theta2 = card["theta1"], card["theta2"]

    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.generate__cylindrical as cyl
    ret = cyl.generate__cylindrical( rI1=rI1, rI2=rI2, rO1=rO1, rO2=rO2, \
                                     theta1=theta1,theta2=theta2, z1=z1, z2=z2 )
    
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
    dx,dy,dz  = card["dx"], card["dy"], card["dz"]
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
    # --- [3] call generate__revolve                --- #
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
    import nkGmshRoutines.generate__sector180 as sec
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
# ===  define__point                                    === #
# ========================================================= #

def define__point( card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__point] card == ???" )
    if ( not( "x0"    in card ) ): card["x0"]    = 0.0
    if ( not( "y0"    in card ) ): card["y0"]    = 0.0
    if ( not( "z0"    in card ) ): card["z0"]    = 0.0
    
    # ------------------------------------------------- #
    # --- [2] call addCircle                        --- #
    # ------------------------------------------------- #
    x0,y0,z0  = card["x0"], card["y0"], card["z0"]
    point     = gmsh.model.occ.addPoint( x0, y0, z0 )
    ret       = [(0,point)]
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define__point_surf                          === #
# ========================================================= #

def define__point_surf( dimtags=None, card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ):
        sys.exit( "[define__point_surf] card == ???" )
    key_of_card = card.keys()
    vertex_list = []
    pattern     = "point[0-9]*"
    for key in key_of_card:
        ret = re.match( pattern, key )
        if ( ret is None ):
            pass
        else:
            vertex_list.append( card[key] )
    nVertex     = len( vertex_list )
    if ( nVertex < 3 ):
        print( "[define__point_surf] too small nVertex number... [ERROR]" )
        sys.exit()
        
    # ------------------------------------------------- #
    # --- [2] prepare arguments                     --- #
    # ------------------------------------------------- #
    vertex         = np.array( vertex_list )
    
    # ------------------------------------------------- #
    # --- [3] call generate__point_surf        --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.generate__polygon as ply
    ret   = ply.generate__polygon( vertex=vertex, returnType="dimtags" )
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [4] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )

# ========================================================= #
# ===  define__quad                                     === #
# ========================================================= #

def define__quad( card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__quad] card == ???" )
    if ( not( "x0"    in card ) ): card["x0"]    = 0.0
    if ( not( "y0"    in card ) ): card["y0"]    = 0.0
    if ( not( "z0"    in card ) ): card["z0"]    = 0.0
    if ( not( "dx"    in card ) ): card["dx"]    = 0.0
    if ( not( "dy"    in card ) ): card["dy"]    = 0.0
    if ( not( "dz"    in card ) ): card["dz"]    = 0.0
    
    # ------------------------------------------------- #
    # --- [2] call addCircle                        --- #
    # ------------------------------------------------- #
    x0,y0,z0  = card["x0"], card["y0"], card["z0"]
    dx,dy     = card["dx"], card["dy"]
    rect      = gmsh.model.occ.addRectangle( x0, y0, z0, dx, dy )
    ret       = [(2,rect)]
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )




# ========================================================= #
# ===  define__circle                                   === #
# ========================================================= #

def define__circle( card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__circle] card == ???" )
    if ( not( "xc"    in card ) ): card["xc"]    = 0.0
    if ( not( "yc"    in card ) ): card["yc"]    = 0.0
    if ( not( "zc"    in card ) ): card["zc"]    = 0.0
    if ( not( "rc"    in card ) ): card["rc"]    = 1.0
    if ( not( "zAxis" in card ) ): card["zAxis"] = []
    
    # ------------------------------------------------- #
    # --- [2] call addCircle                        --- #
    # ------------------------------------------------- #
    xc,yc,zc  = card["xc"], card["yc"], card["zc"]
    rc        = card["rc"]
    circleL   = gmsh.model.occ.addCircle( xc, yc, zc, rc, zAxis=card["zAxis"] )
    lineGroup = gmsh.model.occ.addCurveLoop( [ circleL ] )
    circle    = gmsh.model.occ.addPlaneSurface( [ lineGroup ] )
    ret       = [(2,circle)]
    gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )



# ========================================================= #
# ===  define__circleArc                                === #
# ========================================================= #

def define__circleArc( card=None ):

    dim_, tag_, lDim, sDim, vDim = 0, 1, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__circleArc] card == ???" )
    if ( not( "x0"      in card ) ): card["x0"]      = 0.0
    if ( not( "y0"      in card ) ): card["y0"]      = 0.0
    if ( not( "z0"      in card ) ): card["z0"]      = 0.0
    if ( not( "delta"   in card ) ): card["delta"]   = [0.0,0.0,1.0]
    if ( not( "r0"      in card ) ): card["r0"]      = 1.0
    if ( not( "th1"     in card ) ): card["th1"]     = 0.0
    if ( not( "th2"     in card ) ): card["th2"]     = 360.0
    if ( not( "surface" in card ) ): card["surface"] = False
    if ( not( "volume"  in card ) ): card["volume"]  = False
    
    # ------------------------------------------------- #
    # --- [2] call addCircle                        --- #
    # ------------------------------------------------- #
    th1, th2  = np.pi / 180.0 * card["th1"], np.pi / 180.0 * card["th2"]
    lineC     = gmsh.model.occ.addCircle( card["x0"], card["y0"], card["z0"], card["r0"], \
                                          angle1=th1, angle2=th2 )
    ret       = [(lDim,lineC)]
    
    if ( card["surface"] or card["volume"] ):
        if ( np.round( np.abs( card["th1"]-card["th2"] ), 10 ) == 360.0 ):
            curveLoop = gmsh.model.occ.addCurveLoop( [ lineC ] )
        else:
            pt0       = gmsh.model.occ.addPoint( card["x0"], card["y0"], card["z0"] )
            gmsh.model.occ.synchronize()
            pt1,pt2   = gmsh.model.getBoundary( [(lDim,lineC)], recursive=True, combined=False )
            line1     = gmsh.model.occ.addLine ( pt0, pt1[tag_] )
            line2     = gmsh.model.occ.addLine ( pt2[tag_], pt0 )
            curveLoop = gmsh.model.occ.addCurveLoop( [line1,lineC,line2] )
        surfNum   = gmsh.model.occ.addPlaneSurface( [ curveLoop ] )
        ret       = [ (sDim,surfNum) ]

    if ( card["volume"] ):
        extruded  = gmsh.model.occ.extrude( ret, *card["delta"] )
        ret       = [ dimtag for dimtag in extruded if dimtag[dim_] == vDim ]
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )


# ========================================================= #
# ===  define sector180                                 === #
# ========================================================= #

def define__sector180( card=None ):

    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    dim_, tag_, lDim, sDim, vDim = 0, 1, 1, 2, 3
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__sector180] card == ???" )
    if ( not( "lc"      in card ) ): card["lc"]      = None
    if ( not( "x0"      in card ) ): card["x0"]      = 0.0
    if ( not( "y0"      in card ) ): card["y0"]      = 0.0
    if ( not( "z0"      in card ) ): card["z0"]      = 0.0
    if ( not( "delta"   in card ) ): card["delta"]   = [0.0,0.0,1.0]
    if ( not( "r1"      in card ) ): card["r1"]      = 0.0
    if ( not( "r2"      in card ) ): card["r2"]      = 1.0
    if ( not( "th1"     in card ) ): card["th1"]     = 0.0
    if ( not( "th2"     in card ) ): card["th2"]     = 360.0
    if ( not( "surface" in card ) ): card["surface"] = False
    if ( not( "volume"  in card ) ): card["volume"]  = False

    origin = [ card["x0"], card["y0"] ]
    z0     = card["z0"]
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    import nkGmshRoutines.generate__sector180 as sec
    if ( card["side"] in ["+","+-","-+"] ):
        ret1 = sec.generate__sector180( lc=card["lc"], \
                                        r1=card["r1"], r2=card["r2"], side="+", zoffset=z0, \
                                        origin=origin, fuse=True, \
                                        defineSurf=True, defineVolu=False )
        ret  = ret1
    if ( card["side"] in ["-","+-","-+"] ):
        ret2 = sec.generate__sector180( lc=card["lc"], \
                                        r1=card["r1"], r2=card["r2"], side="-", zoffset=z0, \
                                        origin=origin, fuse=True, \
                                        defineSurf=True, defineVolu=False )
        ret  = ret1
    gmsh.model.occ.synchronize()
    if ( card["side"] in ["+-","-+"] ):
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
# ===  import__occStep                                  === #
# ========================================================= #

def import__occStep( card=None, key=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[import__occStep] card == ???" )
    if ( not( "stepFile"    in card ) ): sys.exit( "[import__occStep] stepFile == ??? " )
    if ( not( "unit"        in card ) ): card["unit"]        = "M"
    if ( not( "keys"        in card ) ): card["keys"]        = None
    if ( not( "synchronize" in card ) ): card["synchronize"] = True

    # ------------------------------------------------- #
    # --- [2] unit settings                         --- #
    # ------------------------------------------------- #
    # --  new command    -- #
    # gmsh.option.setString( "Geometry.OCCTargetUnit", card["unit"] )
    # -- classic command -- #
    if   ( card["unit"].lower() in [ "m"  ] ):
        scaling = 1.0
    elif ( card["unit"].lower() in [ "mm" ] ):
        scaling = 1.0e-3
    else:
        print( "[define__geometry.py] @ import__occStep(),  unit == ??? [ERROR]" )
        sys.exit()
    gmsh.option.setNumber( "Geometry.OCCScaling", scaling )
    
    # ------------------------------------------------- #
    # --- [3] call importShapes                     --- #
    # ------------------------------------------------- #
    ret       = gmsh.model.occ.importShapes( card["stepFile"] )
    dim       = ret[0][0]
    nEntities = len( ret )
    entities  = [ int(dimtag[1]) for dimtag in ret ]

    if ( card["synchronize"] ): gmsh.model.occ.synchronize()

    # ------------------------------------------------- #
    # --- [4] naming                                --- #
    # ------------------------------------------------- #
    if ( card["keys"] is None ):
        if ( nEntities == 1 ):
            card["keys"] = [ key ]
        else:
            baseName     = key + ".{0:" + len( str(nEntities) ) + "}"
            card["keys"] = [ baseName.format( ik+1 ) for ik in range( nEntities ) ]
    ret_dimtags = { card["keys"][ik]:[ret[ik]] for ik in range( nEntities ) }

    # ------------------------------------------------- #
    # --- [5] affine__transform                     --- #
    # ------------------------------------------------- #
    for key in ret_dimtags.keys():
        affine__transform( target=ret_dimtags[key], card=card )

    # ------------------------------------------------- #
    # --- [6] display information                   --- #
    # ------------------------------------------------- #
    print()
    print( "-"*30 + "   [import__occStep.py]    " + "-"*30 )
    print()
    print( "[import__occStep.py] inpFile    == {0}".format( card["stepFile"] ) )
    print( "[import__occStep.py] dim        == {0}".format( dim              ) )
    print( "[import__occStep.py] nEntities  == {0}".format( nEntities        ) )
    print( "[import__occStep.py] entities   == {0}".format( entities         ) )
    print()
    print( "-"*88 )
    print()
    return( ret_dimtags )





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
    gmsh.write( "test/model.msh" )
    gmsh.finalize()
    

