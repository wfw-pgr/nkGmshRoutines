import numpy as np
import os, sys, re
import gmsh
import nkGmshRoutines.generate__sector180 as sec

# ========================================================= #
# ===  define__geometry_2d                              === #
# ========================================================= #

def define__geometry_2d( inpFile="test/geometry.conf", keys=None, names=None, \
                         table=None, dimtags=None ):

    geometry_types = [ "point", "line", "line_surf", "point_surf", \
                       "rectangle", "quad", "circle" ]
    
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
        # --- [2-1] add point                           --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "point" ):
            dimtags[key] = define__point( card=card )

        # ------------------------------------------------- #
        # --- [2-2] add line                            --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "line" ):
            dimtags[key] = define__line( dimtags=dimtags, card=card )

        # ------------------------------------------------- #
        # --- [2-3] line 2 surf                         --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "line_surf" ):
            dimtags[key] = define__line_surf( dimtags=dimtags, card=card )

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
        # --- [2-2] circle shape                        --- #
        # ------------------------------------------------- #
        if ( card["geometry_type"].lower() == "circle" ):
            dimtags[key] = define__circle( card=card )

        # ------------------------------------------------- #
        # --- [2-x] exception                           --- #
        # ------------------------------------------------- #
        if ( not( card["geometry_type"].lower() in geometry_types ) ):
            print( "[define__geometry.py] unknown geometry_type :: {0} "\
                   .format( card["geometry_type"] ) )
            sys.exit()

    return( dimtags )


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
# ===  define__line                                    === #
# ========================================================= #

def define__line( dimtags=None, card=None ):
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__line] card == ???" )
    if ( not( "pt1" in card ) or not( "pt2" in card ) ):
        sys.exit( "[define__line] pt1 / pt2 == ??? " )
    
    # ------------------------------------------------- #
    # --- [2] call addCircle                        --- #
    # ------------------------------------------------- #
    
    # ===== under construction ===== #
    
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
    circleL   = gmsh.model.occ.addCircle( xc, yc, zc, rc, zAxis=zAxis )
    lineGroup = gmsh.model.occ.addCurveLoop( [ circleL ] )
    circle    = gmsh.model.occ.addPlaneSurface( [ lineGroup ] )
    ret       = [(3,circle)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    ret    = affine__transform( target=ret, card=card )
    return( ret )




# ========================================================= #
# ===  affine__transform  ( local )                     === #
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
    ret = define__geometry_2d()
    
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
    gmsh.model.mesh.generate(2)
    gmsh.write( "test/model.msh" )
    gmsh.finalize()
    
