import numpy as np
import os, sys
import gmsh

pDim, lDim, sDim, vDim   = 0, 1, 2, 3
dim_, tag_               = 0, 1

# ========================================================= #
# ===  define__nkCube                                   === #
# ========================================================= #

def define__nkCube( card=None ):

    x_, y_, z_ = 0, 1, 2
    
    # ------------------------------------------------- #
    # --- [1] argument check                        --- #
    # ------------------------------------------------- #
    if ( card is None ): sys.exit( "[define__cube] card == ???" )
    if ( not( "xyz0"      in card ) ): card["xyz0"]      = [ 0., 0., 0. ]
    if (    ( "x0"        in card ) ): card["xyz0"][x_]  = 0.0
    if (    ( "y0"        in card ) ): card["xyz0"][y_]  = 0.0
    if (    ( "z0"        in card ) ): card["xyz0"][z_]  = 0.0
    if (    ( "xyz1"      in card ) ): card["dxyz"]      = np.array( card["xyz1"] ) - np.array( card["xyz0"] )
    if ( not( "dxyz"      in card ) ): card["dxyz"]      = [ 1., 1., 1. ]
    if (    ( "dx"        in card ) ): card["dxyz"][x_]  = card["dx"]
    if (    ( "dy"        in card ) ): card["dxyz"][y_]  = card["dy"]
    if (    ( "dz"        in card ) ): card["dxyz"][z_]  = card["dz"]
    if ( not( "centering" in card ) ): card["centering"] = False
    
    # ------------------------------------------------- #
    # --- [2] call generate__sector180              --- #
    # ------------------------------------------------- #
    if ( card["centering"] ):
        card["xyz0"] = np.array( card["xyz0"] ) - 0.5 * np.array( card["dxyz"] )
    entNum    = gmsh.model.occ.addBox( *(card["xyz0"]), *(card["dxyz"]) )
    ret       = [(vDim,entNum)]
    gmsh.model.occ.synchronize()
    
    # ------------------------------------------------- #
    # --- [3] affine__transform                     --- #
    # ------------------------------------------------- #
    affine__transform( target=ret, card=card )
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

